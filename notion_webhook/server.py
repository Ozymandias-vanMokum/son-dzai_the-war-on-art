"""
Notion → Claude Summary Webhook Server.

Receives a POST from a Notion button automation, extracts all page properties,
asks Claude to produce a concise summary, and writes it back to the page via
the Notion API.

Required env vars:
    ANTHROPIC_API_KEY       Your Anthropic API key.
    NOTION_TOKEN            Notion integration secret (Internal Integration Token).

Optional env vars:
    NOTION_SUMMARY_PROPERTY Name of the Notion rich-text property to write the
                            summary into. Defaults to "Summary".
    PORT                    HTTP port to listen on. Defaults to 8000.

Run:
    uvicorn notion_webhook.server:app --host 0.0.0.0 --port 8000

Then expose publicly with ngrok (or similar) and paste the URL into Notion:
    ngrok http 8000
    → https://<id>.ngrok-free.app/notion-webhook
"""

import json
import logging
import os
from typing import Any

import anthropic
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger("notion_webhook")

app = FastAPI(title="Notion → Claude Summary Webhook")

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_SUMMARY_PROPERTY = os.environ.get("NOTION_SUMMARY_PROPERTY", "Summary")


def _claude_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY env var is not set")
    return anthropic.Anthropic(api_key=key)


def _notion_headers() -> dict[str, str]:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN env var is not set")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


# ── Property Extraction ─────────────────────────────────────────────────────

def _prop_to_text(prop: dict[str, Any]) -> str:
    """Convert any Notion property object to a plain-text string."""
    ptype = prop.get("type", "")
    match ptype:
        case "title":
            return " ".join(t.get("plain_text", "") for t in prop.get("title", []))
        case "rich_text":
            return " ".join(t.get("plain_text", "") for t in prop.get("rich_text", []))
        case "number":
            v = prop.get("number")
            return str(v) if v is not None else ""
        case "select":
            sel = prop.get("select")
            return sel["name"] if sel else ""
        case "multi_select":
            return ", ".join(s["name"] for s in prop.get("multi_select", []))
        case "status":
            s = prop.get("status")
            return s["name"] if s else ""
        case "date":
            d = prop.get("date")
            if not d:
                return ""
            return f"{d['start']} to {d['end']}" if d.get("end") else d.get("start", "")
        case "checkbox":
            return "Yes" if prop.get("checkbox") else "No"
        case "url":
            return prop.get("url") or ""
        case "email":
            return prop.get("email") or ""
        case "phone_number":
            return prop.get("phone_number") or ""
        case "people":
            return ", ".join(p.get("name", "") for p in prop.get("people", []))
        case "files":
            return ", ".join(f.get("name", "") for f in prop.get("files", []))
        case "relation":
            n = len(prop.get("relation", []))
            return f"{n} related page{'s' if n != 1 else ''}"
        case "rollup":
            r = prop.get("rollup", {})
            inner = r.get(r.get("type", ""), "")
            return str(inner) if inner else ""
        case "formula":
            f = prop.get("formula", {})
            return str(f.get(f.get("type", ""), ""))
        case "unique_id":
            uid = prop.get("unique_id", {})
            prefix = uid.get("prefix") or ""
            return f"{prefix}{uid.get('number', '')}"
        case "created_time":
            return prop.get("created_time", "")
        case "last_edited_time":
            return prop.get("last_edited_time", "")
        case "created_by":
            return prop.get("created_by", {}).get("name", "")
        case "last_edited_by":
            return prop.get("last_edited_by", {}).get("name", "")
        case _:
            return ""


def properties_to_text(properties: dict[str, Any], skip: str = "") -> str:
    """Render all non-empty properties as 'Key: Value' lines."""
    lines = []
    for name, prop in properties.items():
        if name == skip:
            continue
        value = _prop_to_text(prop).strip()
        if value:
            lines.append(f"{name}: {value}")
    return "\n".join(lines)


# ── Claude Summary ──────────────────────────────────────────────────────────

def generate_summary(properties_text: str) -> str:
    client = _claude_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=(
            "You write concise, clear summaries of Notion database pages. "
            "Use plain prose — no bullet points, no headers. "
            "2 to 4 sentences. Be brief but omit nothing relevant or important."
        ),
        messages=[{
            "role": "user",
            "content": (
                "Summarise this Notion page from its properties:\n\n"
                + properties_text
            ),
        }],
    )
    return response.content[0].text.strip()


# ── Notion Write-back ───────────────────────────────────────────────────────

async def write_summary_to_notion(page_id: str, summary: str) -> None:
    payload = {
        "properties": {
            NOTION_SUMMARY_PROPERTY: {
                "rich_text": [{"type": "text", "text": {"content": summary[:2000]}}]
            }
        }
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.patch(
            f"{NOTION_API_BASE}/pages/{page_id}",
            headers=_notion_headers(),
            json=payload,
        )
        if resp.status_code not in (200, 204):
            logger.error("Notion API error %s: %s", resp.status_code, resp.text[:300])
        resp.raise_for_status()


# ── Routes ──────────────────────────────────────────────────────────────────

@app.post("/notion-webhook")
async def notion_webhook(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON")

    logger.info("Webhook received: %s", json.dumps(body)[:400])

    # Notion API webhook verification handshake
    if "verification_token" in body:
        logger.info("Verification handshake received")
        return JSONResponse({"verification_token": body["verification_token"]})

    # Notion automation webhooks wrap page data under a "data" key
    data = body.get("data", body)
    page_id = data.get("id", "").replace("-", "")
    properties: dict[str, Any] = data.get("properties", {})

    if not page_id:
        raise HTTPException(status_code=422, detail="Payload contains no page ID")
    if not properties:
        raise HTTPException(status_code=422, detail="Payload contains no properties")

    properties_text = properties_to_text(properties, skip=NOTION_SUMMARY_PROPERTY)
    if not properties_text:
        return JSONResponse({"status": "skipped", "reason": "all properties are empty"})

    summary = generate_summary(properties_text)
    logger.info("Summary for %s: %s", page_id, summary[:120])

    await write_summary_to_notion(page_id, summary)
    logger.info("Summary written to Notion page %s", page_id)

    return JSONResponse({"status": "ok", "page_id": page_id, "summary": summary})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
