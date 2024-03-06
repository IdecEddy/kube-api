from fastapi import APIRouter, Depends, Response, HTTPException, status
from typing import List
from loggingconf import setup_logging
from sqlalchemy.orm import Session
from utils.db import get_db
from models.kubeconf_data import CreateKubeConfigRequest, GetUsersKubeConfigsResponse
from models.kubeconf_db import KubeConfig
from utils.auth import validate_token
router = APIRouter(prefix="/api/v1/k8")
logger = setup_logging()


@router.get("/")
def test_auth():
    return "Welcome to the k8 api"

@router.post("/conf/create")
def create_conf(kubeconfRequest: CreateKubeConfigRequest, db: Session = Depends(get_db), auth_token: str = Depends(validate_token)):
    # Log the operation
    logger.info(f"Creating kubeconfig for user {kubeconfRequest.userId}")
    
    # Create a new KubeConfig record
    new_config = KubeConfig(
        user_id=kubeconfRequest.userId,
        config_data=kubeconfRequest.kubeConfFile
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

@router.get("/conf/{user_id}", response_model=List[GetUsersKubeConfigsResponse])
def get_conf(user_id: int, db: Session = Depends(get_db)):
    # Query the database for kubeconfig(s) associated with the user ID
    configs = db.query(KubeConfig).filter(KubeConfig.user_id == user_id).all()
    
    if not configs:
        raise HTTPException(status_code=404, detail="KubeConfig not found for the specified user ID")
    
    return configs
