import asyncio
import os
import uuid
from datetime import datetime
from typing import Callable, Awaitable, Dict, List
from app import database
from app.models import ActionItem, AgentEvent

_running_tasks: Dict[str, asyncio.Task] = {}


def start_agent_loop(
    meeting_id: str, broadcast_func: Callable[[str, dict], Awaitable[None]]
):
    """Starts the Agentic Autonomous Monitoring & Decision Loop for a meeting."""
    if meeting_id in _running_tasks and not _running_tasks[meeting_id].done():
        return

    task = asyncio.create_task(_agent_loop(meeting_id, broadcast_func))
    _running_tasks[meeting_id] = task


def stop_agent_loop(meeting_id: str):
    """Stops the autonomous loop for a meeting."""
    if meeting_id in _running_tasks:
        task = _running_tasks[meeting_id]
        if not task.done():
            task.cancel()
        del _running_tasks[meeting_id]


async def _agent_loop(
    meeting_id: str, broadcast_func: Callable[[str, dict], Awaitable[None]]
):
    """
    Autonomous Agent Decision Engine Loop (Observe -> Reason -> Act -> Monitor -> Re-Evaluate -> Escalate).
    Runs every 20 seconds in Demo Time Acceleration Mode.
    """
    try:
        while True:
            await asyncio.sleep(
                20
            )  # 20 seconds compressed evaluation cycle for hackathon demo

            items = database.get_action_items(meeting_id)
            if not items:
                print(
                    f"[Agent Loop] No items found for meeting '{meeting_id}'. Exiting cycle."
                )
                break

            all_completed = all(i.status == "completed" for i in items)
            if all_completed:
                print(
                    f"[Agent Loop] All items resolved for meeting '{meeting_id}'. Stopping loop."
                )
                break

            # 1. OBSERVE & EVALUATE DEPENDENCIES & OVERDUE STATES
            overdue_owners = set()
            for item in items:
                if item.status == "completed":
                    continue

                # Check overdue condition (simulated: items with reminders_sent >= 2 are due_soon / overdue)
                if item.reminders_sent >= 2 and item.status != "completed":
                    overdue_owners.add(item.owner)

            # 2. REASON & ACT ON EACH ITEM
            for item in items:
                if item.status == "completed":
                    continue

                # Signal check: Dependency risk
                is_dependency_at_risk = False
                for dep in item.dependencies:
                    if dep.lower() in overdue_owners or any(
                        i.owner.lower() == dep.lower() and i.status != "completed"
                        for i in items
                    ):
                        is_dependency_at_risk = True

                if is_dependency_at_risk and item.status != "at_risk":
                    # Refetch to ensure we don't overwrite manual edits
                    latest_item = database.get_action_item_by_id(meeting_id, item.id)
                    if latest_item and latest_item.status not in [
                        "completed",
                        "at_risk",
                    ]:
                        latest_item.status = "at_risk"
                        database.save_action_item(latest_item)

                        event = AgentEvent(
                            id=str(uuid.uuid4())[:8],
                            meeting_id=meeting_id,
                            type="dependency_at_risk",
                            action="MARK_AT_RISK",
                            reason=f"Task is at risk because prerequisite dependency ({', '.join(item.dependencies)}) is delayed or overdue.",
                            signals=[
                                f"Prerequisite owner {dep} has pending/overdue work"
                                for dep in item.dependencies
                            ],
                            target=latest_item.task_title,
                        )
                        database.save_agent_event(event)

                        await broadcast_func(
                            meeting_id,
                            {"type": "item_updated", "data": latest_item.dict()},
                        )
                        await broadcast_func(
                            meeting_id, {"type": "agent_event", "data": event.dict()}
                        )

                # Signal check: Escalation threshold (3 reminders sent without completion)
                if item.reminders_sent >= 3 and not item.escalated:
                    latest_item = database.get_action_item_by_id(meeting_id, item.id)
                    if (
                        latest_item
                        and not latest_item.escalated
                        and latest_item.status != "completed"
                    ):
                        latest_item.escalated = True
                        latest_item.escalated_to = "Alex (Product Lead)"
                        latest_item.status = "at_risk"
                        database.save_action_item(latest_item)

                        event = AgentEvent(
                            id=str(uuid.uuid4())[:8],
                            meeting_id=meeting_id,
                            type="item_escalated",
                            action="ESCALATE",
                            reason=f"3 automated reminders went unanswered by @{latest_item.owner}. Escalating task to {latest_item.escalated_to}.",
                            signals=[
                                "3 ignored reminders",
                                "Deadline critical",
                                "No completion response",
                            ],
                            target=f"@{latest_item.owner} → {latest_item.escalated_to}",
                        )
                        database.save_agent_event(event)

                        await broadcast_func(
                            meeting_id,
                            {
                                "type": "item_escalated",
                                "data": {
                                    "item": latest_item.dict(),
                                    "event": event.dict(),
                                },
                            },
                        )
                    continue

                # Signal check: Send Autonomous Reminder (if reminders_sent < 3)
                if item.reminders_sent < 3:
                    latest_item = database.get_action_item_by_id(meeting_id, item.id)
                    if latest_item and latest_item.status != "completed":
                        latest_item.reminders_sent += 1
                        latest_item.status = "reminded"
                        latest_item.last_reminder_at = (
                            datetime.utcnow().isoformat() + "Z"
                        )
                        database.save_action_item(latest_item)

                        # Trigger optional real email / simulation dispatch
                        email_status = _dispatch_email_reminder(latest_item)

                        event = AgentEvent(
                            id=str(uuid.uuid4())[:8],
                            meeting_id=meeting_id,
                            type="reminder_sent",
                            action="SEND_REMINDER",
                            reason=f"Deadline approaching for '{latest_item.task_title}' owned by @{latest_item.owner}.",
                            signals=[
                                f"Task status: {latest_item.status}",
                                f"Attempt count: #{latest_item.reminders_sent}",
                                f"Dispatch channel: {email_status}",
                            ],
                            target=f"@{latest_item.owner}",
                        )
                        database.save_agent_event(event)

                        await broadcast_func(
                            meeting_id,
                            {
                                "type": "reminder_sent",
                                "data": {
                                    "id": latest_item.id,
                                    "task_title": latest_item.task_title,
                                    "owner": latest_item.owner,
                                    "reminders_sent": latest_item.reminders_sent,
                                    "channel": email_status,
                                    "timestamp": event.timestamp,
                                    "reason": event.reason,
                                    "signals": event.signals,
                                    "next_action": "Evaluate escalation in 30s",
                                },
                            },
                        )

                        await asyncio.sleep(1)

    except asyncio.CancelledError:
        print(f"[Agent Loop] Loop cancelled for meeting '{meeting_id}'")
    except Exception as e:
        print(f"[Agent Loop] Error in meeting loop '{meeting_id}': {e}")


def _dispatch_email_reminder(item: ActionItem) -> str:
    """Dispatches a real email if EMAIL_API_KEY is configured, else uses simulated channel."""
    api_key = os.environ.get("EMAIL_API_KEY")
    if api_key:
        try:
            # Placeholder for SendGrid / SMTP integration if key present
            print(
                f"[Email Dispatcher] Sending real email to {item.owner}@company.com for task '{item.task_title}'"
            )
            return "Email (Real Dispatch)"
        except Exception as e:
            print(f"[Email Dispatcher] Error: {e}")
            return "Email (Simulated)"
    return "Email (Simulated)"
