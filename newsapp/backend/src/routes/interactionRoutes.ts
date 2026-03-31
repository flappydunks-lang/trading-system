import { Router, Response } from "express";
import prisma from "../db";
import { authMiddleware, AuthRequest } from "../auth";

const router = Router();

// POST /api/interactions - record a user interaction
router.post("/", authMiddleware, async (req: AuthRequest, res: Response) => {
  try {
    const { articleId, type, durationMs } = req.body;

    if (!articleId || !type) {
      res.status(400).json({ error: "articleId and type are required" });
      return;
    }

    const validTypes = ["VIEW", "LIKE", "SAVE", "DISMISS"];
    if (!validTypes.includes(type)) {
      res
        .status(400)
        .json({ error: `type must be one of: ${validTypes.join(", ")}` });
      return;
    }

    // For LIKE/SAVE, toggle: if already exists, remove it
    if (type === "LIKE" || type === "SAVE") {
      const existing = await prisma.userInteraction.findFirst({
        where: { userId: req.userId!, articleId, type },
      });
      if (existing) {
        await prisma.userInteraction.delete({ where: { id: existing.id } });
        res.json({ action: "removed", type });
        return;
      }
    }

    // For VIEW, don't duplicate if recently recorded (within 30 seconds)
    if (type === "VIEW") {
      const recentView = await prisma.userInteraction.findFirst({
        where: {
          userId: req.userId!,
          articleId,
          type: "VIEW",
          createdAt: { gte: new Date(Date.now() - 30000) },
        },
      });
      if (recentView) {
        res.json({ action: "already_viewed" });
        return;
      }
    }

    const interaction = await prisma.userInteraction.create({
      data: {
        userId: req.userId!,
        articleId,
        type,
        durationMs: durationMs ? parseInt(durationMs) : null,
      },
    });

    res.status(201).json({ action: "created", interaction });
  } catch (err) {
    console.error("Interaction error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /api/interactions/saved - get user's saved articles
router.get(
  "/saved",
  authMiddleware,
  async (req: AuthRequest, res: Response) => {
    try {
      const saved = await prisma.userInteraction.findMany({
        where: { userId: req.userId!, type: "SAVE" },
        include: {
          article: {
            include: { topics: { include: { topic: true } } },
          },
        },
        orderBy: { createdAt: "desc" },
      });

      res.json(
        saved.map((s) => ({
          ...s.article,
          topics: s.article.topics.map((at) => at.topic),
          savedAt: s.createdAt,
        }))
      );
    } catch (err) {
      console.error("Saved articles error:", err);
      res.status(500).json({ error: "Internal server error" });
    }
  }
);

export default router;
