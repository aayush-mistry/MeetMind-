import os
import json
import re
import uuid
import asyncio
from typing import List, Dict, Any, Tuple
from app.models import ActionItem, Decision, RiskBlocker, MeetingSummary, MeetingTopic


async def extract_meeting_intelligence(meeting_id: str, transcript_text: str) -> Tuple[
    MeetingSummary,
    List[ActionItem],
    List[Decision],
    List[RiskBlocker],
    List[MeetingTopic],
]:

    if not transcript_text or not transcript_text.strip():
        empty_summary = MeetingSummary(
            meeting_id=meeting_id,
            summary_text="No discussion recorded.",
            action_items_count=0,
            decisions_count=0,
            risks_count=0,
            blockers_count=0,
        )
        return empty_summary, [], [], [], []

    try:
        from app.services.ai.provider_factory import get_ai_provider

        provider = get_ai_provider()
        data = await provider.extract_meeting_intelligence(transcript_text)
    except Exception as e:
        print(f"[Extractor] AI API call error/fallback: {e}")
        data = _heuristic_nlp_extraction(transcript_text)

    # Parse Action Items
    raw_action_items = data.get("action_items", [])
    action_items: List[ActionItem] = []
    item_id_map = {}  # title -> id for resolving dependencies

    for idx, item in enumerate(raw_action_items):
        item_id = f"item_{str(uuid.uuid4())[:6]}"
        title = item.get("task_title") or f"Action item #{idx+1}"
        item_id_map[title.lower()] = item_id

        priority = item.get("priority", "medium")
        if priority not in ["low", "medium", "high", "critical"]:
            priority = "medium"

        owner = item.get("owner", "Unassigned")
        if not owner or owner.lower() in [
            "none",
            "null",
            "unknown",
            "someone",
            "maybe",
        ]:
            owner = "Unassigned"

        confidence = float(item.get("confidence", 0.90))
        needs_review = (
            item.get("needs_review", False)
            or confidence < 0.70
            or owner == "Unassigned"
        )

        status = "needs_review" if needs_review else "pending"

        action_items.append(
            ActionItem(
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
                reminders_sent=0,
            )
        )

    # Parse Decisions
    raw_decisions = data.get("decisions", [])
    decisions: List[Decision] = []
    for d in raw_decisions:
        decisions.append(
            Decision(
                id=f"dec_{str(uuid.uuid4())[:6]}",
                meeting_id=meeting_id,
                decision=d.get("decision", "Decision item"),
                decided_by=d.get("decided_by", "Team"),
                source_quote=d.get("source_quote") or "",
                confidence=float(d.get("confidence", 0.95)),
            )
        )

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

        risks_blockers.append(
            RiskBlocker(
                id=f"rb_{str(uuid.uuid4())[:6]}",
                meeting_id=meeting_id,
                type=rb_type,
                description=rb.get("description", "Risk/Blocker item"),
                severity=sev,
                blocked_task=rb.get("blocked_task"),
                depends_on=rb.get("depends_on"),
                source_quote=rb.get("source_quote") or "",
                confidence=float(rb.get("confidence", 0.90)),
            )
        )

    # Summary
    summary_text = (
        data.get("summary")
        or "The team reviewed project milestones, assigned critical tasks, and aligned on delivery dates."
    )

    risks_count = sum(1 for rb in risks_blockers if rb.type == "risk")
    blockers_count = sum(1 for rb in risks_blockers if rb.type == "blocker")

    summary = MeetingSummary(
        meeting_id=meeting_id,
        summary_text=summary_text,
        action_items_count=len(action_items),
        decisions_count=len(decisions),
        risks_count=risks_count,
        blockers_count=blockers_count,
    )

    # Parse Topics
    raw_topics = data.get("topics", [])
    topics: List[MeetingTopic] = []
    for t in raw_topics:
        topics.append(
            MeetingTopic(
                id=f"topic_{str(uuid.uuid4())[:6]}",
                meeting_id=meeting_id,
                topic_name=t.get("topic_name", "Discussion Topic"),
                start_time=t.get("start_time", ""),
                end_time=t.get("end_time", ""),
                duration=t.get("duration", ""),
                summary=t.get("summary", ""),
                keywords=t.get("keywords", []),
                speakers=t.get("speakers", []),
                confidence=float(t.get("confidence", 0.90)),
                transcript_range=t.get("transcript_range", ""),
            )
        )

    # --- Vector DB Indexing ---
    try:
        from app.services.vector_db import vector_db
        from app.services.ai.embeddings import embedding_service
        
        if vector_db.is_available() and embedding_service.model:
            # 1. Chunk and embed transcript
            chunks = embedding_service.chunk_transcript(transcript_text)
            if chunks:
                chunk_embeddings = embedding_service.get_embeddings(chunks)
                chunk_metadatas = [{"meeting_id": meeting_id, "type": "transcript_chunk"} for _ in chunks]
                vector_db.add_chunks(meeting_id, chunks, chunk_embeddings, chunk_metadatas)

            # 2. Embed topics
            topic_texts = [f"Topic: {t.topic_name}. Summary: {t.summary}. Keywords: {', '.join(t.keywords)}" for t in topics]
            if topic_texts:
                topic_embeddings = embedding_service.get_embeddings(topic_texts)
                topic_metadatas = [{"meeting_id": meeting_id, "type": "topic", "topic_id": t.id, "topic_name": t.topic_name} for t in topics]
                vector_db.add_metadata_items(meeting_id, topic_texts, topic_embeddings, topic_metadatas)

            # 3. Embed Action Items
            ai_texts = [f"Action Item: {ai.task_title}. Owner: {ai.owner}. Desc: {ai.task_description}" for ai in action_items]
            if ai_texts:
                ai_embeddings = embedding_service.get_embeddings(ai_texts)
                ai_metadatas = [{"meeting_id": meeting_id, "type": "action_item", "item_id": ai.id} for ai in action_items]
                vector_db.add_metadata_items(meeting_id, ai_texts, ai_embeddings, ai_metadatas)

            # 4. Embed Decisions
            dec_texts = [f"Decision: {d.decision}. By: {d.decided_by}" for d in decisions]
            if dec_texts:
                dec_embeddings = embedding_service.get_embeddings(dec_texts)
                dec_metadatas = [{"meeting_id": meeting_id, "type": "decision", "decision_id": d.id} for d in decisions]
                vector_db.add_metadata_items(meeting_id, dec_texts, dec_embeddings, dec_metadatas)
                
            # 5. Embed Risks/Blockers
            rb_texts = [f"{rb.type.capitalize()}: {rb.description}. Severity: {rb.severity}" for rb in risks_blockers]
            if rb_texts:
                rb_embeddings = embedding_service.get_embeddings(rb_texts)
                rb_metadatas = [{"meeting_id": meeting_id, "type": rb.type, "item_id": rb.id} for rb in risks_blockers]
                vector_db.add_metadata_items(meeting_id, rb_texts, rb_embeddings, rb_metadatas)
                
            print(f"[Extractor] Successfully indexed meeting {meeting_id} into Vector DB")
            
    except Exception as e:
        print(f"[Extractor] Error indexing to Vector DB: {e}")

    return summary, action_items, decisions, risks_blockers, topics


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
        if any(
            kw in content.lower()
            for kw in ["decision:", "agreed:", "confirmed:", "decided"]
        ):
            decisions.append(
                {
                    "decision": re.sub(
                        r"^(Decision|Confirmed|Agreed):?\s*",
                        "",
                        content,
                        flags=re.IGNORECASE,
                    ),
                    "decided_by": speaker if speaker != "Unassigned" else "Team",
                    "source_quote": line,
                    "confidence": 0.95,
                }
            )
            continue

        # Check for Blocker / Risk
        if (
            "blocker:" in content.lower()
            or "cannot finish" in content.lower()
            or "delay" in content.lower()
        ):
            risks_blockers.append(
                {
                    "type": (
                        "blocker"
                        if "blocker:" in content.lower() or "cannot" in content.lower()
                        else "risk"
                    ),
                    "description": content,
                    "severity": (
                        "high"
                        if "urgent" in content.lower() or "critical" in content.lower()
                        else "medium"
                    ),
                    "blocked_task": "Task integration",
                    "depends_on": speaker,
                    "source_quote": line,
                    "confidence": 0.92,
                }
            )
            continue

        # Check for Action Item keywords
        action_kws = [
            "will",
            "shall",
            "need to",
            "must",
            "going to",
            "take care of",
            "assigned to",
            "own",
            "finish",
            "complete",
            "integrate",
            "implement",
            "update",
            "rotate",
            "run",
            "prepare",
            "hire",
            "finalize",
            "publish",
        ]
        if any(kw in content.lower() for kw in action_kws):
            # Extract date
            deadline = None
            date_match = re.search(
                r"(?:by|before|on|due)\s+([A-Z][a-z]+,?\s+\d{1,2}(?:st|nd|rd|th)?|\d{4}-\d{2}-\d{2}|[A-Z][a-z]+\s+\d{1,2}|tomorrow|next\s+[A-Za-z]+)",
                content,
                re.IGNORECASE,
            )
            if date_match:
                deadline = date_match.group(1).strip()

            # Infer concise title vs description
            title_text = content
            title_text = re.sub(
                r"^(I will|We need to|I'll|Great|Awesome|Perfect|Sure|Also urgent:?)\s*",
                "",
                title_text,
                flags=re.IGNORECASE,
            ).capitalize()
            if len(title_text) > 50:
                title_text = title_text[:47] + "..."

            owner = speaker
            confidence = 0.92
            needs_review = False

            if any(
                w in content.lower()
                for w in ["maybe", "unclear", "someone", "if bandwidth"]
            ):
                owner = "Unassigned"
                confidence = 0.58
                needs_review = True

            priority = "medium"
            if any(
                w in content.lower()
                for w in ["urgent", "critical", "must", "asap", "high priority"]
            ):
                priority = "high"

            action_items.append(
                {
                    "task_title": title_text,
                    "task_description": content,
                    "owner": owner,
                    "deadline": deadline,
                    "priority": priority,
                    "confidence": confidence,
                    "source_quote": line,
                    "needs_review": needs_review,
                    "dependencies": [],
                }
            )

    # Fallback topics
    topics = [
        {
            "topic_name": "General Discussion",
            "start_time": "00:00",
            "end_time": "00:00",
            "duration": "0m",
            "summary": "General meeting discussion.",
            "keywords": ["Discussion"],
            "speakers": [],
            "confidence": 0.5,
            "transcript_range": "",
        }
    ]

    return {
        "summary": "Meeting discussion recorded and heuristically parsed. Please configure an AI provider for better insights.",
        "action_items": action_items,
        "decisions": decisions,
        "risks_blockers": risks_blockers,
        "topics": topics,
    }
