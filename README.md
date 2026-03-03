# RunesCard Social Media AI Agent

An autonomous AI agent that generates and publishes on-brand content for [RunesCard](https://runescard.xyz) across Twitter/X and Farcaster — powered by Google Gemini.

```
social-media-agent/
├── agent.py                      # Main orchestrator (CLI entry point)
├── scheduler.py                  # Automated posting daemon (APScheduler)
├── generators/
│   └── content_generator.py      # LLM content generation (Gemini / OpenAI)
├── publishers/
│   ├── twitter.py                # Twitter/X publisher (Tweepy)
│   └── farcaster.py              # Farcaster publisher (Neynar API)
├── templates/
│   └── runescard_context.txt     # Brand context injected into every prompt
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Quick Start

### 1. Create your virtual environment

```bash
cd social-media-agent
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials (see [API Keys](#api-keys) below).

### 4. Test with dry-run

Preview generated content without posting anything:

```bash
python3 agent.py --dry-run
```

### 5. Go live

```bash
python3 agent.py --live
```

---

## CLI Usage

```
python3 agent.py [options]

Options:
  --dry-run               Preview content without posting (safe default)
  --live                  Force live posting (overrides DRY_RUN=true in .env)
  --platform twitter      Target a single platform
  --platform farcaster    Target a single platform
  --post-type TYPE        Force a content category (see types below)
  --hint "text"           Give the LLM extra context or a hook idea
```

### Content types (`--post-type`)

| Type                  | Description                                  |
| --------------------- | -------------------------------------------- |
| `feature_spotlight`   | Highlight a specific RunesCard feature       |
| `engagement_question` | Ask the community a fun/relevant question    |
| `educational`         | Explain crypto gifting, Base, or Web3 simply |
| `milestone_stat`      | Celebrate growth or usage milestones         |
| `seasonal_trending`   | Tie RunesCard to current events or trends    |
| `call_to_action`      | Drive traffic to the app or referral program |

### Examples

```bash
# Generate one post per platform in dry-run
python3 agent.py --dry-run

# Educational tweet only
python3 agent.py --platform twitter --post-type educational

# Post with a specific hook, live
python3 agent.py --hint "we just hit 10,000 cards sent!" --live

# Farcaster CTA, dry-run
python3 agent.py --platform farcaster --post-type call_to_action --dry-run
```

---

## Automated Scheduler

Run the scheduler daemon to post automatically throughout the day:

```bash
python3 scheduler.py
```

Posts are distributed evenly across 16 waking hours based on `POST_FREQUENCY`.

Run once immediately, then exit:

```bash
python3 scheduler.py --once
```

---

## API Keys

### Google Gemini (default LLM — free tier available)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Set `GEMINI_API_KEY` in `.env`

### Twitter / X

1. Apply for a developer account at [developer.twitter.com](https://developer.twitter.com)
2. Create a project + app with **Read and Write** permissions
3. Generate **API Key**, **API Secret**, **Access Token**, **Access Token Secret**
4. Set all four values in `.env`

### Farcaster (via Neynar — no local wallet required)

1. Sign up at [neynar.com](https://neynar.com) and get an API key
2. Create a **managed signer** for your Farcaster account in the Neynar dashboard
3. Copy the **Signer UUID**
4. Set `NEYNAR_API_KEY` and `FARCASTER_SIGNER_UUID` in `.env`

---

## Configuration Reference (`.env`)

| Variable                      | Default             | Description                                |
| ----------------------------- | ------------------- | ------------------------------------------ |
| `LLM_PROVIDER`                | `gemini`            | `gemini` or `openai`                       |
| `GEMINI_API_KEY`              | —                   | Google Gemini API key                      |
| `OPENAI_API_KEY`              | —                   | OpenAI API key (alternative)               |
| `TWITTER_API_KEY`             | —                   | Twitter consumer key                       |
| `TWITTER_API_SECRET`          | —                   | Twitter consumer secret                    |
| `TWITTER_ACCESS_TOKEN`        | —                   | Twitter access token                       |
| `TWITTER_ACCESS_TOKEN_SECRET` | —                   | Twitter access token secret                |
| `NEYNAR_API_KEY`              | —                   | Neynar API key                             |
| `FARCASTER_SIGNER_UUID`       | —                   | Neynar managed signer UUID                 |
| `ENABLED_PLATFORMS`           | `twitter,farcaster` | Comma-separated active platforms           |
| `POST_FREQUENCY`              | `3`                 | Posts per day (scheduler)                  |
| `DRY_RUN`                     | `true`              | `true` = preview only, `false` = post live |
| `LOG_LEVEL`                   | `INFO`              | `DEBUG`, `INFO`, `WARNING`, `ERROR`        |

---

## Customising Brand Voice

Edit [`templates/runescard_context.txt`](templates/runescard_context.txt) to update:

- Product description and value props
- Tone of voice guidelines
- Hashtags to use
- Things to avoid

This file is injected as context into every LLM prompt.

---

## Deployment Options

| Option             | Notes                                                                     |
| ------------------ | ------------------------------------------------------------------------- |
| **Local cron**     | `0 9,13,17 * * * /path/to/.venv/bin/python3 /path/to/scheduler.py --once` |
| **Railway worker** | Add a `Procfile`: `worker: python3 scheduler.py`                          |
| **GitHub Actions** | Trigger on schedule with `workflow_dispatch`                              |
| **Docker**         | Wrap with a simple `Dockerfile` + `CMD ["python3", "scheduler.py"]`       |
