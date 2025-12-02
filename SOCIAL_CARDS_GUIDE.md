# Social Media Cards Guide

## Overview

StockSignal's social media card system creates shareable, Reddit-optimized analysis cards designed for WSB, Discord, and Twitter contexts. The design philosophy is **value-first, not promotional** - cards provide genuinely useful analysis without looking like spam or advertisements.

---

## Use Cases

### 1. **Reddit/WSB Responses**
Someone posts their AAPL position on r/wallstreetbets, you respond with:
- **Visual Card**: Screenshot the card and upload as an image
- **Text Format**: Copy the markdown comment and paste directly

### 2. **Discord Investment Channels**
Share analysis in Discord servers using:
- **Rich Embeds**: Use the embed JSON with Discord webhooks/bots
- **Screenshot**: Post the visual card as an image

### 3. **Twitter/X Replies**
Respond to stock discussion threads with:
- **Screenshot**: Clean visual card works great as a reply image
- **Text**: Use the reasoning text in your tweet

---

## Component Usage

### Basic Visual Card

```tsx
import SocialMediaCard from '@/components/SocialMediaCard';

<SocialMediaCard
  ticker="AAPL"
  companyName="Apple Inc."
  currentPrice={182.45}
  signal="SELL"
  analysisMode="VALUE (P/E Compression)"
  keyMetric={{
    label: "P/E Compression",
    value: "-15.2%",
    change: "-15.2%"
  }}
  reasoning="Market expects earnings decline. Forward P/E expanded 15.2%, suggesting overvaluation at current levels."
  confidence="high"
  anchor="At current price, AAPL is valued as if it will generate $120B in annual profit — more than Apple's $100B historical peak"
/>
```

**Note**: The `anchor` prop is optional but highly recommended. It provides the "What Would Have To Be True" statement that makes abstract metrics concrete and memorable (e.g., "TSLA would need to 2.4x profits" instead of just "-42.3% compression").

### Compact Version

```tsx
<SocialMediaCard
  {...cardProps}
  compact={true}  // Smaller footprint for mobile
/>
```

---

## API Usage

### Get Card Data (JSON)

```bash
GET /api/social-card?ticker=AAPL&format=json
```

Response:
```json
{
  "ticker": "AAPL",
  "companyName": "Apple Inc.",
  "currentPrice": 182.45,
  "signal": "SELL",
  "analysisMode": "VALUE (P/E Compression)",
  "keyMetric": {
    "label": "P/E Compression",
    "value": "-15.2%",
    "change": "-15.2%"
  },
  "reasoning": "Market expects earnings decline...",
  "confidence": "high",
  "anchor": "At current price, AAPL is valued as if it will generate $120B in annual profit — more than Apple's $100B"
}
```

**Note**: The API automatically includes the `anchor` field when available, providing tangible context that makes the analysis more memorable.

### Get Reddit Comment Format

```bash
GET /api/social-card?ticker=AAPL&format=reddit
```

Response (plain text):
```
**📉 $AAPL Analysis**

**Signal:** SELL | Confidence: ███  
**Price:** $182.45  
**P/E Compression:** -15.2% (-15.2%)

Market expects earnings decline. Forward P/E expanded 15.2%, suggesting overvaluation at current levels.

**What Would Have To Be True:** At current price, AAPL is valued as if it will generate $120B in annual profit — more than Apple's $100B historical peak

*Analysis: VALUE (P/E Compression)*  
^(stocksignal.app • Free • No signup required)
```

**Note**: The anchor statement ("What Would Have To Be True") is automatically included in Reddit format, making the analysis more tangible and easier to remember.

### Get Discord Embed Format

```bash
GET /api/social-card?ticker=AAPL&format=discord
```

Response (JSON):
```json
{
  "title": "$AAPL - SELL",
  "description": "Market expects earnings decline...",
  "color": 15746116,
  "fields": [
    { "name": "Price", "value": "$182.45", "inline": true },
    { "name": "P/E Compression", "value": "-15.2%", "inline": true },
    { "name": "Confidence", "value": "High", "inline": true }
  ],
  "footer": { "text": "VALUE (P/E Compression) • StockSignal" },
  "timestamp": "2024-12-02T18:30:00.000Z"
}
```

---

## Programmatic Usage

### Generate Card Data from Analysis Result

```typescript
import { generateSocialCardData } from '@/lib/generate-social-card';

// Backend analysis result
const analysisResult = {
  ticker: 'AAPL',
  company_name: 'Apple Inc.',
  current_price: 182.45,
  analysis_mode: 'VALUE (P/E Compression)',
  signal: 'SELL',
  confidence: 'high',
  metrics: {
    compression_pct: -15.2,
    trailing_pe: 28.5,
    forward_pe: 32.8
  }
};

// Convert to card format
const cardData = generateSocialCardData(analysisResult);
```

