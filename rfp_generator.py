#!/usr/bin/env python3
"""
AI RFP Response Generator

A tool for generating structured RFP response outlines using OpenAI GPT-4.
Transforms RFP requirements into professional response drafts across all key sections.

Usage:
    python rfp_generator.py --input rfp.md --output response.md
    python rfp_generator.py --input rfp.md --sections "Executive Summary,Technical Approach"
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize Google Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    print("Please create a .env file with: GOOGLE_API_KEY=your-key-here")
    print("\nTo get a free API key:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Click 'Create API Key'")
    print("3. Copy the key to your .env file")
    sys.exit(1)

client = genai.Client(api_key=api_key)


class RFPResponseGenerator:
    """Generate structured RFP responses using AI."""

    # Default sections if none specified
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

    def __init__(self, system_prompt_path=None):
        """
        Initialize the RFP Response Generator.

        Args:
            system_prompt_path: Path to custom system prompt. If None, uses default.
        """
        if system_prompt_path and Path(system_prompt_path).exists():
            with open(system_prompt_path, "r") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = self._get_default_system_prompt()

    def _get_default_system_prompt(self):
        """Return default system prompt for RFP response generation."""
        return """You are an expert RFP response writer with 15+ years of experience in IT services, consulting, and managed services sales. You have led $3M+ in RFP-driven contract wins.

Your role is to generate professional, compelling RFP response sections that:

1. DIRECTLY ADDRESS the client's stated requirements and evaluation criteria
2. DIFFERENTIATE the responding firm's unique value and competitive advantages
3. DEMONSTRATE EXPERIENCE through relevant case studies and project examples
4. FOLLOW BEST PRACTICES in RFP response writing:
   - Executive summaries that hook the reader immediately
   - Clear, numbered, evidence-based claims
   - Compliance matrices showing how you meet each requirement
   - Risk mitigation that shows deep understanding of challenges
   - Realistic team compositions with named roles and responsibilities
   - Detailed methodologies that instill confidence

5. MAINTAIN TONE: Professional, confident, slightly formal but not stuffy
6. INCLUDE STRUCTURE: Use subheadings, bullet points, and formatting for readability
7. ADD SPECIFICITY: Replace generic claims with concrete methodologies and examples
8. SCORE CLARITY: Mark sections with [CUSTOMIZE] where team-specific details are needed

When given an RFP, you will:
- Extract key requirements and evaluation criteria
- Generate comprehensive response sections
- Suggest where competitive differentiation can shine
- Provide a quality score (0-100) indicating compliance and completeness

Remember: The goal is to create a response OUTLINE that your team will customize with:
- Specific company details
- Actual project examples
- Team member names and bios
- Pricing and commercial terms
- References and case studies

