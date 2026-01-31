"""Core logic for commitcraft hook."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TicketInfo:
    """Represents extracted ticket information."""

    ticket: str
    tickets: list[str]

    @property
    def tickets_str(self) -> str:
        """Return comma-separated list of tickets."""
        return ", ".join(self.tickets)


def get_branch_name() -> str:
    """Get the current git branch name."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def extract_tickets(branch: str, regex: str) -> TicketInfo | None:
    """Extract ticket(s) from branch name using regex."""
    tickets = re.findall(regex, branch, re.IGNORECASE)
    if not tickets:
        return None

    # Handle named groups - extract the 'ticket' group if present
    if isinstance(tickets[0], tuple):
        # Named groups return tuples, get first non-empty match
        tickets = [t[0] if isinstance(t, tuple) else t for t in tickets]

    tickets = [t.strip().upper() for t in tickets if t]
    if not tickets:
        return None

    return TicketInfo(ticket=tickets[0], tickets=tickets)


def format_message(
    template: str,
    ticket_info: TicketInfo,
    commit_msg: str,
) -> str:
    """Format the commit message using the template."""
    return template.format(
        ticket=ticket_info.ticket,
        tickets=ticket_info.tickets_str,
        commit_msg=commit_msg,
    )


def format_body(template: str, ticket_info: TicketInfo) -> str:
    """Format the body content using the template."""
    return template.format(
        ticket=ticket_info.ticket,
        tickets=ticket_info.tickets_str,
    )


def update_commit_message(
    filename: str | Path,
    regex: str,
    format_template: str,
    body_template: str | None = None,
) -> bool:
    """
    Update the commit message file with ticket information.

    Returns True if the message was modified, False otherwise.
    """
    filepath = Path(filename)
    contents = filepath.read_text(encoding="utf-8").splitlines(keepends=True)

    if not contents:
        return False

    commit_msg = contents[0].rstrip("\r\n")

    # Skip if commit starts with "fixup!" or "squash!"
    if commit_msg.startswith(("fixup!", "squash!", "amend!", "Merge ")):
        return False

    branch = get_branch_name()
    ticket_info = extract_tickets(branch, regex)

    if not ticket_info:
        return False

    # Skip if ticket already in commit message
    if any(re.search(regex, line, re.IGNORECASE) for line in contents):
        return False

    # Format the new commit subject
    new_subject = format_message(format_template, ticket_info, commit_msg)
    contents[0] = new_subject + "\n"

    # Add body if template provided
    if body_template:
        body_content = format_body(body_template, ticket_info)
        _insert_body(contents, body_content)

    filepath.write_text("".join(contents), encoding="utf-8")
    return True


def _insert_body(contents: list[str], body_content: str) -> None:
    """Insert body content after the subject line with proper spacing."""
    # Ensure blank line after subject
    if len(contents) == 1:
        contents.append("\n")
    elif len(contents) > 1 and contents[1].strip():
        contents.insert(1, "\n")

    # Find position to insert body (after blank line, before any existing body)
    insert_pos = 2 if len(contents) > 1 else 1

    # Check if body already exists (avoid duplicates on amend)
    for line in contents[insert_pos:]:
        if body_content.strip() in line:
            return

    contents.insert(insert_pos, body_content + "\n")
