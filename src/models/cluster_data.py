from pydantic import BaseModel, Field

class ClusterInfoRequest(BaseModel):
    configId: int = Field(..., description="The unique identifier for the cluster config")
    authToken: str = Field(..., description="the authentication token for the user")
