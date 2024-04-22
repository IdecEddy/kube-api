from fastapi import APIRouter, Depends, Response, HTTPException, status
from typing import List

from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from loggingconf import setup_logging
from sqlalchemy.orm import Session
from models.cluster_data import ClusterInfoRequest
from utils.db import get_db
from models.kubeconf_data import (
    CreateKubeConfigRequest,
    GetUsersKubeConfigsResponse,
    GetUsersKubeConfigsRequest,
    deleteUsersKubeConfigsRequest,
)
from models.kubeconf_db import KubeConfig
from utils.auth import validate_token
import yaml
import httpx
from utils.ssl import create_ssl_context
from utils.kubernetesApi import get_nodes, get_node_metrics, get_pod_metrics, get_pods_on_node
from utils.units import convert_cpu_units_to_nanocores, convert_storage_unit_to_bytes
from models.dataclasses import KubeNode
from utils.node import set_pod_metrics, set_resource_allocatable, set_resource_utilization
router = APIRouter(prefix="/api/v1/k8")
logger = setup_logging()


@router.get("/")
def test_auth():
    return "Welcome to the k8 api"


@router.post("/conf/create")
def create_conf(
    kubeconfRequest: CreateKubeConfigRequest,
    db: Session = Depends(get_db),
    auth_token: httpx.Response = Depends(validate_token),
):
    userId = auth_token.json()['payload']['user_id']
    logger.info(f"Creating kubeconfig for user {userId}")

    yamlData = yaml.safe_load(kubeconfRequest.kubeConfFile)

    clusterName = yamlData["clusters"][0]["name"]
    clusterUser = yamlData["users"][0]["name"]

    new_config = KubeConfig(
        user_id=userId,
        config_data=kubeconfRequest.kubeConfFile,
        config_user=clusterUser,
        config_server=clusterName,
        config_label=kubeconfRequest.clusterLabel,
        config_description=kubeconfRequest.clusterDescription,
        ca_file=kubeconfRequest.caFile,
        key_file=kubeconfRequest.keyFile,
        cert_file=kubeconfRequest.certFile,
    )

    # Add the new record to the session and commit it
    db.add(new_config)
    db.commit()

    # Refresh the instance to get the newly generated ID
    db.refresh(new_config)

    # Log the successful creation
    logger.info(f"Created kubeconfig {new_config.id} for user {userId}")

    # Return the ID of the newly created record and a success message
    return {"id": new_config.id, "message": "KubeConfig created successfully."}


@router.post("/conf/users_confs", response_model=List[GetUsersKubeConfigsResponse])
def get_conf(
    getUsersKubeConfigsRequest: GetUsersKubeConfigsRequest,
    db: Session = Depends(get_db),
    auth_token: str = Depends(validate_token),
):
    # Query the database for kubeconfig(s) associated with the user ID
    configs = (
        db.query(KubeConfig)
        .filter(KubeConfig.user_id == getUsersKubeConfigsRequest.userId)
        .all()
    )

    if not configs:
        raise HTTPException(
            status_code=404, detail="KubeConfig not found for the specified user ID"
        )

    return configs

@router.post("/conf/deleteById")
def delete_conf_by_id(
    deleteUsersKubeConfigsRequest: deleteUsersKubeConfigsRequest,
    db: Session = Depends(get_db),
    auth_token: httpx.Response = Depends(validate_token),
):
    authToken = auth_token.json()['payload']['user_id']
    try: 
        conf = (
            db.query(KubeConfig)
            .filter(KubeConfig.id == deleteUsersKubeConfigsRequest.databaseId)
            .one()
        )
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail="could not find record."
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=500, detail="The database has more then one record with the same id this is BAD."
        )

    if conf.user_id is authToken:
        try:
            db.delete(conf)
            db.commit()
            return {"status": 200, "message": "We removed the record"}
        except Exception as e:
            raise HTTPException(
                status_code=404, detail="could not find record."
            )


@router.post("/v")
def get_cluster_infoV2(
        clusterInfoRequest: ClusterInfoRequest,
        db: Session = Depends(get_db),
        authToken: httpx.Response = Depends(validate_token)):

    tokenUserId = authToken.json()["payload"]["user_id"]
    API_URL = "https://192.168.1.162:6443"
    
    try:
        conf = db.query(KubeConfig).filter(KubeConfig.id ==  clusterInfoRequest.configId).one()
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail="could not find record."
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=500, detail="The database has more then one record with the same id this is BAD.")
    
    if tokenUserId == conf.user_id: 
        ssl_context = create_ssl_context(
            caFile=str(conf.ca_file),
            keyFile=str(conf.key_file),
            certFile=str(conf.cert_file))

        response = get_nodes(ssl_context, API_URL).json()
        list_of_nodes = []
        for node in response["items"]:
            kube_node = KubeNode()
            kube_node.name = node.get("metadata", "").get("name", "")
            set_resource_allocatable(node, kube_node)
            node_metrics = get_node_metrics(ssl_context, API_URL, kube_node.name).json()
            set_resource_utilization(node_metrics, kube_node)
            pods = get_pods_on_node(ssl_context, API_URL, kube_node.name).json()
            metrics = get_pod_metrics(ssl_context, API_URL).json()
            kube_node.list_of_pods = set_pod_metrics(metrics, pods, kube_node)
            list_of_nodes.append(kube_node)
        return list_of_nodes
