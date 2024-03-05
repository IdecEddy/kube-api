from fastapi import APIRouter, Depends, Response, HTTPException, status
from loggingconf import setup_logging
from sqlalchemy.orm import Session
from utils.db import get_db
from models.kubeconf_request import KubeConfigRequest

router = APIRouter(prefix="/api/v1/k8")
logger = setup_logging()


@router.get("/")
def test_auth():
    return "Welcome to the k8 api"

@router.post("/conf/create")
def create_conf(kubeconfRequest: KubeConfigRequest, db: Session = Depends(get_db)):
    userId = kubeconfRequest.user_id
    authToken = kubeconfRequest.auth_token
    kubeconfFile = kubeconfRequest.kube_conf_file

    print(userId, authToken, kubeconfFile)
