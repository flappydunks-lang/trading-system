import "dotenv/config";
import express from "express";
import cors from "cors";
import authRoutes from "./routes/authRoutes";
import topicRoutes from "./routes/topicRoutes";
import feedRoutes from "./routes/feedRoutes";
import interactionRoutes from "./routes/interactionRoutes";
import adminRoutes from "./routes/adminRoutes";

const app = express();
const PORT = parseInt(process.env.PORT || "4000", 10);

app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/topics", topicRoutes);
app.use("/api/feed", feedRoutes);
app.use("/api/interactions", interactionRoutes);
app.use("/api/admin", adminRoutes);

// Health check
app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
