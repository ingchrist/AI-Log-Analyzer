from langchain.tools import tool

@tool
def restart_kubernetes_pod(pod_name: str, namespace: str = "default", reason: str = "") -> str:
    """Restart a Kubernetes pod. ALWAYS ask for approval first."""
    print(f"SIMULATED: kubectl delete pod {pod_name} -n {namespace}")
    return f"[SIMULATED] Restarted pod '{pod_name}' in namespace '{namespace}'."
