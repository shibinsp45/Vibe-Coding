import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import vertexai
from google.adk.sessions import VertexAiSessionService

app = FastAPI(title="Manager Dashboard")

# Read settings from environment variables
PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GCP_LOCATION") or "us-east1"
AGENT_RUNTIME_ID = os.getenv("AGENT_RUNTIME_ID")

# Initialize Vertex AI
if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

class ActionRequest(BaseModel):
    approved: bool
    interrupt_id: str

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Manager Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --glass-bg: rgba(255, 255, 255, 0.05);
                --glass-border: rgba(255, 255, 255, 0.1);
                --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                --primary-glow: rgba(99, 102, 241, 0.3);
                --success-glow: rgba(34, 197, 94, 0.3);
                --danger-glow: rgba(239, 68, 68, 0.3);
            }
            body {
                font-family: 'Outfit', sans-serif;
                background-color: #0f111a;
                color: #f8fafc;
                margin: 0;
                min-height: 100vh;
                background-image: 
                    radial-gradient(circle at 15% 50%, var(--primary-glow), transparent 25%),
                    radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.2), transparent 25%);
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 2rem;
            }
            h1 {
                font-weight: 600;
                letter-spacing: 1px;
                margin-bottom: 2rem;
                text-shadow: 0 0 20px rgba(255,255,255,0.2);
            }
            .container {
                width: 100%;
                max-width: 900px;
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }
            .card {
                background: var(--glass-bg);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: var(--glass-shadow);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
            }
            .card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 4px;
                background: linear-gradient(90deg, #6366f1, #8b5cf6);
                opacity: 0.8;
            }
            .header-row {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 1rem;
            }
            .amount {
                font-size: 1.8rem;
                font-weight: 600;
                color: #e2e8f0;
            }
            .detail {
                color: #cbd5e1;
                font-size: 0.95rem;
                margin: 0.3rem 0;
            }
            .label {
                color: #94a3b8;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .actions {
                display: flex;
                gap: 1rem;
                margin-top: 1.5rem;
                justify-content: flex-end;
            }
            button {
                font-family: 'Outfit', sans-serif;
                font-weight: 600;
                padding: 0.6rem 1.5rem;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: all 0.2s ease;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                min-width: 100px;
            }
            .btn-approve {
                background: rgba(34, 197, 94, 0.2);
                color: #4ade80;
                border: 1px solid rgba(34, 197, 94, 0.4);
            }
            .btn-approve:hover {
                background: rgba(34, 197, 94, 0.3);
                box-shadow: 0 0 15px var(--success-glow);
            }
            .btn-reject {
                background: rgba(239, 68, 68, 0.2);
                color: #f87171;
                border: 1px solid rgba(239, 68, 68, 0.4);
            }
            .btn-reject:hover {
                background: rgba(239, 68, 68, 0.3);
                box-shadow: 0 0 15px var(--danger-glow);
            }
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .spinner {
                display: none;
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
                position: absolute;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Modal Styles */
            .modal-overlay {
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(5px);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s ease;
                z-index: 1000;
            }
            .modal-overlay.active {
                opacity: 1;
                pointer-events: all;
            }
            .modal {
                background: var(--glass-bg);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 2rem;
                width: 90%;
                max-width: 500px;
                box-shadow: var(--glass-shadow);
                transform: translateY(20px);
                transition: transform 0.3s ease;
            }
            .modal-overlay.active .modal {
                transform: translateY(0);
            }
            .modal-close {
                background: transparent;
                color: #cbd5e1;
                border: 1px solid #cbd5e1;
                margin-top: 1.5rem;
                width: 100%;
            }
            .modal-close:hover {
                background: rgba(255,255,255,0.1);
            }
            
            .loader-main {
                display: flex;
                align-items: center;
                gap: 10px;
                color: #94a3b8;
            }
            .loader-main::after {
                content: '';
                width: 20px; height: 20px;
                border: 2px solid #6366f1;
                border-radius: 50%;
                border-top-color: transparent;
                animation: spin 1s linear infinite;
            }
        </style>
    </head>
    <body>
        <h1>Manager Dashboard</h1>
        <div id="loading" class="loader-main">Loading pending approvals...</div>
        <div class="container" id="cards-container"></div>

        <div class="modal-overlay" id="modal">
            <div class="modal">
                <h2 id="modal-title">Review Complete</h2>
                <p id="modal-body">The expense report has been finalized.</p>
                <button class="modal-close" onclick="closeModal()">Dismiss</button>
            </div>
        </div>

        <script>
            async function fetchPending() {
                try {
                    const res = await fetch('/api/pending');
                    const data = await res.json();
                    document.getElementById('loading').style.display = 'none';
                    const container = document.getElementById('cards-container');
                    container.innerHTML = '';
                    
                    if (data.length === 0) {
                        container.innerHTML = '<div style="color: #94a3b8; text-align: center;">No pending approvals at this time.</div>';
                        return;
                    }

                    data.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'card';
                        card.id = `card-${item.session_id}`;
                        
                        // Extract details from the payload if available
                        let details = "Review required";
                        if (item.payload && item.payload.message) {
                            details = item.payload.message;
                        }
                        
                        card.innerHTML = `
                            <div class="header-row">
                                <div>
                                    <div class="label">Session ID</div>
                                    <div class="detail" style="font-family: monospace;">${item.session_id}</div>
                                </div>
                                <div class="amount">Action Needed</div>
                            </div>
                            <div class="detail" style="white-space: pre-wrap; margin-top: 1rem; background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">${details}</div>
                            <div class="actions">
                                <button class="btn-reject" onclick="takeAction('${item.session_id}', '${item.interrupt_id}', false, this)">
                                    <span class="btn-text">Reject</span>
                                    <div class="spinner"></div>
                                </button>
                                <button class="btn-approve" onclick="takeAction('${item.session_id}', '${item.interrupt_id}', true, this)">
                                    <span class="btn-text">Approve</span>
                                    <div class="spinner"></div>
                                </button>
                            </div>
                        `;
                        container.appendChild(card);
                    });
                } catch (e) {
                    console.error(e);
                    document.getElementById('loading').textContent = 'Failed to load pending approvals.';
                }
            }

            async function takeAction(sessionId, interruptId, approved, btnElement) {
                const card = document.getElementById(`card-${sessionId}`);
                const buttons = card.querySelectorAll('button');
                
                // Show loading state
                buttons.forEach(b => b.disabled = true);
                btnElement.querySelector('.btn-text').style.opacity = '0';
                btnElement.querySelector('.spinner').style.display = 'block';

                try {
                    const res = await fetch(`/api/action/${sessionId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ approved, interrupt_id: interruptId })
                    });
                    const result = await res.json();
                    
                    // Remove card
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(-20px)';
                    setTimeout(() => card.remove(), 300);
                    
                    // Show modal with final response
                    showModal(approved ? 'Expense Approved' : 'Expense Rejected', 'The agent has resumed processing.');
                    
                    // Refresh if empty
                    setTimeout(() => {
                        const container = document.getElementById('cards-container');
                        if (container.children.length === 0) fetchPending();
                    }, 400);

                } catch (e) {
                    console.error(e);
                    alert("Failed to submit action.");
                    // Reset UI
                    buttons.forEach(b => b.disabled = false);
                    btnElement.querySelector('.btn-text').style.opacity = '1';
                    btnElement.querySelector('.spinner').style.display = 'none';
                }
            }

            function showModal(title, body) {
                document.getElementById('modal-title').textContent = title;
                document.getElementById('modal-body').textContent = body;
                document.getElementById('modal').classList.add('active');
            }
            
            function closeModal() {
                document.getElementById('modal').classList.remove('active');
            }

            // Load on init
            fetchPending();
        </script>
    </body>
    </html>
    """

@app.get("/api/pending")
async def get_pending_sessions():
    if not PROJECT_ID or not AGENT_RUNTIME_ID:
        return []
    
    service = VertexAiSessionService(
        project=PROJECT_ID, 
        location=LOCATION, 
        agent_engine_id=AGENT_RUNTIME_ID
    )
    
    try:
        # User explicitly requested app_name "expense_agent" or similar? The prompt didn't specify app_name, 
        # but earlier we found app_name="expense_agent".
        sessions_resp = await service.list_sessions(app_name="expense_agent", user_id="default-user")
    except Exception as e:
        print(f"Failed to list sessions: {e}")
        return []

    pending_items = []
    
    for s_meta in sessions_resp.sessions:
        try:
            session = await service.get_session(app_name="expense_agent", user_id="default-user", session_id=s_meta.id)
            if not session or not session.events:
                continue
            
            # Find all adk_request_input function calls
            # And check if there is a corresponding function_response
            requests = {}
            responses = set()
            
            for event in session.events:
                # ADK Event structure: event.type, event.name, event.data, event.id
                if getattr(event, "type", "") == "function_call" and getattr(event, "name", "") == "adk_request_input":
                    requests[getattr(event, "id", "")] = event
                elif getattr(event, "type", "") == "function_response" and getattr(event, "name", "") == "adk_request_input":
                    responses.add(getattr(event, "id", ""))
            
            # Unresolved are those in requests but not in responses
            for req_id, req_event in requests.items():
                if req_id not in responses:
                    payload = getattr(req_event, "data", {})
                    # For safety, if data is nested
                    if hasattr(payload, "model_dump"):
                        payload = payload.model_dump()
                    elif not isinstance(payload, dict):
                        payload = {"raw_data": str(payload)}
                    
                    # The message argument might be in payload.get('message')
                    pending_items.append({
                        "session_id": session.id,
                        "interrupt_id": req_id,
                        "payload": payload
                    })
        except Exception as e:
            print(f"Error fetching session {s_meta.id}: {e}")

    return pending_items

@app.post("/api/action/{session_id}")
async def submit_action(session_id: str, action: ActionRequest):
    if not PROJECT_ID or not AGENT_RUNTIME_ID:
        return {"error": "Missing environment configuration"}
        
    resume_payload = {
        "message": {
            "role": "user",
            "parts": [
                {
                    "function_response": {
                        "id": action.interrupt_id,
                        "name": "adk_request_input",
                        "response": {"approved": action.approved}
                    }
                }
            ]
        },
        "session_id": session_id,
        "user_id": "default-user"
    }
    
    try:
        import google.auth
        from google.auth.transport.requests import Request as GoogleAuthRequest
        import requests
        
        credentials, _ = google.auth.default()
        credentials.refresh(GoogleAuthRequest())
        
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json"
        }
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_RUNTIME_ID}:query"
        
        resp = requests.post(url, headers=headers, json={"input": resume_payload})
        resp.raise_for_status()
        return {"status": "success", "response": resp.json()}
    except Exception as e:
        print(f"Error resuming agent for session {session_id}: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
