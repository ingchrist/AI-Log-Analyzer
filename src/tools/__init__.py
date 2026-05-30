from .log_reader import read_log_file, list_log_files
from .actions import restart_kubernetes_pod
from .aws_actions import reboot_rds_instance
from .slack_notifier import send_slack_notification

SAFE_TOOLS = {'read_log_file', 'list_log_files', 'send_slack_notification'}
APPROVAL_REQUIRED_TOOLS = {'reboot_rds_instance', 'restart_kubernetes_pod'}

def requires_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS

def get_all_tools():
    return [read_log_file, list_log_files, restart_kubernetes_pod,
            reboot_rds_instance, send_slack_notification]
