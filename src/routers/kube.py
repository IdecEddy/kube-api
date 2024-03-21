from fastapi import APIRouter, Depends, Response, HTTPException, status
from typing import List

from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from loggingconf import setup_logging
from sqlalchemy.orm import Session
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
from utils.kubernetesApi import get_nodes, describe_node
from models.auth_data import AuthRequest
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


@router.get("/cluster-info")
def get_cluster_info(
        db: Session = Depends(get_db),
        authToken: httpx.Response = Depends(validate_token)):

    tokenUserId = authToken.json()["payload"]["user_id"]

    try:
        conf = db.query(KubeConfig).filter(KubeConfig.id == 1).one()
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail="could not find record."
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=500, detail="The database has more then one record with the same id this is BAD.")

    if tokenUserId == conf.user_id: 
        ca_file = str(conf.ca_file)
        key_file = str(conf.key_file)
        cert_file = str(conf.cert_file)

        ssl_context = create_ssl_context(cert_file, ca_file, key_file)
        response = get_nodes(ssl_context, "https://192.168.50.84:8443") 
        data = response.json()
        result = [
            {
                "nodeName": item["metadata"]["name"], 
                "Status": next(
                    (condition["type"] for condition in item["status"]["conditions"] if condition["type"] == "Ready" and condition["status"] == "True"), 
                    "Not Ready"
                ) 
            } 
            for item in data["items"]
        ]
        listOfPods = []
        for node in result:
            res = describe_node(ssl_context, "https://192.168.50.84:8443", node['nodeName']).json()
            for pod in res['items']:
                podObj = {
                    "name": None,
                    "CPU": "0m",
                    "memory": "0m",
                    "NodeName": None,
                }
                podObj["name"] = pod.get("metadata", {}).get("name",{})
                podObj["NodeName"] = pod.get("spec", {}).get("nodeName", None)
                containers = pod.get("spec",{}).get("containers",{})
                total_cpu = 0
                total_memory = 0
                for container in containers:
                    requests =  container.get("resources",{}).get("requests",{})
                    cpu = requests.get("cpu","0m")
                    memory = requests.get("memory", "0Mi")

                    total_memory += int(memory.rstrip("Mi"))
                    total_cpu += int(cpu.rstrip("m"))

                podObj["CPU"] = str(total_cpu) + "m"
                podObj["memory"] = str(total_memory) + "Mi" 
                listOfPods.append(podObj)
        return listOfPods

        
