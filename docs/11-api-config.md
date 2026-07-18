# AI API Config

## Environment

```env
AI_BASE_URL=https://your-gateway.example/v1
AI_API_KEY=replace-with-your-api-key
AI_CHAT_MODEL=grok-4.5
AI_IMAGE_MODEL=grok-4.5
BLOG_DAILY_CAP=30
BLOG_MIN_WORDS=500
BLOG_MAX_WORDS=2000
BLOG_DEFAULT_INLINE_IMAGES=3
```

> API key **hanya** di `.env` lokal (file di-gitignore). Jangan commit, paste ke issue, atau hardcode di script.

## Chat (OpenAI SDK)

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["AI_API_KEY"],
    base_url=os.environ.get("AI_BASE_URL", "https://your-gateway.example/v1"),
)

resp = client.chat.completions.create(
    model="grok-4.5",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ],
    stream=False,
)
text = resp.choices[0].message.content
```

## Image (`/v1/responses`)

```python
import base64, requests, os

BASE = os.environ["AI_BASE_URL"]
KEY = os.environ["AI_API_KEY"]

payload = {
    "model": "grok-4.5",
    "stream": False,
    "store": False,
    "tools": [{"type": "image_generation"}],
    "input": [{
        "role": "user",
        "content": [{
            "type": "input_text",
            "text": f"Generate an image: {prompt}",
        }],
    }],
}

r = requests.post(
    f"{BASE}/responses",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json=payload,
    timeout=180,
)
r.raise_for_status()
data = r.json()

image_b64 = None
for item in data.get("output") or []:
    if item.get("result"):
        image_b64 = item["result"]
    for c in item.get("content") or []:
        if c.get("b64_json"):
            image_b64 = c["b64_json"]

if image_b64:
    open(out_path, "wb").write(base64.b64decode(image_b64))
```

## Health

```bash
curl -s "$AI_BASE_URL/../health"
curl -s "$AI_BASE_URL/models" \
  -H "Authorization: Bearer $AI_API_KEY"
```

## Error handling

| Code | Action |
|------|--------|
| 401 | stop worker, alert key invalid |
| 429 | backoff 30–120s |
| 5xx | retry 3x |
| empty image | retry / skip fig |
