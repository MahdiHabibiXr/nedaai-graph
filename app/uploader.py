import os
from pathlib import Path
from ufiles import AsyncUFiles
import logfire
import requests
import aiohttp


# configure logfire
logfire.configure(token="x72xM2mT7gVB3xQXm7tHwtbDtkHHDyxPTGzJKyTzpYd0")

ufiles_client = AsyncUFiles(
    ufiles_base_url="https://media.pixy.ir/v1/f",
    usso_base_url="https://sso.pixy.ir",
    api_key=os.getenv("PITOKEN"),
)


async def upload_file(file_path: str | Path, file_name: str | None = None):
    try:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        uploaded_file = await ufiles_client.upload_file(file_path, filename=file_name)
        logfire.info(f"File uploaded : {uploaded_file.url}")
        return uploaded_file.url
    except Exception as e:
        logfire.error(f"Error uploading file: {str(e)}")
        raise


async def tapsage_upload(file_path: str | Path, file_name: str | None = None):
    try:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        url = "https://api.tapsage.com/api/v1/storage"
        headers = {
            "Accept": "*/*",
            "Origin": "https://console.tapsage.com",
            "Referer": "https://console.tapsage.com/",
            "x-api-key": os.getenv("TPSG_TOKEN"),
        }

        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field(
                "files",
                open(file_path, "rb"),
                filename=file_name or file_path.name,
                content_type="application/octet-stream",
            )

            async with session.post(url, headers=headers, data=data) as response:
                result = await response.json()
                logfire.info(f"File uploaded to tapsage: {result['files'][0]['url']}")
                return result["files"][0]["url"]

    except Exception as e:
        logfire.error(f"Error uploading file to tapsage: {str(e)}")
        raise
