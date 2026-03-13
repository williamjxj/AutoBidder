"""
Notification Service

Sends email notifications via Resend (resend.com).
Supports qualified jobs alerts and proposal submission emails.
"""

import html
import logging
from datetime import datetime
from typing import Any

import markdown

from app.config import settings
from app.services.profile_service import UserProfile, profile_service

logger = logging.getLogger(__name__)


def _get_from_email() -> str:
    """
    Get the FROM email address for sending proposals.
    Uses FROM_EMAIL from settings (service@bestitconsulting.ca - verified domain).

    Note: The sender must be from a verified domain in Resend.
    bestitconsulting.ca is verified and ready for production use.

    Returns:
        Formatted FROM email address
    """
    return f"Auto-Bidder <{settings.from_email}>"


def _send_resend_email(
    to_email: str | list[str],
    subject: str,
    html_content: str,
    text_content: str | None = None,
    bcc_email: str | None = None,
) -> bool:
    """
    Send email via Resend API.

    Args:
        to_email: Recipient(s) - string or list
        subject: Email subject
        html_content: HTML body
        text_content: Optional plain text fallback
        bcc_email: Optional BCC recipient for email archiving

    Returns:
        True if sent, False on failure (logged)
    """
    if not settings.resend_api_key:
        return False

    try:
        import resend

        resend.api_key = settings.resend_api_key
    except ImportError as e:
        logger.warning("Resend not installed; skipping email: %s", e)
        return False

    to_list = [to_email] if isinstance(to_email, str) else to_email
    params: dict[str, Any] = {
        "from": _get_from_email(),  # Use FROM email from settings
        "to": to_list,
        "subject": subject,
        "html": html_content,
    }
    if text_content:
        params["text"] = text_content

    # Add BCC if configured
    if bcc_email:
        params["bcc"] = [bcc_email] if isinstance(bcc_email, str) else bcc_email
        logger.debug(f"Adding BCC to email: {bcc_email}")

    try:
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.warning("Resend send failed: %s", e, exc_info=True)
        return False


def _build_signature_html(profile: UserProfile, proposal: Any) -> str:
    """
    Build HTML signature from user profile as a clean plain-list style.

    Args:
        profile: UserProfile with contact information
        proposal: Proposal object for reference ID

    Returns:
        HTML string for email signature
    """
    # Use settings as reliable fallback for name, linkedin, github
    display_name = settings.user_full_name or profile.full_name
    linkedin_url = profile.linkedin or 'https://www.linkedin.com/in/william-jiang-226a7616/'
    github_url = profile.github or 'https://williamjxj.github.io/'

    phone_line = f'<p style="margin: 4px 0; color: #2d3748; font-size: 0.95em;">📞 {html.escape(profile.phone)}</p>' if profile.phone else ''
    email_line = f'<p style="margin: 4px 0; font-size: 0.95em;">📧 <a href="mailto:{html.escape(profile.email)}" style="color: #2c5282; text-decoration: none;">{html.escape(profile.email)}</a></p>' if profile.email else ''
    linkedin_line = f'<p style="margin: 4px 0; font-size: 0.95em;">🔗 LinkedIn: <a href="{html.escape(linkedin_url)}" target="_blank" style="color: #2c5282; text-decoration: none;">{html.escape(linkedin_url)}</a></p>'
    github_line = f'<p style="margin: 4px 0; font-size: 0.95em;">🐱 GitHub: <a href="{html.escape(github_url)}" target="_blank" style="color: #2c5282; text-decoration: none;">{html.escape(github_url)}</a></p>'

    website_line = (
        f'<p style="margin: 4px 0; font-size: 0.95em;">🌐 Website: '
        f'<a href="https://www.bestitconsulting.ca" target="_blank" style="color: #2c5282; text-decoration: none;">https://www.bestitconsulting.ca</a>, '
        f'<a href="https://www.bestitconsultants.ca" target="_blank" style="color: #2c5282; text-decoration: none;">https://www.bestitconsultants.ca</a></p>'
    )

    return f"""  <!-- Signature Section -->
    <footer style="margin-top: 16px; padding-top: 0; border-top: 0;">
    <p style="margin: 0 0 4px 0; color: #2d3748;">Sincerely,</p>
    <p style="margin: 0 0 4px 0; font-weight: 700; font-size: 1.1em; color: #1a365d;">{html.escape(display_name)}</p>
    <p style="margin: 0 0 12px 0; color: #4a5568; font-size: 0.9em; font-style: italic;">{html.escape(profile.title)}</p>
    <div style="margin-bottom: 12px;">
      <img src="{settings.company_logo_url}" alt="{html.escape(settings.company_name)}" style="max-width: 180px; height: auto;" />
    </div>
    {phone_line}
    {email_line}
    {linkedin_line}
    {github_line}
    {website_line}
  </footer>
</body>
</html>"""


