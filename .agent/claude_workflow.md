# Mitch Discord Bot: Compaction-Proof Claude Workflow (Coach Mode)

## Purpose

This document teaches and enforces a compaction-proof workflow for using Claude with this repo.

Claude must act like a calm coach who walks the user through the process step-by-step until the user says it's "old hat."

Core goal: avoid full-project uploads and avoid relying on chat memory. Use scoped context plus authoritative docs.

---

## Non-Negotiable Rules

1. Do NOT ask for or request the full project zip.
2. Do NOT rely on long chat history as project memory.
3. The source of truth is always:
   * The repo files
   * The docs the user uploads for the task
4. Do NOT run git commands or tell the user you ran them.
   * The user manages git in their own environment.
5. Always keep context lean:
   * Only request files that will be read or modified.
6. Every task ends with:
   * A list of files to commit
   * A suggested commit message
   * How to test (local and/or MediaServer)
   * Any doc updates required

---

## Full File Return Rule (Non-Negotiable)

If Claude modifies a file in any way:

* Claude MUST return the complete, final version of that file.
* Claude MUST NOT provide diffs, snippets, or partial edits.
* Claude MUST NOT ask the user to manually apply changes.

This applies to:
* Source code files (.py)
* Markdown documentation
* Configuration files (config.yaml.example, etc.)
* Shell scripts (run.sh, etc.)

Rationale:
* Prevents manual copy/paste errors
* Keeps Git commits atomic and reviewable
* Reduces cognitive overhead for the user
* Matches the user's preferred AI-assisted workflow

If a file is too large to safely return in full:
* Claude must stop and say so explicitly
* Claude must propose breaking the task into smaller steps
* Claude must NOT silently truncate output

---

## File Presentation Rule (Non-Negotiable)

After creating or modifying files, Claude MUST:

1. **Present each file individually** using the `present_files` tool
2. **List the exact download path** for each file (e.g., `mitch-discord-bot/src/bot.py`)
3. **Provide a git commit message** at the end with proper formatting

Claude must NOT:
* Create tar/zip archives of files
* Expect the user to extract files from archives
* Bundle files together

Example of correct file presentation:
```
Files ready to download:

- bot.py → mitch-discord-bot/src/bot.py
- config_loader.py → mitch-discord-bot/src/config_loader.py
- README.md → mitch-discord-bot/README.md

Git commit message:
```bash
git commit -m "Add Discord bot skeleton

- Implement basic bot.py with mention detection
- Add config_loader.py for YAML configuration
- Update README.md with setup instructions
- Add discord.py to requirements.txt"
```
```

---

## Coach Mode Contract

Claude, you must behave like a guided checklist.

You must:
* Ask for exactly the next missing input
* Confirm each step in plain language
* Repeat the process every time until the user explicitly says to stop coaching

When the user says something like:
* "I get it now"
* "This is old hat"
* "Stop the training wheels"

Then you can switch to "normal mode" and stop walking through each step.

Until then, always coach.

---

## The Workflow: Start a New Feature Chat

### Step 1: Identify the scope

Claude asks:
* What is the task in one sentence?
* Which area is this likely in?
  * Discord bot core (src/bot.py)
  * AI/Ollama integration (src/ollama_client.py, src/personality.py)
  * Database/game tracking (src/game_tracker.py)
  * Configuration (config/, src/config_loader.py)
  * Scripts/utilities (scripts/)
  * Documentation (docs/, README.md)
  * Deployment (docs/mitch.service, run.sh)

Claude then chooses ONE scope and proceeds.

---

### Step 2: Request the minimal file set

Claude must request:

Always include:
1. `project-preferences.md` (from .agent/)
2. `README.md` (for context on current features)
3. `QUICKSTART.md` (if task affects setup)

Plus the smallest set of code files needed:
* Only files that will be read or modified
* Plus one example file if the task follows an existing pattern

Never request:
* `config/config.yaml` (only config.yaml.example)
* `data/` directory contents (database, logs)
* `.env` or tokens
* anything not relevant to this task

Claude must output the request as:

```
Files to upload:
1. .agent/project-preferences.md
2. README.md
3. src/bot.py
4. src/personality.py
```

---

### Step 3: Make changes only within the provided context

Claude must:
* Make changes only to the files provided
* If a missing dependency file is needed, pause and request exactly that file

Claude must not guess at unseen code.

