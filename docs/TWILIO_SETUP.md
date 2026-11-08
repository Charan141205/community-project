# Live Twilio SMS & WhatsApp Setup Guide

`flood-ews` includes native support for live SMS and WhatsApp emergency broadcasts in **English, Telugu, and Hindi** using Twilio's Programmable Messaging API.

---

## 1. Prerequisites (Twilio Account)

1. Sign up for a free account at [twilio.com](https://www.twilio.com).
2. On your Twilio Console Dashboard, copy your:
   - **Account SID** (e.g. `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (e.g. `your_auth_token_here`)
   - **Twilio Phone Number** (e.g. `+1234567890`)

---

## 2. Setting Up WhatsApp Sandbox (Free Testing)

1. In the Twilio Console, go to **Messaging > Try it out > Send a WhatsApp message**.
2. Follow the instructions to join your sandbox by sending the activation phrase (e.g. `join <two-words>`) from your WhatsApp to the Twilio WhatsApp sandbox number (`+1 415 523 8886`).
3. Note your Twilio WhatsApp number: `whatsapp:+14155238886`.

---

## 3. Configuring `.env`

Copy `.env.example` to `.env` (or update `.env`):

```bash
# Enable Live Alert Dispatching
MOCK_ALERTS=false

# Twilio Credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 4. Testing Live Alert Dispatching

### Method A: Via Python Test Script
With your `.env` configured, run:

```bash
python scripts/simulate.py --scenario critical --duration 15
```

When sensor nodes surge past 70% (**WARNING**) or 85% (**CRITICAL**), the backend will automatically dispatch real SMS and WhatsApp alerts to all subscribers registered in that ward.

### Method B: Registering Your Phone Number for Alerts
1. Open the Community Portal: [http://localhost:3000/public](http://localhost:3000/public).
2. Click **Get SMS / WhatsApp Alerts**.
3. Enter your phone number (including country code, e.g. `+919876543210`), select your ward (e.g. `Amberpet`), and select your preferred language (`Telugu`, `Hindi`, or `English`).
4. Click **Opt-In for Alerts**.
5. When `drain-01` or `drain-03` escalates, you will receive an emergency notification directly on your mobile device!
