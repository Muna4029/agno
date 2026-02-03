from __future__ import annotations

import os
from typing import Any, Dict, Optional, Union

import httpx
import requests

from agno.utils.log import log_debug, log_error


def get_access_token() -> str:
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("WHATSAPP_ACCESS_TOKEN is not set")
    return access_token


def get_phone_number_id() -> str:
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    if not phone_number_id:
        raise ValueError("WHATSAPP_PHONE_NUMBER_ID is not set")
    return phone_number_id


def get_media(media_id: str) -> bytes:
    """
    Retrieve media bytes from the Facebook Graph API.

    Args:
        media_id: The ID of the media to retrieve.

    Returns:
        Raw media bytes.

    Raises:
        requests.HTTPError: for non-2xx HTTP responses
        ValueError: if the API response does not contain a media url
        requests.RequestException: for network related errors
    """
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    meta = response.json()

    media_url = meta.get("url")
    if not isinstance(media_url, str) or not media_url:
        raise ValueError("Media url not found in Graph API response")

    media_resp = requests.get(media_url, headers=headers)
    media_resp.raise_for_status()
    return media_resp.content


async def get_media_async(media_id: str) -> bytes:
    """
    Async version of get_media.

    Args:
        media_id: The ID of the media to retrieve.

    Returns:
        Raw media bytes.

    Raises:
        httpx.HTTPStatusError: for non-2xx HTTP responses
        ValueError: if the API response does not contain a media url
        httpx.HTTPError: for network related errors
    """
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        meta = response.json()

        media_url = meta.get("url")
        if not isinstance(media_url, str) or not media_url:
            raise ValueError("Media url not found in Graph API response")

        media_resp = await client.get(media_url, headers=headers)
        media_resp.raise_for_status()
        return media_resp.content


def upload_media(media_data: bytes, mime_type: str, filename: str = "file") -> Union[str, Dict[str, Any]]:
    """
    Upload media for WhatsApp via the Facebook Graph API.

    Returns:
        media_id on success, or {"error": "..."} on failure.
    """
    phone_number_id = get_phone_number_id()
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/media"
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    data = {"messaging_product": "whatsapp", "type": mime_type}

    try:
        from io import BytesIO

        file_data = BytesIO(media_data)
        files = {"file": (filename, file_data, mime_type)}

        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        json_resp = response.json()

        media_id = json_resp.get("id")
        if not isinstance(media_id, str) or not media_id:
            return {"error": "Media ID not found in response", "response": json_resp}

        return media_id
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


async def upload_media_async(media_data: bytes, mime_type: str, filename: str = "file") -> Union[str, Dict[str, Any]]:
    """
    Async version of upload_media.

    Returns:
        media_id on success, or {"error": "..."} on failure.
    """
    phone_number_id = get_phone_number_id()
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/media"
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    data = {"messaging_product": "whatsapp", "type": mime_type}

    try:
        from io import BytesIO

        file_data = BytesIO(media_data)
        files = {"file": (filename, file_data, mime_type)}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            json_resp = response.json()

            media_id = json_resp.get("id")
            if not isinstance(media_id, str) or not media_id:
                return {"error": "Media ID not found in response", "response": json_resp}

            return media_id
    except httpx.HTTPStatusError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


async def send_image_message_async(
    media_id: str,
    recipient: str,
    text: Optional[str] = None,
) -> None:
    """Send an image message to a WhatsApp user (asynchronous version)."""
    log_debug(f"Sending WhatsApp image to {recipient}: {text}")
    phone_number_id = get_phone_number_id()
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "image",
        "image": {"id": media_id, "caption": text},
    }

    try:
        async with httpx.AsyncClient() as client:
            import json

            log_debug(f"Request data: {json.dumps(data, indent=2)}")
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            log_debug(f"Response: {response.text}")
    except httpx.HTTPStatusError as e:
        log_error(f"Failed to send WhatsApp image message: {e}")
        log_error(f"Error response: {e.response.text if hasattr(e, 'response') else 'No response text'}")
        raise
    except Exception as e:
        log_error(f"Unexpected error sending WhatsApp image message: {str(e)}")
        raise


def send_image_message(
    media_id: str,
    recipient: str,
    text: Optional[str] = None,
) -> None:
    """Send an image message to a WhatsApp user (synchronous version)."""
    log_debug(f"Sending WhatsApp image to {recipient}: {text}")
    phone_number_id = get_phone_number_id()
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "image",
        "image": {"id": media_id, "caption": text},
    }

    try:
        import json

        log_debug(f"Request data: {json.dumps(data, indent=2)}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        log_debug(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to send WhatsApp image message: {e}")
        log_error(f"Error response: {e.response.text if hasattr(e, 'response') else 'No response text'}")
        raise
    except Exception as e:
        log_error(f"Unexpected error sending WhatsApp image message: {str(e)}")
        raise
