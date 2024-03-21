from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    authToken: str =  Field(..., description="This is a basic auth toekn")
