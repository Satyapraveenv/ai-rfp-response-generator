"""
AI RFP Response Generator — Web App
Built with Streamlit + Claude (Anthropic)
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

from generator import RFPGenerator
from scraper import auto_fill_company_profile

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI RFP Response Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    text-align: center;
  }
  .main-header h1 { color: #e94560; font-size: 2rem; margin: 0; }
  .main-header p  { color: #a8b2d8; font-size: 0.95rem; margin: 0.4rem 0 0; }

  .info-card {
    background: #0f3460;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0 1rem;
    color: #e8eaf6 !important;
  }
  .info-card p, .info-card li, .info-card strong {
    color: #e8eaf6 !important;
  }
  .info-card strong { color: #e94560 !important; }

  .score-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    font-size: 1.1rem;
  }
  .score-high   { background: #d4edda; color: #155724; }
  .score-medium { background: #fff3cd; color: #856404; }
  .score-low    { background: #f8d7da; color: #721c24; }

  .autofill-hint {
    background: linear-gradient(90deg, #0f3460, #1a1a2e);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #a8b2d8 !important;
    font-size: 0.82rem;
    margin: 0.5rem 0 0.8rem;
    border-left: 3px solid #e94560;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state — use widget keys directly so auto-fill works ───────────────
DEFAULTS = {
    "cp_name":         "",
    "cp_website":      "",
    "cp_founded":      "",
    "cp_size":         "",
    "cp_services":     "",
    "cp_diff":         "",
    "cp_certs":        "",
    "cp_industries":   "",
    "cp_clients":      "",
    "cp_case_studies": "",
    "cp_rfp_content":  "",
    "autofill_status": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

SAMPLE_RFP = """# REQUEST FOR PROPOSAL (RFP)
# Quality Engineering & Digital Transformation Services

**Issuing Organization**: HealthFirst Insurance Group
**RFP Number**: HFI-2025-QE-0042
**Response Deadline**: June 15, 2025

## Scope of Work

### QE Transformation
- Assess QA maturity across 6 business-critical applications
- Migrate from 70% manual testing to 80%+ automation coverage
- Implement AI-assisted test generation and defect prediction
- Establish shift-left testing practices in CI/CD pipelines

### DevOps & CI/CD Enablement
- Set up automated pipelines for 3 flagship products (member portal, claims engine, provider directory)
- Integrate testing into Jenkins/GitHub Actions pipelines
- Reduce release cycle from 6 weeks to 2 weeks

### Performance & Security Testing
- Load/stress testing for peak open enrollment (50,000 concurrent users)
- HIPAA compliance and security vulnerability scanning
- Performance testing tools: JMeter, Gatling

### Cloud Migration Testing
- Test support for AWS migration of 3 legacy applications
- Data migration validation and rollback testing

## Technical Requirements
- Automation: Selenium, Playwright, Cypress, RestAssured
- Performance: JMeter or Gatling
- CI/CD: Jenkins, GitHub Actions
- Cloud: AWS (primary), Azure (secondary)
- Mobile: iOS and Android
- Compliance: HIPAA, OWASP Top 10

## Team Requirements
- QE Lead / Architect (10+ years)
- 2-3 Senior Automation Engineers
- 1 Performance Testing Specialist
- 1 DevSecOps Engineer
- 1 Project Manager
- Healthcare domain experience preferred

## Evaluation Criteria
| Criteria | Weight |
|----------|--------|
| Technical approach and methodology | 30% |
| Healthcare QE experience | 25% |
| Team qualifications | 20% |
| Pricing and value | 15% |
| References and case studies | 10% |

## Budget
Year 1 budget: $800K - $1.2M (fixed price for Phase 1 assessment preferred)

