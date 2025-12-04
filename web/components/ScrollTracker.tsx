'use client';

import { useEffect, useRef, useState } from 'react';
import { trackScrollDepth } from '@/lib/analytics/plausible';

// ============================================================================
// Types
// ============================================================================

type ScrollMilestone = 25 | 50 | 75 | 100;

// ============================================================================
// ScrollTracker Component
// ============================================================================

/**
 * Tracks scroll depth milestones using IntersectionObserver
 * 
 * Fires Plausible events when user scrolls to 25%, 50%, 75%, 100% of page.
 * Each milestone fires only once per session.
 * 
 * Usage: Add to app/layout.tsx to track all pages
 */
export default function ScrollTracker() {
  const [firedMilestones, setFiredMilestones] = useState<Set<ScrollMilestone>>(new Set());
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // Load fired milestones from sessionStorage
    const stored = sessionStorage.getItem('scroll-depth-fired');
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ScrollMilestone[];
        setFiredMilestones(new Set(parsed));
      } catch (err) {
        console.error('[ScrollTracker] Failed to parse stored milestones:', err);
      }
    }

    // Create IntersectionObserver
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const milestone = parseInt(entry.target.getAttribute('data-milestone') || '0') as ScrollMilestone;
            
            // Check if already fired
            setFiredMilestones((prev) => {
              if (prev.has(milestone)) {
                return prev; // Already fired
              }

              // Fire event
              trackScrollDepth(milestone);

              // Update state and sessionStorage
              const updated = new Set(prev);
              updated.add(milestone);
              sessionStorage.setItem('scroll-depth-fired', JSON.stringify([...updated]));

              return updated;
            });
          }
        });
      },
      {
        threshold: 0.1, // Trigger when 10% of marker is visible
        rootMargin: '0px',
      }
    );

    // Create marker elements and observe them
    const milestones: ScrollMilestone[] = [25, 50, 75, 100];
    const markers: HTMLDivElement[] = [];

    milestones.forEach((milestone) => {
      const marker = document.createElement('div');
      marker.setAttribute('data-milestone', milestone.toString());
      marker.style.position = 'absolute';
      marker.style.left = '0';
      marker.style.width = '1px';
      marker.style.height = '1px';
      marker.style.pointerEvents = 'none';
      marker.style.opacity = '0';
      
      // Position marker at milestone percentage
      if (milestone === 100) {
        // 100% marker at bottom of page
        marker.style.bottom = '0';
      } else {
        // Other markers at percentage of viewport height
        marker.style.top = `${milestone}vh`;
      }

      document.body.appendChild(marker);
      markers.push(marker);

      if (observerRef.current) {
        observerRef.current.observe(marker);
      }
    });

    // Cleanup
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      markers.forEach((marker) => {
        if (document.body.contains(marker)) {
          document.body.removeChild(marker);
        }
      });
    };
  }, []); // Run once on mount

  // No visual component (tracking only)
  return null;
}