Do NOT generate final, publication-ready content. Generate STRUCTURED OUTLINES that are ready for human customization."""

    def load_rfp_document(self, file_path):
        """
        Load RFP requirements document.

        Args:
            file_path: Path to RFP document (txt, md, or docx supported)

        Returns:
            str: Content of the RFP document
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"RFP file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    def generate_response(self, rfp_content, sections=None):
        """
        Generate RFP response sections.

        Args:
            rfp_content: The RFP requirements text
            sections: List of sections to generate. If None, generates all default sections.

        Returns:
            dict: Contains 'response', 'quality_score', and 'analysis'
        """
        if sections is None:
            sections = self.DEFAULT_SECTIONS

        # Build the user prompt
        user_prompt = self._build_user_prompt(rfp_content, sections)

        try:
            # Combine system prompt and user prompt
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"

            # Call Google Gemini API using new SDK
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=full_prompt,
            )

            generated_response = response.text

            # Extract quality score if present
            quality_score = self._extract_quality_score(generated_response)

            # Estimate token usage (Gemini doesn't provide exact counts in the same way)
            tokens_used = len(full_prompt.split()) + len(generated_response.split())

            return {
                "response": generated_response,
                "quality_score": quality_score,
                "sections": sections,
                "tokens_used": tokens_used,
            }

        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")

    def _build_user_prompt(self, rfp_content, sections):
        """Build the user prompt for the API call."""
        sections_str = "\n".join(f"- {s}" for s in sections)

        return f"""Please analyze the following RFP and generate a comprehensive response outline.

RFP REQUIREMENTS:
---
{rfp_content}
---

SECTIONS TO GENERATE:
{sections_str}

INSTRUCTIONS:
1. Analyze the RFP requirements and extraction key themes, evaluation criteria, and deliverables
2. For EACH section listed above, generate a detailed outline with:
   - Clear subheadings
   - Bullet points highlighting key claims
   - Where specific company details needed, mark as [CUSTOMIZE: description]
   - Supporting methodology or examples

3. AFTER ALL SECTIONS, include:
   - A "QUALITY SCORE" section (0-100) with:
     * Percentage of RFP requirements addressed
     * Evaluation criteria coverage
     * Key gaps or areas needing customization
     * Recommendations for strengthening the response

4. Use professional, consulting-style language
5. Be specific and actionable
6. Include realistic methodologies and frameworks

Generate the response now."""

    def _extract_quality_score(self, response_text):
        """Extract quality score from the response if present."""
        # Look for patterns like "Quality Score: 87/100" or "Score: 92"
        patterns = [
            r"Quality\s+Score:?\s*(\d+)\s*/\s*100",
            r"Score:?\s*(\d+)\s*/\s*100",
            r"(\d+)/100",
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue

        return None

    def save_response(self, response_data, output_path):
        """
        Save generated response to file.

        Args:
            response_data: Dict containing 'response', 'quality_score', etc.
            output_path: Path where to save the response
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response_data["response"])

        print(f"\n✓ Response saved to: {output_path}")
        if response_data.get("quality_score"):
            print(
                f"  Quality Score: {response_data['quality_score']}/100"
            )
        print(f"  Tokens used: {response_data.get('tokens_used', 'N/A')}")

    def generate_summary(self, response_data):
        """Print a summary of the generation result."""
        print("\n" + "=" * 60)
        print("RFP RESPONSE GENERATION SUMMARY")
        print("=" * 60)
        print(f"Sections generated: {len(response_data['sections'])}")
        print(f"  - {chr(10).join(f'  - {s}' for s in response_data['sections'])}")

        if response_data.get("quality_score"):
            print(f"\nQuality Score: {response_data['quality_score']}/100")
            if response_data["quality_score"] >= 85:
                print("  Status: Excellent - ready for customization")
            elif response_data["quality_score"] >= 70:
                print("  Status: Good - may need some enhancement")
            else:
                print("  Status: Review recommended - gaps identified")

        print(f"\nTokens used: {response_data.get('tokens_used', 'N/A')}")
        print("=" * 60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate structured RFP response outlines using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rfp_generator.py --input rfp.md --output response.md
  python rfp_generator.py --input rfp.md --sections "Executive Summary,Technical Approach"
  python rfp_generator.py --input rfp.md --system-prompt custom-prompt.md
        """,
    )

    parser.add_argument(
        "--input", required=True, help="Path to RFP requirements document"
    )
    parser.add_argument(
        "--output",
        default="rfp_response.md",
        help="Output file path (default: rfp_response.md)",
    )
    parser.add_argument(
        "--sections",
        help='Comma-separated list of sections to generate (default: all). Example: "Executive Summary,Technical Approach"',
    )
    parser.add_argument(
        "--system-prompt",
        help="Path to custom system prompt file",
    )

    args = parser.parse_args()

    # Parse sections if provided
    sections = None
    if args.sections:
        sections = [s.strip() for s in args.sections.split(",")]

    try:
        # Initialize generator
        print("Initializing RFP Response Generator...")
        generator = RFPResponseGenerator(system_prompt_path=args.system_prompt)

        # Load RFP
        print(f"Loading RFP from: {args.input}")
        rfp_content = generator.load_rfp_document(args.input)
        print(f"  Loaded {len(rfp_content)} characters")

        # Generate response
        print("\nGenerating RFP response (this may take 1-2 minutes)...")
        result = generator.generate_response(rfp_content, sections=sections)

        # Save response
        generator.save_response(result, args.output)

        # Print summary
        generator.generate_summary(result)

        print("\n✓ Generation complete!")
        print(f"\nNext steps:")
        print(f"1. Review the generated response in: {args.output}")
        print(f"2. Look for [CUSTOMIZE] markers for team-specific details")
        print(f"3. Add specific project examples and case studies")
        print(f"4. Customize pricing and commercial terms")
        print(f"5. Have subject matter experts review and finalize")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
