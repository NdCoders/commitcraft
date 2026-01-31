"""Tests for commitcraft core functionality."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from commitcraft.core import (
    TicketInfo,
    extract_tickets,
    format_body,
    format_message,
    update_commit_message,
)


class TestExtractTickets:
    """Tests for extract_tickets function."""

    def test_simple_ticket(self) -> None:
        result = extract_tickets("NDC-123_feature_branch", r"[A-Z]+-\d+")
        assert result is not None
        assert result.ticket == "NDC-123"
        assert result.tickets == ["NDC-123"]

    def test_named_group(self) -> None:
        result = extract_tickets(
            "feature/NDC-456-some-feature",
            r"(?P<ticket>NDC-\d+)",
        )
        assert result is not None
        assert result.ticket == "NDC-456"

    def test_multiple_tickets(self) -> None:
        result = extract_tickets("NDC-123_NDC-456_feature", r"NDC-\d+")
        assert result is not None
        assert result.tickets == ["NDC-123", "NDC-456"]
        assert result.tickets_str == "NDC-123, NDC-456"

    def test_no_match(self) -> None:
        result = extract_tickets("feature_branch", r"[A-Z]+-\d+")
        assert result is None

    def test_case_insensitive(self) -> None:
        result = extract_tickets("ndc-123_feature", r"NDC-\d+")
        assert result is not None
        assert result.ticket == "NDC-123"


class TestFormatMessage:
    """Tests for format_message function."""

    def test_simple_format(self) -> None:
        ticket_info = TicketInfo(ticket="NDC-123", tickets=["NDC-123"])
        result = format_message("{ticket} {commit_msg}", ticket_info, "Fix bug")
        assert result == "NDC-123 Fix bug"

    def test_multiple_tickets_format(self) -> None:
        ticket_info = TicketInfo(ticket="NDC-123", tickets=["NDC-123", "NDC-456"])
        result = format_message("[{tickets}] {commit_msg}", ticket_info, "Fix bug")
        assert result == "[NDC-123, NDC-456] Fix bug"


class TestFormatBody:
    """Tests for format_body function."""

    def test_jira_link(self) -> None:
        ticket_info = TicketInfo(ticket="NDC-123", tickets=["NDC-123"])
        result = format_body(
            "Ticket: [{ticket}](https://jira.example.com/browse/{ticket})",
            ticket_info,
        )
        assert result == "Ticket: [NDC-123](https://jira.example.com/browse/NDC-123)"


class TestUpdateCommitMessage:
    """Tests for update_commit_message function."""

    @patch("commitcraft.core.get_branch_name")
    def test_adds_ticket_prefix(self, mock_branch: MagicMock, tmp_path: Path) -> None:
        mock_branch.return_value = "NDC-123_feature"
        commit_file = tmp_path / "COMMIT_EDITMSG"
        commit_file.write_text("Fix authentication bug\n")

        result = update_commit_message(
            commit_file,
            regex=r"[A-Z]+-\d+",
            format_template="{ticket} {commit_msg}",
        )

        assert result is True
        assert commit_file.read_text() == "NDC-123 Fix authentication bug\n"

    @patch("commitcraft.core.get_branch_name")
    def test_adds_body(self, mock_branch: MagicMock, tmp_path: Path) -> None:
        mock_branch.return_value = "NDC-123_feature"
        commit_file = tmp_path / "COMMIT_EDITMSG"
        commit_file.write_text("Fix bug\n")

        update_commit_message(
            commit_file,
            regex=r"[A-Z]+-\d+",
            format_template="{ticket} {commit_msg}",
            body_template="Ticket: [{ticket}](https://jira.example.com/browse/{ticket})",
        )

        content = commit_file.read_text()
        assert "NDC-123 Fix bug" in content
        assert "Ticket: [NDC-123]" in content

    @patch("commitcraft.core.get_branch_name")
    def test_skips_fixup_commits(self, mock_branch: MagicMock, tmp_path: Path) -> None:
        mock_branch.return_value = "NDC-123_feature"
        commit_file = tmp_path / "COMMIT_EDITMSG"
        commit_file.write_text("fixup! Previous commit\n")

        result = update_commit_message(
            commit_file,
            regex=r"[A-Z]+-\d+",
            format_template="{ticket} {commit_msg}",
        )

        assert result is False
        assert commit_file.read_text() == "fixup! Previous commit\n"

    @patch("commitcraft.core.get_branch_name")
    def test_skips_if_ticket_exists(self, mock_branch: MagicMock, tmp_path: Path) -> None:
        mock_branch.return_value = "NDC-123_feature"
        commit_file = tmp_path / "COMMIT_EDITMSG"
        commit_file.write_text("NDC-123 Already has ticket\n")

        result = update_commit_message(
            commit_file,
            regex=r"[A-Z]+-\d+",
            format_template="{ticket} {commit_msg}",
        )

        assert result is False

    @patch("commitcraft.core.get_branch_name")
    def test_no_ticket_in_branch(self, mock_branch: MagicMock, tmp_path: Path) -> None:
        mock_branch.return_value = "feature_branch"
        commit_file = tmp_path / "COMMIT_EDITMSG"
        commit_file.write_text("Fix bug\n")

        result = update_commit_message(
            commit_file,
            regex=r"[A-Z]+-\d+",
            format_template="{ticket} {commit_msg}",
        )

        assert result is False
        assert commit_file.read_text() == "Fix bug\n"
