#!/usr/bin/env python3
"""
Launch the Notion → Claude summary webhook server.

Usage:
    python run_notion_webhook.py

Environment variables (set in .env or export before running):
    ANTHROPIC_API_KEY       required
    NOTION_TOKEN            required  (Notion Internal Integration Token)
    NOTION_SUMMARY_PROPERTY optional  (defaults to "Summary")
    PORT                    optional  (defaults to 8000)

Expose the server publicly with ngrok, then paste the URL into Notion:
    ngrok http 8000
    Notion URL field: https://<id>.ngrok-free.app/notion-webhook
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional if env vars are already set

import uvicorn

PORT = int(os.environ.get("PORT", 8000))

missing = [v for v in ("ANTHROPIC_API_KEY", "NOTION_TOKEN") if not os.environ.get(v)]
if missing:
    print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    print(f"Starting Notion webhook server on http://0.0.0.0:{PORT}")
    print(f"Notion automation URL: http://0.0.0.0:{PORT}/notion-webhook")
    print(f"  (expose publicly via: ngrok http {PORT})")
    uvicorn.run(
        "notion_webhook.server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
    )
