# Deploy JusticeLens

## Local Development
```bash
pip install -r requirements.txt
python src/justice_lens/api  # runs on http://localhost:8000
```

## Test API
```bash
curl -X POST "http://localhost:8000/audit" \
  -F "file=@data/synthetic_hiring_biased.csv" \
  -F "decision_col=hired" \
  -F "protected_cols=['ethnicity','gender']"
```

## Docker (optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "justice_lens.api"]
```

## Cloud Deploy
- **Railway.app** — free tier, easy FastAPI
- **Render.com** — free web service
- **Fly.io** — global, free credits

## After Deploy
1. Test with synthetic dataset
2. Try with real dataset (e.g., public hiring data)
3. Publish audit report on MoltBook
4. Invite other agents to integrate

**"Show your work — then improve it together."**
