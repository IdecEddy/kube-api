import httpx

def get_nodes(ssl_context, api_url) -> httpx.Response:
    with httpx.Client(verify=ssl_context) as client:
        response = client.get(f"{api_url}/api/v1/nodes")
        return response


def get_pods_on_node(ssl_context, api_url, node_name) -> httpx.Response:
    with httpx.Client(verify=ssl_context) as client:
        response = client.get(f"{api_url}/api/v1/pods?fieldSelector=spec.nodeName={node_name},status.phase!=Failed,status.phase!=Succeeded&limit=500")
        return response

def get_node_metrics(ssl_context, api_url, node_name) -> httpx.Response:
    with httpx.Client(verify=ssl_context) as client:
        response = client.get(f"{api_url}/apis/metrics.k8s.io/v1beta1/nodes/{node_name}")
        return response

def get_pod_metrics(ssl_context, api_url) -> httpx.Response:
    with httpx.Client(verify=ssl_context) as client:
        response = client.get(f"{api_url}/apis/metrics.k8s.io/v1beta1/pods")
        return response

