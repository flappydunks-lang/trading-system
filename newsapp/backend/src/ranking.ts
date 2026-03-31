import prisma from "./db";

interface RankedArticle {
  id: string;
  externalId: string;
  title: string;
  summary: string;
  sourceName: string;
  sourceUrl: string;
  imageUrl: string | null;
  videoUrl: string | null;
  publishedAt: Date;
  topics: { id: string; name: string; slug: string }[];
  score: number;
  likeCount: number;
  viewCount: number;
  userLiked: boolean;
  userSaved: boolean;
}

// Weights for the ranking formula - tweak these to change behavior
const W_RECENCY = 0.5;
const W_POPULARITY = 0.3;
const W_TOPIC_MATCH = 0.2;

// How far back to look for articles (in days)
const LOOKBACK_DAYS = 7;

// What percentage of the feed should be "explore" articles from non-selected topics
const EXPLORE_RATIO = 0.15;

/**
 * Rank articles for a user's feed.
 *
 * Score formula: score = W_RECENCY * recencyScore + W_POPULARITY * popularityScore + W_TOPIC_MATCH * topicMatchScore
 *
 * - recencyScore: 1 for newest article, 0 for oldest in the window
 * - popularityScore: normalized like+view count (0..1)
 * - topicMatchScore: 1 if article matches at least one user topic, 0 otherwise
 */
export async function rankFeed(
  userId: string,
  options: { page: number; pageSize: number; topicSlug?: string }
): Promise<{ articles: RankedArticle[]; total: number }> {
  const { page, pageSize, topicSlug } = options;

  // Get user's selected topic IDs
  const userTopics = await prisma.userTopic.findMany({
    where: { userId },
    select: { topicId: true },
  });
  const userTopicIds = new Set(userTopics.map((ut) => ut.topicId));

  // Date boundary
  const since = new Date();
  since.setDate(since.getDate() - LOOKBACK_DAYS);

  // Build article query
  const whereClause: any = { publishedAt: { gte: since } };
  if (topicSlug) {
    whereClause.topics = { some: { topic: { slug: topicSlug } } };
  }

  // Fetch articles with their topics and interaction counts
  const articles = await prisma.article.findMany({
    where: whereClause,
    include: {
      topics: { include: { topic: true } },
      interactions: {
        select: { type: true, userId: true },
      },
    },
    orderBy: { publishedAt: "desc" },
  });

  if (articles.length === 0) {
    return { articles: [], total: 0 };
  }

  // Calculate time range for normalization
  const now = Date.now();
  const oldest = Math.min(...articles.map((a) => a.publishedAt.getTime()));
  const timeRange = now - oldest || 1;

  // Calculate max popularity for normalization
  const popularities = articles.map((a) => {
    const likes = a.interactions.filter((i) => i.type === "LIKE").length;
    const views = a.interactions.filter((i) => i.type === "VIEW").length;
    return likes * 3 + views; // Likes weighted more than views
  });
  const maxPop = Math.max(...popularities, 1);

  // Score each article
  const scored: RankedArticle[] = articles.map((article, idx) => {
    const articleTopicIds = article.topics.map((at) => at.topicId);
    const matchesUserTopic = articleTopicIds.some((id) => userTopicIds.has(id));

    const recencyScore =
      (article.publishedAt.getTime() - oldest) / timeRange;
    const popularityScore = popularities[idx] / maxPop;
    const topicMatchScore = matchesUserTopic ? 1 : 0;

    const score =
      W_RECENCY * recencyScore +
      W_POPULARITY * popularityScore +
      W_TOPIC_MATCH * topicMatchScore;

    const likeCount = article.interactions.filter(
      (i) => i.type === "LIKE"
    ).length;
    const viewCount = article.interactions.filter(
      (i) => i.type === "VIEW"
    ).length;
    const userLiked = article.interactions.some(
      (i) => i.userId === userId && i.type === "LIKE"
    );
    const userSaved = article.interactions.some(
      (i) => i.userId === userId && i.type === "SAVE"
    );

    return {
      id: article.id,
      externalId: article.externalId,
      title: article.title,
      summary: article.summary,
      sourceName: article.sourceName,
      sourceUrl: article.sourceUrl,
      imageUrl: article.imageUrl,
      videoUrl: article.videoUrl,
      publishedAt: article.publishedAt,
      topics: article.topics.map((at) => at.topic),
      score,
      likeCount,
      viewCount,
      userLiked,
      userSaved,
    };
  });

  // If no specific topic filter, apply topic matching with explore ratio
  let filtered: RankedArticle[];
  if (!topicSlug && userTopicIds.size > 0) {
    const matched = scored.filter((a) =>
      a.topics.some((t) => userTopicIds.has(t.id))
    );
    const unmatched = scored.filter(
      (a) => !a.topics.some((t) => userTopicIds.has(t.id))
    );

    // Blend: mostly matched topics, plus some explore articles
    const exploreCount = Math.max(
      1,
      Math.floor(pageSize * EXPLORE_RATIO)
    );
    const matchedSorted = matched.sort((a, b) => b.score - a.score);
    const exploreSorted = unmatched.sort((a, b) => b.score - a.score);

    filtered = [
      ...matchedSorted,
      ...exploreSorted.slice(0, exploreCount * page), // gradually include more explore
    ].sort((a, b) => b.score - a.score);
  } else {
    filtered = scored.sort((a, b) => b.score - a.score);
  }

  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const paged = filtered.slice(start, start + pageSize);

  return { articles: paged, total };
}