## Compliance Requirements
- Business Associate Agreement (BAA) under HIPAA required
- SOC 2 Type II preferred
- US-based delivery preferred
"""

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>📋 AI RFP Response Generator</h1>
  <p>BCG-quality proposals · Any company · Any RFP · Powered by Claude AI</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏢 Company Profile")

    # Name + website always first
    st.text_input("Company Name *", key="cp_name",
                  placeholder="e.g. Innominds Software")
    st.text_input("Company Website *", key="cp_website",
                  placeholder="e.g. www.innominds.com")

    # Auto-fill hint
    st.markdown("""
    <div class="autofill-hint">
    ✨ <strong style="color:#e94560">Auto-fill magic:</strong>
    Enter company name + website above, then click below —
    Claude scrapes the site and fills all fields automatically.
    </div>
    """, unsafe_allow_html=True)

    # Auto-fill button
    if st.button("🔍 Auto-fill from Website", use_container_width=True):
        name = st.session_state["cp_name"].strip()
        url  = st.session_state["cp_website"].strip()
        if not name or not url:
            st.session_state["autofill_status"] = "error:Enter Company Name and Website URL first."
        else:
            with st.spinner(f"Scraping {url} and extracting profile..."):
                profile, status = auto_fill_company_profile(name, url)

            if profile:
                mapping = {
                    "cp_founded":      "founded",
                    "cp_size":         "size",
                    "cp_services":     "services",
                    "cp_diff":         "differentiators",
                    "cp_certs":        "certifications",
                    "cp_industries":   "industries",
                    "cp_clients":      "clients",
                    "cp_case_studies": "case_studies",
                }
                for ss_key, profile_key in mapping.items():
                    val = profile.get(profile_key, "")
                    if val and val != "null":
                        st.session_state[ss_key] = str(val)

            st.session_state["autofill_status"] = (
                ("ok:" if profile else "warn:") + status
            )
            st.rerun()

    # Status message
    msg = st.session_state.get("autofill_status", "")
    if msg.startswith("ok:"):
        st.success(msg[3:])
    elif msg.startswith("warn:"):
        st.warning(msg[5:])
    elif msg.startswith("error:"):
        st.error(msg[6:])

    st.markdown("---")
    st.caption("Review and edit auto-filled details below before generating.")

    # Profile fields — key= only, no value= (fixes auto-fill)
    st.text_input("Founded / HQ", key="cp_founded",
                  placeholder="e.g. Founded 1998 · San Jose, CA")
    st.text_input("Company Size", key="cp_size",
                  placeholder="e.g. 3,000+ employees")
    st.text_area("Core Services *", key="cp_services", height=90,
                 placeholder="e.g. Quality Engineering, Test Automation, AI/ML, Cloud Migration")
    st.text_area("Key Differentiators *", key="cp_diff", height=90,
                 placeholder="e.g. AI-native testing frameworks, 68% faster release cycles")
    st.text_area("Certifications & Compliance", key="cp_certs", height=70,
                 placeholder="e.g. CMMI Level 3, ISO 27001, SOC 2 Type II")
    st.text_input("Industries Served", key="cp_industries",
                  placeholder="e.g. Healthcare, BFSI, Hi-Tech, Retail")
    st.text_area("Notable Clients / Wins", key="cp_clients", height=70,
                 placeholder="e.g. Fortune 500 healthcare insurer, Top-5 US bank")
    st.text_area("Relevant Case Studies", key="cp_case_studies", height=100,
                 placeholder="e.g. Reduced regression from 3 weeks to 2 days for a healthcare payer...")

    st.markdown("---")
    st.markdown("### ⚙️ Sections to Generate")
    sections_all = [
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
    selected_sections = st.multiselect(
        "Select sections",
        options=sections_all,
        default=sections_all,
        key="_sections",
        label_visibility="collapsed",
    )

# ── Main area ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📄 RFP Content")

    # Sample RFP button
    btn_col, _ = st.columns([1, 2])
    with btn_col:
        if st.button("📥 Load Sample RFP", use_container_width=True):
            st.session_state["cp_rfp_content"] = SAMPLE_RFP
            st.rerun()

    rfp_content = st.text_area(
        label="RFP content",
        key="cp_rfp_content",
        placeholder="Paste the full RFP text here, or click 'Load Sample RFP' above to try a demo...",
        height=440,
        label_visibility="collapsed",
    )

    uploaded = st.file_uploader("Or upload a .txt / .md file", type=["txt", "md"])
    if uploaded:
        st.session_state["cp_rfp_content"] = uploaded.read().decode("utf-8")
        st.rerun()

with col2:
    st.markdown("### 🎯 What You'll Get")
    st.markdown("""
<div class="info-card">
<p>✅ &nbsp;<strong>Executive Summary</strong> — CEO-ready, conclusion-first</p>
<p>✅ &nbsp;<strong>Technical Approach</strong> — AI-native QE methodology</p>
<p>✅ &nbsp;<strong>Team Structure</strong> — Roles, skills, certifications</p>
<p>✅ &nbsp;<strong>Work Plan</strong> — Phased delivery with milestones</p>
<p>✅ &nbsp;<strong>Risk Mitigation</strong> — Proactive, specific, credible</p>
<p>✅ &nbsp;<strong>Compliance Matrix</strong> — Every requirement mapped</p>
<p>✅ &nbsp;<strong>Pricing Framework</strong> — T&M + fixed-price guidance</p>
<p>✅ &nbsp;<strong>Quality Score</strong> — Honest gap analysis (0–100)</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("### 💡 How to Use")
    st.markdown("""
<div class="info-card">
<p><strong>Step 1</strong> — Enter company name + website in sidebar</p>
<p><strong>Step 2</strong> — Click <strong>🔍 Auto-fill from Website</strong></p>
<p><strong>Step 3</strong> — Review &amp; edit the extracted details</p>
<p><strong>Step 4</strong> — Paste RFP or click <strong>📥 Load Sample RFP</strong></p>
<p><strong>Step 5</strong> — Click <strong>🚀 Generate</strong> and get your proposal!</p>
</div>
""", unsafe_allow_html=True)

