import typer
from typing_extensions import Annotated
import json
from slack_alert_manager import SlackAlertManager
from utils import truncate_text

app = typer.Typer(help="Slack Notificator")


@app.command()
def send_slack_alert(
    slack_endpoint: Annotated[
        str, typer.Argument(help="The Slack webhook endpoint to send the alert to.")
    ],
    workflow_name: Annotated[
        str, typer.Argument(help="The name of the workflow being alerted about.")
    ],
    workflow_duration: Annotated[
        float, typer.Argument(help="The duration of the workflow in seconds.")
    ],
    workflow_failures: Annotated[
        str,
        typer.Argument(help="A JSON string containing details of workflow failures."),
    ],
    workflow_status: Annotated[
        str,
        typer.Argument(
            help="The status of the workflow (e.g., 'Succeeded', 'Failed')."
        ),
    ],
    creation_timestamp: Annotated[
        str,
        typer.Argument(
            help="The timestamp when the workflow was created (ISO 8601 format)."
        ),
    ],
    link_url: Annotated[
        str, typer.Argument(help="A URL pointing to the workflow details in the UI.")
    ],
    severity: Annotated[
        str,
        typer.Argument(
            help="The severity level of the alert (e.g., 'Critical', 'Medium')."
        ),
    ] = "Medium",
    max_lines: Annotated[
        int,
        typer.Argument(
            help="The maximum number of failure lines to include in the alert."
        ),
    ] = 6,
):
    """
    Sends a formatted alert to Slack for a specific workflow based on its status and failures.

    This function processes workflow metadata and failure details to construct a Slack alert
    and sends it to the specified webhook endpoint.

    Args:
        slack_endpoint (str): The Slack webhook endpoint URL.
        workflow_name (str): The name of the workflow being alerted about.
        workflow_duration (float): The duration of the workflow in seconds.
        workflow_failures (str): A JSON string containing details of workflow failures.
        workflow_status (str): The current status of the workflow (e.g., 'Failed').
        creation_timestamp (str): The timestamp when the workflow was created.
        link_url (str): A URL linking to the workflow's details in the UI.
        severity (str, optional): The severity level of the alert. Defaults to 'Medium'.
        max_lines (int, optional): The maximum number of failure lines to include in the alert. Defaults to 6.

    Returns:
        None
    """
    try:
        slack_manager = SlackAlertManager(slack_endpoint)

        results = json.loads(json.loads(workflow_failures))
        sorted_results = sorted(results, key=lambda x: x["displayName"])

        # Build a list of formatted strings summarizing workflow failures.
        # Each string includes the displayName, finishedAt timestamp, and message.
        # Filters are applied to:
        # - Include only unique displayName entries (tracked using seen_display_names).
        # - Exclude messages containing "child" or "No more retries left".
        # - Skip empty or whitespace-only messages.
        seen_display_names = set()
        formatted_lines = [
            f"{item['displayName']} finished at {item['finishedAt']}: {item['message']}"
            for item in sorted_results
            if item["displayName"] not in seen_display_names
            and not seen_display_names.add(item["displayName"])
            and "child" not in item["message"]
            and "No more retries left" not in item["message"]
            and item["message"].strip() != ""
        ]
        if not formatted_lines:
            typer.echo(
                "This alert is omitted because it doesn't bring any valuable information"
            )
            return
        formatted_message = truncate_text("\n".join(formatted_lines[:max_lines]))

        alert_message = (
            f"Workflow *{workflow_name}* status: {workflow_status}\n\n"
            f"*Duration:* {round(workflow_duration / 60, 2)} minutes\n"
            f"*Created:* {creation_timestamp}\n"
            f"<{link_url}|Workflow Details in Argo Workflows>"
        )

        slack_manager.send_alert(
            severity=f"{severity}",
            alert_source="Argo Workflows Exit Handler",
            alert_message=alert_message,
            follow_up_actions="Check workflow logs for details.",
            tail_blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Failures:*\n```{formatted_message}```",
                    },
                }
            ],
        )
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
