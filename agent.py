"""
GitHub Issue Triager using LangGraph.

Analyzes a GitHub issue and produces: severity label, category,
reproduction steps summary, and suggested assignee type.

Usage:
    python agent.py --title "Login fails on mobile Safari" --body "When I try..."
    python agent.py --issue-url https://github.com/owner/repo/issues/123
"""

import argparse
import os
import json
import re

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

TRIAGE_PROMPT = """You are a GitHub issue triager. Analyze the issue and return a JSON object with:
{
  "severity": "critical|high|medium|low",
  "category": "bug|feature|documentation|question|performance|security",
  "priority_score": 1-10,
  "labels": ["list", "of", "suggested", "labels"],
  "summary": "one sentence summary",
  "reproduction_clear": true/false,
  "assignee_type": "frontend|backend|devops|documentation|security|any",
  "needs_more_info": true/false,
  "triage_notes": "2-3 sentences of triager notes"
}
Return only valid JSON, no markdown."""


def parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def triage_issue(title: str, body: str, labels: list[str] = None) -> dict:
    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    )

    issue_text = f"Title: {title}\n\nBody:\n{body}"
    if labels:
        issue_text += f"\n\nExisting labels: {', '.join(labels)}"

    messages = [
        SystemMessage(content=TRIAGE_PROMPT),
        HumanMessage(content=issue_text),
    ]

    response = llm.invoke(messages)
    return parse_json_response(response.content)


def fetch_github_issue(url: str) -> tuple[str, str, list]:
    """Fetch issue details from GitHub API."""
    import requests

    # Match a normal GitHub issue URL
    match = re.match(
        r"^https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)/?$",
        url.strip()
    )

    if not match:
        raise ValueError(
            f"Invalid GitHub issue URL: {url}\n"
            "Expected format: https://github.com/owner/repo/issues/123"
        )

    owner, repo, issue_num = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = ""

    response = requests.get(api_url, headers=headers, timeout=15)

    if response.status_code == 401:
        raise RuntimeError(
            "GitHub returned 401 Unauthorized. Check your GITHUB_TOKEN "
            "in .env. Leave it empty for a public issue if you have no token."
        )

    if response.status_code == 404:
        raise RuntimeError(
            "GitHub issue not found. Check that the repository and issue "
            "number exist and that the issue is publicly accessible."
        )

    response.raise_for_status()
    data = response.json()

    # A pull request also uses the GitHub issues API, but this agent
    # expects an actual issue.
    if "pull_request" in data:
        raise ValueError("That URL points to a pull request, not an issue.")

    return (
        data["title"],
        data.get("body") or "",
        [label["name"] for label in data.get("labels", [])],
    )


    
def apply_github_labels(issue_url: str, labels: list[str]) -> None:
    """Create missing repository labels and apply them to a GitHub issue."""
    import requests

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is missing. Add your GitHub token to .env."
        )

    match = re.match(
        r"^https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)/?$",
        issue_url.strip()
    )
    if not match:
        raise ValueError("Invalid GitHub issue URL.")

    owner, repo, issue_num = match.groups()
    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Keep valid, unique label names.
    clean_labels = list(dict.fromkeys(
        label.strip()[:50]
        for label in labels
        if isinstance(label, str) and label.strip()
    ))

    # Retrieve existing repository labels.
    response = requests.get(
        f"{base_url}/labels",
        headers=headers,
        params={"per_page": 100},
        timeout=15,
    )
    response.raise_for_status()
    existing = {item["name"].casefold() for item in response.json()}

    # Create any missing labels.
    for label in clean_labels:
        if label.casefold() in existing:
            continue

        response = requests.post(
            f"{base_url}/labels",
            headers=headers,
            json={"name": label, "color": "ededed"},
            timeout=15,
        )

        if response.status_code == 422:
            # GitHub may report that the label already exists.
            check = requests.get(
                f"{base_url}/labels",
                headers=headers,
                params={"per_page": 100},
                timeout=15,
            )
            check.raise_for_status()
            existing = {
                item["name"].casefold() for item in check.json()
            }
            if label.casefold() not in existing:
                response.raise_for_status()
        else:
            response.raise_for_status()

        existing.add(label.casefold())

    # Add the suggested labels without removing existing issue labels.
    response = requests.post(
        f"{base_url}/issues/{issue_num}/labels",
        headers=headers,
        json={"labels": clean_labels},
        timeout=15,
    )
    response.raise_for_status()

    print("\n✅ GitHub labels applied successfully:")
    for item in response.json():
        print(f"  - {item['name']}")








def main():
    parser = argparse.ArgumentParser(description="GitHub Issue Triager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--issue-url", help="GitHub issue URL")
    group.add_argument("--title", help="Issue title (use with --body)")
    parser.add_argument("--body", default="", help="Issue body text")
    args = parser.parse_args()

    if args.issue_url:
        print(f"\n🔍 Fetching issue from GitHub...")
        title, body, labels = fetch_github_issue(args.issue_url)
    else:
        title, body, labels = args.title, args.body, []

    print(f"\n🏷️  Triaging: {title}\n")
    result = triage_issue(title, body, labels)

    print("\nAI triage completed.")

    apply_choice = input(
        "\nApply the suggested labels to this GitHub issue? (y/n): "
    ).strip().lower()

    if apply_choice == "y":
        if not args.issue_url:
            print("GitHub issue URL is required to apply labels.")
        else:
            try:
                apply_github_labels(
                    args.issue_url,
                    result.get("labels", [])
                )
            except Exception as exc:
                print(f"\n❌ Could not apply GitHub labels: {exc}")
    else:
        print("Labels were not applied.")

    severity = result.get("severity", "medium")
    labels = result.get("labels", [])
    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")

    print("=" * 60)
    print("📋 TRIAGE REPORT")
    print("=" * 60)
    print(f"{severity_emoji} Severity: {severity.upper()} (Priority: {result.get('priority_score', 'N/A')}/10)")
    print(f"📁 Category: {result.get('category', 'N/A')}")
    print(f"👤 Assignee: {result.get('assignee_type', 'any')} team")
    print(f"🏷️  Labels: {', '.join(labels)}")
    print(f"📝 Summary: {result.get('summary', 'N/A')}")
    print(f"❓ Needs more info: {'Yes' if result.get('needs_more_info') else 'No'}")
    print(f"🔍 Reproduction clear: {'Yes' if result.get('reproduction_clear') else 'No'}")
    print(f"\n💭 Notes: {result.get('triage_notes', 'N/A')}")


if __name__ == "__main__":
    main()