# ── Generate button ───────────────────────────────────────────────────────────
st.markdown("---")
col_btn, col_info = st.columns([2, 3])
with col_btn:
    generate = st.button(
        "🚀 Generate World-Class RFP Response",
        use_container_width=True,
        type="primary",
    )
with col_info:
    st.markdown("*Powered by Claude · BCG-style writing · ~60 seconds · Any company, any RFP*")

# ── Generate logic ────────────────────────────────────────────────────────────
if generate:
    rfp_text     = st.session_state.get("cp_rfp_content", "").strip()
    company_name = st.session_state.get("cp_name", "").strip()

    if not rfp_text:
        st.error("⚠️ Please paste RFP content or click 'Load Sample RFP'.")
    elif not company_name:
        st.error("⚠️ Please enter your Company Name in the sidebar.")
    elif not selected_sections:
        st.error("⚠️ Please select at least one section.")
    else:
        company_profile = {
            "name":            company_name,
            "founded":         st.session_state.get("cp_founded", ""),
            "size":            st.session_state.get("cp_size", ""),
            "hq":              st.session_state.get("cp_founded", ""),
            "website":         st.session_state.get("cp_website", ""),
            "services":        st.session_state.get("cp_services", ""),
            "differentiators": st.session_state.get("cp_diff", ""),
            "certifications":  st.session_state.get("cp_certs", ""),
            "industries":      st.session_state.get("cp_industries", ""),
            "clients":         st.session_state.get("cp_clients", ""),
            "case_studies":    st.session_state.get("cp_case_studies", ""),
        }

        with st.spinner("✍️ Generating your world-class RFP response (~60 seconds)..."):
            try:
                gen    = RFPGenerator()
                result = gen.generate(rfp_text, company_profile, selected_sections)
                st.session_state["result"]       = result
                st.session_state["company_name"] = company_name
            except ValueError as e:
                st.error(f"⚠️ Configuration error: {e}")
            except Exception as e:
                err = str(e)
                if "credit" in err.lower() or "billing" in err.lower():
                    st.error("💳 Add credits at console.anthropic.com/settings/billing")
                elif "api_key" in err.lower() or "auth" in err.lower():
                    st.error("🔑 Invalid API key. Check your .env file.")
                else:
                    st.error(f"❌ {err}")

# ── Results ───────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result           = st.session_state["result"]
    company_name_out = st.session_state.get("company_name", "Company")
    response_text    = result["response"]
    quality_score    = result.get("quality_score")

    st.markdown("---")
    st.markdown(f"## 📊 Response Generated for **{company_name_out}**")

    if quality_score:
        if quality_score >= 85:
            badge_cls, label = "score-high",   f"✅ {quality_score}/100 — Excellent"
        elif quality_score >= 70:
            badge_cls, label = "score-medium",  f"⚠️ {quality_score}/100 — Good"
        else:
            badge_cls, label = "score-low",     f"❗ {quality_score}/100 — Needs Review"
        st.markdown(
            f'<span class="score-badge {badge_cls}">{label}</span>',
            unsafe_allow_html=True,
        )

    st.caption(
        f"Input tokens: {result.get('input_tokens','–')} · "
        f"Output tokens: {result.get('output_tokens','–')}"
    )

    tab_preview, tab_raw, tab_download = st.tabs(
        ["📖 Formatted Preview", "📝 Raw Markdown", "⬇️ Download HTML"]
    )

    with tab_preview:
        st.markdown(response_text)

    with tab_raw:
        st.code(response_text, language="markdown")

    with tab_download:
        gen_obj  = RFPGenerator()
        html_out = gen_obj.to_html(company_name_out, response_text, quality_score)
        st.download_button(
            label="⬇️ Download as HTML",
            data=html_out,
            file_name=f"{company_name_out.lower().replace(' ', '-')}-rfp-response.html",
            mime="text/html",
            use_container_width=True,
        )
        st.markdown("*Open in any browser for the full professional proposal view.*")
        with st.expander("Preview HTML"):
            st.components.v1.html(html_out, height=600, scrolling=True)
