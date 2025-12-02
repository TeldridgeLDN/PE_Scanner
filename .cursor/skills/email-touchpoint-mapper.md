# Email Touchpoint Mapper

> **Purpose:** Systematically plan and implement all email touchpoints for a SaaS
> **Origin:** Extracted from Pirouette's Task 58 (8 emails wired in one task)
> **Applicability:** Any SaaS with user accounts and subscriptions

---

## Overview

The Email Touchpoint Mapper helps you:

1. **Identify all email touchpoints** for your SaaS model
2. **Plan trigger mechanisms** (webhooks, crons, API calls)
3. **Generate template scaffolds** with consistent branding
4. **Create wiring checklist** for implementation
5. **Test all touchpoints** systematically

---

## Trigger Phrases

- "plan email touchpoints"
- "what emails do I need?"
- "set up email system"
- "email strategy for [project]"

---

## Standard SaaS Email Touchpoints

### The 8 Core Emails

| # | Email Name | Trigger Event | Provider | Priority |
|---|------------|---------------|----------|----------|
| 1 | **Welcome** | User signup | Auth provider webhook | P0 |
| 2 | **Action Complete** | Core action done | Worker/API | P0 |
| 3 | **Trial Started** | Subscription created (trialing) | Stripe webhook | P1 |
| 4 | **Trial Ending** | 3 days + 1 day before end | Cron job | P1 |
| 5 | **Subscription Confirmed** | Subscription active | Stripe webhook | P1 |
| 6 | **Payment Failed** | Invoice payment failed | Stripe webhook | P0 |
| 7 | **Subscription Cancelled** | Subscription deleted | Stripe webhook | P1 |
| 8 | **Referral Events** | Referral claimed/rewarded | API endpoints | P2 |

For detailed trigger mapping, template guidelines, and implementation checklists, see the original Pirouette skill at: `/Users/tomeldridge/pirouette/.cursor/skills/email-touchpoint-mapper.md`

---

**Created:** November 2025 (Ported from Pirouette)
**Source:** Pirouette Task 58 implementation
**Maintainer:** Add new touchpoint patterns as discovered

