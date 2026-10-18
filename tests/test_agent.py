
from unittest.mock import patch, Mock

import agent


def test_fetch_github_issue_success():
    """Test fetching an issue and extracting its details."""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Login fails",
        "body": "Login returns a 500 error.",
        "labels": [
            {"name": "bug"},
            {"name": "backend"},
        ],
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        title, body, labels = agent.fetch_github_issue(
            "https://github.com/example/project/issues/1"
        )

    assert title == "Login fails"
    assert body == "Login returns a 500 error."
    assert labels == ["bug", "backend"]

    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


def test_fetch_github_issue_invalid_url():
    """Test that an invalid GitHub issue URL is rejected."""

    with patch("requests.get") as mock_get:
        try:
            agent.fetch_github_issue("not-a-valid-url")
            assert False, "Expected ValueError for invalid URL"
        except ValueError as exc:
            assert "Invalid GitHub issue URL" in str(exc)

        mock_get.assert_not_called()



def test_fetch_github_issue_not_found():
    """Test handling of a GitHub issue that does not exist."""

    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        try:
            agent.fetch_github_issue(
                "https://github.com/example/project/issues/999999"
            )
            assert False, "Expected RuntimeError for a missing issue"
        except RuntimeError as exc:
            assert "GitHub issue not found" in str(exc)




def test_fetch_github_issue_unauthorized():
    """Test handling of GitHub authentication errors."""

    mock_response = Mock()
    mock_response.status_code = 401

    with patch("requests.get", return_value=mock_response):
        try:
            agent.fetch_github_issue(
                "https://github.com/example/project/issues/1"
            )
            assert False, "Expected RuntimeError for unauthorized request"
        except RuntimeError as exc:
            assert "401 Unauthorized" in str(exc)


def test_fetch_pull_request_url():
    """Test that pull requests are rejected."""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Example pull request",
        "body": "This is a pull request.",
        "labels": [],
        "pull_request": {"url": "https://api.github.com/example"},
    }

    with patch("requests.get", return_value=mock_response):
        try:
            agent.fetch_github_issue(
                "https://github.com/example/project/issues/2"
            )
            assert False, "Expected ValueError for a pull request"
        except ValueError as exc:
            assert "pull request" in str(exc).lower()
