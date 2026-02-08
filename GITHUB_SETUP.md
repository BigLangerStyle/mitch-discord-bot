# GitHub Repository Setup Guide

This guide walks you through setting up the GitHub repository with recommended settings and configuration.

---

## ✅ Repository Created

You've already created the repository at:
**https://github.com/BigLangerStyle/mitch-discord-bot**

---

## Next Steps: Repository Configuration

### 1. Add Topics/Tags

Make your repository discoverable by adding relevant topics:

1. Go to your repository on GitHub
2. Click the ⚙️ gear icon next to "About" (top right)
3. Add these topics:
   - `discord-bot`
   - `discord`
   - `python`
   - `ollama`
   - `ai`
   - `gaming`
   - `self-hosted`
   - `sqlite`
   - `discord-py`

### 2. Enable Features

In Settings → General:

**Features to enable:**
- ✅ Issues (for bug reports and feature requests)
- ✅ Discussions (optional - for community questions)
- ❌ Projects (not needed for small project)
- ❌ Wiki (we have docs in the repo)

### 3. Branch Protection (Optional, for later)

Once you start collaborating:

1. Go to Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require pull request before merging
   - ✅ Require approvals: 1
   - ✅ Dismiss stale reviews
   - ✅ Require status checks to pass (when you have CI/CD)

**For now:** Skip this if you're working solo.

### 4. Set Repository Settings

In Settings → General:

**Default branch:** `main` (should already be set)

**Pull Requests:**
- ✅ Allow merge commits
- ✅ Allow squash merging
- ✅ Allow rebase merging
- ✅ Automatically delete head branches

**Archives:**
- ❌ Don't archive (keep it active!)

---

## Recommended GitHub Settings

### Enable Issue Templates (v0.2.0+)

Create `.github/ISSUE_TEMPLATE/` with templates for:
- Bug reports
- Feature requests
- Questions

### Add Pull Request Template (v0.2.0+)

Create `.github/pull_request_template.md` with:
- What changed
- Why it changed
- How to test
- Checklist (tests pass, docs updated, etc.)

### GitHub Actions (Future)

Consider adding workflows for:
- Running tests on PRs
- Linting code
- Building and publishing releases

---

## Repository Visibility

**Current:** Private or Public (your choice)

**To change:**
1. Settings → General → Danger Zone
2. "Change repository visibility"

**Recommendations:**
- **Public:** If you want to share with community, get contributors, build portfolio
- **Private:** If it's just for your gaming group and you're not ready to share

You can always change this later!

---

## Initial Push Instructions

Now that the repository is created and configured, let's push the code:

### Option 1: Fresh Start (Recommended)

```bash
# Navigate to your project directory
cd ~/mitch-discord-bot

# Initialize Git
git init

# Add remote
git remote add origin https://github.com/BigLangerStyle/mitch-discord-bot.git

# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit - v0.1.0 repository structure

- Add project documentation (README, CONTRIBUTING, QUICKSTART)
- Add configuration templates
- Add directory structure
- Add MIT License
- Add .gitignore for Python/Discord projects
- Add project preferences for development workflow"

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option 2: If You Already Have a Git Repo

```bash
cd ~/mitch-discord-bot

# Add remote
git remote add origin https://github.com/BigLangerStyle/mitch-discord-bot.git

# Push
git push -u origin main
```

---

## Verify Everything Worked

After pushing, check on GitHub:

1. **Files visible:** All files and directories show up
2. **README displays:** Front page shows your README.md
3. **License badge:** GitHub detects MIT license
4. **Topics show:** Tags appear under repository name
5. **.gitignore working:** No config.yaml or data/ files committed

---

## Post-Setup: Create a Release

Once v0.1.0 is pushed:

1. Go to Releases → "Create a new release"
2. Click "Choose a tag" → Type `v0.1.0` → "Create new tag"
3. Release title: `v0.1.0 - Repository Structure`
4. Description:
   ```markdown
   ## v0.1.0 - Repository Structure
   
   Initial release establishing the project foundation.
   
   ### What's Included
   - Professional directory structure
   - Core documentation (README, CONTRIBUTING, etc.)
   - Configuration templates
   - MIT License
   - Project workflow guidelines
   
   ### What's NOT Included
   - No implementation code yet
   - No Discord bot functionality
   - No Ollama integration
   
   ### Next Steps
   - v0.2.0 will add Discord bot skeleton
   - v0.3.0 will add Ollama/AI integration
   - v0.4.0 will add game tracking database
   
   **This release is structure only - stay tuned for v0.2.0!**
   ```
5. ✅ Set as latest release
6. Publish release

---

## Troubleshooting

### "Permission denied" when pushing

You need to authenticate:

**Option 1: Personal Access Token**
1. GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Use token as password when pushing

**Option 2: SSH Key**
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH Keys → New SSH Key
3. Change remote: `git remote set-url origin git@github.com:BigLangerStyle/mitch-discord-bot.git`

### "Repository not found"

Double-check the URL and your authentication.

### Files not showing up

Make sure you:
1. `git add .` to stage all files
2. `git commit` to commit them
3. `git push` to send to GitHub

---

## Congratulations! 🎉

Your repository is now set up and ready for v0.2.0 development!

**Repository URL:** https://github.com/BigLangerStyle/mitch-discord-bot

---

**Next:** Start working on v0.2.0 (Discord bot skeleton)
