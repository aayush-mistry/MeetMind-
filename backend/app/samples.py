SAMPLE_TRANSCRIPTS = {
    "product_sync": {
        "title": "Product Launch Sync",
        "description": "Cross-functional launch alignment for v2.0 feature release",
        "text": """
Alex (Product Lead): Welcome everyone. We need to finalize our deliverable readiness for the v2.0 release next Friday.

Riya (Engineering): The backend WebSocket pipeline is 90% complete. I will finish the auto-reconnect fallback and API rate limiting by Monday, July 28.

David (Design Lead): Design review for the dark mode glassmorphism UI is wrapped up. I will hand over the final Figma tokens to Sarah by tomorrow, July 26.

Sarah (Frontend Dev): Perfect. Once David gives me the design tokens, I'll integrate them into the React component system. I'll need to finalize the dashboard responsive view by Wednesday, July 30.

Alex: Great. We also need someone to prepare the live demo script and slide deck for the judges. Sarah, can you own the demo slide deck by July 29?

Sarah: Sure, I can take care of the slide deck.

Marcus (QA Lead): QA automation script execution is pending load testing. Marcus will run end-to-end stress tests on the server on Tuesday, July 29.

Riya: Also urgent: we must rotate our production API keys before launch. Riya will update the environment credentials by Sunday, July 27.

Alex: Decision confirmed: Product v2.0 launch remains scheduled for July 31. Let's touch base again on Wednesday. Thanks team!
""",
    },
    "sprint_planning": {
        "title": "Engineering Sprint Planning",
        "description": "Sprint 14 planning meeting for AI Agent infrastructure",
        "text": """
Elena (Tech Lead): Let's assign tasks for Sprint 14. We have three main epics: LLM Extraction, Background Scheduler, and UI Notifications.

Vikram (Backend Engineer): I will implement the Gemini LLM extraction worker with fallback JSON schema validation by end of day Friday, July 27.

Priya (DevOps): I'll set up the Docker containerization and deployment configuration for Railway by Thursday, July 26. High priority.

Tom (Fullstack Dev): I will build the real-time WebSocket connection state indicator and auto-retry logic in the UI by Monday, July 28.

Elena: Decision: We will use SQLite for local persistence during the hackathon and deploy on Railway.

Tom: Maybe someone from design can finish the landing page hero graphics next week, but it's unclear who has bandwidth.

Vikram: Blocker: Tom cannot finish UI notification toast integration until Priya completes the deployment configuration.
""",
    },
    "executive_briefing": {
        "title": "Q3 Executive Strategy Sync",
        "description": "Quarterly strategic review and action plan",
        "text": """
Jonathan (CEO): We need to accelerate our Agentic AI product rollout to stay ahead in the enterprise market.

Samantha (VP Engineering): Samantha will hire two senior AI engineers by August 15.

Michael (CFO): Michael will finalize the Q4 cloud infrastructure budget allocation by August 5.

Jessica (VP Product): Jessica will publish the customer feedback report and feature roadmap by July 31.

Jonathan: Decision: Executive committee approves the $500k cloud infrastructure expansion budget for Q4.

Samantha: Risk: External cybersecurity firm audit could delay public launching if vulnerability remediation takes more than two weeks.
""",
    },
}
