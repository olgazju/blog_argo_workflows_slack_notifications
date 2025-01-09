import pytest
from unittest.mock import patch
from slack_alert_manager import SlackAlertManager


@pytest.fixture
def slack_manager():
    """Fixture to create a SlackAlertManager instance."""
    return SlackAlertManager(slack_endpoint="mock_endpoint")


@patch.object(SlackAlertManager, "_send_to_slack")
def test_send_alert_success(mock_send_to_slack, slack_manager):
    """
    Test sending an alert successfully.
    Verifies that the _send_to_slack method is called with the correct payload.
    """
    severity = "Critical"
    alert_source = "Data Observer"
    alert_message = "An important alert!"
    follow_up_actions = "Investigate immediately."
    tail_blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Extra info:* Example"}}
    ]

    slack_manager.send_alert(
        severity=severity,
        alert_source=alert_source,
        alert_message=alert_message,
        follow_up_actions=follow_up_actions,
        tail_blocks=tail_blocks,
    )

    mock_send_to_slack.assert_called_once()

    payload = mock_send_to_slack.call_args[0][0]

    assert (
        payload["blocks"][0]["text"]["text"] == f"{alert_source} - {severity} Alert 🔴"
    )
    assert payload["blocks"][1]["text"]["text"] == f"*Alert Message:*\n{alert_message}"
    assert (
        payload["blocks"][2]["text"]["text"]
        == f"*Follow-Up Actions:*\n{follow_up_actions}"
    )
    assert payload["blocks"][3] == tail_blocks[0]


@patch.object(SlackAlertManager, "_send_to_slack")
def test_send_alert_without_tail_blocks(mock_send_to_slack, slack_manager):
    """
    Test sending an alert without tail_blocks.
    Verifies that the payload does not include any additional blocks.
    """
    severity = "High"
    alert_source = "Pipeline Alert"
    alert_message = "Pipeline execution took longer than expected."
    follow_up_actions = "Check logs and reschedule."

    slack_manager.send_alert(
        severity=severity,
        alert_source=alert_source,
        alert_message=alert_message,
        follow_up_actions=follow_up_actions,
    )

    mock_send_to_slack.assert_called_once()

    payload = mock_send_to_slack.call_args[0][0]

    assert len(payload["blocks"]) == 3
    assert (
        payload["blocks"][0]["text"]["text"] == f"{alert_source} - {severity} Alert 🟠"
    )
    assert payload["blocks"][1]["text"]["text"] == f"*Alert Message:*\n{alert_message}"
    assert (
        payload["blocks"][2]["text"]["text"]
        == f"*Follow-Up Actions:*\n{follow_up_actions}"
    )


@patch.object(SlackAlertManager, "_send_to_slack")
def test_send_to_slack_error_handling(mock_send_to_slack, slack_manager):
    """
    Test handling an error during the Slack API call.
    Verifies that the exception is raised when _send_to_slack fails.
    """

    mock_send_to_slack.side_effect = RuntimeError("Failed to send alert")

    with pytest.raises(RuntimeError, match="Failed to send alert"):
        slack_manager.send_alert(
            severity="Medium",
            alert_source="Data Observer",
            alert_message="Test alert message",
            follow_up_actions="No action needed",
        )

    mock_send_to_slack.assert_called_once()
