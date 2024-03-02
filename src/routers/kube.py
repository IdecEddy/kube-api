from fastapi import APIRouter, Depends, Response, HTTPException, status
from loggingconf import setup_logging
from sqlalchemy.orm import Session
from utils.db import get_db

router = APIRouter(prefix="/api/v1/k8")
logger = setup_logging()


@router.get("/")
def test_auth():
    return "Welcome to the k8 api"

