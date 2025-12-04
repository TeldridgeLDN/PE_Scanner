import { test, expect } from '@playwright/test';

/**
 * Landing Page User Journey Tests
 * 
 * Tests the complete landing page experience including:
 * - Hero section with ticker search
 * - Navigation and CTAs
 * - Features section
 * - Pricing section
 * - FAQ interactions
 * - Footer links
 */

test.describe('Landing Page Journey', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  // ============================================================================
  // Hero Section Tests
  // ============================================================================

  test.describe('Hero Section', () => {
    
    test('displays hero headline and value proposition', async ({ page }) => {
      // Check main headline is visible
      await expect(page.locator('h1')).toContainText('Spot Earnings Collapses');
      await expect(page.locator('h1')).toContainText('Before Your Portfolio Does');
      
      // Check subheadline
      await expect(page.getByText('Free analysis reveals which stocks are priced for disaster')).toBeVisible();
      
      // Check trust indicators (use .first() since text appears in multiple places)
      await expect(page.getByText('Results in 30 seconds').first()).toBeVisible();
      await expect(page.getByText('No credit card required').first()).toBeVisible();
      await expect(page.getByText('10 free analyses per day').first()).toBeVisible();
    });

    test('shows free badge indicator', async ({ page }) => {
      await expect(page.getByText('Free analysis • No signup required')).toBeVisible();
    });

    test('ticker search form is visible and functional', async ({ page }) => {
      // Check input is visible
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      await expect(tickerInput).toBeVisible();
      
      // Check analyze button
      const analyzeButton = page.getByRole('button', { name: /Analyze/i });
      await expect(analyzeButton).toBeVisible();
      
      // Button should be disabled when input is empty
      await expect(analyzeButton).toBeDisabled();
      
      // Type a ticker - button should enable
      await tickerInput.fill('AAPL');
      await expect(analyzeButton).toBeEnabled();
    });

    test('shows popular ticker shortcuts', async ({ page }) => {
      // Check popular tickers are displayed
      const popularTickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'BAT', 'BP'];
      
      for (const ticker of popularTickers) {
        await expect(page.getByRole('button', { name: ticker, exact: true })).toBeVisible();
      }
    });

    test('clicking popular ticker fills the input', async ({ page }) => {
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      
      // Click on AAPL popular ticker
      await page.getByRole('button', { name: 'AAPL', exact: true }).click();
      
      // Input should be filled
      await expect(tickerInput).toHaveValue('AAPL');
    });

    test('input auto-uppercases ticker symbols', async ({ page }) => {
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      
      await tickerInput.fill('aapl');
      await expect(tickerInput).toHaveValue('AAPL');
    });
  });

  // ============================================================================
  // Social Proof Section Tests
  // ============================================================================

  test.describe('Social Proof Bar', () => {
    
    test('displays stock analysis statistics', async ({ page }) => {
      await expect(page.getByText('10,000+')).toBeVisible();
      await expect(page.getByText('Stocks analyzed')).toBeVisible();
    });

    test('shows example analysis results', async ({ page }) => {
      // HOOD sell signal
      await expect(page.getByText('-113% SELL')).toBeVisible();
      await expect(page.getByText('HOOD predicted')).toBeVisible();
      
      // BATS.L buy signal
      await expect(page.getByText('+62% BUY')).toBeVisible();
      await expect(page.getByText('BATS.L identified')).toBeVisible();
    });
  });

  // ============================================================================
  // How It Works Section Tests
  // ============================================================================

  test.describe('How It Works Section', () => {
    
    test('displays three step process', async ({ page }) => {
      await expect(page.getByRole('heading', { name: 'How It Works' })).toBeVisible();
      
      // Check all three steps
      await expect(page.getByText('Enter Ticker Symbol')).toBeVisible();
      await expect(page.getByText('AI Analyzes in 30 Seconds')).toBeVisible();
      await expect(page.getByText('Get Shareable Results')).toBeVisible();
    });

    test('shows step descriptions', async ({ page }) => {
      // Step 1 description
      await expect(page.getByText('Type any stock ticker (AAPL, HOOD, BATS.L)')).toBeVisible();
      
      // Step 2 description - check for partial text (use .first() since it appears in multiple places)
      await expect(page.getByText(/classifies your stock into VALUE, GROWTH, or HYPER_GROWTH/).first()).toBeVisible();
      
      // Step 3 description - be more specific
      await expect(page.getByText('Receive a clear BUY/SELL/HOLD signal')).toBeVisible();
    });
  });

  // ============================================================================
  // Features Section Tests
  // ============================================================================

  test.describe('Features Section', () => {
    
    test('displays all 7 analysis features', async ({ page }) => {
      // Scroll to features section first
      await page.locator('#features').scrollIntoViewIfNeeded();
      
      await expect(page.getByRole('heading', { name: 'Comprehensive Analysis Features' })).toBeVisible();
      
      // Check key features using more specific selectors
      await expect(page.locator('h3:has-text("P/E Compression Analysis")')).toBeVisible();
      await expect(page.locator('h3:has-text("Growth Stock (PEG) Support")')).toBeVisible();
      await expect(page.locator('h3:has-text("Hyper-Growth Analysis")')).toBeVisible();
      await expect(page.locator('h3:has-text("Shareable Headlines")')).toBeVisible();
      await expect(page.locator('h3:has-text("Anchoring Context")')).toBeVisible();
      await expect(page.locator('h3:has-text("Fair Value Scenarios")')).toBeVisible();
      await expect(page.locator('h3:has-text("Data Quality Validation")')).toBeVisible();
    });

    test('shows tier badges on features', async ({ page }) => {
      // Scroll to features section first
      await page.locator('#features').scrollIntoViewIfNeeded();
      
      // Check tier badges within feature cards
      const featuresSection = page.locator('#features');
      await expect(featuresSection.getByText('VALUE').first()).toBeVisible();
      await expect(featuresSection.getByText('GROWTH').first()).toBeVisible();
      await expect(featuresSection.getByText('HYPER_GROWTH').first()).toBeVisible();
      await expect(featuresSection.getByText('ALL').first()).toBeVisible();
    });
  });

  // ============================================================================
  // Pricing Section Tests
  // ============================================================================

  test.describe('Pricing Section', () => {
    
    test('displays pricing tiers', async ({ page }) => {
      // Navigate to pricing section
      await page.locator('#pricing').scrollIntoViewIfNeeded();
      
      // Check for pricing section heading
      await expect(page.getByRole('heading', { name: /Pricing|Plans/i })).toBeVisible();
      
      // Check pricing tiers exist (use more specific selectors)
      const pricingSection = page.locator('#pricing');
      await expect(pricingSection.getByText(/Free/i).first()).toBeVisible();
      await expect(pricingSection.getByText(/Pro/i).first()).toBeVisible();
      await expect(pricingSection.getByText(/£25/).first()).toBeVisible();
    });
  });

  // ============================================================================
  // Example Results Section Tests
  // ============================================================================

  test.describe('Example Results Section', () => {
    
    test('shows real analysis examples', async ({ page }) => {
      // Scroll to examples section
      await page.locator('#examples').scrollIntoViewIfNeeded();
      
      await expect(page.getByRole('heading', { name: 'Real Analysis Examples' })).toBeVisible();
      
      // Check HOOD example within examples section
      const examplesSection = page.locator('#examples');
      await expect(examplesSection.getByText('Robinhood')).toBeVisible();
      await expect(examplesSection.getByText('53% drop confirmed')).toBeVisible();
      
      // Check META example
      await expect(examplesSection.getByText('Meta Platforms')).toBeVisible();
      
      // Check BATS.L example
      await expect(examplesSection.getByText('British American Tobacco')).toBeVisible();
    });
  });

  // ============================================================================
  // FAQ Section Tests
  // ============================================================================

  test.describe('FAQ Section', () => {
    
    test('displays FAQ questions', async ({ page }) => {
      await expect(page.getByRole('heading', { name: 'Common Questions' })).toBeVisible();
      
      // Check FAQ questions exist
      await expect(page.getByText('How is this different from a stock screener?')).toBeVisible();
      await expect(page.getByText('Why should I trust AI-generated headlines?')).toBeVisible();
      await expect(page.getByText('Can I cancel anytime?')).toBeVisible();
    });

    test('FAQ accordion expands and collapses', async ({ page }) => {
      // Find first FAQ item
      const firstQuestion = page.locator('details').first();
      
      // Initially the answer should not be visible (details closed)
      const answerText = 'Screeners show current P/E ratios';
      await expect(page.getByText(answerText)).not.toBeVisible();
      
      // Click to expand
      await firstQuestion.locator('summary').click();
      
      // Wait a moment for animation
      await page.waitForTimeout(300);
      
      // Now answer should be visible
      await expect(page.getByText(answerText)).toBeVisible();
      
      // Click again to collapse
      await firstQuestion.locator('summary').click();
      await page.waitForTimeout(300);
      
      // Answer should be hidden again
      await expect(page.getByText(answerText)).not.toBeVisible();
    });
  });

  // ============================================================================
  // Footer Tests
  // ============================================================================

  test.describe('Footer', () => {
    
    test('displays footer with legal links', async ({ page }) => {
      // Scroll to footer
      await page.locator('footer').scrollIntoViewIfNeeded();
      
      // Check legal links
      await expect(page.getByRole('link', { name: 'Privacy Policy' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Terms of Service' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Disclaimer' })).toBeVisible();
    });

    test('legal links navigate correctly', async ({ page }) => {
      // Check privacy link works
      const privacyLink = page.getByRole('link', { name: 'Privacy Policy' });
      await expect(privacyLink).toHaveAttribute('href', '/privacy');
      
      // Check terms link works
      const termsLink = page.getByRole('link', { name: 'Terms of Service' });
      await expect(termsLink).toHaveAttribute('href', '/terms');
    });
  });

  // ============================================================================
  // Navigation Tests
  // ============================================================================

  test.describe('Navigation', () => {
    
    test('navigation links scroll to sections', async ({ page }) => {
      // Check that section anchor links work
      // Look for any navigation that links to features
      const featuresLink = page.getByRole('link', { name: 'Features' });
      
      // This is a soft test - link may not exist in all nav configurations
      const isVisible = await featuresLink.isVisible().catch(() => false);
      
      if (isVisible) {
        await featuresLink.click();
        await page.waitForTimeout(500);
        
        // Features section should be in view
        await expect(page.getByRole('heading', { name: 'Comprehensive Analysis Features' })).toBeInViewport();
      } else {
        // If no nav link, just verify the section exists
        await page.locator('#features').scrollIntoViewIfNeeded();
        await expect(page.getByRole('heading', { name: 'Comprehensive Analysis Features' })).toBeVisible();
      }
    });
  });

  // ============================================================================
  // Responsive Design Tests
  // ============================================================================

  test.describe('Responsive Design', () => {
    
    test('hero section is readable on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      
      // Main content should still be visible
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.getByPlaceholder('Enter stock ticker')).toBeVisible();
    });
  });
});

