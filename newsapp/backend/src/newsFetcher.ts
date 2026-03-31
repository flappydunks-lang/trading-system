/**
 * News ingestion module.
 *
 * This module fetches articles from external APIs/RSS feeds, normalizes them,
 * and stores them in the database with auto-assigned topics.
 *
 * To swap news sources later, implement a new fetcher function that returns
 * NormalizedArticle[] and plug it in below.
 */

import Parser from "rss-parser";
import prisma from "./db";
import { v4 as uuidv4 } from "uuid";

interface NormalizedArticle {
  externalId: string;
  title: string;
  summary: string;
  sourceName: string;
  sourceUrl: string;
  imageUrl?: string;
  publishedAt: Date;
}

// ─── Keyword → Topic mapping ────────────────────────────────────────
// Each key is a topic slug, and the array contains keywords to match
// (case-insensitive) against article title and summary.
const TOPIC_KEYWORDS: Record<string, string[]> = {
  markets: [
    "stocks",
    "market",
    "inflation",
    "fed",
    "investors",
    "economy",
    "wall street",
    "nasdaq",
    "s&p",
    "dow jones",
    "trading",
    "bonds",
    "crypto",
    "bitcoin",
    "earnings",
    "recession",
    "gdp",
    "interest rate",
  ],
  tech: [
    "ai",
    "startup",
    "tech",
    "software",
    "chip",
    "google",
    "apple",
    "microsoft",
    "amazon",
    "meta",
    "openai",
    "semiconductor",
    "robot",
    "data",
    "cyber",
    "app",
    "silicon valley",
    "cloud",
  ],
  us: [
    "biden",
    "trump",
    "congress",
    "supreme court",
    "us",
    "senate",
    "house",
    "republican",
    "democrat",
    "white house",
    "pentagon",
    "fbi",
    "election",
    "governor",
    "federal",
  ],
  world: [
    "russia",
    "ukraine",
    "china",
    "eu",
    "middle east",
    "nato",
    "united nations",
    "africa",
    "asia",
    "europe",
    "japan",
    "india",
    "brazil",
    "uk",
    "france",
    "germany",
    "iran",
    "israel",
    "gaza",
  ],
  sports: [
    "nba",
    "nfl",
    "soccer",
    "world cup",
    "mlb",
    "nhl",
    "tennis",
    "olympics",
    "football",
    "basketball",
    "baseball",
    "golf",
    "championship",
    "playoff",
    "league",
    "coach",
    "midfielder",
  ],
  science: [
    "nasa",
    "space",
    "climate",
    "research",
    "study",
    "discovery",
    "physics",
    "biology",
    "medicine",
    "vaccine",
    "health",
    "disease",
    "cancer",
    "gene",
    "environment",
  ],
};

/**
 * Assign topic slugs to an article based on keyword matching.
 */
function assignTopics(title: string, summary: string): string[] {
  const text = `${title} ${summary}`.toLowerCase();
  const matched: string[] = [];

  for (const [slug, keywords] of Object.entries(TOPIC_KEYWORDS)) {
    for (const keyword of keywords) {
      if (text.includes(keyword.toLowerCase())) {
        matched.push(slug);
        break; // One keyword match is enough per topic
      }
    }
  }

  return matched.length > 0 ? matched : ["general"]; // Fallback to "general"
}

// ─── RSS Feed Fetcher ────────────────────────────────────────────────
// Using public RSS feeds as the default data source. Replace with NewsAPI
// or any other source by implementing a similar function.

const RSS_FEEDS = [
  { url: "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", source: "NY Times" },
  { url: "https://feeds.bbci.co.uk/news/rss.xml", source: "BBC News" },
  { url: "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best", source: "Reuters" },
  { url: "https://feeds.npr.org/1001/rss.xml", source: "NPR" },
  { url: "https://rss.cnn.com/rss/cnn_topstories.rss", source: "CNN" },
  { url: "https://feeds.washingtonpost.com/rss/world", source: "Washington Post" },
];

const parser = new Parser();

