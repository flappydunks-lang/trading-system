import { Router, Request, Response } from "express";
import prisma from "../db";

const router = Router();

// GET /api/topics - list all topics
router.get("/", async (_req: Request, res: Response) => {
  try {
    const topics = await prisma.topic.findMany({ orderBy: { name: "asc" } });
    res.json(topics);
  } catch (err) {
    console.error("Topics error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