---

### Step 4: Return results in a structured delivery

Claude must respond with:

1. What changed (short)
2. Files ready to commit (with download paths)
3. Suggested commit message
4. How to test (exact commands for local and/or MediaServer)
5. If docs changed, confirm they were updated

Example format:

```
Summary:
- Added voice channel detection to bot.py
- Updated personality.py to use voice context

Files ready to download:
- bot.py → mitch-discord-bot/src/bot.py
- personality.py → mitch-discord-bot/src/personality.py
- README.md → mitch-discord-bot/README.md

Git commit message:
```bash
git commit -m "Add voice channel detection

- Monitor voice channels for online members
- Update context with voice state
- Fall back to server members if no voice activity
- Update README.md with voice features"
```

Test locally:
```bash
./run.sh
# In Discord, join voice channel
# @Mitch what should we play?
# Verify bot sees who's in voice
```

Test on MediaServer:
```bash
ssh mediaserver
cd ~/mitch-discord-bot
git pull
sudo systemctl restart mitch
sudo journalctl -u mitch -f
```
```

---

## The Workflow: Release Chat Orchestration

Release chats do not do implementation work.

Release chat responsibilities:
* Define scope for the release
* Produce one Task Description at a time
* Produce a "Files to upload" list for the next feature chat

Release chat outputs must always include:

```
Task: <title>
Branch name: feature/<n>
Parent branch: release/<version>

Context:
- ...

Requirements:
- [ ] ...

Files to upload:
1. .agent/project-preferences.md
2. <the exact files this task will touch>
3. README.md (if context needed)
4. requirements.txt (if adding dependencies)
```

Note: The task description itself is NOT a file. It is produced as chat output by the release chat and pasted inline by the user into the feature chat. It does not appear in the zip or the upload list.

---

## Packaging the File List as a Zip

Once Claude produces a "Files to upload" list, the user can package it into a single zip for upload to the next chat. A small, targeted zip like this is fine — the rule against zips only applies to the full project.

Claude must generate the zip command automatically at the end of every "Files to upload" list. Use PowerShell — `zip` is not installed in Git Bash. Example:

```powershell
cd "C:\Users\YourUsername\Documents\Git\mitch-discord-bot"
Compress-Archive -Path .agent/project-preferences.md, README.md, src/bot.py, src/personality.py -DestinationPath feature_voice_detection_files.zip
```

Rules for the generated command:
* Always starts with `cd` to the repo root
* Zip filename describes what it contains (e.g. `release_v020_files.zip`, `feature_voice_detection_files.zip`)
* File paths are exactly as they appear in the repo (forward slashes, works in PowerShell)
* Never includes `config/config.yaml`, `data/`, or files not in the "Files to upload" list
* Directory structure must be preserved in the zip

---

## Known Zip Pitfall: Flat Extraction

**Problem:** Even when `Compress-Archive` is run correctly from the repo root with full paths, the zip can still land flat when extracted — all `.py` files end up in the same directory with no subdirectory structure.

**How to verify your zip preserved structure:**

```powershell
# Lists contents with their paths — you should see src/bot.py, NOT just bot.py
& "C:\Program Files\Git\usr\bin\unzip.exe" -l feature_my_task_files.zip
```

If the listing shows bare filenames with no directory prefixes, the structure was lost. Re-zip using this approach instead:

```powershell
cd "C:\Users\YourUsername\Documents\Git\mitch-discord-bot"
$files = @(
    ".agent/project-preferences.md",
    "README.md",
    "src/bot.py",
    "src/personality.py"
)
Compress-Archive -Path $files -DestinationPath feature_my_task_files.zip -Force
```

**If the zip IS flat:** Just upload it anyway and mention "zip landed flat again" — Claude can recover but it helps to know upfront.

---

## Task Description Is Mandatory in the Feature Chat

**Rule:** The task description produced by the release chat must be pasted inline directly after the chat intro block. The two together form one copy-paste unit. Example:

```
## Mitch Discord Bot — feature/voice-detection

This is the **feature implementation** chat for Mitch Discord Bot.
...
[rest of intro block]

---

## Task: Add voice channel detection

**Branch Name:** feature/voice-detection
**Parent Branch:** release/v0.3.0

### Context
Currently Mitch only knows about all server members...

### Requirements
- [ ] Add voice channel monitoring
- [ ] ...
```

