import os
import json
import re
import uuid
import asyncio
from typing import List, Dict, Any, Tuple
from app.models import ActionItem, Decision, RiskBlocker, MeetingSummary

SYSTEM_EXTRACTION_PROMPT = """
You are an expert AI Meeting Intelligence Agent. Given a meeting transcript, extract:
1. summary: A concise 2-3 sentence overview of the meeting discussions and outcomes.
2. action_items: A list of actionable commitments made by team members.
   For each action item:
   - task_title: A short 4-8 word action title (Do NOT use full transcript sentences).
   - task_description: Contextual breakdown of what needs to be done.
   - owner: Responsible person's first name, or "Unassigned" if unclear/ambiguous.
   - deadline: Explicit date/timeframe mentioned (e.g., "2026-07-28" or "July 28"), or null.
   - priority: "low" | "medium" | "high" | "critical" (infer from urgency words like urgent/must/critical).
   - confidence: A float from 0.0 to 1.0 representing extraction certainty.
   - source_quote: The exact line/sentence from the transcript.
   - needs_review: true if confidence < 0.70 or owner/deadline is ambiguous/unclear, else false.
   - dependencies: List of string names/tasks that this action depends on (or empty list).
3. decisions: Explicit decisions agreed upon in the meeting.
   - decision: Clear statement of what was decided.
   - decided_by: Person or group responsible (e.g., "Product Lead", "Team", "Alex").
   - source_quote: Verbatim sentence from transcript.
   - confidence: Float 0.0 to 1.0.
4. risks_blockers: Potential risks or active blockers mentioned.
   - type: "risk" or "blocker".
   - description: Explanation of the risk/blocker.
   - severity: "low" | "medium" | "high" | "critical".
   - blocked_task: Task title being impacted if mentioned, or null.
   - depends_on: Person or prerequisite task causing the bottleneck, or null.
   - source_quote: Verbatim sentence.
   - confidence: Float 0.0 to 1.0.

Return ONLY valid JSON matching this exact structure:
{
  "summary": "...",
  "action_items": [...],
  "decisions": [...],
  "risks_blockers": [...]
}
No extra commentary or markdown backticks outside standard json.

Meeting Transcript:
{transcript}
"""

async def extract_meeting_intelligence(
    meeting_id: str, 
    transcript_text: str
) -> Tuple[MeetingSummary, List[ActionItem], List[Decision], List[RiskBlocker]]:
    
    if not transcript_text or not transcript_text.strip():
        empty_summary = MeetingSummary(meeting_id=meeting_id, summary_text="No discussion recorded.", action_items_count=0, decisions_count=0, risks_count=0, blockers_count=0)
        return empty_summary, [], [], []

    api_key = os.environ.get("GEMINI_API_KEY")
    data = None

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = SYSTEM_EXTRACTION_PROMPT.format(transcript=transcript_text)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            data = json.loads(raw_text)
        except Exception as e:
            print(f"[Extractor] Gemini API call error/fallback: {e}")
            data = _heuristic_nlp_extraction(transcript_text)
    else:
        data = _heuristic_nlp_extraction(transcript_text)

    # Parse Action Items
    raw_action_items = data.get("action_items", [])
    action_items: List[ActionItem] = []
    item_id_map = {} # title -> id for resolving dependencies

    for idx, item in enumerate(raw_action_items):
        item_id = f"item_{str(uuid.uuid4())[:6]}"
        title = item.get("task_title") or f"Action item #{idx+1}"
        item_id_map[title.lower()] = item_id
        
        priority = item.get("priority", "medium")
        if priority not in ["low", "medium", "high", "critical"]:
            priority = "medium"

        owner = item.get("owner", "Unassigned")
        if not owner or owner.lower() in ["none", "null", "unknown", "someone", "maybe"]:
            owner = "Unassigned"

        confidence = float(item.get("confidence", 0.90))
        needs_review = item.get("needs_review", False) or confidence < 0.70 or owner == "Unassigned"
        
        status = "needs_review" if needs_review else "pending"

        action_items.append(ActionItem(
            id=item_id,
            meeting_id=meeting_id,
            task_title=title,
            task_description=item.get("task_description") or "",
            owner=owner,
            deadline=item.get("deadline"),
            priority=priority,
            status=status,
            confidence=confidence,
            source_quote=item.get("source_quote") or "",
            needs_review=needs_review,
            dependencies=item.get("dependencies") or [],
            reminders_sent=0
        ))

    # Parse Decisions
    raw_decisions = data.get("decisions", [])
    decisions: List[Decision] = []
    for d in raw_decisions:
        decisions.append(Decision(
            id=f"dec_{str(uuid.uuid4())[:6]}",
            meeting_id=meeting_id,
            decision=d.get("decision", "Decision item"),
            decided_by=d.get("decided_by", "Team"),
            source_quote=d.get("source_quote") or "",
            confidence=float(d.get("confidence", 0.95))
        ))

    # Parse Risks & Blockers
    raw_rb = data.get("risks_blockers", [])
    risks_blockers: List[RiskBlocker] = []
    for rb in raw_rb:
        rb_type = rb.get("type", "risk")
        if rb_type not in ["risk", "blocker"]:
            rb_type = "risk"
        
        sev = rb.get("severity", "medium")
        if sev not in ["low", "medium", "high", "critical"]:
            sev = "medium"

        risks_blockers.append(RiskBlocker(
            id=f"rb_{str(uuid.uuid4())[:6]}",
            meeting_id=meeting_id,
            type=rb_type,
            description=rb.get("description", "Risk/Blocker item"),
            severity=sev,
            blocked_task=rb.get("blocked_task"),
            depends_on=rb.get("depends_on"),
            source_quote=rb.get("source_quote") or "",
            confidence=float(rb.get("confidence", 0.90))
        ))

    # Summary
    summary_text = data.get("summary") or "The team reviewed project milestones, assigned critical tasks, and aligned on delivery dates."
    
    risks_count = sum(1 for rb in risks_blockers if rb.type == "risk")
    blockers_count = sum(1 for rb in risks_blockers if rb.type == "blocker")

    summary = MeetingSummary(
        meeting_id=meeting_id,
        summary_text=summary_text,
        action_items_count=len(action_items),
        decisions_count=len(decisions),
        risks_count=risks_count,
        blockers_count=blockers_count
    )

    return summary, action_items, decisions, risks_blockers

