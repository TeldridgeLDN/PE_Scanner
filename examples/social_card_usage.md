# Social Card Usage Examples

## Scenario: Responding on r/wallstreetbets

### Original WSB Post
```
Title: YOLO'd my entire portfolio into AAPL calls 🚀
Just bought $50k worth of AAPL $190 calls expiring Friday.
Apple is going to moon! Who's with me?? 💎🙌
```

### Your Response (Option 1: Screenshot)

1. **Generate the card data**:
```typescript
// In your browser console or local script
const response = await fetch('https://stocksignal.app/api/social-card?ticker=AAPL&format=json');
const cardData = await response.json();
```

2. **Visit demo page**: `https://stocksignal.app/demo/social-cards`
3. **Take screenshot** of the AAPL SELL card
4. **Upload to Reddit** with your comment:

```
Respectfully, you might want to look at this analysis before those calls expire.

[Image: StockSignal AAPL SELL card]

P/E compression is -15.2%, meaning the market expects earnings decline.
Forward P/E expanded significantly. Might be worth hedging your position.

Not financial advice, just data. Good luck! 🍀
```

### Your Response (Option 2: Text Format)

```bash
# Get Reddit-formatted text
curl "https://stocksignal.app/api/social-card?ticker=AAPL&format=reddit"
```

**Reddit Comment**:
```
**📉 $AAPL Analysis**

**Signal:** SELL | Confidence: ███  
**Price:** $182.45  
**P/E Compression:** -15.2% (-15.2%)

Market expects earnings decline. Forward P/E expanded 15.2%, suggesting overvaluation at current levels.

*Analysis: VALUE (P/E Compression)*  
^(stocksignal.app • Free • No signup required)

---

Not trying to rain on your parade, but you might want to consider the timing on those calls.
Market is pricing in lower earnings ahead. Maybe hedge with some puts? Just my 2¢.
```

---

## Scenario: Discord Investment Server

### Channel: #stock-analysis

**Discord Bot Integration**:

```javascript
// Discord bot code
const { Client, EmbedBuilder } = require('discord.js');

client.on('messageCreate', async (message) => {
  // Trigger: !analyze AAPL
  if (message.content.startsWith('!analyze ')) {
    const ticker = message.content.split(' ')[1].toUpperCase();
    
    // Fetch Discord embed data
    const response = await fetch(
      `https://stocksignal.app/api/social-card?ticker=${ticker}&format=discord`
    );
    const embedData = await response.json();
    
    // Send to Discord
    const embed = new EmbedBuilder()
      .setTitle(embedData.title)
      .setDescription(embedData.description)
      .setColor(embedData.color)
      .addFields(embedData.fields)
      .setFooter(embedData.footer)
      .setTimestamp(embedData.timestamp);
    
    await message.reply({ embeds: [embed] });
  }
});
```

**Result in Discord**:
```
[Rich Embed]
$AAPL - SELL

Market expects earnings decline. Forward P/E expanded 15.2%, 
suggesting overvaluation at current levels.

Price: $182.45     P/E Compression: -15.2%     Confidence: High

VALUE (P/E Compression) • StockSignal
12/2/2024 6:30 PM
```

---

## Scenario: Twitter/X Reply

### Original Tweet
```
@TechInvestor: Just doubled down on $AAPL. 
Best tech stock to own right now. Don't @ me.
```

### Your Reply

1. **Take screenshot** of AAPL SELL card
2. **Upload as reply image**
3. **Keep text minimal**:

```
Interesting timing. Forward P/E suggests market expects earnings decline.

Might be worth a closer look before doubling down. 📊
```

**Result**: 
- Image shows clean, professional analysis
- Your text is conversational, not promotional
- You've added value to the discussion
- Others will click through to StockSignal naturally

---

## Scenario: Personal Trading Journal

### Blog Post Format

```markdown
## Trade Review: AAPL Call Option (Dec 1, 2024)

### Initial Position
- Bought: 5x AAPL $190 calls, exp 12/15
- Entry: $3.50/contract
- Total cost: $1,750

### Analysis at Entry
I checked StockSignal before entry:

![AAPL Analysis Card](aapl-analysis-screenshot.png)

