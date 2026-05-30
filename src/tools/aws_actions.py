from langchain.tools import tool

@tool
def reboot_rds_instance(db_instance_id: str, reason: str = "") -> str:
    """Reboot an AWS RDS instance. ALWAYS ask for approval first."""
    print(f"SIMULATED: aws rds reboot-db-instance --db-instance-identifier {db_instance_id}")
    return f"[SIMULATED] Initiated reboot of RDS '{db_instance_id}'."
