from fireworks.flumina.config import get_api_key
import httpx
from typing import Any, Dict, Optional


# Helper function to format the exception message
def handle_http_status_error(error: httpx.HTTPStatusError) -> None:
    response = error.response

    # Check if the response has a JSON content-type
    if response.headers.get("Content-Type") == "application/json":
        try:
            # Attempt to parse the JSON and use the 'message' field
            error_message = response.json().get("message", response.text)
        except ValueError:
            # Fallback to response text if JSON parsing fails
            error_message = response.text
    else:
        # Use the raw text for non-JSON responses
        error_message = response.text

    # Raise the exception with the custom error message
    raise httpx.HTTPStatusError(
        f"Error response {response.status_code} while requesting {response.url}: {error_message}",
        request=error.request,
        response=response,
    )


# **************************** Accounts ****************************


async def list_accounts() -> Dict[str, Any]:
    url = "https://api.fireworks.ai/v1/accounts"

    headers = {"Authorization": f"Bearer {get_api_key()}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


# **************************** Models ****************************


async def list_models(
    account_id: str, pageToken: Optional[str] = None
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/models"
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    params = {"pageToken": pageToken} if pageToken is not None else {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def get_model(account_id: str, model_id: str) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}"
    headers = {"Authorization": f"Bearer {get_api_key()}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def create_model(
    account_id: str, model_id: str, model_data: Dict[str, Any]
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/models"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }
    data = {
        "modelId": model_id,
        "model": model_data,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def get_model_upload_endpoint(
    account_id: str, model_id: str, filename_to_size: Dict[str, int]
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:getUploadEndpoint"
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    json = {
        "filenameToSize": filename_to_size,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def validate_model_upload(account_id: str, model_id: str) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}:validateUpload"
    headers = {"Authorization": f"Bearer {get_api_key()}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def delete_model(account_id: str, model_id: str) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/models/{model_id}"
    headers = {"Authorization": f"Bearer {get_api_key()}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


# **************************** Deployments ****************************


async def list_deployments(
    account_id: str, pageToken: Optional[str] = None
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments"
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    params = {"pageToken": pageToken} if pageToken is not None else {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def get_deployment(account_id: str, deployment_id: str) -> Dict[str, Any]:
    url = (
        f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}"
    )
    headers = {"Authorization": f"Bearer {get_api_key()}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def create_deployment(
    account_id: str, deployment_data: Dict[str, Any]
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=deployment_data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


async def delete_deployment(
    account_id: str, deployment_id: str, hard: Optional[bool] = None
) -> Dict[str, Any]:
    url = (
        f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}"
    )
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    params = {"hard": hard} if hard is not None else {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


# ******************************* Deployed Models ********************************


async def create_deployed_model(
    account_id: str, deployed_model_data: Dict[str, Any]
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/deployedModels"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=deployed_model_data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)


# Delete deployed model
async def delete_deployed_model(
    account_id: str, deployed_model_id: str
) -> Dict[str, Any]:
    url = f"https://api.fireworks.ai/v1/accounts/{account_id}/deployedModels/{deployed_model_id}"
    headers = {"Authorization": f"Bearer {get_api_key()}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as error:
        handle_http_status_error(error)
