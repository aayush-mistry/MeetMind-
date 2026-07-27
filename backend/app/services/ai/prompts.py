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
{{
  "summary": "...",
  "action_items": [...],
  "decisions": [...],
  "risks_blockers": [...]
}}
No extra commentary or markdown backticks outside standard json.

Meeting Transcript:
{transcript}
"""

AUDIO_TRANSCRIPTION_PROMPT = """
Listen to this audio file. First, identify the original spoken language.
Then, transcribe the audio perfectly. If the audio is not in English, translate the transcription into English.
Return a JSON object with exactly two string keys: 'original_language' and 'english_transcript'.
"""

CHAT_PROMPT_TEMPLATE = """
Use the following meeting transcripts to answer the user's question.

{context}

User Question: {query}
"""
