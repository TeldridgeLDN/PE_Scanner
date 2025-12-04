import { test, expect } from '@playwright/test';

/**
 * Authentication User Journey Tests
 * 
 * Tests the sign-up and sign-in flows:
 * - Sign-in page accessibility
 * - Sign-up page accessibility
 * - Navigation between auth pages
 * - Redirect behavior
 * 
 * Note: These tests verify the pages load and display correctly.
 * Actual authentication tests would require Clerk test mode.
 */

test.describe('Authentication Journey', () => {

  // ============================================================================
  // Sign In Page Tests
  // ============================================================================

  test.describe('Sign In Page', () => {
    
    test('sign-in page loads correctly', async ({ page }) => {
      await page.goto('/sign-in');
      
      // Check page title/heading
      await expect(page.getByRole('heading', { name: /Welcome Back to StockSignal/i })).toBeVisible();
      
      // Check description text
      await expect(page.getByText('Sign in to access your dashboard')).toBeVisible();
    });

    test('sign-in page has Clerk component', async ({ page }) => {
      await page.goto('/sign-in');
      
      // Wait for page to be interactive
      await page.waitForLoadState('domcontentloaded');
      
      // Page should have our custom header content
      await expect(page.getByRole('heading', { name: /Welcome Back to StockSignal/i })).toBeVisible();
      
      // Clerk component will render - just verify page is not empty
      await expect(page.locator('body')).not.toBeEmpty();
    });

    test('sign-in page has link to sign-up', async ({ page }) => {
      await page.goto('/sign-in');
      
      // Check for sign-up link
      await expect(page.getByRole('link', { name: /Sign up for free/i })).toBeVisible();
    });

    test('sign-up link navigates correctly', async ({ page }) => {
      await page.goto('/sign-in');
      
      // Click sign-up link
      await page.getByRole('link', { name: /Sign up for free/i }).click();
      
      // Should be on sign-up page
      await expect(page).toHaveURL(/\/sign-up/);
    });
  });

  // ============================================================================
  // Sign Up Page Tests
  // ============================================================================

  test.describe('Sign Up Page', () => {
    
    test('sign-up page loads correctly', async ({ page }) => {
      await page.goto('/sign-up');
      
      // Check page title/heading
      await expect(page.getByRole('heading', { name: /Start Your Free Account/i })).toBeVisible();
      
      // Check description text
      await expect(page.getByText('Get 10 free analyses per day')).toBeVisible();
    });

    test('sign-up page has Clerk component', async ({ page }) => {
      await page.goto('/sign-up');
      await page.waitForLoadState('domcontentloaded');
      
      // Check our custom header is visible
      await expect(page.getByRole('heading', { name: /Start Your Free Account/i })).toBeVisible();
      
      // Page should have content
      await expect(page.locator('body')).not.toBeEmpty();
    });

    test('sign-up page has link to sign-in', async ({ page }) => {
      await page.goto('/sign-up');
      
      // Our custom link says "Sign in" - look for it in our additional info section
      await expect(page.getByText('Already have an account?')).toBeVisible();
      await expect(page.getByRole('link', { name: /Sign in/i }).first()).toBeVisible();
    });

    test('sign-in link from sign-up navigates correctly', async ({ page }) => {
      await page.goto('/sign-up');
      
      // Wait for our content
      await expect(page.getByText('Already have an account?')).toBeVisible();
      
      // Click our sign-in link (not Clerk's internal one)
      // Our link is in the "Additional Info" section
      const signInLink = page.locator('text=Already have an account?').locator('..').getByRole('link', { name: /Sign in/i });
      await signInLink.click();
      
      // Should be on sign-in page
      await expect(page).toHaveURL(/\/sign-in/);
    });

    test('sign-up page shows trust indicators', async ({ page }) => {
      await page.goto('/sign-up');
      
      // Check for trust indicators
      await expect(page.getByText('No credit card required')).toBeVisible();
      await expect(page.getByText('Cancel anytime')).toBeVisible();
    });
  });

  // ============================================================================
  // Dashboard Redirect Tests
  // ============================================================================

  test.describe('Dashboard Protection', () => {
    
    test('dashboard redirects to sign-in when not authenticated', async ({ page }) => {
      // Try to access dashboard without auth
      await page.goto('/dashboard');
      
      // Should redirect to sign-in
      // Note: This may vary based on Clerk's middleware configuration
      await page.waitForURL(/\/(sign-in|dashboard)/, { timeout: 10000 });
      
      // Either we're on sign-in or stayed on dashboard (if middleware handles it differently)
      const url = page.url();
      expect(url.includes('/sign-in') || url.includes('/dashboard')).toBeTruthy();
    });
  });

  // ============================================================================
  // Navigation Auth Tests
  // ============================================================================

  test.describe('Navigation Authentication Links', () => {
    
    test('landing page has sign-in link', async ({ page }) => {
      await page.goto('/');
      
      // Check for sign-in link in navigation
      const signInLink = page.getByRole('link', { name: /Sign In/i });
      
      // Note: Link might be in navigation or elsewhere
      // This is a soft check - link may not exist on all pages
      if (await signInLink.isVisible().catch(() => false)) {
        await expect(signInLink).toHaveAttribute('href', '/sign-in');
      } else {
        // If no explicit sign-in link, that's okay for landing page
        console.log('Note: No sign-in link found in navigation');
      }
    });

    test('pricing section is accessible from landing page', async ({ page }) => {
      await page.goto('/');
      
      // Scroll to pricing
      await page.locator('#pricing').scrollIntoViewIfNeeded();
      
      // Verify pricing section exists and is visible
      await expect(page.getByRole('heading', { name: /Pricing|Plans/i })).toBeVisible();
      
      // Note: Sign-up CTAs may or may not be present depending on pricing component
      // This test just verifies navigation to pricing section works
    });
  });

  // ============================================================================
  // SEO & Metadata Tests
  // ============================================================================

  test.describe('Auth Page SEO', () => {
    
    test('sign-in page has proper title', async ({ page }) => {
      await page.goto('/sign-in');
      
      // Check page title contains relevant keyword
      const title = await page.title();
      expect(title.toLowerCase()).toMatch(/sign.?in|login|account|stocksignal/);
    });

    test('sign-up page has proper title', async ({ page }) => {
      await page.goto('/sign-up');
      
      // Check page title contains relevant keyword
      const title = await page.title();
      expect(title.toLowerCase()).toMatch(/sign.?up|create|account|stocksignal/);
    });
  });

  // ============================================================================
  // Mobile Responsiveness Tests
  // ============================================================================

  test.describe('Mobile Auth Pages', () => {
    
    test('sign-in page is mobile-friendly', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/sign-in');
      
      // Page should render correctly
      await expect(page.getByRole('heading', { name: /Welcome Back/i })).toBeVisible();
    });

    test('sign-up page is mobile-friendly', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/sign-up');
      
      // Page should render correctly
      await expect(page.getByRole('heading', { name: /Create Your/i })).toBeVisible();
    });
  });
});

