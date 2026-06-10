"""Slack bot integration — access requests and approvals via Slack.

Requires:
  pip install slack-bolt

Environment variables:
  SLACK_BOT_TOKEN: Bot OAuth token (xoxb-...)
  SLACK_SIGNING_SECRET: Request verification secret
  SLACK_APP_TOKEN: App-level token for Socket Mode (xapp-...)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SlackBot:
    """AgentGuard Slack bot for access request workflows."""

    def __init__(self):
        self._app = None
        self._initialized = False

    def initialize(self):
        """Initialize the Slack Bolt app. Call only when Slack is configured."""
        try:
            from slack_bolt.async_app import AsyncApp
            from app.config import settings

            if not settings.slack_bot_token or not settings.slack_signing_secret:
                logger.warning("Slack not configured — bot disabled")
                return

            self._app = AsyncApp(
                token=settings.slack_bot_token,
                signing_secret=settings.slack_signing_secret,
            )
            self._register_handlers()
            self._initialized = True
            logger.info("Slack bot initialized")
        except ImportError:
            logger.warning("slack-bolt not installed — Slack bot disabled")
        except Exception as e:
            logger.error(f"Slack bot init failed: {e}")

    def _register_handlers(self):
        """Register Slack event handlers and commands."""
        app = self._app

        @app.command("/access")
        async def handle_access_command(ack, body, say):
            """Handle /access slash command."""
            await ack()
            text = body.get("text", "").strip()
            user_id = body.get("user_id", "")

            if not text:
                await say(
                    text="Usage: `/access <request>` — e.g. `/access I need read access to GitHub`",
                    channel=body["channel_id"],
                )
                return

            # Run through agent pipeline
            from app.agents.orchestrator import run_agent_pipeline

            result = await run_agent_pipeline(user_message=text, user_id=None)

            response_text = result.get("response", "Unable to process request.")
            blocks = self._build_response_blocks(result, user_id)

            await say(blocks=blocks, text=response_text, channel=body["channel_id"])

        @app.command("/ask")
        async def handle_ask_command(ack, body, say):
            """Handle /ask slash command for knowledge base questions."""
            await ack()
            text = body.get("text", "").strip()

            if not text:
                await say(
                    text="Usage: `/ask <question>` — Ask about policies, procedures, or compliance",
                    channel=body["channel_id"],
                )
                return

            from app.services.chat import chat_with_rag

            result = await chat_with_rag(message=text)

            blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": result["response"]},
                },
            ]

            if result.get("sources"):
                source_text = " | ".join(
                    f"`{s['doc_type']}` ({s['similarity']*100:.0f}%)"
                    for s in result["sources"][:3]
                )
                blocks.append({
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"📚 Sources: {source_text}"}],
                })

            await say(blocks=blocks, text=result["response"], channel=body["channel_id"])

        @app.action("approve_request")
        async def handle_approve(ack, body, say):
            """Handle inline approve button click."""
            await ack()
            # Extract metadata from action
            action_value = body["actions"][0].get("value", "")
            user = body.get("user", {}).get("username", "unknown")
            await say(
                text=f"✓ Request approved by @{user}. Grant ID: {action_value}",
                channel=body["channel"]["id"],
            )

        @app.action("deny_request")
        async def handle_deny(ack, body, say):
            """Handle inline deny button click."""
            await ack()
            user = body.get("user", {}).get("username", "unknown")
            await say(
                text=f"✗ Request denied by @{user}.",
                channel=body["channel"]["id"],
            )

    def _build_response_blocks(self, result: dict, slack_user_id: str) -> list[dict]:
        """Build Slack Block Kit response with inline approval buttons."""
        response_text = result.get("response", "")
        phase = result.get("phase", "")
        policy_result = result.get("policy_result", {}) or {}
        risk_score = policy_result.get("risk_score", 0)

        blocks: list[dict[str, Any]] = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response_text},
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Risk: `{risk_score:.2f}` | Phase: `{phase}`"},
                ],
            },
        ]

        # Add approval buttons for pending requests
        prov = result.get("provisioning_result", {}) or {}
        if prov.get("ticket_id") and not prov.get("grant_id"):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✓ Approve"},
                        "style": "primary",
                        "action_id": "approve_request",
                        "value": prov["ticket_id"],
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✗ Deny"},
                        "style": "danger",
                        "action_id": "deny_request",
                        "value": prov["ticket_id"],
                    },
                ],
            })

        return blocks

    @property
    def is_ready(self) -> bool:
        return self._initialized and self._app is not None


slack_bot = SlackBot()
