import json
import http.client
from typing import Optional, List, Dict


class SlackAlertManager:
    """
    A class for managing and sending alerts to Slack using a webhook endpoint.

    Attributes:
        slack_endpoint (str): The Slack webhook endpoint URL.
        severity_to_emoji (dict): A mapping of alert severity levels to corresponding emojis.

    Methods:
        send_alert(severity, alert_source, alert_message, follow_up_actions, tail_blocks=None):
            Constructs and sends a formatted alert payload to Slack.
        _send_to_slack(payload):
            Sends a raw payload to the configured Slack webhook endpoint.
    """

    severity_to_emoji = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🔵",
        "Complete": "🟢",
    }

    def __init__(self, slack_endpoint: str) -> None:
        """
        Initializes the SlackAlertManager with the provided Slack webhook endpoint.

        Args:
            slack_endpoint (str): The Slack webhook endpoint URL.
        """
        self.slack_endpoint = slack_endpoint

    def send_alert(
        self,
        severity: str,
        alert_source: str,
        alert_message: str,
        follow_up_actions: str,
        tail_blocks: Optional[List[Dict]] = None,
    ) -> None:
        """
        Builds and sends an alert payload to Slack.

        Args:
            severity (str): The alert severity level (e.g., 'Critical', 'High', 'Medium', 'Low').
            alert_source (str): The source of the alert (e.g., 'Data Observer', 'Monitoring').
            alert_message (str): The main message content for the alert.
            follow_up_actions (str): The recommended actions to take in response to the alert.
            tail_blocks (Optional[List[Dict]]): Additional optional Slack blocks to append to the message.

        Raises:
            RuntimeError: If the Slack API response indicates a failure.
        """
        emoji = self.severity_to_emoji.get(severity, "🔵")
        severity_header = f"{alert_source} - {severity} Alert {emoji}"

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": severity_header}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Alert Message:*\n{alert_message}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Follow-Up Actions:*\n{follow_up_actions}",
                },
            },
        ]

        if tail_blocks:
            blocks.extend(tail_blocks)

        payload = {"blocks": blocks}
        self._send_to_slack(payload)

    def _send_to_slack(self, payload: Dict) -> None:
        """
        Sends a raw payload to the configured Slack webhook endpoint.

        Args:
            payload (dict): The payload to send to Slack.

        Raises:
            RuntimeError: If the Slack API response status is not 200 (OK).
        """
        conn = http.client.HTTPSConnection("hooks.slack.com")
        headers = {"Content-type": "application/json"}
        try:
            conn.request("POST", self.slack_endpoint, json.dumps(payload), headers)
            response = conn.getresponse()
            if response.status != 200:
                raise RuntimeError(
                    f"Failed to send alert: {response.status} {response.reason}"
                )
        finally:
            conn.close()
