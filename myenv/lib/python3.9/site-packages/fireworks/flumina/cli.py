from fireworks.flumina.config import get_api_key, set_api_key
from fireworks.flumina.crud import (
    list_accounts,
    list_models,
    get_model,
    create_model,
    get_model_upload_endpoint,
    validate_model_upload,
    delete_model,
    list_deployments,
    get_deployment,
    create_deployment,
    delete_deployment,
    create_deployed_model,
)
from fireworks.flumina.exec import exec_flumina_script
from fireworks.flumina.logger import get_logger
from fireworks.flumina.openapi import generate_curl_commands
from fireworks.flumina.util import log_time

import argparse
import asyncio
from gitignore_parser import parse_gitignore
import httpx
import json
import importlib.resources
import os
import shutil
import socket
import stat
import sys
from tabulate import tabulate
import textwrap
import time
import traceback
import torch
import tqdm
from typing import Any, Dict, List, Optional, Tuple


def flumina_validate(args):
    file_path = os.getcwd()
    world_size = args.world_size
    master_addr = "127.0.0.1"
    master_port = _find_open_port()

    # Validate fireworks.json setup before spawning processes
    _validate_setup(file_path)

    # Determine available GPUs for round-robin assignment
    available_gpus = torch.cuda.device_count()
    if available_gpus < world_size:
        get_logger().warning(
            f"Requested {world_size} processes, but only {available_gpus} GPUs are available. "
            "Some processes will share the same GPU."
        )

    # Launch worker processes for validation using torch.multiprocessing
    processes = []
    try:
        # Spawn processes and add to the list
        torch.multiprocessing.spawn(
            flumina_worker,
            args=(file_path, world_size, master_addr, master_port, available_gpus),
            nprocs=world_size,
            join=True
        )
        print(
            "Flumina validation successful! Now you can upload the model to Fireworks "
            "with a command like `flumina deploy my-model-name`"
        )

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully by terminating all processes
        print("\nKeyboardInterrupt received. Terminating all subprocesses...")
        for p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(-1)

    except Exception as e:
        get_logger().error(f"Validation failed: {str(e)}")
        sys.exit(-1)

    finally:
        # Ensure that any remaining active subprocesses are killed
        for p in processes:
            if p.is_alive():
                p.terminate()


