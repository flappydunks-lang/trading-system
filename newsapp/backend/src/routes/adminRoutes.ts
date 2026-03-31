import { Router, Request, Response } from "express";
import { ingestNews } from "../newsFetcher";

const router = Router();

// POST /api/admin/fetch-news - trigger article ingestion
// In production, protect this endpoint or run as a cron job.
router.post("/fetch-news", async (_req: Request, res: Response) => {
  try {
    const result = await ingestNews();
    res.json({
      message: "News ingestion complete",
      ...result,
    });
  } catch (err) {
    console.error("Fetch news error:", err);
    res.status(500).json({ error: "Failed to fetch news" });
  }
});

export default router;
