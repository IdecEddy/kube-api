from fastapi import APIRouter, Depends, Response, HTTPException, status
from typing import List
from loggingconf import setup_logging
from sqlalchemy.orm import Session
from utils.db import get_db
from models.kubeconf_data import CreateKubeConfigRequest, GetUsersKubeConfigsResponse, GetUsersKubeConfigsRequest
from models.kubeconf_db import KubeConfig
from utils.auth import validate_token
import yaml

router = APIRouter(prefix="/api/v1/k8")
logger = setup_logging()


@router.get("/")
def test_auth():
    return "Welcome to the k8 api"

@router.post("/conf/create")
def create_conf(kubeconfRequest: CreateKubeConfigRequest, db: Session = Depends(get_db), auth_token: str = Depends(validate_token)):
    logger.info(f"Creating kubeconfig for user {kubeconfRequest.userId}")
    
    yamlData = yaml.safe_load(kubeconfRequest.kubeConfFile)

    clusterName = yamlData['clusters'][0]['name']
    clusterUser = yamlData['users'][0]['name']

    new_config = KubeConfig(
        user_id=kubeconfRequest.userId,
        config_data=kubeconfRequest.kubeConfFile,
        kube_user=clusterUser,
        kube_server=clusterName,
        conf_label="this is a name"
    )

    # Add the new record to the session and commit it
    db.add(new_config)
    db.commit()

    # Refresh the instance to get the newly generated ID
    db.refresh(new_config)

    # Log the successful creation
    logger.info(f"Created kubeconfig {new_config.id} for user {kubeconfRequest.userId}")

    # Return the ID of the newly created record and a success message
    return {"id": new_config.id, "message": "KubeConfig created successfully."}

@router.post("/conf/users_confs", response_model=List[GetUsersKubeConfigsResponse])
def get_conf(getUsersKubeConfigsRequest: GetUsersKubeConfigsRequest, db: Session = Depends(get_db), auth_token: str = Depends(validate_token)):
    # Query the database for kubeconfig(s) associated with the user ID
    configs = db.query(KubeConfig).filter(KubeConfig.user_id == getUsersKubeConfigsRequest.userId).all()

    if not configs:
        raise HTTPException(status_code=404, detail="KubeConfig not found for the specified user ID")

    return configs