def _find_open_port():
    """Finds an open port on the host system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def _validate_setup(file_path):
    """Validates the fireworks.json and flumina.py setup before running validation."""
    with log_time("Validating fireworks.json"):
        fw_json_path = os.path.join(file_path, "fireworks.json")
        if not os.path.exists(fw_json_path):
            get_logger().error(
                "fireworks.json does not exist in the current directory. Ensure "
                "you have run flumina init in this directory"
            )
            sys.exit(-1)

        with open(fw_json_path, "r") as f:
            loaded_fw_json = json.load(f)
            if loaded_fw_json.get("_is_flumina_model", None) != True:
                get_logger().error(
                    "fireworks.json did not have correct _is_flumina_model. Ensure "
                    "you have run flumina init in this directory"
                )
                sys.exit(-1)

def flumina_worker(rank, file_path, world_size, master_addr, master_port, available_gpus):
    """Worker function to run exec_flumina_script in a distributed setting."""
    os.environ["RANK"] = str(rank)
    os.environ["WORLD_SIZE"] = str(world_size)
    os.environ["MASTER_ADDR"] = master_addr
    os.environ["MASTER_PORT"] = str(master_port)

    # Assign a CUDA device based on the rank (round-robin across available GPUs)
    cuda_device = rank % available_gpus
    torch.cuda.set_device(torch.device("cuda", cuda_device))

    script_path = os.path.join(file_path, "flumina.py")
    if not os.path.exists(script_path):
        get_logger().error(
            "flumina.py does not exist in the current directory. Ensure "
            "you have run flumina init in this directory"
        )
        sys.exit(-1)

    try:
        # Run the actual script validation
        exported_mod, _ = exec_flumina_script(script_path)

        if len(exported_mod.path_to_method_name) == 0:
            get_logger().error(
                "Flumina module did not define any endpoint paths. Ensure you "
                "define at least one path with the @path decorator on a method"
            )
            sys.exit(-1)

    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        get_logger().error(f"Validation script failed on rank {rank}:\n{error_message}")
        sys.exit(-1)


def flumina_init_app(args):
    if os.listdir() and not args.allow_non_empty:
        get_logger().error(
            "Tried to initialize Flumina app in a non-empty directory. "
            "Pass --allow-non-empty to bypass this check"
        )
        sys.exit(-1)

    static_assets = {
        "flumina_py_template.txt": "flumina.py",
        "fluminaignore_template.txt": ".fluminaignore",
        "requirements.txt": "requirements.txt",
    }

    for template_filename, dest_filename in static_assets.items():
        with importlib.resources.open_text(
            "fireworks.flumina.assets", template_filename
        ) as f:
            flumina_py_template = f.read()

        cwd = os.getcwd()
        with open(os.path.join(cwd, dest_filename), "w") as f:
            f.write(flumina_py_template)

    fireworks_json = {"_is_flumina_model": True}
    with open(os.path.join(cwd, "fireworks.json"), "w") as f:
        json.dump(fireworks_json, f)

    os.mkdir(os.path.join(cwd, "data"))


def _copy_directory_contents(src_dir, dest_dir):
    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Loop through all files and directories in the source directory
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)

        # If it's a directory, recursively copy it
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
        # If it's a file, copy it to the destination
        else:
            shutil.copy2(src_item, dest_item)


def flumina_init_from_hf(args):
    # Delegate to flumina_init to set up initial structure
    flumina_init(args)

    # Download specified model from HF hub
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        get_logger().exception("")
        get_logger().error(
            f"Failed to import huggingface_hub. Ensure you have it "
            f"installed, e.g. via pip install huggingface_hub"
        )

    snapshot_download_path = snapshot_download(repo_id=args.model_repo)

    cwd = os.getcwd()
    # Copy contents of snapshot_download_path into /data
    dest_data_dir = os.path.join(cwd, "data")
    _copy_directory_contents(src_dir=snapshot_download_path, dest_dir=dest_data_dir)

    # Best effort to try to detect the correct model class
    model_repo, model_classname = None, None

    model_index_json_path = os.path.join(dest_data_dir, "model_index.json")
    if os.path.exists(model_index_json_path):
        with open(model_index_json_path, "r") as f:
            loaded_model_index = json.load(f)

        if (
            loaded_model_index.get("_diffusers_version", None) is not None
            and loaded_model_index.get("_class_name", None) is not None
        ):
            model_repo = "diffusers"
            model_classname = loaded_model_index["_class_name"]

    # Overwrite flumina.py to contain the HF template
    with importlib.resources.open_text(
        "fireworks.flumina.assets", "flumina_hf_template.txt"
    ) as f:
        flumina_py_template = f.read()

    assert (model_repo is not None) == (model_classname is not None)
    if model_repo is not None:
        flumina_py_template = flumina_py_template.format(
            model_class_import_str=f"from {model_repo} import {model_classname}",
            model_classname_str=model_classname,
        )
    else:
        flumina_py_template = flumina_py_template.format(
            model_class_import_str="",
            model_classname_str="ModelClassname",
        )

    static_assets = {
        "fluminaignore_template.txt": ".fluminaignore",
        "requirements.txt": "requirements.txt",
    }

    for template_filename, dest_filename in static_assets.items():
        with importlib.resources.open_text(
            "fireworks.flumina.assets", template_filename
        ) as f:
            flumina_py_template = f.read()

        cwd = os.getcwd()
        with open(os.path.join(cwd, dest_filename), "w") as f:
            f.write(flumina_py_template)

    cwd = os.getcwd()
    with open(os.path.join(cwd, "flumina.py"), "w") as f:
        f.write(flumina_py_template)


def flumina_init_addon(args):
    if os.listdir() and not args.allow_non_empty:
        get_logger().error(
            "Tried to initialize Flumina app in a non-empty directory. "
            "Pass --allow-non-empty to bypass this check"
        )
        sys.exit(-1)

    fireworks_json = {
        "_is_flumina_model": True,
        "_flumina_addon_type": args.addon_type,
    }
    with open("fireworks.json", "w") as f:
        json.dump(fireworks_json, f)

    static_assets = {
        "fluminaignore_template.txt": ".fluminaignore",
    }

    for template_filename, dest_filename in static_assets.items():
        with importlib.resources.open_text(
            "fireworks.flumina.assets", template_filename
        ) as f:
            flumina_py_template = f.read()

        cwd = os.getcwd()
        with open(os.path.join(cwd, dest_filename), "w") as f:
            f.write(flumina_py_template)


def extract_components_from_resource_id(path, resource_type: str = "models"):
    # Split the string by '/'
    components = path.split("/")

    # Ensure the format is as expected
    if (
        len(components) >= 4
        and components[0] == "accounts"
        and components[2] == resource_type
    ):
        # Extract the 2nd and 4th components
        second_component = components[1]  # "fireworks"
        fourth_component = components[3]  # "flux-1-dev-controlnet-union"

        return second_component, fourth_component
    else:
        raise ValueError(
            f"Expected resource name in the format accounts/{{account_id}}/{resource_type}/{{resource_id}} "
            f"but got {path}"
        )


def resolve_user_scoped_resource_name(
    name: str, user_account_id: str, resource_type: str
):
    if "/" not in name:
        return user_account_id, name

    account_id, resource_id = extract_components_from_resource_id(name, resource_type)
    return account_id, resource_id


def generate_url(
    model_acct_id: str,
    model_id: str,
    deployment_account_id: Optional[str] = None,
    deployment_id: Optional[str] = None,
    path_override: Optional[str] = None,
):
    if path_override is not None:
        url = f"https://api.fireworks.ai/inference{path_override}"
    else:
        url = f"https://api.fireworks.ai/inference/v1/workflows/accounts/{model_acct_id}/models/{model_id}"

    if deployment_account_id is not None:
        assert deployment_id is not None
        url = f"{url}?deployment=accounts/{deployment_account_id}/deployments/{deployment_id}"

    return url


def _account_id_from_account_name(account_name: str):
    keyword, account_id = account_name.split("/")
    assert keyword == "accounts"
    return account_id


async def resolve_account_id(args):
    # Fetch the list of accounts
    accounts = await list_accounts()

    # Extract account IDs from the account names
    account_ids = [
        _account_id_from_account_name(account["name"])
        for account in accounts["accounts"]
    ]

    # If only one account exists, return it automatically
    if len(account_ids) == 1:
        return account_ids[0]

    # If there are multiple accounts, prompt the user to select one
    print("Please select an account ID from the following options:")
    for idx, account_id in enumerate(account_ids, 1):
        print(f"{idx}. {account_id}")

    # Keep prompting the user until a valid selection is made
    while True:
        try:
            selection = int(input("Enter the number of the account to select: ")) - 1
            if 0 <= selection < len(account_ids):
                return account_ids[selection]
            else:
                print(
                    f"Invalid selection. Please enter a number between 1 and {len(account_ids)}."
                )
        except ValueError:
            print("Invalid input. Please enter a number.")


# Models CRUD
async def _flumina_list_models(args):
    account_id = await resolve_account_id(args)

    models = []

    response_json = await list_models(account_id=account_id)
    models.extend(response_json["models"])
    pageToken = response_json.get("nextPageToken", "")

    while pageToken != "":
        response_json = await list_models(account_id, pageToken=pageToken)
        models.extend(response_json["models"])
        pageToken = response_json.get("nextPageToken", "")

    # account_id, model_id
    to_fetch: List[Tuple[str, str]] = []

    for m in models:
        if m["kind"] not in {"FLUMINA_BASE_MODEL", "FLUMINA_ADDON"}:
            continue

        (
            account_id,
            model_id,
        ) = extract_components_from_resource_id(m["name"])
        to_fetch.append((account_id, model_id))

    gathered_models: List[Dict[str, Any]] = await asyncio.gather(
        *[get_model(account_id, model_id) for account_id, model_id in to_fetch]
    )

    headers = ["account_id", "model_id", "state", "base_model_id", "url_prefix"]
    results: List[Tuple[str, str, str, str, str]] = []

    for m in gathered_models:
        account_id, model_id = extract_components_from_resource_id(m["name"])

        state = m["state"]
        if m["peftDetails"] is not None:
            base_model_account_id, base_model_id = extract_components_from_resource_id(
                m["name"]
            )
            base_model_name = f"{base_model_account_id}/{base_model_id}"
        else:
            base_model_name = ""

        default_deployment: Dict[str, Any] = None
        for ref in m["deployedModelRefs"]:
            if ref["default"]:
                default_deployment = ref
                break

        if default_deployment is not None:
            url_prefix = generate_url(account_id, model_id)
        else:
            url_prefix = f"<no default deployment>"

        results.append((account_id, model_id, state, base_model_name, url_prefix))

    # Print the table
    print(tabulate(results, headers=headers, tablefmt="plain"))


def flumina_list_models(args):
    return asyncio.run(_flumina_list_models(args))


async def _flumina_get_model(args):
    user_account_id = await resolve_account_id(args)
    model_account_id, model_id = resolve_user_scoped_resource_name(
        args.model_name, user_account_id, resource_type="models"
    )

    response_json = await get_model(account_id=model_account_id, model_id=model_id)

    print(json.dumps(response_json))


def flumina_get_model(args):
    return asyncio.run(_flumina_get_model(args))


async def _get_deployments(account_id: str):
    # Step 1: Get all deployments
    deployments = []
    deployments_response = await list_deployments(account_id)
    deployments.extend(deployments_response["deployments"])
    pageToken = deployments_response.get("nextPageToken", "")

    while pageToken != "":
        deployments_response = await list_deployments(account_id, pageToken=pageToken)
        deployments.extend(deployments_response["deployments"])
        pageToken = deployments_response.get("nextPageToken", "")

    # Step 2: Extract baseModel from each deployment and call get_model for it
    get_models_coros = []
    for d in deployments:
        base_model = d["baseModel"]
        account_id, model_id = extract_components_from_resource_id(base_model)
        get_models_coros.append(get_model(account_id, model_id))

    gathered_models = await asyncio.gather(*get_models_coros)

    # Step 3: Filter the models where kind == "FLUMINA_BASE_MODEL"
    filtered_deployments = []
    for i, model in enumerate(gathered_models):
        if model["kind"] == "FLUMINA_BASE_MODEL":
            filtered_deployments.append(deployments[i])

    return filtered_deployments


# Deployments CRUD
async def _flumina_list_deployments(args):
    account_id = await resolve_account_id(args)
    gathered_deployments = await _get_deployments(account_id)

    headers = ["account_id", "deployment_id", "state", "base_model_id", "url_prefix"]
    results: List[Tuple[str, str, str, str, str]] = []

    for d in gathered_deployments:
        account_id, deployment_id = extract_components_from_resource_id(
            d["name"], resource_type="deployments"
        )

        state = d["state"]
        base_model_id = d["baseModel"]
        model_account_id, model_id = extract_components_from_resource_id(
            base_model_id, resource_type="models"
        )

        url_prefix = generate_url(model_account_id, model_id, account_id, deployment_id)

        results.append((account_id, deployment_id, state, base_model_id, url_prefix))

    print(tabulate(results, headers=headers, tablefmt="plain"))


def flumina_list_deployments(args):
    return asyncio.run(_flumina_list_deployments(args))


async def _flumina_get_deployment(args):
    user_account_id = await resolve_account_id(args)
    deployment_account_id, deployment_id = resolve_user_scoped_resource_name(
        args.deployment_name, user_account_id, resource_type="deployments"
    )

    response_json = await get_deployment(
        account_id=deployment_account_id,
        deployment_id=deployment_id,
    )

    print(json.dumps(response_json))


def flumina_get_deployment(args):
    return asyncio.run(_flumina_get_deployment(args))


async def get_openapi_json(
    model_account_id: str, model_id: str, account_id: str, deployment_id: str
):
    path_override = (
        f"/v1/workflows/accounts/{model_account_id}/models/{model_id}/openapi.json"
    )
    openapi_url = generate_url(
        model_account_id, model_id, account_id, deployment_id, path_override
    )

    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            openapi_url, headers=headers, json={}
        )  # Empty JSON body
        response.raise_for_status()  # Raise exception for any HTTP errors
        return response.json()  # Decode the JSON response


async def _flumina_list_endpoints(args):
    account_id = await resolve_account_id(args)
    gathered_deployments = await _get_deployments(account_id)

    headers = ["account_id", "deployment_id", "path", "url"]
    results: List[Tuple[str, str, str, str, str]] = []

    for d in gathered_deployments:
        account_id, deployment_id = extract_components_from_resource_id(
            d["name"], resource_type="deployments"
        )

        base_model_id = d["baseModel"]
        model_account_id, model_id = extract_components_from_resource_id(
            base_model_id, resource_type="models"
        )

        openapi_spec = await get_openapi_json(
            model_account_id=model_account_id,
            model_id=model_id,
            account_id=account_id,
            deployment_id=deployment_id,
        )

        for path, _ in openapi_spec["paths"].items():
            url = generate_url(
                model_account_id, model_id, account_id, deployment_id, path
            )

            results.append((account_id, deployment_id, path, url))

    print(tabulate(results, headers=headers, tablefmt="plain"))


def flumina_list_endpoints(args):
    return asyncio.run(_flumina_list_endpoints(args))


async def _flumina_get_schema(args):
    user_account_id = await resolve_account_id(args)
    deployment_account_id, deployment_id = resolve_user_scoped_resource_name(
        args.deployment_name, user_account_id, resource_type="deployments"
    )
    d = await get_deployment(deployment_account_id, deployment_id)
    base_model_id = d["baseModel"]
    model_account_id, model_id = extract_components_from_resource_id(
        base_model_id, resource_type="models"
    )

    openapi_spec = await get_openapi_json(
        model_account_id=model_account_id,
        model_id=model_id,
        account_id=deployment_account_id,
        deployment_id=deployment_id,
    )

    if args.format == "openapi":
        print(openapi_spec)
    elif args.format == "curl":
        curl_commands = generate_curl_commands(
            openapi_spec,
            api_url="https://api.fireworks.ai/inference",
            default_headers=[f"-H 'Authorization: Bearer {get_api_key()}'"],
            query_params=[
                f"deployment=accounts/{deployment_account_id}/deployments/{deployment_id}"
            ],
        )
        for command in curl_commands:
            print(textwrap.indent(command, "    ")[4:])
            print()
    else:
        raise ValueError(f"Unexpected format {args.format} specified")


def flumina_get_schema(args):
    return asyncio.run(_flumina_get_schema(args))


def read_flumina_config() -> dict:
    # Get the current working directory
    checkpoint_dir = os.getcwd()

    # Construct the path to "fireworks.json"
    config_path = os.path.join(checkpoint_dir, "fireworks.json")

    # Open and read the JSON file
    with open(config_path, "r") as file:
        config_data = json.load(file)

    return config_data


def build_filename_to_size_map() -> Dict[str, int]:
    # Initialize the map to store filename to size mapping
    filename_to_size = {}

    # Get the current working directory
    top_level_dir = os.getcwd()

    # Define the path to the .fluminaignore file
    fluminaignore_path = os.path.join(top_level_dir, ".fluminaignore")

    # Parse the .fluminaignore file if it exists
    ignore_rules = None
    if os.path.exists(fluminaignore_path):
        ignore_rules = parse_gitignore(fluminaignore_path)

    # Use os.walk to recursively traverse files while avoiding symlink loops
    for root, dirs, files in os.walk(top_level_dir, followlinks=False):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip files that match any rules in .fluminaignore
            if ignore_rules and ignore_rules(file_path):
                continue

            # Ensure no infinite traversal through symlinks
            try:
                file_stat = os.lstat(file_path)
                # Skip if it's a symlink
                if stat.S_ISLNK(file_stat.st_mode):
                    continue
            except OSError as e:
                # If there's an issue accessing the file, skip it
                print(f"Error accessing {file_path}: {e}")
                continue

            # Get the file size and add it to the map
            try:
                file_size = os.path.getsize(file_path)
                relative_path = os.path.relpath(file_path, top_level_dir)
                filename_to_size[relative_path] = file_size
            except OSError as e:
                # Handle any issues accessing the file size
                print(f"Error getting size for {file_path}: {e}")

    return filename_to_size


async def upload_file(client: httpx.AsyncClient, filename: str, gcs_uri: str) -> None:
    # Check if the file exists locally
    if not os.path.exists(filename):
        print(f"File {filename} does not exist. Skipping.")
        return filename, False

    try:
        # Get the file size for progress tracking
        file_size = os.path.getsize(filename)

        # Determine the Content-Type (you can improve this by inferring the type from the file extension)
        content_type = "application/octet-stream"  # Use a default content type

        # Open the file in binary mode and upload it in chunks
        with open(filename, "rb") as file:
            with tqdm.tqdm(
                total=file_size, unit="B", unit_scale=True, desc=filename
            ) as progress_bar:
                # Custom async generator to read the file in chunks and update progress
                async def file_chunk_generator():
                    while True:
                        chunk = await asyncio.to_thread(
                            file.read, 1024 * 1024
                        )  # 1 MB chunks
                        if not chunk:
                            break
                        progress_bar.update(len(chunk))
                        yield chunk

                # Perform the upload using a PUT request to the signed GCS URI with streaming
                print(f"Uploading {filename} to Fireworks...")
                headers = {
                    "Content-Type": content_type,
                    "x-goog-content-length-range": f"{file_size},{file_size}",
                }
                response = await client.put(
                    gcs_uri, data=file_chunk_generator(), headers=headers
                )
                print(f"Done uploading {filename} to Fireworks!")

                # Check the response status
                if response.status_code == 200:
                    print(f"Successfully uploaded {filename}")
                    return filename, True
                else:
                    print(
                        f"Failed to upload {filename}. Status: {response.status_code} {response.content}"
                    )
                    return filename, False

    except Exception as e:
        print(f"Error uploading {filename}: {type(e)} {e}")
        return filename, False


async def upload_files_to_gcs(filename_to_uri: Dict[str, str]) -> None:
    async with httpx.AsyncClient(timeout=None) as client:
        # Create a list of coroutines for each file upload
        upload_tasks = [
            upload_file(client, filename, gcs_uri)
            for filename, gcs_uri in filename_to_uri.items()
        ]

        # Run the upload tasks concurrently
        results = await asyncio.gather(*upload_tasks)

        # Check for any failed uploads
        failed = [r for r in results if not r[1]]
        if len(failed) > 0:
            raise RuntimeError(f"Failed to upload files: {[r[0] for r in failed]}")


async def _flumina_create_model(args):
    user_account_id = await resolve_account_id(args)
    model_account_id, model_id = resolve_user_scoped_resource_name(
        args.model_name, user_account_id, resource_type="models"
    )

    # Create model in control plane db
    model = {}

    flumina_config = read_flumina_config()
    if not flumina_config.get("_is_flumina_model", False):
        raise ValueError(f"Current directory does not contain a Flumina model")

    # TODO:
    # displayName
    # description
    # githubUrl
    # huggingFaceUrl

    addon_type = flumina_config.get("_flumina_addon_type", "")
    if addon_type != "":
        if args.base_model is None:
            raise ValueError(f"Must specify --base-model if uploading an addon")
        split = args.base_model.split("/")
        if len(split) != 4 or split[0] != "accounts" or split[2] != "models":
            raise ValueError(
                f"--base-model must be a resource name like accounts/my-account/models/my-model"
            )

        model["kind"] = "FLUMINA_ADDON"
        model["peftDetails"] = {
            "baseModel": args.base_model,
        }
    else:
        model["kind"] = "FLUMINA_BASE_MODEL"
        model["baseModelDetails"] = {
            "worldSize": args.world_size,
        }

    model["public"] = args.public

    created_model = await create_model(
        account_id=model_account_id,
        model_id=model_id,
        model_data=model,
    )

    filename_to_size: Dict[str, int] = build_filename_to_size_map()

    model_upload_endpoint = await get_model_upload_endpoint(
        account_id=model_account_id,
        model_id=model_id,
        filename_to_size=filename_to_size,
    )
    assert len(model_upload_endpoint["filenameToUnsignedUris"]) == 0
    assert len(model_upload_endpoint["filenameToSignedUrls"]) == len(filename_to_size)

    await upload_files_to_gcs(
        filename_to_uri=model_upload_endpoint["filenameToSignedUrls"]
    )

    await validate_model_upload(account_id=model_account_id, model_id=model_id)


def flumina_create_model(args):
    return asyncio.run(_flumina_create_model(args))


async def _flumina_delete_model(args):
    user_account_id = await resolve_account_id(args)
    model_account_id, model_id = resolve_user_scoped_resource_name(
        args.model_name, user_account_id, resource_type="models"
    )

    await delete_model(account_id=model_account_id, model_id=model_id)


def flumina_delete_model(args):
    return asyncio.run(_flumina_delete_model(args))


async def _flumina_create_deployment(args):
    user_account_id = await resolve_account_id(args)
    model_account_id, model_id = resolve_user_scoped_resource_name(
        args.model_name, user_account_id, resource_type="models"
    )

    model_resource_name = f"accounts/{model_account_id}/models/{model_id}"

    ACCELERATOR_MAP = {
        "H100": "NVIDIA_H100_80GB",
        "A100": "NVIDIA_A100_80GB",
    }

    deployment = {
        "baseModel": model_resource_name,
        "minReplicaCount": args.min_replica_count,
        "maxReplicaCount": args.max_replica_count or max(args.min_replica_count, 1),
        "acceleratorType": ACCELERATOR_MAP[args.accelerator_type],
        "enable_addons": True,
    }
    created_deployment = await create_deployment(
        account_id=user_account_id,
        deployment_data=deployment,
    )
    # TODO: improve this prinout
    print(created_deployment)

    return created_deployment


def flumina_create_deployment(args):
    return asyncio.run(_flumina_create_deployment(args))


async def _flumina_create_deployed_addon(args):
    user_account_id = await resolve_account_id(args)
    addon_account_id, addon_id = resolve_user_scoped_resource_name(
        args.addon_name, user_account_id, resource_type="models"
    )
    deployment_account_id, deployment_id = resolve_user_scoped_resource_name(
        args.deployment_name, user_account_id, resource_type="deployments"
    )

    # Validate addon exists and is the correct  type
    addon = await get_model(addon_account_id, addon_id)
    if addon["kind"] != "FLUMINA_ADDON":
        raise ValueError(
            f"Model {addon_account_id}/{addon_id} is not a Flumina addon (it is a {addon['kind']})"
        )
    base_model_account_id, base_model_id = extract_components_from_resource_id(
        addon["peftDetails"]["baseModel"]
    )

    # Validate deployment exists and the underlying model is the correct type
    deployment = await get_deployment(deployment_account_id, deployment_id)
    model_account_id, model_id = extract_components_from_resource_id(
        deployment["baseModel"]
    )
    model = await get_model(model_account_id, model_id)
    if model["kind"] != "FLUMINA_BASE_MODEL":
        raise ValueError(
            f"Model {model_account_id}/{model_id} deployed on deployment {deployment_account_id}/{deployment_id} is not a Flumina model (it is a {model['kind']})"
        )

    if (base_model_account_id != model_account_id) or (base_model_id != model_id):
        raise ValueError(
            f"Addon {addon_account_id}/{addon_id} expected base model {base_model_account_id}/{base_model_id} but deployment {deployment_account_id}/{deployment_id} has model {model_account_id}/{model_id}"
        )

    await create_deployed_model(
        user_account_id,
        deployed_model_data={
            "model": f"accounts/{addon_account_id}/models/{addon_id}",
            "deployment": f"accounts/{deployment_account_id}/deployments/{deployment_id}",
        },
    )

    # TODO: Poll deployed-model status and return its schema
    # TODO: List and delete addons


def flumina_create_deployed_addon(args):
    return asyncio.run(_flumina_create_deployed_addon(args))


async def _flumina_delete_deployment(args):
    user_account_id = await resolve_account_id(args)
    deployment_account_id, deployment_id = resolve_user_scoped_resource_name(
        args.deployment_name, user_account_id, resource_type="deployments"
    )

    await delete_deployment(
        account_id=deployment_account_id, deployment_id=deployment_id
    )


def flumina_delete_deployment(args):
    return asyncio.run(_flumina_delete_deployment(args))


async def _flumina_deploy(args):
    user_account_id = await resolve_account_id(args)
    model_account_id, model_id = resolve_user_scoped_resource_name(
        args.model_name, user_account_id, resource_type="models"
    )

    try:
        # Check for model existence. If it exists, skip upload.
        await get_model(account_id=model_account_id, model_id=model_id)
        get_logger().info(
            f"Model {model_account_id}/{model_id} already exists. Deploying that one..."
        )
        exists = True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            exists = False
        else:
            raise

    if not exists:
        get_logger().info(
            f"Model {model_account_id}/{model_id} does not exist, creating from current directory..."
        )
        if args.skip_validation:
            get_logger().info(f"Skipping app validation as requested")
        else:
            get_logger().info(f"Validating Flumina app...")
            flumina_validate(args)
        get_logger().info(f"Creating Flumina model on Fireworks...")
        await _flumina_create_model(args)

    get_logger().info(f"Deploying Flumina model {model_account_id}/{model_id}...")
    created_deployment = await _flumina_create_deployment(args)
    deployment_acct_id, deployment_id = extract_components_from_resource_id(
        created_deployment["name"], "deployments"
    )

    # Poll until deployment is in READY or failed state
    start_time = time.time()
    while True:
        deployment = await get_deployment(
            account_id=deployment_acct_id,
            deployment_id=deployment_id,
        )
        state = deployment["state"]

        # Overwrite the previous output
        print(
            f"\rWaiting for deployment {deployment_acct_id}/{deployment_id}. Current state: {state}. Elapsed sec: {int(time.time() - start_time)}...",
            end="",
            flush=True,
        )

        if state == "READY":
            break
        elif state in {"STATE_UNSPECIFIED", "CREATING", "UPDATING"}:
            time.sleep(1)
            continue
        else:
            # 'DELETING', 'FAILED', 'DELETED'
            raise RuntimeError(f"Deployment encountered state {state}. Aborting.")

    # Print final status on a new line
    print()  # Move to a new line after the loop

    # Poll until schema endpoint is up
    start_time = time.time()
    while True:
        try:
            print(
                f"\rWaiting for deployment {deployment_acct_id}/{deployment_id} to be reachable. Elapsed sec: {int(time.time() - start_time)}",
                end="",
                flush=True,
            )
            await get_openapi_json(
                model_account_id, model_id, deployment_acct_id, deployment_id
            )
            break
        except httpx.HTTPStatusError as e:
            if e.response.status_code in {404, 503}:
                time.sleep(1)
                continue
            else:
                raise
    print()

    args.deployment_name = f"accounts/{deployment_acct_id}/deployments/{deployment_id}"
    get_logger().info(
        f"Deployment {deployment_acct_id}/{deployment_id} is ready! Try it with the following commands:"
    )
    await _flumina_get_schema(args)


def flumina_deploy(args):
    asyncio.run(_flumina_deploy(args))


# Recursive function to define subcommands
def add_subcommand(subparsers, name, func, help_text, arguments=None):
    parser = subparsers.add_parser(name, help=help_text)
    if arguments:
        for arg_name, arg_params in arguments.items():
            parser.add_argument(arg_name, **arg_params)
    parser.set_defaults(func=func)


def flumina_set_api_key(args):
    if not args.api_key:
        raise ValueError(f"Expected API key to be specified but got {args.api_key}")

    set_api_key(args.api_key)


# Recursive function to create the command tree
def build_command_tree():
    parser = argparse.ArgumentParser(description="Flumina CLI Tool")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="The Flumina command to run"
    )

    # Command tree structure
    commands = {
        "set-api-key": {
            "help": "Set fireworks API key for accessing Fireworks services.",
            "func": flumina_set_api_key,
            "arguments": {
                "api_key": {
                    "type": str,
                    "help": "The Fireworks API key to write to disk.",
                },
            },
        },
        "init": {
            "help": "Initialize a Flumina app",
            "subcommands": {
                "app": {
                    "func": flumina_init_app,
                    "help": "Initialize an empty Flumina app in the current directory",
                    "arguments": {
                        "--allow-non-empty": {
                            "action": "store_true",
                            "help": "Allow initialization of a Flumina app in a non-empty folder",
                        }
                    },
                },
                "from_hf": {
                    "func": flumina_init_from_hf,
                    "help": "Initialize a Flumina app from the specified HF repo in the current directory",
                    "arguments": {
                        "model_repo": {
                            "type": str,
                            "help": "The Hugging Face app name to initialize from",
                        },
                        "--allow-non-empty": {
                            "action": "store_true",
                            "help": "Allow initialization of a Flumina app in a non-empty folder",
                        },
                    },
                },
                "addon": {
                    "func": flumina_init_addon,
                    "help": "Initialize a Flumina addon repo in the current app",
                    "arguments": {
                        "addon_type": {
                            "type": str,
                            "help": "The addon type to initialize. The possible addon types and their schemas are defined by each base model.",
                        },
                        "--allow-non-empty": {
                            "action": "store_true",
                            "help": "Allow initialization of a Flumina app in a non-empty folder",
                        },
                    },
                },
            },
        },
        "validate": {
            "func": flumina_validate,
            "help": "Validate the Flumina repo in the current directory",
            "arguments": {
                "--world-size": {
                    "type": int,
                    "help": "The distributed world size (# of workers) under which to run "
                            "the app for validation",
                    "default": 1,
                }
            },
        },
        "deploy": {
            "func": flumina_deploy,
            "help": "Validate, upload, deploy, and return schema for the current directory.",
            "arguments": {
                "model_name": {
                    "type": str,
                    "help": "The resource name of the model to be created. Can either be a model id (e.g. my-model) "
                    "or a fully-qualified resource name (e.g. accounts/my-account/models/my-model)",
                },
                "--public": {
                    "action": "store_true",
                    "help": "Set this flag to make the model public",
                },
                "--base-model": {
                    "type": str,
                    "help": "Resource id of the base model to associate with this model, "
                    "e.g. accounts/myaccount/models/mymodel. Must be specified if "
                    "uploading an addon model. Should not be specified otherwise.",
                    "default": None,
                },
                "--world-size": {
                    "type": int,
                    "help": "The distributed world size (# of workers) under which the created "
                            "model should run",
                    "default": 1,
                },
                "--min-replica-count": {
                    "type": int,
                    "help": "Minimum number of replicas for the deployment. Defaults to 0.",
                    "default": 0,
                },
                "--max-replica-count": {
                    "type": int,
                    "help": "Maximum number of replicas for the deployment. If not specified, the default is max(min_replica_count, 1)",
                    "default": None,
                },
                "--accelerator-type": {
                    "type": str,
                    "help": "The type of GPU accelerator on which the deployment should be run. One of H100 or A100. Default H100.",
                    "choices": ["H100", "A100"],
                    "default": "H100",
                },
                "--format": {
                    "type": str,
                    "help": "The format in which to print the deployment's schema",
                    "choices": ["openapi", "curl"],
                    "default": "curl",
                },
                "--skip-validation": {
                    "action": "store_true",
                    "help": "Skip app validation. Not recommended -- only intended for use in automated testing scenarios",
                },
            },
        },
        "get": {
            "help": "Get resources",
            "subcommands": {
                "model": {
                    "func": flumina_get_model,
                    "help": "Get Flumina model",
                    "arguments": {
                        "model_name": {
                            "type": str,
                            "help": "Name of the model to get. Can either be a model id (e.g. my-model) "
                            "or a fully-qualified resource name (e.g. accounts/my-account/models/my-model)",
                        },
                    },
                },
                "deployment": {
                    "func": flumina_get_deployment,
                    "help": "Get Flumina deployment",
                    "arguments": {
                        "deployment_name": {
                            "type": str,
                            "help": "Resource ID of the deployment to look up. Can either be a deployment id (e.g. 012456) "
                            "or a fully-qualified resource name (e.g. accounts/my-accounts/deployments/0123456)",
                        },
                    },
                },
                "schema": {
                    "func": flumina_get_schema,
                    "help": "Get schema from a specified Flumina deployment",
                    "arguments": {
                        "deployment_name": {
                            "type": str,
                            "help": "Resource ID of the deployment to look up. Can either be a deployment id (e.g. 012456) "
                            "or a fully-qualified resource name (e.g. accounts/my-accounts/deployments/0123456)",
                        },
                        "--format": {
                            "type": str,
                            "help": "The format in which to print the deployment's schema",
                            "choices": ["openapi", "curl"],
                            "default": "openapi",
                        },
                    },
                },
            },
        },
        "list": {
            "help": "List resources",
            "subcommands": {
                "models": {
                    "func": flumina_list_models,
                    "help": "List Flumina models",
                    "arguments": {
                        "--account_id": {
                            "type": str,
                            "help": "The Fireworks account ID to use for looking up the resources.",
                            "required": False,
                        }
                    },
                },
                "deployments": {
                    "func": flumina_list_deployments,
                    "help": "List Flumina deployments",
                    "arguments": {
                        "--account_id": {
                            "type": str,
                            "help": "The Fireworks account ID to use for looking up the resources.",
                            "required": False,
                        }
                    },
                },
                "endpoints": {
                    "func": flumina_list_endpoints,
                    "help": "List endpoints",
                    "arguments": {
                        "--account_id": {
                            "type": str,
                            "help": "The Fireworks account ID to use for looking up the resources.",
                            "required": False,
                        }
                    },
                },
            },
        },
        "create": {
            "help": "Create resources",
            "subcommands": {
                "model": {
                    "func": flumina_create_model,
                    "help": "Upload the current directory to Fireworks as a Flumina model",
                    "arguments": {
                        "model_name": {
                            "type": str,
                            "help": "The resource name of the model to be created. Can either be a model id (e.g. my-model) "
                            "or a fully-qualified resource name (e.g. accounts/my-account/models/my-model)",
                        },
                        "--base-model": {
                            "type": str,
                            "help": "Resource id of the base model to associate with this model, "
                            "e.g. accounts/myaccount/models/mymodel. Must be specified if "
                            "uploading an addon model. Should not be specified otherwise.",
                            "default": None,
                        },
                        "--public": {
                            "action": "store_true",
                            "help": "Set this flag to make the model public",
                        },
                        "--world-size": {
                            "type": int,
                            "help": "The distributed world size (# of workers) under which the created "
                                    "model should run",
                            "default": 1,
                        },
                    },
                },
                "deployment": {
                    "func": flumina_create_deployment,
                    "help": "Deploy an existing Flumina model",
                    "arguments": {
                        "model_name": {
                            "type": str,
                            "help": "The resource name of the model to deploy. Can either be a model id (e.g. my-model) "
                            "or a fully-qualified resource name (e.g. accounts/my-account/models/my-model)",
                        },
                        "--min-replica-count": {
                            "type": int,
                            "help": "Minimum number of replicas for the deployment. Defaults to 0.",
                            "default": 0,
                        },
                        "--max-replica-count": {
                            "type": int,
                            "help": "Maximum number of replicas for the deployment. If not specified, the default is max(min_replica_count, 1)",
                            "default": None,
                        },
                        "--accelerator-type": {
                            "type": str,
                            "help": "The type of GPU accelerator on which the deployment should be run. One of H100 or A100. Default H100.",
                            "choices": ["H100", "A100"],
                            "default": "H100",
                        },
                    },
                },
                "deployed_addon": {
                    "func": flumina_create_deployed_addon,
                    "help": "Deploy an existing Flumina add-on to an existing deployment",
                    "arguments": {
                        "addon_name": {
                            "type": str,
                            "help": "The resource name of the addon to deploy. Can either be a model id (e.g. my-model) "
                            "or a fully-qualified resource name (e.g. accounts/my-account/models/my-model)",
                        },
                        "deployment_name": {
                            "type": str,
                            "help": "The resource name of the deployment on which to deploy the addon. Can either be a deployment id (e.g. 0123456) "
                            "or a fully-qualified resource name (e.g. accounts/my-account/deployments/0123456)",
                        },
                    },
                },
            },
        },
        "delete": {
            "help": "Delete resources",
            "subcommands": {
                "model": {
                    "func": flumina_delete_model,
                    "help": "Delete an existing Flumina model",
                    "arguments": {
                        "model_name": {
                            "type": str,
                            "help": "Model ID of the model to create",
                        },
                    },
                },
                "deployment": {
                    "func": flumina_delete_deployment,
                    "help": "Delete an existing Flumina deployment",
                    "arguments": {
                        "deployment_name": {
                            "type": str,
                            "help": "Resource ID of the deployment to delete. Can either be a deployment id (e.g. 012456) "
                            "or a fully-qualified resource name (e.g. accounts/my-accounts/deployments/0123456)",
                        },
                    },
                },
            },
        },
    }

    def add_commands(subparsers, command_dict):
        for cmd_name, cmd_info in command_dict.items():
            if "subcommands" in cmd_info:
                sub_parser = subparsers.add_parser(cmd_name, help=cmd_info["help"])
                sub_subparsers = sub_parser.add_subparsers(
                    dest="subcommand", required=True
                )
                add_commands(sub_subparsers, cmd_info["subcommands"])
            else:
                add_subcommand(
                    subparsers,
                    cmd_name,
                    cmd_info["func"],
                    cmd_info["help"],
                    cmd_info.get("arguments"),
                )

    add_commands(subparsers, commands)

    return parser


def main():
    # Build and parse arguments
    parser = build_command_tree()
    args = parser.parse_args()

    # Call the corresponding function
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
