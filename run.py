import uvicorn
from backend.config import PORT, HOST

if __name__ == "__main__":
    print(f"Starting DocuPulse AI (Sarvam AI Document Intelligence Agent) on http://{HOST}:{PORT}")
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)
