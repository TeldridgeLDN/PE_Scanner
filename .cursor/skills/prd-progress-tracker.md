# PRD Progress Tracker Workflow

> **Purpose:** Track implementation progress against PRD requirements
> **Origin:** Extracted from Pirouette's PRD_ALIGNMENT_CHECK.md pattern
> **Applicability:** Any project with a PRD and task management

---

## Overview

The PRD Progress Tracker provides:

1. **Automated alignment checking** - Compare tasks vs PRD
2. **Coverage analysis** - What's done, what's missing
3. **Gap identification** - Requirements not yet addressed
4. **Progress visualization** - Percentage complete by section
5. **Drift detection** - When implementation diverges from PRD

---

## Trigger Phrases

- "check PRD alignment"
- "how are we tracking against PRD?"
- "PRD progress report"
- "what PRD requirements are missing?"

---

## Tracking Protocol

### Step 1: Load PRD Structure

Parse the PRD to extract trackable requirements.

### Step 2: Load Task Status

Query Taskmaster for current state:

```javascript
// MCP Tool
mcp_task-master-ai_get_tasks({
  projectRoot: "/path/to/project",
  status: "done",
  withSubtasks: true
})
```

Or CLI:
```bash
task-master list --status=done --with-subtasks
```

For detailed mapping matrices, coverage calculations, and gap analysis, see the original Pirouette skill at: `/Users/tomeldridge/pirouette/.cursor/skills/prd-progress-tracker.md`

---

**Created:** November 2025 (Ported from Pirouette)
**Source:** Pirouette PRD_ALIGNMENT_CHECK.md pattern
**Maintainer:** Update tracking categories as needed

