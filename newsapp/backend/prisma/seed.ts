import "dotenv/config";
import prisma from "../src/db";
import bcrypt from "bcryptjs";

const TOPICS = [
  { name: "Tech", slug: "tech" },
  { name: "Markets", slug: "markets" },
  { name: "US", slug: "us" },
  { name: "World", slug: "world" },
  { name: "Sports", slug: "sports" },
  { name: "Science", slug: "science" },
  { name: "General", slug: "general" },
];

const SAMPLE_ARTICLES = [
  {
    externalId: "seed-1",
    title: "AI Startup Raises $500M to Build Next-Gen Language Models",
    summary:
      "A San Francisco-based AI startup has closed a massive funding round to develop advanced language models that could rival GPT-5. The company plans to hire 200 researchers.",
    sourceName: "TechCrunch",
    sourceUrl: "https://example.com/ai-startup",
    imageUrl: "https://placehold.co/800x600/1a1a2e/e94560?text=AI+Startup",
    publishedAt: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
    topicSlugs: ["tech"],
  },
  {
    externalId: "seed-2",
    title: "S&P 500 Hits Record High as Tech Stocks Rally",
    summary:
      "The S&P 500 reached a new all-time high today, driven by strong earnings from major tech companies. Investors remain optimistic about AI-driven growth.",
    sourceName: "Bloomberg",
    sourceUrl: "https://example.com/sp500-record",
    imageUrl: "https://placehold.co/800x600/0f3460/e94560?text=Markets",
    publishedAt: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
    topicSlugs: ["markets", "tech"],
  },
  {
    externalId: "seed-3",
    title: "Congress Passes Bipartisan Infrastructure Bill",
    summary:
      "After months of negotiations, Congress has passed a $1.2 trillion infrastructure bill that includes funding for roads, bridges, and broadband internet expansion.",
    sourceName: "Reuters",
    sourceUrl: "https://example.com/infrastructure-bill",
    imageUrl: "https://placehold.co/800x600/16213e/0f3460?text=Congress",
    publishedAt: new Date(Date.now() - 1000 * 60 * 120), // 2 hours ago
    topicSlugs: ["us"],
  },
  {
    externalId: "seed-4",
    title: "NBA Playoffs: Lakers Advance After Dominant Game 7 Win",
    summary:
      "The Los Angeles Lakers secured their spot in the conference finals with a commanding Game 7 victory. LeBron James led the team with 38 points and 12 assists.",
    sourceName: "ESPN",
    sourceUrl: "https://example.com/lakers-game7",
    imageUrl: "https://placehold.co/800x600/533483/e94560?text=NBA",
    publishedAt: new Date(Date.now() - 1000 * 60 * 180), // 3 hours ago
    topicSlugs: ["sports"],
  },
  {
    externalId: "seed-5",
    title: "EU Agrees on Landmark Digital Markets Regulation",
    summary:
      "The European Union has reached a deal on sweeping new regulations for big tech companies, requiring major platforms to open up their ecosystems and share data.",
    sourceName: "BBC News",
    sourceUrl: "https://example.com/eu-digital-markets",
    imageUrl: "https://placehold.co/800x600/1a1a2e/e94560?text=EU+Tech",
    publishedAt: new Date(Date.now() - 1000 * 60 * 240), // 4 hours ago
    topicSlugs: ["world", "tech"],
  },
  {
    externalId: "seed-6",
    title: "NASA's James Webb Telescope Captures New Galaxy Formation",
    summary:
      "The James Webb Space Telescope has captured stunning images of a galaxy forming 13 billion years ago, providing unprecedented insights into the early universe.",
    sourceName: "NASA",
    sourceUrl: "https://example.com/jwst-galaxy",
    imageUrl: "https://placehold.co/800x600/0f3460/e94560?text=NASA",
    publishedAt: new Date(Date.now() - 1000 * 60 * 300), // 5 hours ago
    topicSlugs: ["science"],
  },
  {
    externalId: "seed-7",
    title: "Federal Reserve Signals Rate Cut Expected in Coming Months",
    summary:
      "Fed Chair has indicated that the central bank is likely to cut interest rates in the next few months, citing cooling inflation and a softening labor market.",
    sourceName: "CNBC",
    sourceUrl: "https://example.com/fed-rate-cut",
    imageUrl: "https://placehold.co/800x600/16213e/e94560?text=Fed",
    publishedAt: new Date(Date.now() - 1000 * 60 * 360), // 6 hours ago
    topicSlugs: ["markets", "us"],
  },
  {
    externalId: "seed-8",
    title: "Ukraine and Russia Begin Prisoner Exchange Amid Ceasefire Talks",
    summary:
      "Both nations have initiated a large-scale prisoner swap as part of renewed diplomatic efforts. International mediators are cautiously optimistic about progress.",
    sourceName: "Al Jazeera",
    sourceUrl: "https://example.com/ukraine-prisoner-swap",
    imageUrl: "https://placehold.co/800x600/533483/0f3460?text=World",
    publishedAt: new Date(Date.now() - 1000 * 60 * 420), // 7 hours ago
    topicSlugs: ["world"],
  },
  {
    externalId: "seed-9",
    title: "Apple Unveils New MacBook Pro with M5 Chip",
    summary:
      "Apple's latest MacBook Pro features the new M5 chip, promising 40% faster performance and 20-hour battery life. Pre-orders start next week.",
    sourceName: "The Verge",
    sourceUrl: "https://example.com/apple-m5",
    imageUrl: "https://placehold.co/800x600/1a1a2e/0f3460?text=Apple+M5",
    publishedAt: new Date(Date.now() - 1000 * 60 * 480), // 8 hours ago
    topicSlugs: ["tech"],
  },
  {
    externalId: "seed-10",
    title: "World Cup 2026 Venues Announced with Surprising Additions",
    summary:
      "FIFA has announced the final list of host cities for the 2026 World Cup. Several smaller cities made in, surprising fans and officials alike.",
    sourceName: "BBC Sport",
    sourceUrl: "https://example.com/wc2026-venues",
    imageUrl: "https://placehold.co/800x600/0f3460/16213e?text=World+Cup",
    publishedAt: new Date(Date.now() - 1000 * 60 * 540), // 9 hours ago
    topicSlugs: ["sports", "world"],
  },
  {
    externalId: "seed-11",
    title: "New Study Finds Coffee May Reduce Risk of Alzheimer's Disease",
    summary:
      "A comprehensive study of 300,000 participants found that regular coffee consumption is associated with a 30% lower risk of developing Alzheimer's disease.",
    sourceName: "Nature",
    sourceUrl: "https://example.com/coffee-alzheimers",
    imageUrl: "https://placehold.co/800x600/533483/1a1a2e?text=Health",
    publishedAt: new Date(Date.now() - 1000 * 60 * 600), // 10 hours ago
    topicSlugs: ["science"],
  },
  {
    externalId: "seed-12",
    title: "Bitcoin Surges Past $100K as Institutional Investors Pile In",
    summary:
      "Bitcoin has broken through the $100,000 barrier for the first time, fueled by massive inflows from institutional investors and new ETF approvals.",
    sourceName: "CoinDesk",
    sourceUrl: "https://example.com/btc-100k",
    imageUrl: "https://placehold.co/800x600/16213e/533483?text=Bitcoin",
    publishedAt: new Date(Date.now() - 1000 * 60 * 660), // 11 hours ago
    topicSlugs: ["markets", "tech"],
  },
];

