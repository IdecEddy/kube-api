from routers.kube import KubeNode
from utils.units import convert_cpu_units_to_nanocores, convert_storage_unit_to_bytes
from models.dataclasses import KubePod

def set_resource_allocatable(node, kube_node):
    node_status = node.get("status", "")
    node_allocatable = node_status.get("allocatable", "")

    cpu = node_allocatable.get("cpu", 0)
    memory = node_allocatable.get("memory", 0)

    cpu = convert_cpu_units_to_nanocores(cpu)
    memory = convert_storage_unit_to_bytes(memory)

    kube_node.cpu = cpu
    kube_node.memory = memory

def set_resource_utilization(node_metrics, kube_node):
    cpu_metrics = node_metrics.get("usage", 0).get("cpu", 0)
    memory_metrics = node_metrics.get("usage", 0).get("memory",)

    cpu_metrics = convert_cpu_units_to_nanocores(cpu_metrics)
    memory_metrics = convert_storage_unit_to_bytes(memory_metrics)

    kube_node.cpu_utilization = cpu_metrics
    kube_node.memory_utilization = memory_metrics

def build_pod_info(pods, kube_node: KubeNode):
    pod_info = []
    pod_list = pods.get("items",[])
    for pod in pod_list:
        pod_info_item = {}

        pod_info_item["name"] = pod.get("metadata", {}).get("name", "")
        pod_info_item["namespace"] = pod.get("metadata",{}).get("namespace", "")
        pod_info_item["node"] = kube_node.name

        containers = pod.get("spec",{}).get("containers", [])
        pod_info_item["cpu_limit"], pod_info_item["memory_limit"] = add_up_pod_limit(containers)
        pod_info.append(pod_info_item)
    return pod_info

def add_up_pod_limit(containers):
    cpu_limit = 0
    memory_limit = 0
    for container in containers:
        cpu_limit += convert_cpu_units_to_nanocores(container.get("resources",{}).get("limits", {}).get("cpu", 0))
        memory_limit += convert_storage_unit_to_bytes(container.get("resources",{}).get("limits",{}).get("memory",0))

    return (cpu_limit, memory_limit)



def build_pod_metrics(metrics):
    pod_metrics = []
    pod_list = metrics.get("items", [])
    for pod in pod_list:
        pod_metric_item = {}
        resource_usage = {}
        
        pod_metric_item["name"] = pod.get("metadata", {}).get("name", "")
        pod_metric_item["namespace"] = pod.get("metadata", {}).get("namespace", "")
        
        containers = pod.get("containers", [])
        
        cpu_total = 0
        memory_total = 0
    
        for container in containers:
            cpu = convert_cpu_units_to_nanocores(container.get("usage", {}).get("cpu", 0))
            memory = convert_storage_unit_to_bytes(container.get("usage", {}).get("memory", 0))

            cpu_total += cpu
            memory_total += memory

        resource_usage["cpu"] = cpu_total
        resource_usage["memory"] = memory_total

        pod_metric_item["usage"] = resource_usage
        pod_metrics.append(pod_metric_item)
    return pod_metrics

def set_pod_metrics(metrics, pods, kube_node):
    kube_pod_list = []
    
    pod_info = build_pod_info(pods, kube_node)
    pod_metrics = build_pod_metrics(metrics)
    pod_lookup = {(item["name"], item["namespace"]): item for item in pod_info}
    
    for pod in pod_metrics:
        key = (pod["name"], pod["namespace"])
        if key in pod_lookup:
            pod_info = pod_lookup[key]
            kube_pod = KubePod()
            kube_pod.name = pod["name"]
            kube_pod.namespace = pod["namespace"]
            kube_pod.cpu = pod["usage"]["cpu"]
            kube_pod.memory = pod["usage"]["memory"]
            kube_pod.cpu_limit = pod_info["cpu_limit"]
            kube_pod.memory_limit = pod_info["memory_limit"]
            kube_pod_list.append(kube_pod)
    return kube_pod_list
            