### Generate Reddit Comment

```typescript
import { generateRedditComment } from '@/lib/generate-social-card';

const redditText = generateRedditComment(cardData);
console.log(redditText);
// Copy and paste into Reddit
```

### Generate Discord Embed

```typescript
import { generateDiscordEmbed } from '@/lib/generate-social-card';

const embedData = generateDiscordEmbed(cardData);

// Send via Discord webhook
await fetch(webhookUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ embeds: [embedData] })
});
```

---

## Design Principles

### ✅ What We DO
- Show clear, factual analysis
- Use professional, clean design
- Include confidence indicators
- Provide context with key metrics
- Subtle branding at bottom
- "Free • No signup" messaging

### ❌ What We DON'T DO
- No "click here" CTAs
- No promotional language
- No large logos or watermarks
- No financial advice disclaimers
- No urgency tactics ("Act now!")
- No affiliate links or spam

### Philosophy

These cards are designed to be **genuinely helpful contributions** to investment discussions, not advertisements. The goal is to provide value first, brand awareness second. Users will naturally check out StockSignal if the analysis is good.

---

## "What Would Have To Be True" Anchoring

### Overview

Social cards include an optional **anchor statement** that makes abstract analysis tangible and memorable. Instead of just showing "-42.3% compression," the anchor explains what that means in concrete terms.

### Anchoring Strategies

Based on the analysis mode and metrics, the system generates different types of anchor statements:

#### 1. **Profit Multiplication** (VALUE mode with severe negative compression)
**When**: P/E compression < -30%  
**Format**: "Market expects profits to DROP X%. To return to fair value, [TICKER] would need to grow profits Y.Yx"  
**Example**: "Market expects profits to DROP 58%. To return to fair value, TSLA would need to grow profits 2.4x"

**Why This Works**: Makes the market's pessimism tangible. Users immediately understand the magnitude of expected decline and what recovery would require.

#### 2. **Growth Requirements** (GROWTH mode with high P/E)
**When**: P/E > 30 in GROWTH mode  
**Format**: "To justify P/E of X, [TICKER] needs Y% annual earnings growth for 5 years. Only 5% of companies achieve this."  
**Example**: "To justify P/E of 65, NVDA needs 65% annual earnings growth for 5 years. Only 5% of companies achieve this."

**Why This Works**: Contextualizes high valuations with realistic growth requirements. The "5% of companies" reference provides perspective.

#### 3. **Mega-Cap Comparison** (VALUE mode with market cap > $500B)
**When**: Market cap exceeds $500B and moderate compression  
**Format**: "At current price, [TICKER] is valued as if it will generate $XB in annual profit — more than Apple's $100B"  
**Example**: "At current price, AAPL is valued as if it will generate $120B in annual profit — more than Apple's $100B historical peak"

**Why This Works**: Anchors to Apple's well-known profitability. Users understand that surpassing Apple's profits is exceptional.

#### 4. **Profitability Gap** (HYPER_GROWTH mode with high P/S)
**When**: P/S > 10 in HYPER_GROWTH mode  
**Format**: "At Xx sales, [TICKER] needs to achieve Y points higher profitability to justify valuation (current Rule of 40: Z)"  
**Example**: "At 18.5x sales, PLTR needs to achieve 45 points higher profitability to justify valuation (current Rule of 40: 35)"

**Why This Works**: Explains the profitability improvement required for expensive hyper-growth stocks.

#### 5. **Value Proposition** (Attractive valuations)
**When**: Low PEG or attractive P/S with strong Rule of 40  
**Format**: "[TICKER] is paying X.XXx for each % of growth — attractive valuation for Y% growth rate"  
**Example**: "NVDA is paying 0.68x for each % of growth — attractive valuation for 72% growth rate"

**Why This Works**: Highlights value opportunities with concrete price-to-growth ratio.

### Design Integration

The anchor appears in a **highlighted callout box** in the visual card:
- Light gray background (`bg-slate-50`)
- Left teal border (`border-l-4 border-primary/30`)
- Small uppercase label: "WHAT WOULD HAVE TO BE TRUE"
- Medium-weight text for emphasis

**Visual Hierarchy**:
1. Signal & Price (top)
2. Key Metric (large)
3. Reasoning (standard)
4. **Anchor (highlighted callout)** ← Makes abstract concrete
5. Analysis mode (footer)

### Reddit Format

In Reddit comments, the anchor appears as a **bold section**:

