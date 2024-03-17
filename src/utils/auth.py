import httpx
from fastapi import HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED

# Configuration Variables
VALIDATE_ENDPOINT = "https://127.0.0.1:8000/api/v1/auth/verify_auth_token"
IS_PRODUCTION = True  # Set based on your environment

# Assuming the use of OAuth2 with Bearer tokens, but adjust according to your needs


async def validate_token(request: Request) -> httpx.Response:
    body = await request.json()
    authToken = body.get("authToken")
    if not authToken:
        raise HTTPException(status_code=400, detail="AuthToken missing")
    body = {
        "authToken": authToken,
        "audience": "platform-frontend",
    }
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(VALIDATE_ENDPOINT, json=body)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            print(response.json().get("message"))
            return response
        except httpx.HTTPStatusError as exc:
            print(f"HTTP error occurred: {exc}")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        # In case of exceptions, redirect to login is handled by raising an HTTPException
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Failed to validate the token"
        )