async def _format_proposal_as_html(proposal: Any, user_id: str) -> str:
    """
    Format a proposal in formal HTML for email.
    Converts markdown content to HTML for better presentation.

    Args:
        proposal: Proposal object with title, description, budget, etc.
        user_id: User UUID for profile lookup

    Returns:
        Complete HTML email body
    """
    # Get user profile (KB first, .env fallback)
    profile = await profile_service.get_user_profile(user_id)

    budget = html.escape(proposal.budget) if proposal.budget else None
    timeline = html.escape(proposal.timeline) if proposal.timeline else None
    skills_list = ", ".join(html.escape(s) for s in (proposal.skills or [])) or None
    client = html.escape(proposal.client_name or "")
    platform = html.escape(proposal.job_platform or "")
    greeting = f"Dear {client} Hiring Team," if client else "Dear Hiring Team,"

    # Convert markdown description to HTML
    proposal_content = proposal.description or ""

    # Configure markdown with common extensions
    md = markdown.Markdown(extensions=[
        'extra',  # Includes tables, fenced code, etc.
        'nl2br',  # Newline to <br>
        'sane_lists',  # Better list handling
    ])
    proposal_html = md.convert(proposal_content)

    # Add inline styles to markdown elements for email compatibility
    proposal_html = proposal_html.replace('<h1>', '<h1 style="color: #1a365d; font-size: 1.5em; margin: 1.2em 0 0.6em 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3em;">')
    proposal_html = proposal_html.replace('<h2>', '<h2 style="color: #2c5282; font-size: 1.3em; margin: 1em 0 0.5em 0; border-left: 4px solid #4299e1; padding-left: 0.5em;">')
    proposal_html = proposal_html.replace('<h3>', '<h3 style="color: #2d3748; font-size: 1.1em; margin: 0.8em 0 0.4em 0;">')
    proposal_html = proposal_html.replace('<p>', '<p style="margin: 0.6em 0; line-height: 1.7;">')
    proposal_html = proposal_html.replace('<ul>', '<ul style="margin: 0.8em 0; padding-left: 1.5em; line-height: 1.8;">')
    proposal_html = proposal_html.replace('<ol>', '<ol style="margin: 0.8em 0; padding-left: 1.5em; line-height: 1.8;">')
    proposal_html = proposal_html.replace('<li>', '<li style="margin: 0.3em 0;">')
    proposal_html = proposal_html.replace('<blockquote>', '<blockquote style="margin: 1em 0; padding: 0.8em 1.2em; background: #f7fafc; border-left: 4px solid #4299e1; color: #2d3748; font-style: italic;">')
    proposal_html = proposal_html.replace('<code>', '<code style="background: #edf2f7; padding: 0.2em 0.4em; border-radius: 3px; font-family: monospace; font-size: 0.9em; color: #d83534;">')
    proposal_html = proposal_html.replace('<pre>', '<pre style="background: #2d3748; color: #e2e8f0; padding: 1em; border-radius: 5px; overflow-x: auto; margin: 1em 0;">')
    proposal_html = proposal_html.replace('<a ', '<a style="color: #2c5282; text-decoration: none; border-bottom: 1px dotted #2c5282;" ')
    proposal_html = proposal_html.replace('<strong>', '<strong style="color: #1a365d; font-weight: 600;">')
    proposal_html = proposal_html.replace('<table>', '<table style="border-collapse: collapse; width: 100%; margin: 1em 0; border: 1px solid #e2e8f0;">')
    proposal_html = proposal_html.replace('<th>', '<th style="background: #f7fafc; padding: 0.6em; text-align: left; border: 1px solid #e2e8f0; font-weight: 600; color: #2c5282;">')
    proposal_html = proposal_html.replace('<td>', '<td style="padding: 0.6em; border: 1px solid #e2e8f0;">')

    # Build project summary rows only when values are present
    budget_row = f'''<tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 12px 16px; color: #2d3748; font-weight: 600; width: 140px; background: #f7fafc;">💰 Budget:</td>
          <td style="padding: 12px 16px; color: #1a365d; font-weight: 500;">{budget}</td>
        </tr>''' if budget else ''
    timeline_row = f'''<tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 12px 16px; color: #2d3748; font-weight: 600; background: #f7fafc;">⏱️ Timeline:</td>
          <td style="padding: 12px 16px; color: #1a365d; font-weight: 500;">{timeline}</td>
        </tr>''' if timeline else ''
    skills_row = f'''<tr>
          <td style="padding: 12px 16px; color: #2d3748; font-weight: 600; vertical-align: top; background: #f7fafc;">🛠️ Skills:</td>
          <td style="padding: 12px 16px; color: #1a365d;">{skills_list}</td>
        </tr>''' if skills_list else ''
    project_summary_section = f'''    <!-- Project Summary Box -->
    <section style="background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); padding: 24px; margin: 0; border-radius: 0 0 8px 8px;">
      <div style="display: flex; align-items: center; margin-bottom: 16px;">
        <div style="width: 4px; height: 24px; background: linear-gradient(180deg, #48bb78 0%, #38a169 100%); margin-right: 12px; border-radius: 2px;"></div>
        <h3 style="margin: 0; color: #1a365d; font-size: 1.2em; font-weight: 600;">💼 Project Summary</h3>
      </div>
      <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        {budget_row}
        {timeline_row}
        {skills_row}
      </table>
    </section>''' if (budget or timeline or skills_list) else ''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(proposal.title)}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #2d3748; max-width: 700px; margin: 0 auto; padding: 20px; background: #ffffff;">

  <!-- Header Section -->
  <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 8px 8px 0 0; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div style="border-left: 4px solid #ffd700; padding-left: 16px;">
      <h1 style="margin: 0 0 8px 0; font-size: 1.75em; font-weight: 600; color: #ffffff;">{html.escape(proposal.title)}</h1>
      {f'<p style="margin: 4px 0; font-size: 0.95em; opacity: 0.95;"><strong>📋 Client:</strong> {client}</p>' if client else ''}
      {f'<p style="margin: 4px 0; font-size: 0.95em; opacity: 0.95;"><strong>🌐 Platform:</strong> {platform}</p>' if platform else ''}
    </div>
  </header>

  <!-- Main Content -->
  <main style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 0 0 8px 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">

    <!-- Proposal Content -->
    <section style="padding: 24px; border-bottom: 1px solid #e2e8f0;">
      <div style="display: flex; align-items: center; margin-bottom: 16px;">
        <div style="width: 4px; height: 24px; background: linear-gradient(180deg, #4299e1 0%, #667eea 100%); margin-right: 12px; border-radius: 2px;"></div>
        <h2 style="margin: 0; color: #1a365d; font-size: 1.3em; font-weight: 600;">📝 Proposal Details</h2>
      </div>
      <div style="font-size: 0.95em; color: #2d3748;">
        <p style="margin: 0 0 16px 0;">{greeting}</p>
{proposal_html}
      </div>
    </section>

