"""
AI RFP Response Generator - Core Engine
Uses Claude (Anthropic) to generate world-class RFP responses.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import markdown as md_lib

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)


class RFPGenerator:
    DEFAULT_SECTIONS = [
        "Executive Summary",
        "Company Background & Qualifications",
        "Technical Approach & Methodology",
        "Project Team & Organizational Structure",
        "Work Plan & Timeline",
        "Risk Management & Mitigation",
        "Compliance Matrix",
        "Pricing & Cost Structure",
        "References & Case Studies",
    ]

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Add it to your .env file.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        prompt_path = Path(__file__).parent / "prompts" / "bcg_system_prompt.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "You are a world-class RFP response writer with expertise in IT services and consulting."

    def generate(self, rfp_content: str, company_profile: dict, sections: list = None) -> dict:
        if sections is None:
            sections = self.DEFAULT_SECTIONS

        user_prompt = self._build_prompt(rfp_content, company_profile, sections)

        message = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=8000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text
        quality_score = self._extract_quality_score(response_text)

        return {
            "response":      response_text,
            "quality_score": quality_score,
            "sections":      sections,
            "input_tokens":  message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }

    def _build_prompt(self, rfp_content: str, company: dict, sections: list) -> str:
        sections_str = "\n".join(f"- {s}" for s in sections)

        company_block = f"""
COMPANY RESPONDING TO THIS RFP:
- Name: {company.get('name', '[Company Name]')}
- Founded / Size: {company.get('founded', 'N/A')} | {company.get('size', 'N/A')}
- Headquarters: {company.get('hq', 'N/A')}
- Core Services: {company.get('services', 'N/A')}
- Key Differentiators: {company.get('differentiators', 'N/A')}
- Certifications & Compliance: {company.get('certifications', 'N/A')}
- Industries Served: {company.get('industries', 'N/A')}
- Notable Clients: {company.get('clients', 'N/A')}
- Relevant Case Studies: {company.get('case_studies', 'N/A')}
- Website: {company.get('website', 'N/A')}
"""

        return f"""You are responding to the following RFP on behalf of {company.get('name', 'our company')}.

{company_block}

RFP REQUIREMENTS:
---
{rfp_content}
---

SECTIONS TO GENERATE:
{sections_str}

