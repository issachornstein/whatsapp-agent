# WhatsApp Agent — setup guide

A basic auto-reply agent for the Meta WhatsApp Business Platform.
When someone texts your WhatsApp business number, this replies automatically.

## What you need from Meta

1. Open developers.facebook.com → your app → **WhatsApp → API Setup**.
2. Copy the **Phone number ID** (under the test number, "Phone number identifier").
3. Get a **permanent token**: the token on the API Setup page expires in 24 hours.
   Go to Business Settings → System Users → create one → assign your app →
   generate a token with `whatsapp_business_messaging`. Save it somewhere safe.

## Deploy the code (free, ~10 minutes)

Easiest path is Render:

1. Put these files in a GitHub repo (or zip-upload; Render needs a repo).
2. Go to render.com → New → **Web Service** → connect the repo.
3. Build command: `pip install -r requirements.txt`
   Start command: `gunicorn app:app`
4. In Render's **Environment** tab add:
   - `WHATSAPP_TOKEN` = your permanent token
   - `PHONE_NUMBER_ID` = the phone number ID from Meta
   - `VERIFY_TOKEN` = `SRCU5l20ahfPxJJq0s0Pnt4H4foKVwDe`
5. Deploy. Render gives you a public URL like `https://your-app.onrender.com`.

Quick local test alternative: run `python app.py` and expose it with
`ngrok http 5000` — use the ngrok HTTPS URL as the webhook below.

## Connect Meta to your server

1. In your Meta app → **WhatsApp → Configuration**:
   - Callback URL: `https://your-app.onrender.com/webhook`
   - Verify token: `SRCU5l20ahfPxJJq0s0Pnt4H4foKVwDe`
   - Click **Verify and save**.
2. Under **Webhook fields**, subscribe to `messages`.
3. Text your WhatsApp business number from a registered test number —
   you should get an automatic reply.

## Customize replies

Edit `build_reply()` in `app.py` — add keywords and answers for your
business (e.g. seller-lead qualifying questions). Redeploy after editing.

## Notes

- Replies are free when the customer messages first (24-hour window).
  Messaging them first requires a pre-approved template.
- The test number only talks to numbers listed in API Setup → "To".
  Add your phone there before testing.
