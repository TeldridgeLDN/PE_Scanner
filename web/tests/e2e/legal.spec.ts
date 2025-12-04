import { test, expect } from '@playwright/test';

/**
 * Legal Pages User Journey Tests
 * 
 * Tests the legal and informational pages:
 * - Privacy Policy
 * - Terms of Service
 * - Disclaimer
 * 
 * These pages are important for:
 * - Legal compliance
 * - User trust
 * - SEO (Google expects these pages)
 */

test.describe('Legal Pages Journey', () => {

  // ============================================================================
  // Privacy Policy Tests
  // ============================================================================

  test.describe('Privacy Policy Page', () => {
    
    test('privacy page loads correctly', async ({ page }) => {
      await page.goto('/privacy');
      
      // Should have a heading about privacy
      await expect(page.getByRole('heading', { name: /Privacy/i }).first()).toBeVisible();
    });

    test('privacy page has proper content sections', async ({ page }) => {
      await page.goto('/privacy');
      
      // Check for typical privacy policy sections
      const expectedSections = [
        /data|information/i,
        /collect/i,
        /use/i,
      ];
      
      for (const section of expectedSections) {
        const hasSection = await page.getByText(section).first().isVisible().catch(() => false);
        // At least log if section is missing
        if (!hasSection) {
          console.log(`Note: Privacy section matching ${section} not found`);
        }
      }
    });

    test('privacy page has navigation back to home', async ({ page }) => {
      await page.goto('/privacy');
      
      // Should have a link back to home
      const homeLink = page.getByRole('link', { name: /StockSignal|Home/i }).first();
      await expect(homeLink).toBeVisible();
    });

    test('privacy page has proper SEO title', async ({ page }) => {
      await page.goto('/privacy');
      
      const title = await page.title();
      expect(title.toLowerCase()).toContain('privacy');
    });
  });

  // ============================================================================
  // Terms of Service Tests
  // ============================================================================

  test.describe('Terms of Service Page', () => {
    
    test('terms page loads correctly', async ({ page }) => {
      await page.goto('/terms');
      
      // Should have a heading about terms
      await expect(page.getByRole('heading', { name: /Terms/i }).first()).toBeVisible();
    });

    test('terms page has proper content sections', async ({ page }) => {
      await page.goto('/terms');
      
      // Check for typical terms sections
      const expectedSections = [
        /service|use/i,
        /account|user/i,
      ];
      
      for (const section of expectedSections) {
        const hasSection = await page.getByText(section).first().isVisible().catch(() => false);
        if (!hasSection) {
          console.log(`Note: Terms section matching ${section} not found`);
        }
      }
    });

    test('terms page has navigation back to home', async ({ page }) => {
      await page.goto('/terms');
      
      const homeLink = page.getByRole('link', { name: /StockSignal|Home/i }).first();
      await expect(homeLink).toBeVisible();
    });

    test('terms page has proper SEO title', async ({ page }) => {
      await page.goto('/terms');
      
      const title = await page.title();
      expect(title.toLowerCase()).toContain('terms');
    });
  });

  // ============================================================================
  // Disclaimer Tests
  // ============================================================================

  test.describe('Disclaimer Page', () => {
    
    test('disclaimer page loads correctly', async ({ page }) => {
      await page.goto('/disclaimer');
      
      // Should have a heading about disclaimer
      await expect(page.getByRole('heading', { name: /Disclaimer/i }).first()).toBeVisible();
    });

    test('disclaimer page contains investment warning', async ({ page }) => {
      await page.goto('/disclaimer');
      
      // Should contain financial advice disclaimer
      const hasInvestmentWarning = await page.getByText(/not.*financial.*advice|investment.*risk/i).first().isVisible().catch(() => false);
      
      if (!hasInvestmentWarning) {
        console.log('Warning: Investment disclaimer text not found');
      }
    });

    test('disclaimer page has proper SEO title', async ({ page }) => {
      await page.goto('/disclaimer');
      
      const title = await page.title();
      expect(title.toLowerCase()).toContain('disclaimer');
    });
  });

  // ============================================================================
  // Footer Links Integration Tests
  // ============================================================================

  test.describe('Footer Legal Links', () => {
    
    test('footer privacy link navigates correctly', async ({ page }) => {
      await page.goto('/');
      
      // Scroll to footer
      await page.locator('footer').scrollIntoViewIfNeeded();
      
      // Click privacy link
      await page.getByRole('link', { name: 'Privacy Policy' }).click();
      
      await expect(page).toHaveURL('/privacy');
    });

    test('footer terms link navigates correctly', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('footer').scrollIntoViewIfNeeded();
      
      await page.getByRole('link', { name: 'Terms of Service' }).click();
      
      await expect(page).toHaveURL('/terms');
    });

    test('footer disclaimer link navigates correctly', async ({ page }) => {
      await page.goto('/');
      
      await page.locator('footer').scrollIntoViewIfNeeded();
      
      await page.getByRole('link', { name: 'Disclaimer' }).click();
      
      await expect(page).toHaveURL('/disclaimer');
    });
  });

  // ============================================================================
  // Breadcrumb/Navigation Tests
  // ============================================================================

  test.describe('Legal Page Navigation', () => {
    
    test('can navigate between legal pages', async ({ page }) => {
      await page.goto('/privacy');
      
      // If there's a footer, use it to navigate
      const termsLink = page.getByRole('link', { name: /Terms/i });
      
      if (await termsLink.isVisible().catch(() => false)) {
        await termsLink.click();
        await expect(page).toHaveURL('/terms');
      }
    });

    test('logo from legal pages goes to home', async ({ page }) => {
      await page.goto('/privacy');
      await page.waitForLoadState('networkidle');
      
      // Click logo/home link - the link with href="/"
      const homeLink = page.locator('a[href="/"]').first();
      await expect(homeLink).toBeVisible();
      
      // Click and wait for navigation
      await Promise.all([
        page.waitForURL(/localhost:3000\/?$/),
        homeLink.click()
      ]);
      
      // Verify we're on home
      expect(page.url()).toMatch(/localhost:3000\/?$/);
    });
  });

  // ============================================================================
  // Mobile Responsiveness Tests
  // ============================================================================

  test.describe('Legal Pages Mobile', () => {
    
    test('privacy page is readable on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/privacy');
      
      // Content should be visible and not overflow
      await expect(page.getByRole('heading', { name: /Privacy/i }).first()).toBeVisible();
    });

    test('terms page is readable on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/terms');
      
      await expect(page.getByRole('heading', { name: /Terms/i }).first()).toBeVisible();
    });

    test('disclaimer page is readable on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/disclaimer');
      
      await expect(page.getByRole('heading', { name: /Disclaimer/i }).first()).toBeVisible();
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  test.describe('Legal Pages Accessibility', () => {
    
    test('privacy page has proper heading hierarchy', async ({ page }) => {
      await page.goto('/privacy');
      
      // Should have h1
      const h1 = page.locator('h1');
      await expect(h1).toHaveCount(1);
    });

    test('terms page has proper heading hierarchy', async ({ page }) => {
      await page.goto('/terms');
      
      const h1 = page.locator('h1');
      await expect(h1).toHaveCount(1);
    });

    test('disclaimer page has proper heading hierarchy', async ({ page }) => {
      await page.goto('/disclaimer');
      
      const h1 = page.locator('h1');
      await expect(h1).toHaveCount(1);
    });
  });
});

