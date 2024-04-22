from pydantic import BaseModel, Field


class CreateKubeConfigRequest(BaseModel):
    authToken: str = Field(..., description="The authentication token for the user")
    kubeConfFile: str = Field(..., description="The content of the kubeconfig file")
    clusterLabel: str = Field(..., description="The label of the cluster")
    clusterDescription: str = Field(..., description="The description of the cluser")
    caFile: str = Field(..., description="the cert auth for a cluster")
    keyFile: str = Field(..., description="the key file for a user")
    certFile: str = Field(..., description="the cert file for a user")


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


class deleteUsersKubeConfigsRequest(BaseModel):
    authToken: str = Field(..., description="The auth token to provide to the auth API")
    databaseId: int = Field(..., description="The database id that we want to delete")

