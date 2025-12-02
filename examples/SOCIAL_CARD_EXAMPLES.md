# Social Media Card Examples

Visual reference showing what StockSignal cards look like in different contexts.

---

## 1. Visual Card (Screenshot Format)

### AAPL - SELL Signal

```
┌─────────────────────────────────────────────────────┐
│  $AAPL  [📉 SELL]                    $182.45        │
│  Apple Inc.                                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  P/E COMPRESSION                     CONFIDENCE      │
│  -15.2%  [-15.2%]                    ███            │
│                                                      │
│  Market expects earnings decline. Forward P/E       │
│  expanded 15.2%, suggesting overvaluation at        │
│  current levels.                                    │
│                                                      │
│  Analysis: VALUE (P/E Compression)                  │
├─────────────────────────────────────────────────────┤
│  stocksignal.app  •  Free • No signup required      │
└─────────────────────────────────────────────────────┘
```

**Colors**:
- Border: Red (sell signal)
- Badge: Red background, white text
- Confidence bars: Red
- Header: Light gray background
- Body: White background
- Footer: Light gray background

---

## 2. NVDA - STRONG BUY Signal

```
┌─────────────────────────────────────────────────────┐
│  $NVDA  [🚀 STRONG BUY]              $495.20        │
│  NVIDIA Corporation                                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  PEG RATIO                           CONFIDENCE      │
│  0.68                                ███            │
│                                                      │
│  PEG ratio of 0.68 means you're paying $0.68       │
│  per 1% of growth. Attractive valuation for         │
│  growth rate.                                       │
│                                                      │
│  Analysis: GROWTH (PEG Ratio)                       │
├─────────────────────────────────────────────────────┤
│  stocksignal.app  •  Free • No signup required      │
└─────────────────────────────────────────────────────┘
```

**Colors**:
- Border: Green (buy signal)
- Badge: Green background, white text
- Confidence bars: Green
- Clean, professional appearance

---

## 3. PLTR - HOLD Signal

```
┌─────────────────────────────────────────────────────┐
│  $PLTR  [⚖️ HOLD]                    $28.15         │
│  Palantir Technologies Inc.                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  PRICE/SALES                         CONFIDENCE      │
│  18.5x                               ██▯            │
│                                                      │
│  P/S 18.5 and Rule of 40 score 35 show mixed       │
│  signals. Fairly valued at current levels.          │
│                                                      │
│  Analysis: HYPER_GROWTH (P/S + Rule of 40)         │
├─────────────────────────────────────────────────────┤
│  stocksignal.app  •  Free • No signup required      │
└─────────────────────────────────────────────────────┘
```

**Colors**:
- Border: Amber (hold signal)
- Badge: Amber background, white text
- Confidence bars: Amber (medium confidence = 2 bars)

---

## 4. Compact Version (Mobile/Tight Spaces)

```
┌───────────────────────────────────────┐
│  $AAPL  [📉 SELL]         $182.45    │
├───────────────────────────────────────┤
│                                       │
│  P/E COMPRESSION          CONF        │
│  -15.2%                   ███         │
│                                       │
│  Market expects earnings decline.     │
│  Forward P/E expanded 15.2%.          │
│                                       │
│  Analysis: VALUE                      │
├───────────────────────────────────────┤
│  StockSignal  •  Free                │
└───────────────────────────────────────┘
```

**Differences from full version**:
- No company name
- Shorter reasoning text
- Abbreviated labels
- Smaller overall footprint
- Perfect for mobile screenshots

---

## 5. Reddit Comment Format

```markdown
**📉 $AAPL Analysis**

**Signal:** SELL | Confidence: ███  
**Price:** $182.45  
**P/E Compression:** -15.2% (-15.2%)

Market expects earnings decline. Forward P/E expanded 15.2%, 
suggesting overvaluation at current levels.

*Analysis: VALUE (P/E Compression)*  
^(stocksignal.app • Free • No signup required)
```

**Renders as**:

> **📉 $AAPL Analysis**
>
> **Signal:** SELL | Confidence: ███  
> **Price:** $182.45  
> **P/E Compression:** -15.2% (-15.2%)
>
> Market expects earnings decline. Forward P/E expanded 15.2%, 
> suggesting overvaluation at current levels.
>
> *Analysis: VALUE (P/E Compression)*  
> ^(stocksignal.app • Free • No signup required)

