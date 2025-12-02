# PE Scanner Frontend

Next.js 15 frontend for PE Scanner - Stock Valuation Made Simple.

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Deployment**: Vercel (planned)

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp env.example .env.local

# Edit .env.local with your values
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
web/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   ├── globals.css        # Global styles + design tokens
│   └── report/            # Results pages (future)
├── components/            # React components
├── lib/                   # Utilities
│   ├── analytics/         # Plausible tracking
│   └── email/             # Email templates (Resend)
├── public/                # Static assets
└── env.example            # Environment variables template
```

## Environment Variables

See `env.example` for required variables.

**Development:**
- `NEXT_PUBLIC_API_URL`: Flask API endpoint (default: http://localhost:5000)
- `NEXT_PUBLIC_APP_URL`: Frontend URL (default: http://localhost:3000)

**Production (Vercel):**
- `NEXT_PUBLIC_API_URL`: https://pe-scanner-api.railway.app
- `NEXT_PUBLIC_APP_URL`: https://pe-scanner.com
- `NEXT_PUBLIC_PLAUSIBLE_DOMAIN`: pe-scanner.com
- `RESEND_API_KEY`: Email service key

## Design Tokens

Design tokens are defined in `app/globals.css`:

**Colors:**
- Primary: Indigo (#6366f1) - Trust/finance
- Buy: Green (#10b981) - Positive signals
- Sell: Red (#ef4444) - Warning signals
- Hold: Amber (#f59e0b) - Neutral signals

**Typography:**
- System font stack for performance
- Fluid typography (responsive sizing)

**Animations:**
- Fade in, slide up, scale in
- Float animation for interactive elements

## Integration with Backend

The frontend communicates with the Flask API:

```typescript
// Example API call
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze/HOOD`);
const data = await response.json();
```

## Deployment

### Vercel (Recommended)

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push to main

### Manual Deployment

```bash
npm run build
npm start
```

## Development Workflow

1. `task-master next` - Get next task
2. Implement feature
3. Test locally: `npm run dev`
4. `task-master set-status --id=X --status=done`

## Related Documentation

- **Backend API**: `/src/pe_scanner/api/`
- **Task Master**: `/.taskmaster/docs/`
- **PRD**: `/.taskmaster/docs/prd.txt`
- **Launch Strategy**: `/.taskmaster/docs/web_launch_strategy.md`

---

**Built with ❤️ for investors who deserve better valuation tools**
