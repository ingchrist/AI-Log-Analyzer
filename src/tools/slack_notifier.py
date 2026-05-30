from langchain.tools import tool

@tool
def send_slack_notification(channel: str, summary: str, severity: str = "P1") -> str:
    """Send an incident notification to Slack."""
    print(f"SIMULATED Slack to {channel}: [{severity}] {summary}")
    return "Notification sent."
