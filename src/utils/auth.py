import httpx
from fastapi import HTTPException, Request 
from starlette.status import HTTP_401_UNAUTHORIZED

# Configuration Variables
VALIDATE_ENDPOINT = "https://127.0.0.1:8000/api/v1/auth/verify_token"
IS_PRODUCTION = True  # Set based on your environment

# Assuming the use of OAuth2 with Bearer tokens, but adjust according to your needs

async def validate_token(request: Request) -> str:
    body = await request.json()
    print(body)
    authToken = body.get("authToken")
    if not authToken:
        raise HTTPException(status_code=400, detail="AuthToken missing")
    refreshToken = body.get("refreshToken")
    if not refreshToken:
        raise HTTPException(status_code=400, detail="RefreshToken missing")
    body = {
        "authToken": authToken,
        "refreshToken": refreshToken,
        "audience": "platform-frontend",
    }
    verify = IS_PRODUCTION
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(VALIDATE_ENDPOINT, json=body)
            if response.status_code != 200:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
            print(response.json().get("message"))
            # You may want to return the new auth token if it was refreshed
            return authToken  # or response.json().get("authToken") if you're updating it
        except httpx.HTTPStatusError as exc:
            print(f"HTTP error occurred: {exc}")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        # In case of exceptions, redirect to login is handled by raising an HTTPException
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Failed to validate the token")
