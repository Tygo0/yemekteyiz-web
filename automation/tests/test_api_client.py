"""
Unit tests for BackendClient's error-message truncation. This exists because a
validator rejection with many errors (e.g. a bad vision extraction complaining
about dozens of contestants missing dishes/scores) can easily produce an
error_message longer than the backend's 2000-char cap
(AutomationFailureReportSchema.error_message), which would otherwise crash
report_failure() itself with an unhandled 400 and mask the real error.
"""
from automation.api_client.client import MAX_ERROR_MESSAGE_LENGTH, _truncate_error_message


def test_short_message_passes_through_unchanged():
    assert _truncate_error_message("short error") == "short error"


def test_message_at_exact_limit_passes_through_unchanged():
    message = "x" * MAX_ERROR_MESSAGE_LENGTH
    assert _truncate_error_message(message) == message


def test_long_message_is_truncated_to_max_length():
    message = "x" * (MAX_ERROR_MESSAGE_LENGTH * 5)
    result = _truncate_error_message(message)
    assert len(result) <= MAX_ERROR_MESSAGE_LENGTH


def test_long_message_truncation_notes_how_much_was_omitted():
    message = "x" * (MAX_ERROR_MESSAGE_LENGTH + 500)
    result = _truncate_error_message(message)
    assert "500 more characters" in result
    assert result.startswith("x")
