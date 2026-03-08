"""
Notification Service

Sends email notifications via Resend (resend.com).
Supports qualified jobs alerts and proposal submission emails.
"""

import html
import logging
from typing import Any, Dict, List

from app.config import settings

logger = logging.getLogger(__name__)

# Default sender (Resend: use verified domain or onboarding@resend.dev for testing)
DEFAULT_FROM_EMAIL = "Auto-Bidder <onboarding@resend.dev>"


def _send_resend_email(
    to_email: str | List[str],
    subject: str,
    html_content: str,
    text_content: str | None = None,
) -> bool:
    """
    Send email via Resend API.

    Args:
        to_email: Recipient(s) - string or list
        subject: Email subject
        html_content: HTML body
        text_content: Optional plain text fallback

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
    params: Dict[str, Any] = {
        "from": DEFAULT_FROM_EMAIL,
        "to": to_list,
        "subject": subject,
        "html": html_content,
    }
    if text_content:
        params["text"] = text_content

    try:
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.warning("Resend send failed: %s", e, exc_info=True)
        return False


def _format_proposal_as_html(proposal: Any) -> str:
    """
    Format a proposal in formal HTML for email.

    Args:
        proposal: Proposal object with title, description, budget, timeline, skills, etc.

    Returns:
        HTML string suitable for email body
    """
    title = html.escape(str(proposal.title or "Proposal"))
    description = html.escape(str(proposal.description or "")).replace("\n", "<br>")
    client = html.escape(str(proposal.client_name or "N/A"))
    platform = html.escape(str(proposal.job_platform or "N/A"))
    budget = html.escape(str(proposal.budget or "To be discussed"))
    timeline = html.escape(str(proposal.timeline or "To be discussed"))
    skills = (
        ", ".join(html.escape(s) for s in (proposal.skills or []))
        if proposal.skills
        else "N/A"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Proposal: {title}</title>
  <style>
    body {{ font-family: Georgia, 'Times New Roman', serif; line-height: 1.6; color: #333; max-width: 640px; margin: 0 auto; padding: 24px; }}
    h1 {{ font-size: 1.5em; color: #1a1a1a; border-bottom: 2px solid #2c5282; padding-bottom: 8px; margin-top: 0; }}
    h2 {{ font-size: 1.1em; color: #2c5282; margin-top: 24px; margin-bottom: 8px; }}
    .meta {{ font-size: 0.9em; color: #666; margin-bottom: 20px; }}
    .content {{ margin: 16px 0; }}
    .section {{ margin-bottom: 20px; }}
    .label {{ font-weight: 600; color: #555; }}
    hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 24px 0; }}
    footer {{ font-size: 0.85em; color: #888; margin-top: 32px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">
    Client: {client} &bull; Platform: {platform}
  </div>

  <h2>Proposal</h2>
  <div class="content">{description}</div>

  <hr>
  <div class="section">
    <span class="label">Budget:</span> {budget}
  </div>
  <div class="section">
    <span class="label">Timeline:</span> {timeline}
  </div>
  <div class="section">
    <span class="label">Relevant Skills:</span> {skills}
  </div>

  <hr>
  <footer>
    This proposal was submitted via Auto-Bidder.
    {"Generated with AI." if getattr(proposal, "generated_with_ai", False) else ""}
  </footer>
</body>
</html>"""


async def notify_qualified_jobs(
    user_email: str,
    qualified_jobs: List[Dict[str, Any]],
    threshold: float = 0.80,
) -> int:
    """
    Send email notification for qualified jobs above threshold.

    Args:
        user_email: Recipient email address
        qualified_jobs: List of job dicts with qualification_score, title, id, etc.
        threshold: Minimum score to include in notification (default 0.80)

    Returns:
        Number of jobs included in the email (0 if skipped or no jobs above threshold)
    """
    if not settings.resend_api_key:
        logger.info(
            "RESEND_API_KEY not set; skipping notification for %s",
            user_email,
        )
        return 0

    above_threshold = [
        j for j in qualified_jobs
        if (j.get("qualification_score") or 0) >= threshold
    ]
    if not above_threshold:
        logger.debug(
            "No jobs above threshold %.2f for %s; skipping notification",
            threshold,
            user_email,
        )
        return 0

    subject = f"Auto-Bidder: {len(above_threshold)} high-quality job matches"
    lines = [
        f"We found {len(above_threshold)} job(s) matching your profile (score ≥ {threshold:.0%}):",
        "",
    ]
    for j in above_threshold[:10]:
        title = j.get("title") or "Untitled"
        score = j.get("qualification_score", 0)
        job_id = j.get("id", "")
        lines.append(f"• {title} (match: {score:.0%})")
        if job_id:
            lines.append(f"  Job ID: {job_id}")
        lines.append("")
    if len(above_threshold) > 10:
        lines.append(f"... and {len(above_threshold) - 10} more.")
    body = "\n".join(lines)
    html_body = body.replace("\n", "<br>")

    if _send_resend_email(user_email, subject, f"<p>{html_body}</p>", body):
        logger.info(
            "Notification sent to %s for %d jobs (threshold=%.2f)",
            user_email,
            len(above_threshold),
            threshold,
        )
        return len(above_threshold)
    return 0


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


async def send_test_proposal_email(
    target_email: str,
    proposal: Any,
) -> bool:
    """
    Send a test proposal email to the target address.
    Used for manual/mock projects testing.
    """
    if not settings.resend_api_key:
        logger.info(
            "RESEND_API_KEY not set; skipping test proposal email for %s",
            target_email,
        )
        logger.info(f"TEST PROPOSAL CONTENT for {target_email}:\n{proposal.description}")
        return True

    subject = f"TEST PROPOSAL: {proposal.title}"
    body = f"""
New test proposal submitted via Auto-Bidder.

Project: {proposal.title}
Platform: {proposal.job_platform}
Client: {proposal.client_name}

--- PROPOSAL CONTENT ---
{proposal.description}

--- METADATA ---
Generated with AI: {proposal.generated_with_ai}
AI Model: {proposal.ai_model_used}
"""
    html_body = body.replace("\n", "<br>")

    if _send_resend_email(target_email, subject, f"<pre>{html_body}</pre>", body):
        logger.info("Test proposal email sent to %s", target_email)
        return True
    return False


async def send_proposal_submission_email(
    to_email: str,
    proposal: Any,
) -> bool:
    """
    Send a submitted proposal to the customer as formal HTML email.

    Called when user clicks "Submit Proposal". Formats the proposal in HTML
    and sends to the configured PROPOSAL_SUBMIT_EMAIL (or provided to_email).

    Args:
        to_email: Recipient email address
        proposal: Proposal object (title, description, budget, timeline, skills, etc.)

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

    subject = f"Proposal: {proposal.title}" if proposal.title else "New Proposal"
    html_content = _format_proposal_as_html(proposal)
    plain_content = (
        f"Proposal: {proposal.title}\n\n"
        f"Client: {proposal.client_name or 'N/A'}\n"
        f"Platform: {proposal.job_platform or 'N/A'}\n\n"
        f"--- PROPOSAL ---\n{proposal.description or ''}\n\n"
        f"Budget: {proposal.budget or 'To be discussed'}\n"
        f"Timeline: {proposal.timeline or 'To be discussed'}\n"
        f"Skills: {', '.join(proposal.skills or []) or 'N/A'}"
    )

    if _send_resend_email(to_email, subject, html_content, plain_content):
        logger.info("Proposal submission email sent to %s: %s", to_email, subject)
        return True
    return False
