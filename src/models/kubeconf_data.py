from pydantic import BaseModel, Field

class CreateKubeConfigRequest(BaseModel):
    userId: int = Field(..., description="The unique identifier for the user")
    authToken: str = Field(..., description="The authentication token for the user")
    refreshToken: str = Field(...,description="The users refresh toekn")
    kubeConfFile: str = Field(..., description="The content of the kubeconfig file")


class GetUsersKubeConfigsResponse(BaseModel):
    id: int
    user_id: int
    config_data: str

    class Config:
        orm_mode = True
