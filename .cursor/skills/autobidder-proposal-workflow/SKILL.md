---
name: autobidder-proposal-workflow
description: >
  Guides Claude through AutoBidder's end-to-end AI proposal generation workflow.
  Use this skill whenever the user wants to generate, draft, review, or refine a 
  freelance proposal — including when they paste a job description, say "write a bid",
  "generate a proposal", "draft a proposal for this job", "help me respond to this 
  posting", "what should I write for this job", or share a job URL. Also trigger when
  the user asks about proposal strategy, how to customize a template, or whether a 
  job is a good fit. Even if the request seems simple ("quick proposal for this"), 
  use this skill — it encodes AutoBidder's full quality workflow and should always
  be consulted when proposals are involved.
---

# AutoBidder — Proposal Generation Workflow

AutoBidder's core value: turn a raw job posting into a compelling, personalized 
proposal in ~2 minutes. This skill walks through every step of that pipeline.

## Workflow Overview

```
Job Posting → [1] Analyze → [2] RAG Query → [3] Prompt Build → [4] Generate → [5] Format & Send
```

---

## Step 1 — Analyze the Job Posting

Parse the job description for these signals. If the user hasn't provided one, ask for it.

**Extract:**
- **Required skills** — languages, frameworks, tools (exact keywords matter for RAG)
- **Nice-to-have skills** — secondary requirements
- **Project type** — greenfield build, existing codebase, consulting, audit, etc.
- **Client tone** — formal (enterprise), casual (startup), technical (dev-led), vague (non-tech)
- **Budget/timeline signals** — fixed price vs hourly, urgency language
- **Red flags** — unrealistic scope, missing budget, "spec work" requests
- **Key pain point** — what problem is the client trying to solve? (1 sentence)

**Fit assessment:** Rate the job Good / Acceptable / Skip based on:
- Tech stack overlap with portfolio
- Realistic scope
- Client communication quality

If rated Skip, tell the user why and stop. Don't generate a proposal for bad-fit jobs.

---

## Step 2 — Query the Knowledge Base (RAG)

Before writing, identify the best portfolio evidence to pull from ChromaDB.

**Construct retrieval queries** — one per major skill cluster found in Step 1:
```
query_1 = "<primary_tech> project experience"
query_2 = "<project_type> case study"  
query_3 = "<industry/domain> freelance work"
```

**ChromaDB call pattern** (backend endpoint: `POST /api/knowledge/search`):
```json
{
  "query": "<query_string>",
  "n_results": 3,
  "where": { "doc_type": { "$in": ["portfolio", "case_study", "resume"] } }
}
```

**From the retrieved chunks, identify:**
- Most relevant project names + outcomes (quantified if possible)
- Technologies used that match the job
- Any testimonials or client results

If retrieval returns weak results (similarity < 0.7 or chunks feel generic), tell the 
user the knowledge base may lack relevant content and suggest what to upload.

Read `references/rag-query-patterns.md` for advanced retrieval strategies and 
metadata filtering examples.

---

## Step 3 — Build the Generation Prompt

Compose the LLM prompt using this template structure:

```
SYSTEM:
You are an expert freelance proposal writer. Write in first person, confidently 
but not arrogantly. Be specific — use numbers, project names, and outcomes.
Never use filler phrases like "I am passionate about" or "I believe I am a 
great fit". Keep the proposal under 350 words unless the job explicitly asks for detail.

USER:
## Job Analysis
[paste Step 1 analysis]

## Relevant Portfolio Context
[paste top 2-3 RAG chunks]

## Proposal Requirements
- Tone: [formal / casual / technical]
- Focus angle: [cost efficiency / speed / quality / domain expertise]
- Must mention: [specific tech from job posting]
- Call to action: [suggest a call / ask a clarifying question / offer a free audit]

Write a proposal with these sections:
1. Opening hook (1-2 sentences addressing the client's core pain point)
2. Relevant experience (2-3 sentences, specific project + outcome)
3. Approach (2-3 sentences describing HOW you'd solve their problem)
4. Call to action (1 sentence)
```

**Model selection** (AutoBidder backend `POST /api/proposals/generate`):
- GPT-4: use for complex technical jobs, enterprise tone, multi-requirement parsing
- DeepSeek: use for budget-conscious jobs, speed-priority, or when GPT-4 is rate-limited

Read `references/prompt-templates.md` for tone-specific prompt variants and 
keyword injection strategies.

---

## Step 4 — Generate and Review

Call the generation endpoint or run the prompt. Then review the output against:

**Quality checklist:**
- [ ] Opens with client's pain point, not "I am a developer with X years..."
- [ ] At least one specific project name or quantified outcome
- [ ] Mentions 2+ required technologies from the job posting by name
- [ ] Approach section shows *how*, not just *what*
- [ ] CTA is a question or next step (not "I look forward to hearing from you")
- [ ] Word count 200–350 (adjust for platform: Upwork ~250, direct email ~300)
- [ ] No generic AI phrases: "leverage", "utilize", "seamlessly", "passionate"

If the draft fails ≥2 checklist items, revise the prompt and regenerate. 
Show the user the draft and checklist results together.

---

## Step 5 — Format as HTML Email for Resend

Once the proposal text is approved, format it for delivery via the Resend API.

**HTML email structure** (backend: `POST /api/emails/send`):
```html
<html>
<body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; 
             color: #1a1a1a; line-height: 1.7;">
  <p>[Opening hook]</p>
  <p>[Relevant experience]</p>
  <p>[Approach]</p>
  <p>[CTA]</p>
  <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
  <p style="font-size: 13px; color: #666;">
    [Sender name] · [Title] · [Portfolio URL]
  </p>
</body>
</html>
```

**Resend payload:**
```json
{
  "from": "you@yourdomain.com",
  "to": ["client@example.com"],
  "bcc": ["archive@yourdomain.com"],
  "subject": "Re: [Job Title] — Proposal",
  "html": "<html>...</html>"
}
```

Remind the user to set BCC to their archive address (configured in `.env` as 
`RESEND_BCC_EMAIL`) so all sent proposals are logged.

---

## Output Format

Always present results in this order:
1. **Job Fit Assessment** (Good / Acceptable / Skip + 1-line reason)
2. **Key signals extracted** (bullet list: skills, tone, pain point)
3. **RAG queries used** (show what was searched)
4. **Draft proposal** (in a code block or quoted section)
5. **Checklist results** (pass/fail per item)
6. **HTML email snippet** (collapsible / on request)

---

## Common Failure Modes

| Problem | Fix |
|---|---|
| Proposal sounds generic | Add more RAG context; force-include a specific project name |
| Wrong tone | Re-analyze client's posting language; adjust SYSTEM prompt tone |
| Too long | Set explicit word limit in prompt; cut approach to 2 sentences |
| Missing required tech keywords | Inject them explicitly in `Must mention:` field |
| Bad RAG results | Check ChromaDB collection; suggest uploading better portfolio docs |
