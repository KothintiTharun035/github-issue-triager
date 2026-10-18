
# 🤖 AI-Powered GitHub Issue Triager

An AI-powered developer tool that analyzes GitHub issues using Google Gemini, identifies issue severity and category, generates structured triage reports, and optionally applies suggested labels through the GitHub REST API.

## 🚀 Features

- **AI-Powered Triage:** Analyzes GitHub issue titles and descriptions using Google Gemini 2.5 Flash.
- **Severity Assessment:** Estimates issue severity and priority.
- **Issue Classification:** Identifies the issue category and recommends relevant labels.
- **Structured Reports:** Generates summaries, investigation notes, and reproduction clarity assessments.
- **GitHub Integration:** Fetches public issue details and applies suggested labels using the GitHub REST API.
- **Cloud Execution:** Runs through GitHub Actions without requiring your computer to remain running.
- **Controlled Label Application:** Supports read-only triage and optional label application.

## 🛠️ Tech Stack

- **Language:** Python
- **LLM:** Google Gemini 2.5 Flash
- **AI Framework:** LangChain
- **API Integration:** GitHub REST API
- **Automation:** GitHub Actions
- **Configuration:** Python dotenv

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
AI Triage Report
       |
       v
Suggested Labels
       |
       v
Optional GitHub Label Application
```

## 📋 Example Output

For an issue such as "Login fails after entering valid credentials", the agent can generate:

- **Severity:** Critical
- **Category:** Bug
- **Suggested labels:** `bug`, `critical`, `authentication`, `backend`, `500-error`
- **Summary:** Login fails after valid credentials are entered.
- **Recommended action:** Investigate the authentication API and backend logs.

*The actual output depends on the issue details and AI response.*

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/KothintiTharun035/github-issue-triager.git
cd github-issue-triager
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
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

Use a Google Gemini API key for AI requests. A GitHub token with suitable repository Issues permissions is required when applying labels.

**Security:** Never commit `.env` or expose API keys and access tokens in screenshots or logs.

### 5. Run a triage using a GitHub issue URL

```bash
python agent.py --issue-url "https://github.com/OWNER/REPOSITORY/issues/1"
```

### 6. Apply suggested labels

```bash
python agent.py --issue-url "https://github.com/OWNER/REPOSITORY/issues/1" --apply-labels
```

Only use label application on issues you are authorized to modify.

## ☁️ GitHub Actions

The project includes a manually triggered GitHub Actions workflow.

1. Open the repository's **Actions** tab.
2. Select **GitHub Issue Triager**.
3. Click **Run workflow**.
4. Enter the full GitHub issue URL.
5. Choose whether to apply the suggested labels.
6. Start the workflow and inspect the logs.

Configure these repository Actions secrets before running the workflow:

- `GOOGLE_API_KEY`
- `GH_PERSONAL_ACCESS_TOKEN`

The workflow passes the GitHub personal access token to the application as `GITHUB_TOKEN`.

## 📁 Project Structure

```text
github-issue-triager/
├── .github/
│   └── workflows/
│       └── triage.yml
├── agent.py
├── requirements.txt
├── metadata.yaml
├── .gitignore
└── README.md
```

## 🔮 Future Enhancements

- Automatically triage issues when they are opened.
- Add a web dashboard for viewing triage reports.
- Improve automated testing and error handling.
- Add configurable label validation and duplicate-label checks.
- Track triage history and evaluate classification quality.

## 👨‍💻 Author

**Tharun Kothinti**

GitHub: [KothintiTharun035](https://github.com/KothintiTharun035)

---

*Built to explore LLM-powered developer tools, API integration, and cloud workflow automation.*
