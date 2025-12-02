'use client';

import Link from 'next/link';
import { ButtonHTMLAttributes, AnchorHTMLAttributes } from 'react';
import { trackEvent } from '@/lib/analytics/plausible';

// ============================================================================
// Types
// ============================================================================

type ButtonVariant = 'primary' | 'secondary' | 'outline';

interface BaseProps {
  /** Button style variant */
  variant?: ButtonVariant;
  /** Analytics label for tracking (e.g., "Hero CTA - Get Started") */
  label: string;
  /** Page location for analytics (e.g., "homepage", "pricing", "report") */
  location: string;
  /** Button content */
  children: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Loading state */
  isLoading?: boolean;
}

interface LinkButtonProps extends BaseProps {
  /** Next.js Link href */
  href: string;
  /** Custom click handler (runs before navigation) */
  onClick?: () => void;
  /** Open in new tab */
  external?: boolean;
}

interface ActionButtonProps extends BaseProps, Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'children' | 'onClick'> {
  /** No href = regular button */
  href?: never;
  /** Custom click handler */
  onClick?: () => void;
}

type TrackableButtonProps = LinkButtonProps | ActionButtonProps;

// ============================================================================
// Variant Styles
// ============================================================================

const VARIANT_STYLES: Record<ButtonVariant, string> = {
  primary: `
    bg-gradient-to-r from-[#0d9488] to-[#0369a1]
    text-white 
    hover:shadow-lg hover:-translate-y-0.5 
    active:translate-y-0
    border-2 border-transparent
  `,
  secondary: `
    bg-white 
    text-primary 
    border-2 border-primary 
    hover:bg-primary/5
  `,
  outline: `
    bg-transparent 
    text-slate-700 
    border-2 border-slate-300 
    hover:border-primary hover:text-primary hover:bg-primary/5
  `,
};

const BASE_STYLES = `
  inline-flex items-center justify-center gap-2
  px-6 py-3 
  font-semibold rounded-lg 
  transition-all duration-200
  focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:translate-y-0
`;

// ============================================================================
// TrackableButton Component
// ============================================================================

export default function TrackableButton(props: TrackableButtonProps) {
  const {
    variant = 'primary',
    label,
    location,
    children,
    className = '',
    isLoading = false,
    onClick: customOnClick,
    ...restProps
  } = props;

  // ============================================================================
  // Analytics Tracking
  // ============================================================================

  const handleClick = (e: React.MouseEvent) => {
    // Track CTA click with metadata
    trackEvent('CTA_Clicked', {
      variant,
      label,
      location,
    });

    // Run custom onClick handler if provided
    if (customOnClick) {
      customOnClick();
    }

    // For action buttons, prevent default if disabled or loading
    if (!props.href) {
      const actionProps = restProps as Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'children' | 'onClick'>;
      if (actionProps.disabled || isLoading) {
        e.preventDefault();
      }
    }
  };

  // ============================================================================
  // Style Computation
  // ============================================================================

  const variantClasses = VARIANT_STYLES[variant];
  const combinedClassName = `${BASE_STYLES} ${variantClasses} ${className}`.trim();

  // ============================================================================
  // Loading Spinner
  // ============================================================================

  const LoadingSpinner = () => (
    <svg
      className="animate-spin h-5 w-5"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );

  // ============================================================================
  // Render Link Button
  // ============================================================================

  if (props.href) {
    const { href, external } = props as LinkButtonProps;

    // External link
    if (external || href.startsWith('http')) {
      return (
        <a
          href={href}
          className={combinedClassName}
          onClick={handleClick}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={label}
        >
          {isLoading && <LoadingSpinner />}
          {children}
        </a>
      );
    }

    // Internal Next.js Link
    return (
      <Link
        href={href}
        className={combinedClassName}
        onClick={handleClick}
        aria-label={label}
      >
        {isLoading && <LoadingSpinner />}
        {children}
      </Link>
    );
  }

  // ============================================================================
  // Render Action Button
  // ============================================================================

  const actionProps = restProps as Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'children' | 'onClick'>;
  
  return (
    <button
      {...actionProps}
      className={combinedClassName}
      onClick={handleClick}
      disabled={actionProps.disabled || isLoading}
      aria-label={label}
    >
      {isLoading && <LoadingSpinner />}
      {children}
    </button>
  );
}

