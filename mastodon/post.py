import os
import io
import httpx
import asyncio


MASTODON_BASE_URL = os.getenv("MASTODON_HOST_URL")
MASTODON_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

http = httpx.AsyncClient(
    base_url=MASTODON_BASE_URL,
    headers={
        "Authorization": f"Bearer {MASTODON_TOKEN}",
    },
)


def from_file(path: str):
    with open(path, "rb") as file:
        return file


async def upload(path: str | io.BytesIO, filename: str):
    file = path if isinstance(path, io.BytesIO) else from_file(path)

    res = await http.post(
        url="/api/v2/media",
        files={"file": (filename, file)},
        # timeout 10 minutes
        timeout=600,
    )

    data = res.json()

    if not res.is_success:
        return data, True

    retry = 0
    still_processing = True
    while still_processing:
        # is upload still processing in the server?
        # this will prevent continue to post to status.
        process = await http.get(f"api/v1/media/{data['id']}")
        code = process.status_code
        still_processing = code == 206
        data = process.json()

        if still_processing:
            retry += 1

            if retry > 100:
                raise TimeoutError("Failed to finish the upload process")

            await asyncio.sleep(1)

        elif code != 200 and code != 202:
            raise ConnectionError(f"HTTP error: {code}")

    return data, not res.is_success


async def send_status(
    text: str,
    media_ids: list[str] = [],
    reply_id: str | None = None,
    spoiler: bool = False,
):
    res = await http.post(
        url="/api/v1/statuses",
        json={
            "status": text,
            "in_reply_to_id": reply_id,
            "media_ids": media_ids,
            "sensitive": spoiler,
        },
    )

    data = res.json()

    return data, not res.is_success
