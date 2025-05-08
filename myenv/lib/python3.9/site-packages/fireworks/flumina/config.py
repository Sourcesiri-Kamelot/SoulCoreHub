from fireworks.flumina.logger import get_logger

import configparser
import os


class AuthConfig:
    def __init__(
        self,
        account_id="",
        issuer_url="",
        client_id="",
        cognito_domain="",
        id_token="",
        refresh_token="",
        api_key="",
    ):
        self.account_id = account_id
        self.issuer_url = issuer_url
        self.client_id = client_id
        self.cognito_domain = cognito_domain
        self.id_token = id_token
        self.refresh_token = refresh_token
        self.api_key = api_key

    def load_from_ini(self, filepath):
        """Load configuration from an ini file without a section header."""
        config = configparser.ConfigParser()

        # Read the file by adding a dummy section header if it's missing
        with open(filepath, "r") as file:
            file_content = file.read()

        # If no section header, add a default one
        if not file_content.startswith("["):
            file_content = "[DEFAULT]\n" + file_content

        # Now parse the modified content
        config.read_string(file_content)

        # Retrieve values from the 'DEFAULT' section
        self.account_id = config.get("DEFAULT", "account_id", fallback="")
        self.issuer_url = config.get("DEFAULT", "issuer_url", fallback="")
        self.client_id = config.get("DEFAULT", "client_id", fallback="")
        self.cognito_domain = config.get("DEFAULT", "cognito_domain", fallback="")
        self.id_token = config.get("DEFAULT", "id_token", fallback="")
        self.refresh_token = config.get("DEFAULT", "refresh_token", fallback="")
        self.api_key = config.get("DEFAULT", "api_key", fallback="")


def set_api_key(api_key: str):
    """Directly set the API key in the auth.ini file by writing the `api_key` line."""
    auth_dir_path = os.path.expanduser("~/.fireworks")
    auth_ini_path = os.path.join(auth_dir_path, "auth.ini")

    # Create the directory if it doesn't exist
    if not os.path.exists(auth_dir_path):
        os.makedirs(auth_dir_path)

    # Initialize a list to hold lines of the file
    lines = []

    # Check if the file exists and load the current content
    if os.path.exists(auth_ini_path):
        with open(auth_ini_path, "r") as file:
            lines = file.readlines()

    # Look for the line starting with 'api_key' and replace it
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith("api_key"):
            lines[i] = f"api_key = {api_key}\n"
            key_found = True
            break

    # If the api_key was not found, append it at the end
    if not key_found:
        lines.append(f"api_key = {api_key}\n")

    # Write the updated content back to the file
    with open(auth_ini_path, "w") as file:
        file.writelines(lines)

    get_logger().info(f"API key updated successfully in {auth_ini_path}")


def get_api_key():
    def _api_key_help():
        raise RuntimeError(
            f"Could not find Fireworks API key. Either pass FIREWORKS_API_KEY or API_KEY "
            f"environment variable, or initialize ~/.fireworks/auth.ini, "
            f"for example through `flumina set-api-key <key>`"
        )

    api_key = os.environ.get("FIREWORKS_API_KEY", None)
    if api_key is not None:
        return api_key

    api_key = os.environ.get("API_KEY", None)
    if api_key is not None:
        return api_key

    auth_ini_path = os.path.expanduser("~/.fireworks/auth.ini")
    if not os.path.exists(auth_ini_path):
        _api_key_help()

    ac = AuthConfig()
    ac.load_from_ini(auth_ini_path)

    if ac.api_key == "":
        _api_key_help()

    return ac.api_key
