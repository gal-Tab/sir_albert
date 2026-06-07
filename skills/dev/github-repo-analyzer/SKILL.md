---
name: github-repo-analyzer
description: Analyze a GitHub repository to provide a concise, strategic summary of its purpose, features, activity, and status. Use when the user asks to "check this repo", "analyze this github project", or asks for the status/details of a GitHub link.
---

# github-repo-analyzer

This skill generates a standardized, strategic summary of a GitHub repository. It fetches the repository's metadata (stars, last updated date, language, archived status) and parses its README to understand its core functionality and key features.

## Triggers

Use this skill when the user provides a GitHub link or asks about a specific repository:
- "Check this repo: [Link]"
- "Analyze this repo: [Owner/Repo]"
- "What is the status of [Project] on GitHub?"
- "Summarize this github project."

## Workflow

1. **Fetch Repository Metadata:**
   Use the GitHub API or a web fetch tool to retrieve the repository's basic stats:
   - Stargazers count
   - Last updated / pushed date
   - Main language
   - Archived status (True/False)
2. **Analyze the README/Content:**
   Fetch and read the repository's README file (or webpage) to understand what the project actually does, beyond just the short tagline.
   *If the README is missing or very sparse:* Fetch the repository's file tree and key configuration files (e.g., `package.json`, `requirements.txt`, `docker-compose.yml`, or main source files) to infer its primary purpose, dependencies, and core features.

3. **Generate the Summary:**
   Structure the response exactly as follows (always in English, unless the user explicitly asks for another language):

   📌 **[Owner/Repo Name]**
   - **What it does:** A clear, strategic summary of the project's purpose and core value proposition (1-2 sentences).
   - **Key Features:** A bulleted list of 2-3 standout features or capabilities extracted from the README.
   - **Status:** Active 🟢 / Archived 🔴 / Inactive 🟡 (based on recent commit activity and archived flag)
   - **Stats:** [X] ⭐ | Language: [Language] | Last Updated: [Date]

## Examples

### Example 1: Large, Complex Repository (e.g., AMAP-ML/SkillClaw)
**User:** "Analyze this repo: https://github.com/AMAP-ML/SkillClaw"
**Action:**
1. Fetch API data: 751 stars, updated recently, Python, not archived.
2. Fetch README: Understand it's an Agentic Evolver for collective skill evolution across multiple agents.
3. Reply:
📌 **AMAP-ML/SkillClaw**
- **What it does:** SkillClaw is a framework that enables AI agents to continuously and collectively evolve their skills based on real session data. Instead of isolated libraries, it auto-deduplicates, improves, and shares skills across multiple agents and devices.
- **Key Features:**
  - Operates silently in the background via a local API proxy.
  - Supports an "Evolve Server" with shared storage (OSS/S3) for team-wide skill cross-pollination.
  - Includes a validation flow to stage and review AI-generated skills before publishing.
- **Status:** Active & Popular 🟢
- **Stats:** 751 ⭐ | Main Language: Python | Last Updated: April 19, 2026

### Example 2: Small/Personal Repository (e.g., everyGal/agent_knowledgebase)
**User:** "Check everyGal/agent_knowledgebase"
**Action:**
1. Fetch API data: 0 stars, updated recently, Python, not archived.
2. Fetch README: Understand it's a Claude Code plugin for structured, persistent memory.
3. Reply:
📌 **everyGal/agent_knowledgebase**
- **What it does:** A Claude Code plugin that provides an AI agent with a persistent, structured memory system by automatically compiling dropped files (PDFs, Markdown, Git repos) into a searchable wiki.
- **Key Features:**
  - Answers domain-specific questions by consulting the generated wiki first and citing sources.
  - Auto-manages categories like sources, entities, concepts, and comparisons.
  - Highly customizable via a `wiki-schema.md` file to define domain rules.
- **Status:** Active (New/Private) 🟢
- **Stats:** 0 ⭐ | Main Language: Python | Last Updated: April 17, 2026

### Example 3: Archived/Abandoned Repository
**User:** "What's the deal with feder-cr/Jobs_Applier_AI_Agent_AIHawk?"
**Action:**
1. Fetch API data: 29k+ stars, archived=true.
2. Fetch README: It was an automated job application tool.
3. Reply:
📌 **feder-cr/Jobs_Applier_AI_Agent_AIHawk**
- **What it does:** AIHawk was a massive automation tool designed to streamline the job hunting process by automatically tailoring resumes and applying for jobs on behalf of the user.
- **Key Features:**
  - Automated job applications across various platforms.
  - Tailored resumes to match specific job descriptions using AI.
- **Status:** Archived / Abandoned 🔴
- **Stats:** 29,686 ⭐ | Main Language: Python | Last Updated: [Date]
