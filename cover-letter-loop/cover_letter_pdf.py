"""
Cover Letter PDF Generator

Converts a cover letter markdown/text to a professionally formatted PDF using fpdf2.

Usage:
    from cover_letter_pdf import generate_cover_letter_pdf
    
    generate_cover_letter_pdf(
        body_text="Dear Hiring Manager, ...",
        company="Company Name",
        department="Role Title",
        location="City, State",
        output_path="/path/to/output.pdf",
        applicant_name="Your Name",
        address="123 Main St, City, State ZIP",
        email="you@example.com",
        phone="(555) 123-4567",
        letter_date="March 17, 2026",
        salutation="Dear Hiring Team,"
    )

Dependencies:
    - fpdf2 (pip install fpdf2)
    - Spectral font files in fonts/ directory (optional; falls back to standard fonts)
      - fonts/Spectral-Regular.ttf
      - fonts/Spectral-Bold.ttf
"""

import os
from pathlib import Path
from fpdf import FPDF
from datetime import datetime


def load_user_config(config_path=None):
    """
    Load user configuration from config.json or career-context/profile.md.
    
    Args:
        config_path: Path to config file. If None, searches for standard locations.
    
    Returns:
        dict with keys: name, email, phone, address
    
    Raises:
        FileNotFoundError if config not found.
    """
    if config_path is None:
        candidates = [
            Path("config.json"),
            Path.home() / "AI Agent Context" / "career-context" / "profile.md",
            Path.home() / "Documents" / "Claude" / "AI Agent Context" / "career-context" / "profile.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                break
        else:
            raise FileNotFoundError(
                "No config found. Provide config_path or place config.json in working directory."
            )
    
    config_path = Path(config_path)
    
    if config_path.suffix == ".json":
        import json
        with open(config_path) as f:
            return json.load(f)
    elif config_path.suffix == ".md":
        # Simple parser for profile.md format (adjust as needed)
        with open(config_path) as f:
            content = f.read()
        config = {}
        for line in content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                config[key.strip().lower()] = value.strip()
        return config
    else:
        raise ValueError(f"Unsupported config format: {config_path.suffix}")


def generate_cover_letter_pdf(
    body_text,
    company,
    department,
    location,
    output_path,
    *,
    applicant_name,
    address,
    email,
    phone,
    letter_date,
    salutation,
):
    """
    Generate a professional cover letter PDF.
    
    Args:
        body_text (str): Full cover letter body (including salutation and signature).
        company (str): Company name.
        department (str): Role/department title.
        location (str): Job location.
        output_path (str): Path where PDF will be saved.
        applicant_name (str): Applicant's full name.
        address (str): Applicant's address.
        email (str): Applicant's email.
        phone (str): Applicant's phone.
        letter_date (str): Letter date (e.g., "March 17, 2026").
        salutation (str): Salutation line (e.g., "Dear Hiring Manager,").
    
    Returns:
        Path object of the saved PDF.
    
    Raises:
        ValueError if required fields are missing.
    """
    # Validate inputs
    required = {
        "body_text": body_text,
        "company": company,
        "output_path": output_path,
        "applicant_name": applicant_name,
        "address": address,
        "email": email,
        "phone": phone,
    }
    for field, value in required.items():
        if not value:
            raise ValueError(f"Required field missing: {field}")
    
    # Create output directory if needed
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize PDF
    pdf = FPDF(format="letter", unit="in")
    pdf.add_page()
    
    # Set margins (0.75" left/right, 0.5" top, 0.5" bottom)
    pdf.set_left_margin(0.75)
    pdf.set_right_margin(0.75)
    pdf.set_top_margin(0.5)
    
    # Try to load Spectral font; fall back to Helvetica if unavailable
    fonts_dir = Path(__file__).parent / "fonts"
    use_spectral = False
    if fonts_dir.exists():
        try:
            regular_font = fonts_dir / "Spectral-Regular.ttf"
            bold_font = fonts_dir / "Spectral-Bold.ttf"
            if regular_font.exists() and bold_font.exists():
                pdf.add_font("Spectral", "", str(regular_font))
                pdf.add_font("Spectral", "B", str(bold_font))
                use_spectral = True
        except Exception:
            pass  # Fall back to default font
    
    # Header: Applicant name and contact info
    header_font = "Spectral" if use_spectral else "Helvetica"
    body_font = "Spectral" if use_spectral else "Helvetica"
    
    # Name (25pt, dark blue)
    pdf.set_font(header_font, "B", size=25)
    pdf.set_text_color(25, 51, 102)  # Dark blue
    pdf.cell(0, 0.3, applicant_name, ln=True, align="L")
    
    # Contact info (10.5pt, near-black)
    pdf.set_font(body_font, size=10.5)
    pdf.set_text_color(32, 32, 32)  # Near-black
    contact = f"{email} | {phone}"
    pdf.cell(0, 0.15, contact, ln=True, align="L")
    pdf.cell(0, 0.05, address, ln=True, align="L")
    
    # Spacing
    pdf.ln(0.2)
    
    # Letter date
    pdf.set_font(body_font, size=10.5)
    pdf.cell(0, 0.15, letter_date, ln=True, align="L")
    
    # Spacing
    pdf.ln(0.1)
    
    # Company info (recipient)
    pdf.set_font(body_font, size=10.5)
    pdf.cell(0, 0.15, company, ln=True, align="L")
    pdf.cell(0, 0.15, f"{department}, {location}", ln=True, align="L")
    
    # Spacing
    pdf.ln(0.1)
    
    # Salutation
    pdf.set_font(body_font, size=10.5)
    pdf.cell(0, 0.15, salutation, ln=True, align="L")
    
    # Spacing
    pdf.ln(0.05)
    
    # Body text
    pdf.set_font(body_font, size=10.5)
    pdf.set_text_color(32, 32, 32)
    
    # Parse body into paragraphs and render
    paragraphs = body_text.split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Remove salutation if it appears in body (already rendered above)
        if para.startswith("Dear "):
            continue
        # Remove signature block if present (will add our own)
        if para == "Sincerely," or para.startswith("Sincerely"):
            continue
        
        # Wrap and render paragraph
        pdf.multi_cell(0, 0.15, para, align="L")
        pdf.ln(0.08)
    
    # Closing
    pdf.ln(0.08)
    pdf.set_font(body_font, size=10.5)
    pdf.cell(0, 0.15, "Sincerely,", ln=True, align="L")
    
    # Spacing for signature
    pdf.ln(0.3)
    
    # Signature (name)
    pdf.set_font(body_font, size=10.5)
    pdf.cell(0, 0.15, applicant_name, ln=True, align="L")
    
    # Save PDF
    output_path = Path(output_path)
    pdf.output(str(output_path))
    
    return output_path


if __name__ == "__main__":
    # Example usage
    example_body = """Dear Hiring Manager,

Your company is building something interesting, and I am excited to contribute.

I have direct experience in the core challenge of your role. Specifically, I led the pricing migration that saved the company 20% on operational costs while improving customer retention by 12%.

In my previous role, I also led a cross-functional team through a complex product transition, demonstrating the kind of leadership and communication your team needs.

I would welcome a conversation about how my experience aligns with your needs. Thank you for your consideration.

"""

    output = generate_cover_letter_pdf(
        body_text=example_body,
        company="Example Company",
        department="Product Manager",
        location="New York, NY",
        output_path="example_cover_letter.pdf",
        applicant_name="Jane Doe",
        address="123 Main St, New York, NY 10001",
        email="jane@example.com",
        phone="(555) 123-4567",
        letter_date="March 17, 2026",
        salutation="Dear Hiring Manager,",
    )
    print(f"PDF generated: {output}")
