const API_BASE = "/api";

async function request<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }

  return res.json();
}

// ─── Auth ────────────────────────────────────────────────────────────

export interface AuthResponse {
  token: string;
  user: { id: string; email: string; selectedTopics: Topic[] };
}

export function signup(
  email: string,
  password: string,
  selectedTopics: string[] = []
) {
  return request<AuthResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, selectedTopics }),
  });
}

export function login(email: string, password: string) {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getMe() {
  return request<{ id: string; email: string; selectedTopics: Topic[] }>(
    "/auth/me"
  );
}

export function updateTopics(selectedTopics: string[]) {
  return request<{ selectedTopics: Topic[] }>("/auth/topics", {
    method: "PUT",
    body: JSON.stringify({ selectedTopics }),
  });
}

// ─── Topics ──────────────────────────────────────────────────────────

export interface Topic {
  id: string;
  name: string;
  slug: string;
}

export function getTopics() {
  return request<Topic[]>("/topics");
}

// ─── Feed ────────────────────────────────────────────────────────────

export interface Article {
  id: string;
  externalId: string;
  title: string;
  summary: string;
  sourceName: string;
  sourceUrl: string;
  imageUrl: string | null;
  videoUrl: string | null;
  publishedAt: string;
  topics: Topic[];
  score: number;
  likeCount: number;
  viewCount: number;
  userLiked: boolean;
  userSaved: boolean;
}

export interface FeedResponse {
  articles: Article[];
  page: number;
  pageSize: number;
  total: number;
  hasMore: boolean;
}

export function getFeed(page = 1, pageSize = 10, topic?: string) {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
  });
  if (topic) params.set("topic", topic);
  return request<FeedResponse>(`/feed?${params}`);
}

// ─── Interactions ────────────────────────────────────────────────────

export function sendInteraction(
  articleId: string,
  type: "VIEW" | "LIKE" | "SAVE" | "DISMISS",
  durationMs?: number
) {
  return request<{ action: string }>("/interactions", {
    method: "POST",
    body: JSON.stringify({ articleId, type, durationMs }),
  });
}

export function getSavedArticles() {
  return request<(Article & { savedAt: string })[]>("/interactions/saved");
}