def _heuristic_nlp_extraction(text: str) -> Dict[str, Any]:
    """Smart heuristic fallback parser if API key is not present."""
    action_items = []
    decisions = []
    risks_blockers = []
    
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    
    for line in lines:
        if len(line) < 15:
            continue
            
        speaker = "Unassigned"
        content = line
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                speaker_match = re.match(r"^([A-Za-z0-9\s\(\)]+)", parts[0].strip())
                if speaker_match:
                    raw_name = speaker_match.group(1).split("(")[0].strip()
                    speaker = raw_name.split()[0] if raw_name.split() else "Unassigned"
                content = parts[1].strip()

        # Check for Decision
        if any(kw in content.lower() for kw in ["decision:", "agreed:", "confirmed:", "decided"]):
            decisions.append({
                "decision": re.sub(r"^(Decision|Confirmed|Agreed):?\s*", "", content, flags=re.IGNORECASE),
                "decided_by": speaker if speaker != "Unassigned" else "Team",
                "source_quote": line,
                "confidence": 0.95
            })
            continue

        # Check for Blocker / Risk
        if "blocker:" in content.lower() or "cannot finish" in content.lower() or "delay" in content.lower():
            risks_blockers.append({
                "type": "blocker" if "blocker:" in content.lower() or "cannot" in content.lower() else "risk",
                "description": content,
                "severity": "high" if "urgent" in content.lower() or "critical" in content.lower() else "medium",
                "blocked_task": "Task integration",
                "depends_on": speaker,
                "source_quote": line,
                "confidence": 0.92
            })
            continue

        # Check for Action Item keywords
        action_kws = ["will", "shall", "need to", "must", "going to", "take care of", "assigned to", "own", "finish", "complete", "integrate", "implement", "update", "rotate", "run", "prepare", "hire", "finalize", "publish"]
        if any(kw in content.lower() for kw in action_kws):
            # Extract date
            deadline = None
            date_match = re.search(r"(?:by|before|on|due)\s+([A-Z][a-z]+,?\s+\d{1,2}(?:st|nd|rd|th)?|\d{4}-\d{2}-\d{2}|[A-Z][a-z]+\s+\d{1,2}|tomorrow|next\s+[A-Za-z]+)", content, re.IGNORECASE)
            if date_match:
                deadline = date_match.group(1).strip()

            # Infer concise title vs description
            title_text = content
            title_text = re.sub(r"^(I will|We need to|I'll|Great|Awesome|Perfect|Sure|Also urgent:?)\s*", "", title_text, flags=re.IGNORECASE).capitalize()
            if len(title_text) > 50:
                title_text = title_text[:47] + "..."

            owner = speaker
            confidence = 0.92
            needs_review = False

            if any(w in content.lower() for w in ["maybe", "unclear", "someone", "if bandwidth"]):
                owner = "Unassigned"
                confidence = 0.58
                needs_review = True

            priority = "medium"
            if any(w in content.lower() for w in ["urgent", "critical", "must", "asap", "high priority"]):
                priority = "high"

            action_items.append({
                "task_title": title_text,
                "task_description": content,
                "owner": owner,
                "deadline": deadline,
                "priority": priority,
                "confidence": confidence,
                "source_quote": line,
                "needs_review": needs_review,
                "dependencies": []
            })

    summary_text = "The team met to review deliverable readiness, assign ownership for key modules, document explicit project decisions, and mitigate potential dependency risks."
    
    return {
        "summary": summary_text,
        "action_items": action_items,
        "decisions": decisions,
        "risks_blockers": risks_blockers
    }