async function fetchFromRSS(): Promise<NormalizedArticle[]> {
  const articles: NormalizedArticle[] = [];

  for (const feed of RSS_FEEDS) {
    try {
      const parsed = await parser.parseURL(feed.url);
      for (const item of parsed.items.slice(0, 15)) {
        // Limit per feed
        if (!item.title || !item.link) continue;

        // Create a deterministic external ID from the link
        const externalId = Buffer.from(item.link).toString("base64").slice(0, 100);

        // Extract image from content or media
        let imageUrl: string | undefined;
        const mediaContent = (item as any)["media:content"];
        if (mediaContent?.$.url) {
          imageUrl = mediaContent.$.url;
        }
        // Also check enclosure
        if (!imageUrl && item.enclosure?.url) {
          imageUrl = item.enclosure.url;
        }

        articles.push({
          externalId,
          title: item.title,
          summary: (item.contentSnippet || item.content || item.title || "").slice(0, 300),
          sourceName: feed.source,
          sourceUrl: item.link,
          imageUrl,
          publishedAt: item.pubDate ? new Date(item.pubDate) : new Date(),
        });
      }
    } catch (err) {
      console.error(`Failed to fetch RSS from ${feed.source}:`, err);
      // Continue with other feeds
    }
  }

  return articles;
}

// ─── NewsAPI Fetcher (use if you have an API key) ─────────────────────
// Sign up at https://newsapi.org to get a free API key.
// Set NEWS_API_KEY in your .env file to enable this fetcher.

async function fetchFromNewsAPI(): Promise<NormalizedArticle[]> {
  const apiKey = process.env.NEWS_API_KEY;
  if (!apiKey) return [];

  try {
    const response = await fetch(
      `https://newsapi.org/v2/top-headlines?country=us&pageSize=50&apiKey=${encodeURIComponent(apiKey)}`
    );
    const data: any = await response.json();

    if (data.status !== "ok") {
      console.error("NewsAPI error:", data.message);
      return [];
    }

    return data.articles.map((a: any) => ({
      externalId: Buffer.from(a.url).toString("base64").slice(0, 100),
      title: a.title || "Untitled",
      summary: (a.description || a.title || "").slice(0, 300),
      sourceName: a.source?.name || "Unknown",
      sourceUrl: a.url,
      imageUrl: a.urlToImage || undefined,
      publishedAt: a.publishedAt ? new Date(a.publishedAt) : new Date(),
    }));
  } catch (err) {
    console.error("NewsAPI fetch error:", err);
    return [];
  }
}

// ─── Main Ingestion Function ─────────────────────────────────────────

export async function ingestNews(): Promise<{ created: number; skipped: number }> {
  console.log("Starting news ingestion...");

  // Try NewsAPI first (if key is set), fall back to RSS
  let articles = await fetchFromNewsAPI();
  if (articles.length === 0) {
    articles = await fetchFromRSS();
  }

  console.log(`Fetched ${articles.length} articles from external sources`);

  // Get all topics from DB for mapping
  const topics = await prisma.topic.findMany();
  const topicBySlug = new Map(topics.map((t) => [t.slug, t.id]));

  let created = 0;
  let skipped = 0;

  for (const article of articles) {
    // Skip if we already have this article
    const existing = await prisma.article.findUnique({
      where: { externalId: article.externalId },
    });
    if (existing) {
      skipped++;
      continue;
    }

    // Assign topics
    const matchedSlugs = assignTopics(article.title, article.summary);
    const topicConnections = matchedSlugs
      .map((slug) => topicBySlug.get(slug))
      .filter((id): id is string => !!id)
      .map((topicId) => ({ topicId }));

    try {
      await prisma.article.create({
        data: {
          externalId: article.externalId,
          title: article.title,
          summary: article.summary,
          sourceName: article.sourceName,
          sourceUrl: article.sourceUrl,
          imageUrl: article.imageUrl || null,
          publishedAt: article.publishedAt,
          topics: { create: topicConnections },
        },
      });
      created++;
    } catch (err) {
      console.error(`Failed to create article "${article.title}":`, err);
      skipped++;
    }
  }

  console.log(`Ingestion complete: ${created} created, ${skipped} skipped`);
  return { created, skipped };
}