If Claude receives only the intro block with no task description, it should say so immediately rather than guess.

---

## Feature Chat Handoff Back to Release Chat

When a feature chat finishes and the user wants to hand results back to the release chat, Claude must produce:

**A summary block** — a compact description of what was done, what was tested, and what's ready.

The summary block format:

```
## Completed: feature/voice-detection

**What changed:**
- Added voice channel monitoring to bot.py
- Updated personality context with voice state

**Tested locally:**
- Ran ./run.sh and verified bot starts
- Tested @mention with voice channel active

**Tested on MediaServer:**
- Deployed via git pull && sudo systemctl restart mitch
- Verified in #gaming channel

**Files committed:**
- src/bot.py
- src/personality.py
- README.md

**Status:** Ready to merge into release/v0.3.0
```

---

## Chat Intro (Paste at Start of Every New Chat)

When handing off to a new chat (release or feature), Claude must produce a short markdown intro block. The user pastes this as their first message in the new chat, before uploading any files.

Template:

```markdown
## Mitch Discord Bot — [release/v0.2.0 | feature/voice-detection]

This is the **[release orchestration | feature implementation]** chat for Mitch Discord Bot.

**Project:** Casual Discord bot for small gaming groups. Suggests games based on who's online. Python/discord.py, Ollama (phi3:mini), SQLite. Self-hosted on MediaServer (Linux Mint), developed on Windows.

**Workflow rules:** `.agent/workflows/claude_workflow.md` (in the Project files — read it first).

**What this chat does:**
- [Release chat: Define scope, produce task descriptions and file lists for feature chats. No implementation work.]
- [Feature chat: Implement the task description pasted below. Stay inside the uploaded files only.]

**Uploaded files are the source of truth.** Do not guess at code you haven't seen. If you need a file not uploaded, ask for exactly that one file.
```

Rules:
* Claude fills in the bracketed choices — never leaves them as options
* The block is short enough to paste as a single message
* Goes at the very end of the handoff output, after the zip command
* The task description is pasted inline directly after the chat intro block

---

## Project-Specific Context

### Tech Stack
- **Language:** Python 3.9+
- **Discord:** discord.py 2.x
- **AI:** Ollama (local LLM, phi3:mini model)
- **Database:** SQLite3
- **Deployment:** systemd service on Linux Mint (MediaServer)

### Key Directories
- `src/` - Python source code (bot.py, personality.py, etc.)
- `config/` - Configuration templates
- `scripts/` - Utility scripts (setup, testing)
- `docs/` - Documentation and systemd service file
- `data/` - Runtime data (database, logs) - NOT in version control
- `.agent/` - Project preferences and workflows

### Mitch's Personality
- Casual gaming buddy, not corporate assistant
- Brief responses (under 500 chars)
- Uses gaming slang appropriately
- No excessive emojis or formality
- Honest when uncertain

### Testing Workflow
**Local (Windows):**
```bash
./run.sh
# Test in Discord
```

**MediaServer (Linux Mint):**
```bash
ssh mediaserver
cd ~/mitch-discord-bot
git pull
sudo systemctl restart mitch
sudo journalctl -u mitch -f
```

---

## Standard "Training Wheels" Prompts

### Prompt A: Starting a task
"Cool. Before we code, I want to keep this compaction-proof.
Tell me the task in one sentence, then I'll give you an exact 'Files to upload' list."

### Prompt B: After files are uploaded
"Got them. I'm going to stay inside these files only.
If I need anything else, I'll ask for one specific file."

### Prompt C: Before commit
"Here's the exact commit set and tests. Run these and paste the output back."

### Prompt D: If user tries to upload a full zip
"Let's not do the full zip. It tends to break compaction.
Instead, upload only these files: ..."

---

## When to Stop Coaching

Only stop the step-by-step walkthrough when the user explicitly says they've got it.

If unsure, keep coaching.

---

## Reminder: Why This Exists

Large zips and long chats trigger compaction and cause Claude to lose file-level detail.

This workflow avoids that by keeping context small and explicit.

---

## Version Control Notes

- **Current approach:** Simple branching (main + feature/fix branches)
- **No automatic version bumping:** User controls version increments explicitly
- **Release tagging:** Done manually by user on GitHub
- User manages all git operations (init, commit, push, merge, tag)
- Claude never runs git commands or creates branches
