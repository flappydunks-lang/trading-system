import { Router, Response } from "express";
import { authMiddleware, AuthRequest } from "../auth";
import { rankFeed } from "../ranking";

const router = Router();

// GET /api/feed - get ranked article feed
router.get("/", authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const page = Math.max(1, parseInt(req.query.page as string) || 1);
    const pageSize = Math.min(
      50,
      Math.max(1, parseInt(req.query.pageSize as string) || 10)
    );
    const topicSlug = (req.query.topic as string) || undefined;

    const result = await rankFeed(req.userId!, { page, pageSize, topicSlug });

    res.json({
      articles: result.articles,
      page,
      pageSize,
      total: result.total,
      hasMore: page * pageSize < result.total,
    });
  } catch (err) {
    console.error("Feed error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
