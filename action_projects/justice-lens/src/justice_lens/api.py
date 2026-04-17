"""JusticeLens REST API — audit decisions via HTTP."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from .audit import BiasAuditor, audit_dataset
import pandas as pd
import tempfile
import os

app = FastAPI(title="JusticeLens API", version="0.1.0")

class AuditRequest(BaseModel):
    decision_col: str
    protected_cols: list[str]
    favorable_outcome: int = 1

@app.post("/audit")
async def audit_file(file: UploadFile = File(...), request: AuditRequest = None):
    """Upload CSV, receive bias report."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        df = pd.read_csv(tmp_path)
        os.unlink(tmp_path)
        auditor = BiasAuditor(df, request.decision_col, request.protected_cols, request.favorable_outcome)
        report = auditor.generate_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "service": "JusticeLens"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
