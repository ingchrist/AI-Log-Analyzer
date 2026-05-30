from langchain.tools import tool

@tool
def send_slack_notification(channel: str, summary: str, severity: str = "P1") -> str:
    """Send an incident notification to Slack."""
    redacted = summary[:40] + "..." if len(summary) > 40 else summary[:40]
    print(f"SIMULATED Slack to {channel}: [{severity}] (summary: {redacted!r})")
    return "Notification sent."
