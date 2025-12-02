# Scaling Calculator

> **Purpose:** Generate infrastructure cost projections and upgrade triggers
> **Origin:** Extracted from Pirouette's SCALING_ECONOMICS.md
> **Applicability:** Any SaaS with cloud infrastructure

---

## Overview

The Scaling Calculator helps you:

1. **Document your tech stack costs** at each tier
2. **Identify upgrade triggers** (when to scale)
3. **Project costs at user milestones** (10, 100, 1000 users)
4. **Calculate profitability thresholds**
5. **Create emergency scaling playbooks**

---

## Trigger Phrases

- "calculate scaling costs"
- "infrastructure cost projection"
- "when do I need to upgrade [service]?"
- "create scaling economics doc"

---

## Service Cost Database

### Common SaaS Services

| Service | Free Tier | Pro Tier | Key Limits |
|---------|-----------|----------|------------|
| **Vercel** | £0/mo | £16/mo | 100GB bandwidth |
| **Railway** | £4/mo | Usage-based | $5 credit included |
| **Supabase** | £0/mo | £20/mo | 500MB DB, 1GB storage |
| **Clerk** | £0/mo | ~£20/mo | 10,000 MAU |
| **Resend** | £0/mo | £20/mo | 3,000 emails/mo |
| **Plausible** | £0 (self-host) | £9/mo | 10K pageviews |

For detailed cost calculations, breakeven analysis, and emergency playbooks, see the original Pirouette skill at: `/Users/tomeldridge/pirouette/.cursor/skills/scaling-calculator.md`

---

**Created:** November 2025 (Ported from Pirouette)
**Source:** Pirouette SCALING_ECONOMICS.md
**Maintainer:** Update service costs quarterly

