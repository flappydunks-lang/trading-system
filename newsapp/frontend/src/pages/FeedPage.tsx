import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  getFeed,
  getTopics,
  sendInteraction,
  type Article,
  type Topic,
} from "../api";
import { useAuth } from "../context/AuthContext";
import StoryCard from "../components/StoryCard";
import TopicFilterBar from "../components/TopicFilterBar";

export default function FeedPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [activeTopic, setActiveTopic] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const viewedRef = useRef<Set<string>>(new Set());
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Load topics once
  useEffect(() => {
    getTopics().then(setTopics);
  }, []);

  // Load feed articles
  const loadArticles = useCallback(
    async (pageNum: number, reset = false) => {
      setLoading(true);
      try {
        const res = await getFeed(pageNum, 10, activeTopic || undefined);
        setArticles((prev) =>
          reset ? res.articles : [...prev, ...res.articles]
        );
        setHasMore(res.hasMore);
        setPage(pageNum);
      } catch (err) {
        console.error("Feed load error:", err);
      } finally {
        setLoading(false);
      }
    },
    [activeTopic]
  );

  // Reset feed when topic changes
  useEffect(() => {
    setArticles([]);
    setCurrentIndex(0);
    viewedRef.current.clear();
    loadArticles(1, true);
  }, [activeTopic, loadArticles]);

  // Send VIEW interaction when card becomes visible
  useEffect(() => {
    if (articles.length === 0) return;
    const article = articles[currentIndex];
    if (!article || viewedRef.current.has(article.id)) return;
    viewedRef.current.add(article.id);
    sendInteraction(article.id, "VIEW").catch(() => {});
  }, [currentIndex, articles]);

  // Handle scroll snap detection
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    function handleScroll() {
      const scrollTop = container!.scrollTop;
      const height = container!.clientHeight;
      const idx = Math.round(scrollTop / height);
      setCurrentIndex(idx);

      // Load more when near the end
      if (idx >= articles.length - 3 && hasMore && !loading) {
        loadArticles(page + 1);
      }
    }

    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, [articles.length, hasMore, loading, page, loadArticles]);

  function handleInteraction(articleId: string, type: string) {
    setArticles((prev) =>
      prev.map((a) => {
        if (a.id !== articleId) return a;
        if (type === "LIKE") {
          return {
            ...a,
            userLiked: !a.userLiked,
            likeCount: a.userLiked ? a.likeCount - 1 : a.likeCount + 1,
          };
        }
        if (type === "SAVE") {
          return { ...a, userSaved: !a.userSaved };
        }
        if (type === "DISMISS") {
          return a; // Could filter out dismissed articles
        }
        return a;
      })
    );
  }

  return (
    <div className="relative bg-gray-950">
      <TopicFilterBar
        topics={topics}
        activeTopic={activeTopic}
        onSelect={setActiveTopic}
      />

      {/* Profile button */}
      <button
        onClick={() => navigate("/profile")}
        className="fixed top-3 right-4 z-50 w-9 h-9 rounded-full bg-white/15 backdrop-blur-sm text-white flex items-center justify-center text-sm font-bold hover:bg-white/25 transition"
        title="Profile"
      >
        {user?.email?.[0]?.toUpperCase() || "?"}
      </button>

      {/* Feed container */}
      <div
        ref={containerRef}
        className="snap-container no-scrollbar"
      >
        {articles.map((article) => (
          <StoryCard
            key={article.id}
            article={article}
            onInteraction={handleInteraction}
          />
        ))}

        {loading && articles.length === 0 && (
          <div className="snap-item flex items-center justify-center">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-gray-400">Loading your feed...</p>
            </div>
          </div>
        )}

        {!loading && articles.length === 0 && (
          <div className="snap-item flex items-center justify-center">
            <div className="text-center px-6">
              <p className="text-2xl mb-2">📰</p>
              <p className="text-gray-300 font-semibold mb-2">
                No articles yet
              </p>
              <p className="text-gray-500 text-sm">
                Try selecting different topics or check back later.
              </p>
            </div>
          </div>
        )}

        {!hasMore && articles.length > 0 && (
          <div className="snap-item flex items-center justify-center">
            <div className="text-center px-6">
              <p className="text-2xl mb-2">✨</p>
              <p className="text-gray-300 font-semibold">You're all caught up!</p>
              <p className="text-gray-500 text-sm mt-1">
                Check back later for more stories.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
