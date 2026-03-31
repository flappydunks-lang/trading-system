import { Router, Request, Response } from "express";
import bcrypt from "bcryptjs";
import prisma from "../db";
import { signToken, authMiddleware, AuthRequest } from "../auth";

const router = Router();

// POST /api/auth/signup
router.post("/signup", async (req: Request, res: Response) => {
  try {
    const { email, password, selectedTopics } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: "Email and password are required" });
      return;
    }

    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      res.status(409).json({ error: "Email already registered" });
      return;
    }

    const passwordHash = await bcrypt.hash(password, 10);

    const user = await prisma.user.create({
      data: {
        email,
        passwordHash,
        selectedTopics: {
          create: Array.isArray(selectedTopics)
            ? selectedTopics.map((topicId: string) => ({ topicId }))
            : [],
        },
      },
      include: { selectedTopics: { include: { topic: true } } },
    });

    const token = signToken(user.id);
    res.status(201).json({
      token,
      user: {
        id: user.id,
        email: user.email,
        selectedTopics: user.selectedTopics.map((ut) => ut.topic),
      },
    });
  } catch (err) {
    console.error("Signup error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/auth/login
router.post("/login", async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: "Email and password are required" });
      return;
    }

    const user = await prisma.user.findUnique({
      where: { email },
      include: { selectedTopics: { include: { topic: true } } },
    });

    if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
      res.status(401).json({ error: "Invalid email or password" });
      return;
    }

    const token = signToken(user.id);
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        selectedTopics: user.selectedTopics.map((ut) => ut.topic),
      },
    });
  } catch (err) {
    console.error("Login error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /api/auth/me - get current user info
router.get(
  "/me",
  authMiddleware,
  async (req: AuthRequest, res: Response) => {
    try {
      const user = await prisma.user.findUnique({
        where: { id: req.userId },
        include: { selectedTopics: { include: { topic: true } } },
      });
      if (!user) {
        res.status(404).json({ error: "User not found" });
        return;
      }
      res.json({
        id: user.id,
        email: user.email,
        selectedTopics: user.selectedTopics.map((ut) => ut.topic),
      });
    } catch (err) {
      console.error("Me error:", err);
      res.status(500).json({ error: "Internal server error" });
    }
  }
);

// PUT /api/auth/topics - update selected topics
router.put(
  "/topics",
  authMiddleware,
  async (req: AuthRequest, res: Response) => {
    try {
      const { selectedTopics } = req.body;
      if (!Array.isArray(selectedTopics)) {
        res.status(400).json({ error: "selectedTopics must be an array" });
        return;
      }

      // Delete existing selections, then create new ones
      await prisma.userTopic.deleteMany({ where: { userId: req.userId! } });
      await prisma.userTopic.createMany({
        data: selectedTopics.map((topicId: string) => ({
          userId: req.userId!,
          topicId,
        })),
      });

      const user = await prisma.user.findUnique({
        where: { id: req.userId },
        include: { selectedTopics: { include: { topic: true } } },
      });

      res.json({
        selectedTopics: user!.selectedTopics.map((ut) => ut.topic),
      });
    } catch (err) {
      console.error("Update topics error:", err);
      res.status(500).json({ error: "Internal server error" });
    }
  }
);

export default router;