**Key Metrics**:
- Signal: SELL
- P/E Compression: -15.2%
- Confidence: High

Market was pricing in earnings decline, but I thought the 
setup was oversold. Decided to take the risk anyway.

### Outcome
Position closed at $1.20/contract (-66% loss).

**Lesson Learned**: Should have listened to the P/E compression 
signal. Market was right about earnings decline. Next time, 
I'll pay more attention to forward P/E expansion as a warning sign.
```

---

## Scenario: Email Newsletter

### Weekly Stock Picks Email

```html
<h2>⚠️ Stocks to Watch This Week</h2>

<h3>$AAPL - Proceed with Caution</h3>

<img src="aapl-social-card.png" alt="AAPL Analysis" style="max-width: 500px;" />

<p>
Apple is showing concerning signs this week. Our P/E compression 
analysis indicates the market expects earnings decline, with forward 
P/E expanding 15.2%.
</p>

<p>
<strong>What this means:</strong> Analysts are lowering earnings estimates. 
If you're holding AAPL calls or a large position, consider taking profits 
or adding downside protection.
</p>

<p>
<em>Analysis powered by StockSignal's free valuation tool</em>
</p>
```

---

## Scenario: Investment Group Chat

### WhatsApp/Telegram Message

**Text Version**:
```
📉 AAPL Update:

Signal: SELL (High Confidence)
Price: $182.45
P/E Compression: -15.2%

Market expects earnings decline. Forward P/E expanded 
significantly, suggesting overvaluation.

Not loving the setup here. Might trim my position before ER.

[Screenshot attached]

Source: StockSignal (free tool, no signup needed)
```

---

## Scenario: YouTube Video

### "Stock Analysis" Video Description

```markdown
# AAPL Stock Analysis - December 2024

## Key Points
- Current Price: $182.45
- Signal: SELL
- P/E Compression: -15.2%

![AAPL Analysis](thumbnail-aapl.png)

Market is pricing in earnings decline with forward P/E expansion 
of 15.2%. This is a bearish signal for near-term price action.

## Tools Used
- StockSignal (free): https://stocksignal.app
- TradingView for charts
- Company financials from 10-K

## Timestamps
0:00 - Overview
2:30 - P/E Compression Analysis ← StockSignal card shown
5:15 - Chart Analysis
8:00 - Final Verdict

---

*Full analysis generated using StockSignal's free valuation tool.*
*No affiliation, just a tool I found useful.*
```

---

## Best Practices Summary

### ✅ DO:
1. **Add context**: Don't just drop the card
2. **Be conversational**: Natural, helpful tone
3. **Credit the tool**: "Using StockSignal" builds trust
4. **Engage with responses**: Answer questions
5. **Share when relevant**: Not every thread needs it

### ❌ DON'T:
1. **Spam multiple subreddits**: Quality over quantity
2. **Make it promotional**: Lead with value, not marketing
3. **Give financial advice**: "Not financial advice" isn't a shield
4. **Ignore context**: Read the room before posting
5. **Post the same card repeatedly**: Varies your contributions

---

## Pro Tips

### Make It Personal
```
Instead of:
"Here's the analysis:" [card]

Try:
"I ran this through StockSignal before buying and... 
actually changed my mind. Check it out:" [card]
```

### Admit When You're Wrong
```
"I bought AAPL calls yesterday, but this analysis shows 
P/E compression is negative. Might have been a bad trade. 
Anyone else seeing this?" [card]
```

### Ask Questions
```
"StockSignal is showing SELL but momentum is strong. 
What am I missing here?" [card]
```

### Compare With Other Analysis
```
"Interesting - my DCF model says BUY but P/E compression 
says SELL. Here's the StockSignal card:" [card]

"Anyone else seeing this divergence?"
```

---

## Measurement & Iteration

Track what works:
- Screenshot vs. text format engagement
- Which subreddits respond best
- Time of day for posts
- Types of discussions that fit naturally

The goal is **genuine value addition**, not marketing metrics. 
If people find it helpful, the brand grows. If it feels spammy, 
stop and reassess.

---

## Questions?

- Demo page: https://stocksignal.app/demo/social-cards
- Full guide: `SOCIAL_CARDS_GUIDE.md`
- API docs: `API_DOCUMENTATION.md`

