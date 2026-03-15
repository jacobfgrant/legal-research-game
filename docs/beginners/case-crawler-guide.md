# Case Crawler — Claude Code Guide

---

## 1. How to Use This File

This file tells Claude Code how to work with you. You don't need to memorize it or follow any instructions here yourself — just leave it in the root of your project folder (as `CLAUDE.md`) and Claude Code will read it automatically.

**Your workflow is simple:**

- Open Claude Code in your project folder.
- Tell it what you want in plain language. ("Add a timer." "Make the search page look better." "Create a new scenario about property law.")
- It builds what you ask for. You review the result. Rinse and repeat.

You can ask Claude Code to explain anything at any time — what a file does, why something works the way it does, what your options are.

If something breaks, just tell Claude Code what happened ("I clicked submit and got an error page") and it will diagnose and fix it.

---

## 2. About This Project

This is **Case Crawler**, a legal research puzzle game. The full game concept is documented in `docs/case-crawler-concept.md` — read that for the complete vision.

The short version: players are junior associates who research legal issues under time pressure, build arguments from cases and statutes, face opposing counsel's rebuttal, and get scored on relevance, strength, completeness, and efficiency.

**Important context for Claude Code:** The person directing this project is a law student and game designer, not a programmer. She decides what the game does; you decide how to build it. Always explain what you're doing and why in plain language. When she asks for a feature, build it. When she asks a question, answer it — don't start building something she didn't ask for.

---

## 3. Tech Stack

These technology choices are already made. Don't change them without discussing it first.

- **SvelteKit** — The frontend framework. It handles what the player sees and interacts with — search results, card animations, drag-and-drop, timers. It's fast and has built-in support for the smooth transitions and animations that make a game feel polished.
- **Python + FastAPI** — The backend (server-side code). It stores your progress, serves up the case database, and handles anything that needs to persist between sessions. FastAPI is modern and well-documented.
- **SQLite** — A database that lives in a single file in your project folder — no server to install or configure.
- **Docker** — Packages the whole application so anyone can run it with one command, regardless of what's on their computer.

---

## 4. Rules for Claude Code

Follow these rules in all work on this project.

**Communication:** Before doing anything, explain what you're about to do and why in 1-2 plain-language sentences. If you use a technical term, define it briefly in parentheses. Never dump unexplained jargon.

**Simplicity:** Always choose the simplest approach that works. No microservices (splitting the app into many separate programs), no complex infrastructure, no unnecessary abstraction layers. This is a small web game — build it like one.

**Ask before big changes:** If a request would require restructuring significant parts of the codebase, explain what's involved and get confirmation before proceeding.

**Virtual environments:** Always use a Python virtual environment (an isolated space for this project's packages). Never install packages globally on the system.

**Dependencies:** Minimize external packages. Use Python's standard library where practical. When you add a new dependency, explain what it does and why it's needed.

**Git:** Commit after each logical unit of work. Keep commit messages short and descriptive. If a commit isn't self-explanatory, briefly explain what you committed and why.

**Errors:** When something goes wrong, explain what happened in plain language, what it means, and how you're fixing it. Don't silently fix things — she should understand what went wrong so she can avoid it or recognize it later.

**No scope creep:** Build exactly what's asked for. Don't add features, optimizations, or "improvements" that weren't requested. If you think something would be a good idea, suggest it — don't just do it.

**File organization:** Keep the project structure flat and simple. Don't create deep directory hierarchies or split things into many small files without a good reason.

**Testing:** Write tests for game logic (scoring, argument evaluation, citation chains, etc.) but don't over-test trivial things. When you write a test, explain in a sentence what it checks.

**Game data:** Cases, statutes, scenarios, and other game content go in editable data files (JSON or YAML), not hardcoded in the application. She should be able to open a data file, edit a case name or add a new scenario, without touching any code.

---

## 5. Project Structure

Here's what the project looks like when it's set up:

```
case-crawler/
  CLAUDE.md              -- this file (instructions for Claude Code)
  frontend/              -- the SvelteKit app (what the player sees and interacts with)
  backend/               -- the FastAPI server (saves progress, serves case data)
    app.py               -- the main backend application
    data/                -- game content: cases, statutes, scenarios (editable JSON/YAML)
    requirements.txt     -- list of Python packages the backend needs
  tests/                 -- automated tests for game logic
  Dockerfile             -- instructions for packaging the app in Docker
  docker-compose.yml     -- configuration for running the app with Docker
```

Each piece has one job. If you're ever unsure where something lives, just ask Claude Code.

---

## 6. Getting Started

Once you have Claude Code open in your project folder, here's how to get up and running. Just say these things (or something like them) — Claude Code handles the rest.

**Step 1:** *"Set up the project."*
Claude Code will create the folder structure, set up a virtual environment, install the necessary packages, and get everything ready to run.

**Step 2:** *"Show me what it looks like."*
Claude Code will start the development server and tell you what URL to open in your browser. You'll see a basic page — nothing fancy yet, but it proves everything is wired up.

**Step 3:** *"Add a sample case and let me search for it."*
Claude Code will create some example game content (a fictional case or two, maybe a statute) and connect it to the search mechanic. Now you can type a search term and see results — the core research loop, working.

**From here, you're driving.** Start shaping the game: adjust how search works, design the argument-building interface, add new scenarios, tweak scoring, change how things look. You're the game designer. Tell Claude Code what you want the player's experience to be, and it will figure out how to build it.

---

## 7. Ideas to Try

Once the basics are running, here are things you could ask Claude Code to do. These are just starting points — you'll have your own ideas.

- "Make the search results page look more like Westlaw."
- "Add a timer that counts down my billable hours as I research."
- "Create a new case about landlord-tenant law."
- "Make it so finding a key case unlocks a bonus."
- "Show a score summary at the end of each round."
- "Let me see which cases I've already found during a scenario."
- "Add opposing counsel's rebuttal after I submit my argument."
- "Highlight the citation links in case text so I can click through to the cited case."
- "Create a short tutorial scenario that teaches the basics."
- "Make the argument builder drag-and-drop so I can reorder my authorities."
