# The Brief — CLAUDE.md Project Guide

This file does two things: it tells Claude Code how to work with you on this project, and it gives you a reference for how the project is set up. Copy this file into the root of your project folder and rename it `CLAUDE.md`.

---

## 1. How to Use This File

This file is instructions for Claude Code — the AI programming tool you'll be using to build The Brief. You don't need to memorize it or even read every line. Here's what matters:

- **Put this file in your project folder** as `CLAUDE.md`. Claude Code reads it automatically every time you start a session.
- **Open Claude Code in your project folder and just talk.** Describe what you want in plain language. "I want the player to choose between two research paths" is a perfectly good instruction.
- **Ask Claude Code to explain anything.** If it does something you don't understand, say "explain what you just did." It will.
- **If something breaks, just say what happened.** "The page is blank" or "I got an error when I clicked the choice" is enough. Claude Code will figure it out.
- **Your job is to design the game.** Write the story. Design the cases. Decide how choices branch and what consequences they have. Claude Code handles the programming. Your expertise in law and storytelling is what makes this game good — the code is just plumbing.

---

## 2. About This Project

This is **The Brief** — an interactive narrative game where legal research drives the story. The player is a junior associate at a law firm, making research decisions that branch the story in different directions. Think *Phoenix Wright* meets a legal thriller, grounded in how legal research actually works.

See `docs/the-brief-concept.md` for the full concept document.

**About the person you're working with:** She is a law student and the game's designer and writer. She does not write code. When she describes a feature, implement it. When she asks a question, answer it — don't start building something she was just asking about. Explain everything you do in plain language. If you use a technical term, define it briefly in parentheses.

---

## 3. Tech Stack

These technology choices are already made. Don't switch to something else unless there's a specific, compelling reason and you've explained why.

- **Python + Flask** — The backend (server-side code that runs the game). Flask is a simple, well-documented web framework that's good for small projects like this.
- **HTMX** — Makes web pages interactive without writing much JavaScript. It works by adding special attributes to regular HTML elements, so the pages stay simple and readable.
- **SQLite** — The database. It's just a single file — no setup, no server, no accounts. It stores player progress, choices, and game state.
- **Vanilla HTML/CSS** — The pages and styling. No complex frontend frameworks. Just standard web technologies that are easy to read and edit.
- **Docker** — For deployment (getting the game running on a server). It packages everything together so the game runs anywhere with one command.

---

## 4. Rules for Claude Code

Follow these rules in every session. They are not suggestions.

- **Communication:** Before doing anything, explain what you're about to do and why in 1-2 plain-language sentences. No jargon without explanation. If you use a technical term, define it briefly in parentheses the first time.
- **Simplicity:** Always choose the simplest approach that works. No microservices (splitting the app into many small programs), no complex infrastructure, no unnecessary abstractions. This is a small web game. Build it like one.
- **Ask before big changes:** If a request would require restructuring significant parts of the codebase, explain what's involved and get confirmation before proceeding.
- **Virtual environments:** Always use a Python virtual environment (an isolated space for this project's packages so they don't interfere with anything else on the computer). Never install packages globally.
- **Dependencies:** Minimize external packages. Use Python's built-in tools where practical. When you do add a package, explain what it does and why it's needed.
- **Git:** Commit (save a snapshot of the code) after each logical unit of work. Keep commit messages short and descriptive. If a commit isn't self-explanatory, briefly explain what you saved and why.
- **Errors:** When something goes wrong, explain what happened in plain language, what it means, and how you're fixing it. Don't silently fix things — she should understand what went wrong.
- **No scope creep:** Only build what's asked for. Don't add features, optimizations, or "improvements" that weren't requested. If you think something would be a good addition, suggest it — don't just build it.
- **File organization:** Keep the project structure flat and simple. Don't create deep directory hierarchies.
- **Story content:** All narrative content — dialogue, case descriptions, branching logic, character details — goes in editable data files (JSON or YAML), not hardcoded in the application. She should be able to write and edit story content by editing those files directly, without touching any code.
- **Testing:** Write tests for game logic (branching, state tracking, choice consequences) but don't over-test trivial things.

---

## 5. Project Structure

Here's what the project folder looks like. Each item in one sentence:

```
the-brief/
  CLAUDE.md            -- This file. Instructions for Claude Code.
  app.py               -- The main application that runs the game.
  templates/           -- HTML page templates (what the player sees).
  static/              -- CSS stylesheets and images.
  story/               -- Story content, case data, and branching logic (this is where you write).
  tests/               -- Automated tests for game logic.
  requirements.txt     -- List of Python packages the project needs.
  Dockerfile           -- Packages the app for deployment.
  docker-compose.yml   -- Runs the app with one command on any server.
```

The `story/` folder is yours. That's where your cases, dialogue, characters, and branching paths live as data files you can read and edit.

---

## 6. Getting Started

Once you have Claude Code installed and open in your project folder, here's how to get rolling:

**Step 1:** Tell Claude Code: *"Set up the project."*
It will create the folder structure above, set up a virtual environment, and install the packages listed in the tech stack.

**Step 2:** Tell Claude Code: *"Run the dev server and show me how to open it."*
It will start the game locally on your computer and tell you the URL to open in your browser (usually something like `http://localhost:5000`).

**Step 3:** Tell Claude Code: *"Add a sample chapter so I can see how it works."*
It will create a short demo chapter with a couple of branching choices so you can see the narrative flow in action.

**Step 4:** Start designing. Open the story files and start writing. Ask Claude Code to add features, change the look, add characters, build new mechanics — whatever the game needs. You're the designer now.

---

## 7. Ideas to Try

Here are things you could say to Claude Code to start building out the game. These are just starting points — ask for whatever you want.

- *"Write a first chapter where I'm assigned a breach of contract case by a senior partner."*
- *"Make it so choosing to research the UCC leads to a different outcome than researching common law."*
- *"Add a character — a senior partner named Margaret who's tough but fair."*
- *"Show me a relationship tracker so I can see how the partner feels about my work."*
- *"Make the courtroom scene more dramatic — add a pause before the judge rules."*
- *"Let the player go back and try a different research path."*
- *"Save the player's progress so they can come back later."*
- *"Add a time pressure mechanic — the player has limited turns before the deadline."*
- *"Show me what happens if the player misses the key case. Write that branch."*
- *"Make the opposing counsel smarter in Chapter 3 if the player beat them in Chapter 1."*

You know what makes legal research interesting. You know what makes a story compelling. That's the hard part — and it's your part. The code is the easy part.
