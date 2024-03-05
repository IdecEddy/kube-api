from pydantic import BaseModel, Field

class KubeConfigRequest(BaseModel):
    user_id: int = Field(..., description="The unique identifier for the user")
    auth_token: str = Field(..., description="The authentication token for the user")
    kube_conf_file: str = Field(..., description="The content of the kubeconfig file")

