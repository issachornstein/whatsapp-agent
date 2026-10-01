"""
Basic WhatsApp agent webhook for the Meta WhatsApp Business Platform.

How it works:
  1. Meta calls GET /webhook once to verify your server (uses VERIFY_TOKEN).
  2. Every incoming WhatsApp message arrives as POST /webhook.
  3. The agent replies automatically via the Graph API.

Setup is in README.md. Secrets come from environment variables only.
"""

import os

import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
GRAPH_VERSION = "v26.0"

# ---------------------------------------------------------------------------
# Edit your replies here
# ---------------------------------------------------------------------------
DEFAULT_REPLY = (
    "Hi! Thanks for reaching out. This is an automated reply — "
    "tell me what you're looking for and I'll get back to you shortly."
)


def build_reply(incoming_text: str) -> str:
    """Decide what to say back. Add your own keywords below."""
    t = incoming_text.strip().lower()
    if any(w in t for w in ("price", "cost", "how much")):
        return "Pricing depends on the property — send me the address and I'll run the numbers."
    if any(w in t for w in ("hello", "hi", "hey", "yo")):
        return "Hey! What property are you asking about?"
    if "hours" in t or "open" in t:
        return "We're available 7 days a week — just drop your question here."
    return DEFAULT_REPLY


# ---------------------------------------------------------------------------
# Webhook endpoints
# ---------------------------------------------------------------------------
@app.get("/webhook")
def verify():
    """One-time handshake Meta performs when you save the webhook URL."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


@app.post("/webhook")
def incoming():
    """Receives every incoming message event from Meta."""
    data = request.get_json(force=True, silent=True) or {}
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                # Only handle plain text messages for now
                if msg.get("type") == "text":
                    sender = msg["from"]
                    text = msg["text"].get("body", "")
                    try:
                        send_text(sender, build_reply(text))
                    except Exception as exc:  # noqa: BLE001 - keep webhook fast
                        app.logger.exception("Reply failed: %s", exc)
    # Always answer fast so Meta doesn't retry the event
    return "OK", 200


@app.get("/")
def index():
    return "WhatsApp agent is running.", 200


# ---------------------------------------------------------------------------
# Sending
# ---------------------------------------------------------------------------
def send_text(to: str, text: str) -> None:
    """Send a WhatsApp text message via the Cloud API."""
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
