import { MetadataRoute } from 'next';

/**
 * Dynamic sitemap for StockSignal
 * Next.js automatically serves this at /sitemap.xml
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://stocksignal.app';

  // Static pages
  const staticPages = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly' as const,
      priority: 1.0,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: new Date('2024-12-02'),
      changeFrequency: 'monthly' as const,
      priority: 0.3,
    },
    {
      url: `${baseUrl}/terms`,
      lastModified: new Date('2024-12-02'),
      changeFrequency: 'monthly' as const,
      priority: 0.3,
    },
    {
      url: `${baseUrl}/disclaimer`,
      lastModified: new Date('2024-12-02'),
      changeFrequency: 'monthly' as const,
      priority: 0.3,
    },
  ];

  // In future, can add dynamic stock report pages here
  // by fetching popular tickers from the API

  return staticPages;
}


