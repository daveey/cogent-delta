---
name: cogamer.configure
description: Interactive setup for your cogent's identity. Uses a multi-step plan to collect name, personality, and vibe, then writes COGENT.md. Commits and pushes when done.
---

# Configure Cogent Identity

Set up the cogent's personality in COGENT.md using a multi-step plan.

## Steps

### 1. Read Current State

Read `COGENT.md` to see if it's already configured or still the default placeholder.

### 2. Create Plan

Create a plan with these steps. The user fills in each step by editing the plan:

```
Step 1: Choose a name
  - What's your cogent's name? This is the identity your agent carries into tournaments and freeplay.
  - Answer: <fill in>

Step 2: Define personality
  - Describe your cogent in a few sentences. Aggressive? Cautious? Chaotic? Chill?
  - Answer: <fill in>

Step 3: Set a motto / vibe
  - A one-liner that captures their energy.
  - Examples: "Move fast, hold nothing", "Patience is a junction", "All your extractors are belong to us"
  - Answer: <fill in>

Step 4: Strategy philosophy (optional)
  - e.g. "defense wins games", "rush early, scale late", "adapt to everything"
  - Answer: <fill in, or "skip">
```

Wait for the user to approve the plan (they'll fill in answers and approve).

### 3. Write COGENT.md

Once the plan is approved with answers filled in, generate COGENT.md:

```markdown
# {Name}

> {Motto / Vibe}

## Personality

{Personality description}

## Strategy Philosophy

{Strategy philosophy, or "Evolving — no fixed doctrine yet." if skipped}
```

### 4. Commit and Push

```bash
git add COGENT.md
git commit -m "Configure cogent identity: {Name}"
git push
```
