from pydantic import BaseModel, Field


class CreateKubeConfigRequest(BaseModel):
    userId: int = Field(..., description="The unique identifier for the user")
    authToken: str = Field(..., description="The authentication token for the user")
    kubeConfFile: str = Field(..., description="The content of the kubeconfig file")
    clusterLabel: str = Field(..., description="The label of the cluster")
    clusterDescription: str = Field(..., description="The description of the cluser")


class GetUsersKubeConfigsResponse(BaseModel):
    id: int
    user_id: int
    config_data: str
    config_user: str
    config_server: str
    config_label: str
    config_description: str

    class Config:
        orm_mode = True


class GetUsersKubeConfigsRequest(BaseModel):
    userId: int = Field(..., description="The unique identifier for the user")
    authToken: str = Field(..., description="the authentication token for the user")
