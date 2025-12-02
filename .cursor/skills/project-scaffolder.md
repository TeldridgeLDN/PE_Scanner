# Project Scaffolder Agent

> **Purpose:** Rapidly scaffold new SaaS projects with battle-tested patterns from Pirouette
> **Origin:** Extracted from Pirouette development (Nov 2025)
> **Applicability:** Any SaaS project, especially freemium models

---

## Overview

The Project Scaffolder combines multiple learnings from Pirouette's development into a single agent that can:

1. **Create PRD from idea** - Comprehensive product requirements
2. **Generate task list** - Via Taskmaster integration
3. **Set up email touchpoints** - All 8 standard SaaS emails
4. **Create scaling economics doc** - Cost projections
5. **Scaffold feature gating** - Free/Pro tier patterns

---

## Trigger Phrases

- "scaffold new project"
- "create new SaaS project"
- "set up [project name]"
- "initialize project from idea"

---

## Scaffolding Protocol

### Phase 1: Discovery (5-10 minutes)

Ask the user these questions to understand the project:

```markdown
## Project Discovery Questions

### Core Product
1. **What problem does this solve?** (One sentence)
2. **Who is the target user?** (Primary persona)
3. **What's the core feature?** (The "aha" moment)

### Business Model
4. **Pricing model?** (Freemium, subscription, one-time, usage-based)
5. **Price points?** (Free tier limits, Pro tier price)
6. **Revenue target?** (Month 3, Month 6, Month 12)

### Technical
7. **Tech stack preference?** (Next.js, React, Vue, etc.)
8. **Database preference?** (Supabase, Planetscale, MongoDB)
9. **Auth provider?** (Clerk, Auth0, NextAuth)
10. **Any existing code to import?** (Sibling projects)
```

For details on complete PRD generation, implementation, and integration with other skills, see the original Pirouette skill at: `/Users/tomeldridge/pirouette/.cursor/skills/project-scaffolder.md`

---

**Created:** November 2025 (Ported from Pirouette)
**Source:** Pirouette project learnings
**Maintainer:** Update after each new project scaffolded