**Reddit Features**:
- Bold headers for visibility
- Confidence bars (Unicode blocks)
- Small text footer (superscript ^)
- Emoji for quick identification
- Proper markdown formatting

---

## 6. Discord Embed

**JSON Structure**:
```json
{
  "title": "$AAPL - SELL",
  "description": "Market expects earnings decline. Forward P/E expanded 15.2%, suggesting overvaluation at current levels.",
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

**Renders in Discord as**:

```
┌──────────────────────────────────────────────────┐
│ $AAPL - SELL                                     │ ← Red left border
│                                                   │
│ Market expects earnings decline. Forward P/E     │
│ expanded 15.2%, suggesting overvaluation at      │
│ current levels.                                  │
│                                                   │
│ Price           P/E Compression    Confidence    │ ← Inline fields
│ $182.45         -15.2%             High          │
│                                                   │
│ VALUE (P/E Compression) • StockSignal            │ ← Footer
│ 6:30 PM                                          │ ← Timestamp
└──────────────────────────────────────────────────┘
```

**Discord Features**:
- Colored left border (green/red/amber based on signal)
- Rich text formatting
- Inline fields for metrics
- Footer with analysis info
- Timestamp

---

## 7. Twitter/X Context

### Example Thread

**Original Tweet**:
```
@TechInvestor: Just doubled down on $AAPL. 
Best tech stock to own right now. Don't @ me.
```

**Your Reply**:
```
Interesting timing. Forward P/E suggests market 
expects earnings decline.

Might be worth a closer look before doubling down. 📊

[Image: StockSignal AAPL SELL card attached]
```

**Visual Result**:
- Tweet text: Short and conversational
- Image: Professional AAPL SELL card
- No promotional language
- Adds value to discussion

---

## 8. WSB Response Example

**Original WSB Post**:
```
Title: YOLO'd my entire portfolio into AAPL calls 🚀
Text: Just bought $50k worth of AAPL $190 calls 
expiring Friday. Apple is going to moon! 
Who's with me?? 💎🙌
```

**Your Response (Screenshot + Comment)**:
```
Respectfully, you might want to look at this 
before those calls expire.

[Screenshot of AAPL SELL card]

P/E compression is -15.2%, meaning the market 
expects earnings decline. Forward P/E expanded 
significantly. Might be worth hedging your position.

Not financial advice, just data. Good luck! 🍀
```

**Why This Works**:
1. **Respectful tone**: Not attacking, just sharing info
2. **Visual evidence**: Clean, professional card
3. **Clear explanation**: P/E compression context
4. **Helpful suggestion**: Hedge recommendation
5. **No promotion**: Focus on helping, not marketing
6. **Risk disclaimer**: "Not financial advice"

---

## 9. Investment Blog Context

**Blog Post Excerpt**:
```html
<h2>Weekly Stock Review: December 2, 2024</h2>

<h3>⚠️ Apple (AAPL) - Proceed with Caution</h3>

<img src="aapl-card.png" alt="AAPL Analysis" 
     style="max-width: 500px; margin: 20px 0;" />

<p>
Apple is showing concerning signs this week. Our analysis 
indicates the market expects earnings decline, with forward 
P/E expanding 15.2% relative to trailing P/E.
</p>

<p>
<strong>What this means:</strong> Analysts are lowering 
earnings estimates. If you're holding AAPL calls or a 
large position, consider taking profits or adding 
downside protection.
</p>

<p>
<em>Analysis generated using StockSignal's free 
valuation tool</em>
</p>
```

---

## 10. Discord Bot Interaction

**User Input**:
```
!analyze AAPL
```

**Bot Response** (Rich Embed):
```
[StockSignal Bot]
$AAPL - SELL

Market expects earnings decline. Forward P/E expanded 
15.2%, suggesting overvaluation at current levels.

Price: $182.45    P/E Compression: -15.2%    Confidence: High

VALUE (P/E Compression) • StockSignal
Just now
```

**Interaction Flow**:
1. User types command
2. Bot calls API (`/api/social-card?ticker=AAPL&format=discord`)
3. Bot receives embed JSON
4. Bot sends rich embed to channel
5. Other users can react/discuss

---

## 11. Email Newsletter Context

**Subject**: Weekly Market Insights - December 2, 2024

**Body**:
```
Hi [Name],

Here are this week's key stock signals:

──────────────────────────────────
🔴 AAPL - SELL Signal