```markdown
**What Would Have To Be True:** Market expects profits to DROP 58%. 
To return to fair value, TSLA would need to grow profits 2.4x
```

This makes it easy to scan and highly memorable for Reddit users.

### Why Anchoring Matters

**Problem**: Abstract metrics like "-42.3% compression" are hard to remember and internalize.

**Solution**: Concrete statements that answer "what would have to happen for this valuation to make sense?"

**Results**:
- More memorable (concrete > abstract)
- Easier to share ("TSLA needs 2.4x profits" vs. "negative compression")
- More credible (specific calculations)
- Better discussions (tangible points to debate)

### Compact Mode

In compact mode, the anchor is **hidden** to save space. It's only shown in full-size visual cards and text formats (Reddit, Discord descriptions).

---

## Analysis Mode Support

Cards automatically adapt to all three analysis modes:

### VALUE Mode (P/E Compression)
- **Key Metric**: P/E Compression percentage
- **Reasoning**: Earnings growth/decline expectations
- **Example**: "+26.7% compression indicates undervaluation"

### GROWTH Mode (PEG Ratio)
- **Key Metric**: PEG Ratio
- **Reasoning**: Price per unit of growth
- **Example**: "PEG 0.68 means $0.68 per 1% growth"

### HYPER_GROWTH Mode (P/S + Rule of 40)
- **Key Metric**: Price/Sales ratio
- **Reasoning**: Valuation vs. growth fundamentals
- **Example**: "P/S 18.5 with Rule of 40 score 35"

---

## Demo Page

Visit `/demo/social-cards` to see:
- Live examples of all signal types
- Visual card previews
- Reddit comment format
- Discord embed JSON
- Compact version
- Design principles

---

## Signal Types

Cards support all signal types with appropriate styling:

| Signal | Emoji | Color | Use Case |
|--------|-------|-------|----------|
| STRONG_BUY | 🚀 | Green | High conviction buy |
| BUY | 📈 | Green | Standard buy signal |
| HOLD | ⚖️ | Amber | Neutral/wait |
| SELL | 📉 | Red | Standard sell signal |
| STRONG_SELL | 🔴 | Red | High conviction sell |

---

## Confidence Indicators

Visual bars show confidence level:

- **High**: `███` (3 bars)
- **Medium**: `██▯` (2 bars)
- **Low**: `█▯▯` (1 bar)

Colors match signal type (green for BUY, red for SELL, amber for HOLD).

---

## Best Practices

### Reddit/WSB
1. **Be helpful, not promotional**: Lead with value
2. **Screenshot the card**: Upload as an image in your comment
3. **Or use text format**: Copy the markdown directly
4. **Add your own commentary**: Don't just drop the card
5. **Respond to questions**: Be engaged, not spammy

### Discord
1. **Use rich embeds**: Better UX than plain text
2. **Post in appropriate channels**: Investment/stock discussions
3. **Add context**: Explain why you're sharing
4. **Don't spam**: Quality over quantity

### Twitter/X
1. **Screenshot works best**: Visual cards get more engagement
2. **Keep tweet short**: Let the card do the talking
3. **Reply to relevant threads**: Don't cold-post
4. **Use hashtags sparingly**: $TICKER is usually enough

---

## Technical Details

### Component Props

```typescript
interface SocialMediaCardProps {
  ticker: string;              // Stock symbol
  companyName?: string;        // Full company name (optional)
  currentPrice: number;        // Current stock price
  signal: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  analysisMode: string;        // e.g., "VALUE (P/E Compression)"
  keyMetric: {
    label: string;             // e.g., "P/E Compression"
    value: string;             // e.g., "-15.2%"
    change?: string;           // Optional change indicator
  };
  reasoning: string;           // 1-2 sentence explanation
  confidence: 'high' | 'medium' | 'low';
  compact?: boolean;           // Smaller version (default: false)
}
```

### Styling

Cards use the StockSignal design system:
- **Colors**: Teal primary, buy green, sell red
- **Fonts**: System font stack for clarity
- **Spacing**: Consistent with main site
- **Borders**: 2px for prominence
- **Shadows**: Subtle for depth

---

## Future Enhancements

Potential additions:
- PNG/JPEG image export API
- Customizable color themes
- Additional metrics display
- Historical signal accuracy
- Multi-ticker comparison cards

---

## Support

Questions or issues? Check:
- Demo page: `/demo/social-cards`
- API docs: `API_DOCUMENTATION.md`
- Design system: `.cursor/rules/design-system.mdc`

---

**Remember**: These cards are tools for helping others, not marketing materials. Use them to add value to conversations, and the brand will grow organically.

