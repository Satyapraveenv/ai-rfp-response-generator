# 📋 AI RFP Response Generator

**BCG-quality RFP proposals in ~60 seconds — for any company, any RFP**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?style=flat-square)
![Claude](https://img.shields.io/badge/Powered%20by-Claude%20AI-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## What It Does

A **Streamlit web app** that generates world-class RFP responses powered by Anthropic's Claude AI.

Enter your company name + website URL → Claude scrapes the site and auto-fills your company profile → paste the RFP → get a BCG-quality proposal in ~60 seconds.

**Output includes:**
- Executive Summary (CEO-readable, conclusion-first)
- Technical Approach & Methodology
- Project Team & Organizational Structure
- Work Plan & Timeline with milestones
- Risk Management & Mitigation
- Compliance Matrix (every RFP requirement mapped)
- Pricing & Cost Structure
- References & Case Studies
- Quality Score (0–100) with gap analysis

---

## The Problem

RFP responses are a **necessary evil** in consulting sales:

- **40–80 hours** of senior consultant time per response
- **~80% of effort is structural**: reformulating past responses, aligning to criteria, ensuring completeness
- **High consistency cost**: manually checking for compliance gaps and missing criteria
- **Opportunity cost**: senior talent stuck doing templated work instead of strategy

This is exactly where AI excels: structured, knowledge-intensive, pattern-based work.

---

## Quick Start

### Prerequisites

```bash
Python 3.8+
Anthropic API key (get one at https://console.anthropic.com)
```

### Installation

```bash
git clone https://github.com/Satyapraveenv/ai-rfp-response-generator.git
cd ai-rfp-response-generator
pip install -r requirements.txt
```

### Configure API Key

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Get your API key at [console.anthropic.com](https://console.anthropic.com). New accounts get free credits to start.

### Run the App

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## How to Use

1. **Enter company name + website** in the sidebar
2. Click **🔍 Auto-fill from Website** — Claude scrapes the site and fills all profile fields automatically
3. Review and edit the extracted details
4. **Paste your RFP** in the main area (or click **📥 Load Sample RFP** for a demo)
5. Click **🚀 Generate World-Class RFP Response**
6. Download the polished HTML proposal

---

## Auto-fill Feature

The auto-fill feature scrapes up to 5 pages from the company website (homepage, /about, /services, /industries, /case-studies) and uses Claude to extract:

- Founded year & HQ location
- Company size & employee count
- Core services & offerings
- Key differentiators
- Certifications & compliance (ISO, SOC 2, CMMI, etc.)
- Industries served
- Notable clients
- Relevant case studies with metrics

All fields are editable before generation — review and customize as needed.

---

## Writing Quality

Responses follow **BCG-style writing principles**:

- **Pyramid Principle** — Lead with conclusion, then evidence
- **MECE** — Mutually Exclusive, Collectively Exhaustive sections
- **Quantified claims** — Specific numbers, not vague language
- **AI-native framing** — Quality Engineering positioned as AI-first, not legacy QA
- **Client-centric mirroring** — Uses the client's exact language from the RFP
- **Risk intelligence** — Proactively names risks the client hasn't mentioned

---

## Architecture

```
ai-rfp-response-generator/
├── app.py                          # Streamlit web app (main entry point)
├── generator.py                    # Claude API integration + HTML export
├── scraper.py                      # Website scraper + profile extractor
├── prompts/
│   └── bcg_system_prompt.md        # BCG-style writing system prompt
├── examples/
│   └── sample-rfp-requirements.md  # Sample RFP for testing
├── templates/
│   └── rfp-response-template.md    # Response structure reference
├── innominds-rfp.md                # Demo RFP (HealthFirst Insurance)
├── innominds-demo-response.html    # Demo output (rendered proposal)
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Business Impact

| Metric | Impact |
|--------|--------|
| **Time Saved** | 30–50 hours per RFP (38–62% reduction) |
| **Compliance** | 95%+ coverage of evaluation criteria |
| **Turnaround** | ~60 seconds vs. 3–5 days |
| **Consistency** | Same high standard across all responses |
| **Scale** | Bid more RFPs without adding headcount |

---

## Roadmap

- [ ] PDF and DOCX RFP upload support
- [ ] Multi-turn refinement (iterate sections with AI feedback)
- [ ] Saved company profiles (reuse across RFPs)
- [ ] Side-by-side RFP requirement ↔ response view
- [ ] Team collaboration (mark sections for review)
- [ ] CRM integration (Salesforce, HubSpot)

---

## License

MIT License — 2025 — Satya Praveen Vemuri

---

## About the Author

**Satya Praveen Vemuri** — Pre-sales & RFP Strategy

- Led $3M+ in RFP-driven enterprise wins
- Built RFP processes for high-growth IT services firms
- 10+ years in technology sales and solutions engineering

**Connect**: [LinkedIn](https://www.linkedin.com/in/satyapraveenv/)

---

## Disclaimer

This tool generates response outlines and drafts, not final RFP submissions. All generated content must be reviewed, customized, and approved by qualified team members before submission.