STRICT FORMATTING RULES — FOLLOW EXACTLY:
1. Use ONLY standard markdown: # headings, **bold**, - bullet lists, numbered lists, and | pipe tables.
2. NEVER use ASCII art, box drawings, or code fences (``` or ~~~) for any diagrams — use markdown tables instead.
3. For team structures, timelines, and architectures: use clean markdown tables with | column headers |.
4. Every major section must start with ## followed by a section number and title (e.g. ## 1. Executive Summary).
5. Sub-sections use ### (e.g. ### 1.1 Our Approach).

CONTENT RULES:
1. Write as a world-class consultant — specific, quantified, client-centric.
2. Use the Pyramid Principle: lead with the conclusion, support with evidence.
3. Position {company.get('name', 'our company')} as the obvious, low-risk, high-value choice.
4. Frame Quality Engineering as AI-native: autonomous testing, self-healing scripts, predictive defect intelligence.
5. Mirror the client's exact language and requirements.
6. Mark [CUSTOMIZE: instruction] wherever real company data is needed.
7. End with a ## Quality Score section showing a score out of 100 with gap analysis.

Generate the full response now. Make it exceptional."""

    def _extract_quality_score(self, text: str) -> int | None:
        patterns = [
            r"Quality\s+Score:?\s*\**(\d+)\**\s*/\s*100",
            r"Score:?\s*\**(\d+)\**\s*/\s*100",
            r"\*\*(\d+)/100\*\*",
            r"(\d+)/100",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        return score
                except (ValueError, IndexError):
                    continue
        return None

    def to_html(self, company_name: str, response_md: str, score: int | None,
                company_profile: dict = None) -> str:
        """Convert markdown response to a polished, professional HTML document."""
        if company_profile is None:
            company_profile = {}

        # ── 1. Parse markdown to HTML using proper library ────────────────────
        extensions = ["tables", "fenced_code", "nl2br", "sane_lists", "attr_list"]
        body_html = md_lib.markdown(response_md, extensions=extensions)

        # ── 2. Highlight [CUSTOMIZE: ...] markers ─────────────────────────────
        body_html = re.sub(
            r'\[CUSTOMIZE:([^\]]+)\]',
            r'<span class="customize">[CUSTOMIZE:\1]</span>',
            body_html
        )

        # ── 3. Inject section IDs for navigation ─────────────────────────────
        section_ids = []
        def add_id(m):
            tag   = m.group(1)
            text  = re.sub(r'<[^>]+>', '', m.group(2))          # strip inner tags
            slug  = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            # Only anchor H1 / H2 for TOC
            if tag in ('h1', 'h2'):
                section_ids.append((slug, text))
            return f'<{tag} id="{slug}">{m.group(2)}</{tag}>'

        body_html = re.sub(r'<(h[123])>(.*?)</\1>', add_id, body_html, flags=re.DOTALL)

        # ── 4. Build TOC from H2 sections ─────────────────────────────────────
        toc_items = "".join(
            f'<a href="#{slug}">{text}</a>'
            for slug, text in section_ids
            if not text.lower().startswith('rfp response')   # skip top-level title
        )

        # ── 5. Score badge & dynamic header values ────────────────────────────
        display_score   = score or 92
        score_color     = "#28a745" if display_score >= 85 else "#ffc107" if display_score >= 70 else "#dc3545"
        company_hq      = company_profile.get("hq") or company_profile.get("founded") or ""
        company_size    = company_profile.get("size", "")
        company_website = company_profile.get("website", "")

        # ── 6. Assemble full HTML ─────────────────────────────────────────────
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RFP Response — {company_name}</title>
<style>
/* ── Reset & base ─────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #f0f2f8;
  color: #1a1a2e;
  line-height: 1.75;
  font-size: 15px;
}}

/* ── Header ───────────────────────────────────────────── */
.header {{
  background: linear-gradient(135deg, #0f3460 0%, #16213e 60%, #1a1a2e 100%);
  color: #ffffff;
  padding: 2.5rem 4rem 2rem;
}}
.header-top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}}
.header-logo {{
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: 2px;
  color: #e94560;
  margin-bottom: 0.6rem;
  text-transform: uppercase;
}}
.header-logo span {{ color: #ffffff; font-weight: 300; }}
.header h1 {{
  font-size: 1.7rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin-bottom: 0.4rem;
  border: none;
  padding: 0;
}}
.header-subtitle {{
  color: #a8b2d8;
  font-size: 0.9rem;
}}
.score-badge {{
  background: {score_color};
  color: #ffffff;
  padding: 0.6rem 1.4rem;
  border-radius: 24px;
  font-weight: 700;
  font-size: 1rem;
  white-space: nowrap;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}}
.header-meta {{
  display: flex;
  gap: 1rem;
  margin-top: 1.4rem;
  flex-wrap: wrap;
}}
.meta-chip {{
  background: rgba(255,255,255,0.1);
  color: #cbd5f0;
  padding: 0.35rem 0.9rem;
  border-radius: 20px;
  font-size: 0.8rem;
  border: 1px solid rgba(255,255,255,0.15);
}}

/* ── Sticky TOC nav ───────────────────────────────────── */
.toc-nav {{
  background: #ffffff;
  border-bottom: 3px solid #e94560;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow-x: auto;
  white-space: nowrap;
}}
.toc-nav a {{
  display: inline-block;
  color: #0f3460;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.85rem 0.9rem;
  border-bottom: 3px solid transparent;
  margin-bottom: -3px;
  transition: color 0.2s, border-color 0.2s;
}}
.toc-nav a:hover {{
  color: #e94560;
  border-bottom-color: #e94560;
}}

/* ── Content wrapper ──────────────────────────────────── */
.content {{
  max-width: 1050px;
  margin: 2.5rem auto;
  padding: 0 2rem 5rem;
}}

/* ── Section cards ────────────────────────────────────── */
.content > h1, .content > h2 {{
  margin-top: 0;
}}
.section-card {{
  background: #ffffff;
  border-radius: 12px;
  padding: 2rem 2.5rem;
  margin-bottom: 1.8rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.06);
}}

/* ── Typography ───────────────────────────────────────── */
h1 {{
  font-size: 1.5rem;
  color: #0f3460;
  margin: 0 0 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 3px solid #e94560;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
h2 {{
  font-size: 1.25rem;
  color: #0f3460;
  margin: 1.8rem 0 0.8rem;
  padding: 0.5rem 0 0.5rem 1rem;
  border-left: 4px solid #e94560;
  background: #f8f9ff;
  border-radius: 0 6px 6px 0;
}}
h3 {{
  font-size: 1.05rem;
  color: #16213e;
  margin: 1.4rem 0 0.6rem;
  font-weight: 700;
}}
h4 {{
  font-size: 0.9rem;
  color: #555;
  margin: 1rem 0 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 600;
}}
p {{ margin: 0.7rem 0; color: #2d2d4e; }}
hr {{ border: none; border-top: 1px solid #e8eaf0; margin: 1.5rem 0; }}
strong {{ color: #0f3460; }}
em {{ color: #555; }}

/* ── Lists ────────────────────────────────────────────── */
ul, ol {{
  margin: 0.6rem 0 0.6rem 1.6rem;
  padding: 0;
}}
li {{
  margin: 0.35rem 0;
  color: #2d2d4e;
  line-height: 1.7;
}}
li p {{ margin: 0; }}

/* ── Tables ───────────────────────────────────────────── */
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 1.2rem 0;
  font-size: 0.88rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08);
}}
thead tr {{
  background: #0f3460;
  color: #ffffff;
}}
thead th {{
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.85rem;
  letter-spacing: 0.3px;
}}
tbody tr {{ border-bottom: 1px solid #eef0f8; }}
tbody tr:nth-child(even) {{ background: #f8f9ff; }}
tbody tr:hover {{ background: #eef2ff; transition: background 0.15s; }}
tbody td {{ padding: 0.65rem 1rem; vertical-align: top; }}

/* ── Code blocks ──────────────────────────────────────── */
pre {{
  background: #f4f6fb;
  border: 1px solid #e0e4f0;
  border-radius: 8px;
  padding: 1rem 1.2rem;
  overflow-x: auto;
  margin: 1rem 0;
  font-size: 0.82rem;
  line-height: 1.6;
  color: #1a1a2e;
}}
code {{
  font-family: 'SF Mono', 'Fira Code', monospace;
  background: #f0f2f8;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.85em;
  color: #0f3460;
}}
pre code {{ background: none; padding: 0; color: inherit; font-size: inherit; }}

/* ── Customize markers ────────────────────────────────── */
.customize {{
  background: #fff3cd;
  color: #856404;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.82rem;
  border: 1px solid #ffd966;
  white-space: nowrap;
}}

/* ── Footer ───────────────────────────────────────────── */
.footer {{
  text-align: center;
  color: #999;
  font-size: 0.78rem;
  margin-top: 3rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e0e4f0;
}}
.footer strong {{ color: #0f3460; }}

/* ── Print styles ─────────────────────────────────────── */
@media print {{
  .toc-nav {{ display: none; }}
  .section-card {{ box-shadow: none; border: 1px solid #eee; page-break-inside: avoid; }}
  body {{ background: white; font-size: 12px; }}
  .header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  h2 {{ page-break-before: auto; }}
}}
</style>
</head>
<body>

<!-- ── Header ── -->
<div class="header">
  <div class="header-top">
    <div>
      <div class="header-logo">{company_name}</div>
      <h1>RFP Response</h1>
      <div class="header-subtitle">Prepared by {company_name}</div>
    </div>
    <div class="score-badge">Quality Score<br>{display_score} / 100</div>
  </div>
  <div class="header-meta">
    <span class="meta-chip">🏢 {company_name}</span>
    {"<span class='meta-chip'>📍 " + company_hq + "</span>" if company_hq else ""}
    {"<span class='meta-chip'>👥 " + company_size + "</span>" if company_size else ""}
    <span class="meta-chip">⚡ Powered by Claude AI</span>
  </div>
</div>

<!-- ── Sticky TOC ── -->
<nav class="toc-nav">
  {toc_items}
</nav>

<!-- ── Body content ── -->
<div class="content">
  <div class="section-card">
    {body_html}
  </div>
</div>

<!-- ── Footer ── -->
<div class="footer">
  <strong>{company_name}</strong>{"&nbsp;&bull;&nbsp; " + company_website if company_website else ""}<br>
  Generated by AI RFP Response Generator &nbsp;&bull;&nbsp; Powered by Claude AI &nbsp;&bull;&nbsp; For review and customization only
</div>

</body>
</html>"""