async function seed() {
  console.log("Seeding database...");

  // Create topics
  for (const topic of TOPICS) {
    await prisma.topic.upsert({
      where: { slug: topic.slug },
      update: {},
      create: topic,
    });
  }
  console.log(`Created ${TOPICS.length} topics`);

  // Get topic map
  const topics = await prisma.topic.findMany();
  const topicBySlug = new Map(topics.map((t) => [t.slug, t.id]));

  // Create sample articles
  for (const article of SAMPLE_ARTICLES) {
    const { topicSlugs, ...articleData } = article;
    const topicIds = topicSlugs
      .map((slug) => topicBySlug.get(slug))
      .filter((id): id is string => !!id);

    await prisma.article.upsert({
      where: { externalId: article.externalId },
      update: {},
      create: {
        ...articleData,
        topics: {
          create: topicIds.map((topicId) => ({ topicId })),
        },
      },
    });
  }
  console.log(`Created ${SAMPLE_ARTICLES.length} sample articles`);

  // Create a test user
  const passwordHash = await bcrypt.hash("password123", 10);
  const user = await prisma.user.upsert({
    where: { email: "test@example.com" },
    update: {},
    create: {
      email: "test@example.com",
      passwordHash,
      selectedTopics: {
        create: [
          { topicId: topicBySlug.get("tech")! },
          { topicId: topicBySlug.get("markets")! },
          { topicId: topicBySlug.get("science")! },
        ],
      },
    },
  });
  console.log(`Created test user: ${user.email} (password: password123)`);

  console.log("Seed complete!");
}

seed()
  .catch((e) => {
    console.error("Seed error:", e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
