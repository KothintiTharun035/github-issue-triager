
# 🤖 AI-Powered GitHub Issue Triager

An AI-powered developer tool that analyzes GitHub issues using Google Gemini, classifies issue severity, generates structured triage reports, and optionally applies suggested labels through the GitHub REST API.

The project supports local execution, manual GitHub Actions workflows, and reusable workflows that other developers can configure in their own repositories.

## 🚀 Features

- **AI-Powered Analysis:** Uses Google Gemini 2.5 Flash to analyze issue titles and descriptions.
- **Severity Assessment:** Estimates severity and priority.
- **Issue Classification:** Identifies categories and recommends relevant labels.
- **Structured Reports:** Generates summaries, investigation notes, and reproduction clarity assessments.
- **GitHub REST API:** Fetches issue details and optionally applies suggested labels.
- **Cloud Execution:** Runs through GitHub Actions.
- **Reusable Workflow:** Allows other repositories to call the triager workflow.
- **Controlled Changes:** Supports read-only analysis and optional label application.
- **Automated Testing:** Includes pytest tests for successful fetching, invalid URLs, missing issues, authentication errors, and pull-request rejection.

## 🛠️ Tech Stack

- **Language:** Python 3.12+
- **LLM:** Google Gemini 2.5 Flash
- **AI Framework:** LangChain
- **API Integration:** GitHub REST API
- **Automation:** GitHub Actions
- **Testing:** pytest
- **Configuration:** python-dotenv

## 🏗️ Architecture

```text
GitHub Issue URL
       |
       v
GitHub REST API
       |
       v
Fetch Issue Details
       |
       v
Google Gemini 2.5 Flash
       |
       v
Severity, Category, Summary
and Suggested Labels
       |
       v
Structured Triage Report
       |
       v
Optional Label Application
       |
       v
GitHub Issue Updated
```

## 📋 Example Output

For an issue titled "Login fails after entering valid credentials", the agent can produce a report like:

- **Severity:** Critical
- **Category:** Bug
- **Suggested labels:** `bug`, `critical`, `authentication`, `backend`, `500-error`
- **Summary:** Users cannot log in after entering valid credentials.
- **Recommended action:** Investigate the authentication API and backend logs.

Actual output depends on the issue details and Gemini's response.

## 📁 Project Structure

```text
github-issue-triager/
├── .github/
│   └── workflows/
│       ├── triage.yml
│       ├── reusable-triage.yml
│       └── example-caller.yml
├── tests/
│   └── test_agent.py
├── agent.py
├── requirements.txt
├── metadata.yaml
├── .gitignore
└── README.md
```

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/KothintiTharun035/github-issue-triager.git
cd github-issue-triager
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

Obtain a Gemini API key through Google AI Studio.

A GitHub token with appropriate Issues permissions is needed when applying labels. Public issue fetching may work without a token, subject to GitHub API limits.

Never commit `.env` or expose tokens in logs, screenshots, or source code.

### 5. Run read-only triage

```bash
python agent.py --issue-url "https://github.com/OWNER/REPOSITORY/issues/1"
```

### 6. Apply suggested labels

```bash
python agent.py --issue-url "https://github.com/OWNER/REPOSITORY/issues/1" --apply-labels
```

Only apply labels to repositories where you have permission to modify issues.

## 🧪 Automated Tests

Run the test suite:

```bash
python -m pytest -v
```

The current test suite covers:

- Successful issue fetching
- Invalid issue URLs
- GitHub 404 responses
- GitHub 401 responses
- Pull-request URL rejection

The tests mock GitHub API responses and do not need to modify real issues.

## ☁️ GitHub Actions: Manual Triage

The project includes a manually triggered workflow.

1. Open the repository's **Actions** tab.
2. Select **GitHub Issue Triager**.
3. Click **Run workflow**.
4. Enter the full GitHub issue URL.
5. Choose whether to apply suggested labels.
6. Run the workflow and inspect the report.

Configure these repository Actions secrets:

- `GOOGLE_API_KEY`
- `GH_PERSONAL_ACCESS_TOKEN`

The workflow passes the GitHub personal access token to the application as `GITHUB_TOKEN`.

Keep label application disabled for the initial test.

## 🌐 Reuse the Workflow in Another Repository

Other developers can call the reusable workflow from their own repositories without copying the Python implementation.

### 1. Add a caller workflow

In the target repository, create:

`.github/workflows/ai-issue-triager.yml`

Use this example:

```yaml
name: AI Issue Triager

on:
  workflow_dispatch:
    inputs:
      issue_url:
        description: "Full GitHub issue URL"
        required: true
        type: string
      apply_labels:
        description: "Apply AI-suggested labels"
        required: true
        type: boolean
        default: false

permissions:
  contents: read
  issues: write

jobs:
  triage:
    uses: KothintiTharun035/github-issue-triager/.github/workflows/reusable-triage.yml@main
    with:
      issue_url: ${{ inputs.issue_url }}
      apply_labels: ${{ inputs.apply_labels }}
    secrets:
      GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

### 2. Configure the Gemini API key

In the target repository, go to:

**Settings → Secrets and variables → Actions → New repository secret**

Create a secret named:

`GOOGLE_API_KEY`

Set its value to the developer's own Gemini API key.

Do not send the key to the project author or commit it to the repository.

### 3. Run the workflow

1. Open **Actions → AI Issue Triager**.
2. Click **Run workflow**.
3. Enter an issue URL belonging to the target repository.
4. Keep `apply_labels` set to `false` for the first run.
5. Inspect the triage report in the logs.

### 4. Permissions and access

- The reusable workflow must be accessible to the calling repository.
- The caller workflow grants `issues: write` for label application.
- The calling repository's `GITHUB_TOKEN` is used to modify issues in that repository.
- Organization policies or repository settings may restrict token permissions.
- Read-only triage should be tested before enabling label application.

The caller does not need to share a personal GitHub access token with the project author.

## 🔐 Security Considerations

- Store API keys in environment variables or GitHub Actions secrets.
- Never commit `.env` or access tokens.
- Grant only the permissions needed for the workflow.
- Keep label application opt-in until the generated results are reviewed.
- Test on an issue you control before using the tool in other repositories.

## 🔮 Future Enhancements

- Automatically triage issues when they are opened.
- Add a web dashboard for reviewing AI reports.
- Add stronger label validation and duplicate-label handling.
- Expand automated tests and error-handling coverage.
- Track triage quality and classification accuracy.
- Support configurable severity and label policies.

## 👨‍💻 Author

**Tharun Kothinti**

GitHub: [KothintiTharun035](https://github.com/KothintiTharun035)

Project repository: [github-issue-triager](https://github.com/KothintiTharun035/github-issue-triager)

---

Built to explore LLM-powered developer tools, GitHub API integration, automated testing, and reusable cloud workflows.
