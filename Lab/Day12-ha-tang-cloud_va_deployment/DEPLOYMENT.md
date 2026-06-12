# Deployment Information

## Public URL
https://agent-production-1401.up.railway.app/

## Platform
Railway

## Service
- Service name: `agent`
- Environment: `production`
- Region: `sfo`

## Deployment Method
```bash
cd Lab/Day12-ha-tang-cloud_va_deployment/06-lab-complete
railway service link agent
railway up --service agent --detach
railway domain
```

## Runtime Verification

### Root URL check
```bash
curl -sS https://agent-production-1401.up.railway.app/ | head -c 200
```
Expected result:
- Returns Streamlit HTML content (UI is up and serving).

### Header check
```bash
curl -I https://agent-production-1401.up.railway.app/
```
Expected result:
- HTTP success response from Railway edge.

## Environment Variables Set (required for chatbot mode)
- `OPENAI_API_KEY`
- `TMDB_API_KEY`
- `DEFAULT_PROVIDER=openai`
- `DEFAULT_MODEL=gpt-4o-mini`
- `TMDB_LANGUAGE=vi-VN`
- `TMDB_REGION=VN`

Optional variables:
- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`

## Command to export variables to Railway
```bash
railway service link agent

railway variables set \
  OPENAI_API_KEY="sk-xxx" \
  TMDB_API_KEY="tmdb_xxx" \
  DEFAULT_PROVIDER="openai" \
  DEFAULT_MODEL="gpt-4o-mini" \
  TMDB_LANGUAGE="vi-VN" \
  TMDB_REGION="VN"
```

## Notes
- This production URL currently serves the Streamlit application UI.
- Secret values are managed via Railway variables, not committed to source code.