{project_summary_section}
  </main>

{_build_signature_html(profile, proposal)}"""


async def get_user_email(user_id: str) -> str | None:
    """
    Fetch user email from users table.

    Args:
        user_id: User UUID

    Returns:
        Email string or None if not found
    """
    from app.core.database import get_db_pool

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT email FROM users WHERE id = $1::uuid",
            user_id,
        )
    return row["email"] if row and row.get("email") else None


async def send_proposal_submission_email(
    to_email: str,
    proposal: Any,
) -> bool:
    """
    Send a submitted proposal to the customer as formal HTML email.

    Called when user clicks "Submit Proposal". Formats the proposal in HTML
    and sends to the configured PROPOSAL_SUBMIT_EMAIL (or provided to_email).

    Uses ProfileService to get user profile from knowledge base (falls back to .env).

    Args:
        to_email: Recipient email address
        proposal: Proposal object (title, description, budget, timeline, skills, user_id, etc.)

    Returns:
        True if sent successfully, False otherwise (logged, does not raise)
    """
    if not settings.resend_api_key:
        logger.info(
            "RESEND_API_KEY not set; skipping proposal submission email to %s",
            to_email,
        )
        logger.info(
            "PROPOSAL (would have been sent): subject=%s, len=%d",
            getattr(proposal, "title", "?"),
            len(str(getattr(proposal, "description", ""))),
        )
        return False

    # Get user profile (from KB or .env defaults)
    user_id = getattr(proposal, "user_id", None)
    if not user_id:
        logger.warning("Proposal missing user_id, using default profile")
        profile = profile_service._get_default_profile()
    else:
        profile = await profile_service.get_user_profile(user_id)
    # In TEST_MODE, override recipient to TEST_EMAIL
    original_email = to_email
    if settings.test_mode and settings.test_email:
        to_email = settings.test_email
        logger.info(
            f"TEST_MODE: Redirecting email from {original_email} to {to_email}"
        )

    # Get BCC email from settings for archiving sent proposals
    bcc_email = settings.bcc_email if settings.bcc_email else None
    if bcc_email:
        logger.info(f"BCC enabled: {bcc_email} will receive copy of proposal")

    subject = f"Proposal: {proposal.title}" if proposal.title else "New Proposal"
    html_content = await _format_proposal_as_html(proposal, user_id or "")

    budget_text = f"Budget: {proposal.budget}\n" if proposal.budget else ""
    timeline_text = f"Timeline: {proposal.timeline}\n" if proposal.timeline else ""
    skills_text = f"Skills: {', '.join(proposal.skills)}\n" if proposal.skills else ""
    details_section = f"--- DETAILS ---\n{budget_text}{timeline_text}{skills_text}\n" if (proposal.budget or proposal.timeline or proposal.skills) else ""

    plain_content = (
        f"Dear {proposal.client_name + ' Hiring Team' if proposal.client_name else 'Hiring Team'},\n\n"
        f"Proposal: {proposal.title}\n\n"
        f"Client: {proposal.client_name or 'N/A'}\n"
        f"Platform: {proposal.job_platform or 'N/A'}\n\n"
        f"--- PROPOSAL ---\n{proposal.description or ''}\n\n"
        f"{details_section}"
        f"{'=' * 60}\n\n"
        f"Sincerely,\n\n"
        f"{settings.user_full_name or profile.full_name}\n"
        f"{profile.title}\n\n"
        f"📞 {profile.phone or '236-992-3846'}\n"
        f"📧 {profile.email or 'service@bestitconsulting.ca'}\n"
        f"🔗 LinkedIn: {profile.linkedin or 'https://www.linkedin.com/in/william-jiang-226a7616/'}\n"
        f"🐱 GitHub: {profile.github or 'https://williamjxj.github.io/'}\n"
        f"🌐 Website: https://www.bestitconsulting.ca, https://www.bestitconsultants.ca\n"
    )

    if _send_resend_email(to_email, subject, html_content, plain_content, bcc_email):
        logger.info("Proposal submission email sent to %s: %s", to_email, subject)
        if bcc_email:
            logger.info(f"BCC copy sent to {bcc_email} for archiving")
        return True
    return False