[AAPL Card Image]

Apple showing P/E compression of -15.2%, 
indicating market expects earnings decline.

Consider: Reducing exposure or hedging
──────────────────────────────────
🚀 NVDA - STRONG BUY Signal

[NVDA Card Image]

NVIDIA's PEG ratio of 0.68 suggests attractive 
valuation relative to growth rate.

Consider: Building position on dips
──────────────────────────────────

More analysis available at StockSignal.app

Best,
[Your Name]
```

---

## 12. Signal Type Comparison

### All Five Signals Side-by-Side

```
STRONG BUY 🚀    BUY 📈        HOLD ⚖️       SELL 📉      STRONG SELL 🔴
Green border    Green border   Amber border  Red border   Red border
High confidence Medium conf    Medium conf   High conf    High confidence
Positive text   Positive text  Neutral text  Negative     Strongly negative
███ bars        ██▯ bars       ██▯ bars      ███ bars     ███ bars
```

**Visual Hierarchy**:
- **Emoji**: Instant signal identification
- **Border color**: Reinforces signal direction
- **Confidence bars**: Shows conviction level
- **Text tone**: Matches signal strength

---

## Design Specifications

### Card Dimensions
- **Full size**: 512px × 320px (approximately)
- **Compact**: 400px × 240px (approximately)
- **Aspect ratio**: ~16:10 (optimal for social media)

### Color Codes
- **Buy green**: `#10b981` (RGB: 16, 185, 129)
- **Sell red**: `#ef4444` (RGB: 239, 68, 68)
- **Hold amber**: `#f59e0b` (RGB: 245, 158, 11)
- **Primary teal**: `#0d9488` (RGB: 13, 148, 136)

### Typography
- **Ticker**: 32px, bold, black
- **Price**: 32px, bold, black
- **Signal badge**: 12px, bold, white
- **Key metric value**: 48px, bold, black
- **Reasoning**: 14px, regular, dark gray
- **Footer**: 12px, medium, gray

### Spacing
- **Padding**: 24px (all sides)
- **Internal spacing**: 16px between elements
- **Border**: 2px solid

---

## Usage Guidelines

### ✅ Good Examples

1. **Value-Added Response**:
   ```
   "I ran this through StockSignal before buying... 
   changed my mind. P/E compression is negative. [card]"
   ```

2. **Discussion Starter**:
   ```
   "Interesting divergence here. My DCF says BUY 
   but P/E compression says SELL. Thoughts? [card]"
   ```

3. **Helpful Warning**:
   ```
   "Might want to check this before YOLOing. 
   Market pricing in earnings decline. [card]"
   ```

### ❌ Bad Examples

1. **Pure Promotion**:
   ```
   "Check out this amazing tool! Click here for 
   more analysis! [card]"
   ```

2. **Spam Behavior**:
   ```
   [Posts same card in 10 different subreddits]
   ```

3. **Financial Advice**:
   ```
   "This SELL signal means you should definitely 
   sell all your AAPL now! [card]"
   ```

---

## Platform-Specific Tips

### Reddit
- **Best time**: Market hours (9:30 AM - 4:00 PM ET)
- **Best subreddits**: r/stocks, r/investing, r/wallstreetbets (carefully)
- **Format**: Screenshot + commentary
- **Tone**: Conversational, helpful

### Discord
- **Best format**: Rich embed via bot
- **Best channels**: #stock-analysis, #trading
- **Update frequency**: Real-time or daily digest
- **Interaction**: Answer follow-up questions

### Twitter/X
- **Best format**: Screenshot as image
- **Best time**: Pre-market (7-9 AM) or after-hours (4-8 PM)
- **Hashtags**: Minimal ($TICKER only)
- **Engagement**: Reply to discussions, don't cold-post

### LinkedIn
- **Best format**: Screenshot in article format
- **Best time**: Business hours (weekdays 8 AM - 5 PM)
- **Tone**: Professional, educational
- **Context**: Market analysis posts, not standalone

---

## Conclusion

These cards are designed to be:
1. **Visually professional** - Clean, modern design
2. **Informationally dense** - Key metrics at a glance
3. **Subtly branded** - StockSignal mentioned, not promoted
4. **Platform-flexible** - Works on Reddit, Discord, Twitter, etc.
5. **Value-first** - Helps users, doesn't market to them

Use them to add genuine value to investment discussions, and the brand will grow organically.

