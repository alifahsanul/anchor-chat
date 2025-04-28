import httpx

async def fetch_url_content(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        response.raise_for_status()
        return response.text
