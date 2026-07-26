import re

with open(r"d:\MeetMind--main\backend\app\main.py", "r", encoding="utf-8") as f:
    content = f.read()

new_func = """async def process_uploaded_meeting(meeting_id: str, file_path: str, metadata: Dict):
    \"\"\"Process an uploaded audio/video file.
    Handles extraction, transcription, translation, and AI analysis.
    Broadcasts stage updates over WebSocket.
    \"\"\"
    async def stage_update(stage: str, progress: float = 0.0):
        await broadcast(meeting_id, {"type": "stage_update", "stage": stage, "progress": progress})

    await stage_update("Uploading Audio to Gemini", progress=0.1)
    
    try:
        from google import genai
        import json
        client = genai.Client()
        
        # Upload the file to Gemini
        print(f"Uploading {file_path} to Gemini API...")
        uploaded_file = await run_in_threadpool(client.files.upload, file=file_path)
        
        await stage_update("Transcribing and Translating", progress=0.3)
        
        # Request transcription and language detection
        prompt = (
            "Listen to this audio file. First, identify the original spoken language. "
            "Then, transcribe the audio perfectly. If the audio is not in English, translate the transcription into English. "
            "Return a JSON object with exactly two string keys: 'original_language' and 'english_transcript'."
        )
        
        response = await run_in_threadpool(
            client.models.generate_content,
            model='gemini-2.5-flash',
            contents=[prompt, uploaded_file]
        )
        
        # Delete file from Gemini
        await run_in_threadpool(client.files.delete, name=uploaded_file.name)
        
        # Parse JSON output
        try:
            # Clean markdown code blocks if any
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            detected_lang = data.get("original_language", "Unknown")
            transcript = data.get("english_transcript", "")
        except Exception as e:
            print("Failed to parse Gemini JSON:", e)
            detected_lang = "Unknown"
            transcript = response.text

    except Exception as e:
        print(f"[Gemini Audio] Transcription failed: {e}")
        detected_lang = "en"
        transcript = "Transcription failed due to API error."

    await stage_update(f"Language Detected: {detected_lang}", progress=0.6)
    
    # Save meeting record
    from app.models import Meeting
    meeting = Meeting(
        id=meeting_id, 
        title=metadata.get("file_name", "Uploaded Recording"), 
        description="Uploaded recording", 
        transcript=transcript, 
        created_at=datetime.utcnow().isoformat()
    )
    await run_in_threadpool(database.save_meeting, meeting)
    
    # Update metadata fields in DB
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        \"\"\"UPDATE meetings SET meeting_type=?, original_language=?, translation_language=?, file_name=?, file_size=?, processing_time_seconds=? WHERE id=?\"\"\",
        (
            metadata.get("meeting_type"),
            detected_lang,
            "en",
            metadata.get("file_name"),
            metadata.get("file_size"),
            int(datetime.utcnow().timestamp() - datetime.fromisoformat(meeting.created_at).timestamp()),
            meeting_id,
        ),
    )
    conn.commit()
    conn.close()

    await stage_update("Generating AI Summary", progress=0.8)
    await process_agentic_pipeline(meeting_id, transcript)
    await stage_update("Completed", progress=1.0)

    # Cleanup local file
    if os.path.exists(file_path):
        os.remove(file_path)
"""

# Use regex to replace everything between async def process_uploaded_meeting and @app.post("/api/meeting/{meeting_id}/items")
pattern = re.compile(r'async def process_uploaded_meeting.*?@app\.post\("/api/meeting/\{meeting_id\}/items"\)', re.DOTALL)
new_content = pattern.sub(new_func + '\n@app.post("/api/meeting/{meeting_id}/items")', content)

with open(r"d:\MeetMind--main\backend\app\main.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Patched main.py")
