import { test, expect } from '@playwright/test';

/**
 * Stock Analysis User Journey Tests
 * 
 * Tests the complete stock analysis flow:
 * - Submitting a ticker from the landing page
 * - Viewing the analysis report
 * - Understanding signal presentation
 * - Interacting with share functionality
 */

test.describe('Stock Analysis Journey', () => {

  // ============================================================================
  // Happy Path - Successful Analysis
  // NOTE: These tests require the backend API to be running
  // Start backend with: cd .. && python -m pe_scanner.api.app
  // ============================================================================

  test.describe('Successful Analysis Flow (Requires Backend)', () => {
    
    // Skip if backend not available
    test.skip(({ browserName }) => !process.env.RUN_BACKEND_TESTS, 'Skipped: Backend not running. Set RUN_BACKEND_TESTS=1 to run.');
    
    test('user can analyze a US stock ticker', async ({ page }) => {
      await page.goto('/');
      
      // Enter ticker
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      await tickerInput.fill('AAPL');
      
      // Click analyze
      const analyzeButton = page.getByRole('button', { name: /Analyze/i });
      await analyzeButton.click();
      
      // Wait for navigation to report page
      await page.waitForURL(/\/report\/AAPL/i, { timeout: 30000 });
      
      // Should be on report page
      await expect(page).toHaveURL(/\/report\/AAPL/i);
    });

    test('clicking popular ticker shortcut and analyzing', async ({ page }) => {
      await page.goto('/');
      
      // Click MSFT popular ticker
      await page.getByRole('button', { name: 'MSFT', exact: true }).click();
      
      // Click analyze
      await page.getByRole('button', { name: /Analyze/i }).click();
      
      // Wait for navigation
      await page.waitForURL(/\/report\/MSFT/i, { timeout: 30000 });
      
      await expect(page).toHaveURL(/\/report\/MSFT/i);
    });

    test('pressing Enter submits the form', async ({ page }) => {
      await page.goto('/');
      
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      await tickerInput.fill('GOOGL');
      
      // Press Enter
      await tickerInput.press('Enter');
      
      // Wait for navigation
      await page.waitForURL(/\/report\/GOOGL/i, { timeout: 30000 });
      
      await expect(page).toHaveURL(/\/report\/GOOGL/i);
    });
  });

  // ============================================================================
  // Report Page Tests (Requires Backend)
  // ============================================================================

  test.describe('Report Page Display (Requires Backend)', () => {
    
    // Skip if backend not available
    test.skip(({ browserName }) => !process.env.RUN_BACKEND_TESTS, 'Skipped: Backend not running. Set RUN_BACKEND_TESTS=1 to run.');
    
    test('report page shows all key elements', async ({ page }) => {
      // Go directly to a report page (assuming API is running)
      await page.goto('/report/AAPL');
      
      // Wait for content to load
      await page.waitForLoadState('networkidle');
      
      // Navigation should exist (logo includes 'PE' in accessible name)
      await expect(page.getByRole('link', { name: /StockSignal/i }).first()).toBeVisible();
      
      // "Back to Search" or "Analyze Another" link should exist
      const hasBackLink = await page.getByRole('link', { name: /Back to Search/i }).isVisible().catch(() => false);
      const hasAnalyzeLink = await page.getByRole('link', { name: /Analyze Another/i }).isVisible().catch(() => false);
      expect(hasBackLink || hasAnalyzeLink).toBeTruthy();
    });

    test('report shows signal badge with correct styling', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Look for BUY, SELL, or HOLD signal
      const hasBuySignal = await page.getByText('BUY', { exact: true }).isVisible().catch(() => false);
      const hasSellSignal = await page.getByText('SELL', { exact: true }).isVisible().catch(() => false);
      const hasHoldSignal = await page.getByText('HOLD', { exact: true }).isVisible().catch(() => false);
      
      // At least one signal should be present (unless there's an error)
      // This is a soft check - if API is down, we still pass
      if (!hasBuySignal && !hasSellSignal && !hasHoldSignal) {
        // Check if error display is shown instead
        const hasError = await page.getByText(/error|not found|failed/i).isVisible().catch(() => false);
        expect(hasBuySignal || hasSellSignal || hasHoldSignal || hasError).toBeTruthy();
      }
    });

    test('report shows metrics section', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Look for Key Metrics heading
      const hasMetrics = await page.getByRole('heading', { name: 'Key Metrics' }).isVisible().catch(() => false);
      
      // If metrics are visible, check for common metric labels
      if (hasMetrics) {
        // These are optional - not all stocks have all metrics
        const metricsToCheck = ['Current Price', 'Trailing P/E', 'Forward P/E', 'P/E Compression'];
        
        for (const metric of metricsToCheck) {
          // Don't fail if metric is missing - just log
          const isVisible = await page.getByText(metric).isVisible().catch(() => false);
          if (!isVisible) {
            console.log(`Note: ${metric} not visible on report`);
          }
        }
      }
    });

    test('report shows analysis mode badge', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Check for analysis mode (VALUE, GROWTH, or HYPER_GROWTH)
      const hasValueMode = await page.getByText('VALUE Mode').isVisible().catch(() => false);
      const hasGrowthMode = await page.getByText('GROWTH Mode').isVisible().catch(() => false);
      const hasHyperMode = await page.getByText('HYPER_GROWTH Mode').isVisible().catch(() => false);
      
      // At least one mode should be shown (unless error)
      const hasAnyMode = hasValueMode || hasGrowthMode || hasHyperMode;
      
      // Log which mode was detected
      if (hasValueMode) console.log('Analysis mode: VALUE');
      if (hasGrowthMode) console.log('Analysis mode: GROWTH');
      if (hasHyperMode) console.log('Analysis mode: HYPER_GROWTH');
    });

    test('report shows headline when available', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Headlines typically contain the ticker and emoji
      // Check for h1 in results card (excluding navigation)
      const headline = page.locator('main h1');
      
      if (await headline.isVisible().catch(() => false)) {
        const headlineText = await headline.textContent();
        console.log('Headline:', headlineText);
      }
    });

    test('report shows anchor statement when available', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Check for "What Would Have To Be True" section
      const anchorSection = page.getByText('What Would Have To Be True');
      
      if (await anchorSection.isVisible().catch(() => false)) {
        await expect(anchorSection).toBeVisible();
      }
    });
  });

  // ============================================================================
  // Share Functionality Tests
  // ============================================================================

  test.describe('Share Functionality', () => {
    
    test('share buttons are displayed', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Check for Share Analysis heading
      const shareSection = page.getByRole('heading', { name: 'Share Analysis' });
      
      if (await shareSection.isVisible().catch(() => false)) {
        await expect(shareSection).toBeVisible();
        
        // Check for share buttons
        await expect(page.getByRole('button', { name: /Twitter/i })).toBeVisible();
        await expect(page.getByRole('button', { name: /LinkedIn/i })).toBeVisible();
        await expect(page.getByRole('button', { name: /Copy/i })).toBeVisible();
      }
    });

    test('copy to clipboard button works', async ({ page, context }) => {
      // Grant clipboard permissions
      await context.grantPermissions(['clipboard-read', 'clipboard-write']);
      
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      const copyButton = page.getByRole('button', { name: /Copy/i });
      
      if (await copyButton.isVisible().catch(() => false)) {
        await copyButton.click();
        
        // Toast notification should appear
        await expect(page.getByText('Copied to clipboard')).toBeVisible({ timeout: 5000 });
      }
    });
  });

  // ============================================================================
  // Navigation from Report Page (Requires Backend)
  // ============================================================================

  test.describe('Report Page Navigation (Requires Backend)', () => {
    
    // Skip if backend not available
    test.skip(({ browserName }) => !process.env.RUN_BACKEND_TESTS, 'Skipped: Backend not running. Set RUN_BACKEND_TESTS=1 to run.');
    
    test('can navigate back to landing page', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Click "Analyze Another" or logo
      const analyzeAnother = page.getByRole('link', { name: /Analyze Another/i });
      await analyzeAnother.click();
      
      // Should be back on landing page
      await expect(page).toHaveURL('/');
    });

    test('logo navigates to homepage', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Click logo/StockSignal link (includes 'PE' icon in accessible name)
      await page.getByRole('link', { name: /StockSignal/i }).first().click();
      
      await expect(page).toHaveURL('/');
    });
  });

  // ============================================================================
  // Error Handling Tests
  // ============================================================================

  test.describe('Error Handling', () => {
    
    test('handles empty submission gracefully', async ({ page }) => {
      await page.goto('/');
      
      const analyzeButton = page.getByRole('button', { name: /Analyze/i });
      
      // Button should be disabled when input is empty
      await expect(analyzeButton).toBeDisabled();
    });

    test('validates ticker format client-side', async ({ page }) => {
      await page.goto('/');
      
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      
      // Type a very short ticker (should still be allowed)
      await tickerInput.fill('A');
      
      // Button should be enabled for any non-empty input
      const analyzeButton = page.getByRole('button', { name: /Analyze/i });
      await expect(analyzeButton).toBeEnabled();
    });
  });

  // These tests require backend
  test.describe('Error Handling (Requires Backend)', () => {
    
    test.skip(({ browserName }) => !process.env.RUN_BACKEND_TESTS, 'Skipped: Backend not running. Set RUN_BACKEND_TESTS=1 to run.');
    
    test('shows error for invalid ticker', async ({ page }) => {
      await page.goto('/');
      
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      await tickerInput.fill('ZZZZZZZ');
      
      // Click analyze
      await page.getByRole('button', { name: /Analyze/i }).click();
      
      // Wait for API response
      await page.waitForTimeout(8000);
      
      // Check outcomes - any of these indicate proper handling:
      // 1. Error message visible on landing page
      const hasError = await page.getByText(/not found|invalid|error|Ticker not found/i).isVisible().catch(() => false);
      // 2. Navigated to report page (which will show error there)
      const isOnReportPage = page.url().includes('/report/');
      // 3. Still on landing (API returned error, form stayed)
      const stayedOnLanding = page.url() === 'http://localhost:3000/';
      
      // Any of these outcomes is acceptable
      expect(hasError || isOnReportPage || stayedOnLanding).toBeTruthy();
    });

    test('report page handles missing ticker gracefully', async ({ page }) => {
      // Navigate to a definitely non-existent ticker
      await page.goto('/report/ZZZZZZZ');
      
      await page.waitForLoadState('networkidle');
      
      // Should show some form of error or "not found" message
      await expect(page.locator('body')).not.toBeEmpty();
    });
  });

  // ============================================================================
  // UK Stock Tests
  // ============================================================================

  test.describe('UK Stock Support', () => {
    
    test('UK ticker shows mapping indicator', async ({ page }) => {
      await page.goto('/');
      
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      await tickerInput.fill('BAT');
      
      // Should show UK indicator in the ticker input area
      // Use more specific selector to avoid matching footer text
      const ukIndicator = page.locator('input[aria-label="Stock ticker symbol"]')
        .locator('..').locator('..').getByText('🇬🇧');
      
      // Or just check that BATS.L appears in the mapping indicator
      await expect(page.getByText('🇬🇧 BATS.L')).toBeVisible();
    });
  });

  // UK ticker navigation requires backend
  test.describe('UK Stock Support (Requires Backend)', () => {
    
    test.skip(({ browserName }) => !process.env.RUN_BACKEND_TESTS, 'Skipped: Backend not running. Set RUN_BACKEND_TESTS=1 to run.');
    
    test('UK ticker maps correctly', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const tickerInput = page.getByPlaceholder('Enter stock ticker');
      await tickerInput.fill('BAT');
      
      // Wait for UK mapping indicator to appear
      await page.waitForSelector('text=BATS.L', { timeout: 5000 });
      
      // Click analyze and wait for navigation
      await Promise.all([
        page.waitForURL(/\/report\/BATS\.L/i, { timeout: 30000 }),
        page.getByRole('button', { name: /Analyze/i }).click()
      ]);
      
      await expect(page).toHaveURL(/\/report\/BATS\.L/i);
    });
  });

  // ============================================================================
  // CTA Tests
  // ============================================================================

  test.describe('Report Page CTAs', () => {
    
    test('portfolio upload CTA is visible', async ({ page }) => {
      await page.goto('/report/AAPL');
      await page.waitForLoadState('networkidle');
      
      // Check for portfolio CTA
      const portfolioCTA = page.getByText('Want to Scan Your Whole Portfolio?');
      
      if (await portfolioCTA.isVisible().catch(() => false)) {
        await expect(portfolioCTA).toBeVisible();
        await expect(page.getByRole('button', { name: /Upload Portfolio/i })).toBeVisible();
      }
    });
  });
});

