"""
Company Website Scraper
Scrapes a company website and uses Claude to extract structured company profile data.
"""

import os
import re
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import anthropic

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Pages most likely to have company profile info
PRIORITY_PATHS = [
    "",              # homepage
    "/about",
    "/about-us",
    "/company",
    "/who-we-are",
    "/services",
    "/solutions",
    "/capabilities",
    "/industries",
    "/sectors",
    "/our-work",
    "/case-studies",
    "/clients",
]


def _clean_text(html: str) -> str:
    """Extract readable text from HTML, stripping navigation/footer noise."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove noisy elements
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "noscript", "iframe", "form", "svg", "img"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_page(url: str, timeout: int = 10) -> str | None:
    """Fetch a single page and return cleaned text, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
            return _clean_text(resp.text)
    except Exception:
        pass
    return None


def scrape_company_website(base_url: str, max_pages: int = 5) -> str:
    """
    Scrape up to max_pages from the company website.
    Returns combined cleaned text from all successfully fetched pages.
    """
    if not base_url.startswith("http"):
        base_url = "https://" + base_url

    # Normalise base URL
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    collected = []
    seen = set()

    for path in PRIORITY_PATHS:
        if len(collected) >= max_pages:
            break
        url = urljoin(base, path) if path else base
        if url in seen:
            continue
        seen.add(url)

        text = _fetch_page(url)
        if text and len(text) > 200:
            page_label = path or "homepage"
            collected.append(f"=== PAGE: {page_label} ===\n{text[:3000]}")
            time.sleep(0.3)   # polite delay

    return "\n\n".join(collected) if collected else ""


def extract_profile_with_claude(
    scraped_text: str,
    company_name: str,
    website_url: str,
) -> dict:
    """
    Send scraped text to Claude and extract structured company profile as JSON.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found.")

    client = anthropic.Anthropic(api_key=api_key)

    system = """You are a business analyst specializing in extracting structured company information
from website content. You extract accurate, specific information and return it as clean JSON.
Never invent data that isn't present — use null for fields you cannot find."""

    prompt = f"""Analyze the following website content from {company_name} ({website_url}) and extract
a structured company profile for use in RFP responses.

WEBSITE CONTENT:
---
{scraped_text[:12000]}
---

Return a JSON object with EXACTLY these fields (use null if info not found):

{{
  "founded": "year founded and any tagline, e.g. 'Founded 2005 | 20 years of excellence'",
  "size": "employee count and specialists, e.g. '500+ employees | 100+ QE specialists'",
  "hq": "headquarters location and delivery centers",
  "services": "comma-separated list of core services/offerings",
  "differentiators": "3-5 key competitive differentiators, what makes them unique",
  "certifications": "quality/security certifications (ISO, CMMI, SOC2, etc.)",
  "industries": "comma-separated industries they serve",
  "clients": "notable clients or types of clients (be specific if named)",
  "case_studies": "any specific project wins, case studies, or results with numbers"
}}

Return ONLY the JSON object. No explanation, no markdown fences."""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = msg.content[0].text.strip()
    # Strip markdown fences if Claude added them
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return empty profile
        return {}


def auto_fill_company_profile(company_name: str, website_url: str) -> tuple[dict, str]:
    """
    Main entry point: scrape website + extract profile with Claude.
    Returns (profile_dict, status_message).
    """
    if not website_url:
        return {}, "Please enter a website URL first."

    # Step 1: Scrape
    scraped = scrape_company_website(website_url)
    if not scraped:
        return {}, (
            f"Could not scrape {website_url}. "
            "The site may block automated access. Please fill in details manually."
        )

    # Step 2: Extract with Claude
    profile = extract_profile_with_claude(scraped, company_name, website_url)
    if not profile:
        return {}, "Could not extract profile from website. Please fill in details manually."

    # Step 3: Clean up nulls
    cleaned = {k: (v if v and v != "null" else "") for k, v in profile.items()}

    pages_scraped = scraped.count("=== PAGE:")
    return cleaned, f"✅ Auto-filled from {pages_scraped} page(s) on {website_url}. Review and edit before generating."
