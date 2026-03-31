import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  getTopics,
  updateTopics,
  getSavedArticles,
  type Topic,
  type Article,
} from "../api";
import { useAuth } from "../context/AuthContext";

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [savedArticles, setSavedArticles] = useState<Article[]>([]);
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState<"topics" | "saved">("topics");

  useEffect(() => {
    getTopics().then(setTopics);
    getSavedArticles().then(setSavedArticles);
  }, []);

  useEffect(() => {
    if (user?.selectedTopics) {
      setSelected(new Set(user.selectedTopics.map((t) => t.id)));
    }
  }, [user]);

  function toggleTopic(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSave() {
    setSaving(true);
    try {
      const res = await updateTopics([...selected]);
      updateUser({ selectedTopics: res.selectedTopics });
    } catch (err) {
      console.error("Failed to update topics:", err);
    } finally {
      setSaving(false);
    }
  }

  function timeAgo(dateStr: string): string {
    const seconds = Math.floor(
      (Date.now() - new Date(dateStr).getTime()) / 1000
    );
    if (seconds < 60) return "just now";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  }

  return (
    <div className="min-h-dvh bg-gray-950 text-white">
      {/* Header */}
      <div className="sticky top-0 bg-gray-950/80 backdrop-blur-md border-b border-white/10 px-4 py-4 z-10">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <button
            onClick={() => navigate("/")}
            className="text-gray-400 hover:text-white transition"
          >
            ← Back
          </button>
          <h1 className="text-lg font-bold">Profile</h1>
          <button
            onClick={() => {
              logout();
              navigate("/login");
            }}
            className="text-red-400 hover:text-red-300 text-sm transition"
          >
            Log out
          </button>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 py-6">
        {/* User info */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-2xl font-bold mx-auto mb-3">
            {user?.email?.[0]?.toUpperCase()}
          </div>
          <p className="text-gray-400 text-sm">{user?.email}</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-900 rounded-lg p-1 mb-6">
          <button
            onClick={() => setTab("topics")}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition ${
              tab === "topics"
                ? "bg-gray-800 text-white"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            My Topics
          </button>
          <button
            onClick={() => setTab("saved")}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition ${
              tab === "saved"
                ? "bg-gray-800 text-white"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            Saved ({savedArticles.length})
          </button>
        </div>

        {/* Topics tab */}
        {tab === "topics" && (
          <div>
            <p className="text-gray-400 text-sm mb-4">
              Select topics you're interested in to personalize your feed.
            </p>
            <div className="flex flex-wrap gap-3 mb-6">
              {topics.map((topic) => (
                <button
                  key={topic.id}
                  onClick={() => toggleTopic(topic.id)}
                  className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all ${
                    selected.has(topic.id)
                      ? "bg-indigo-600 text-white ring-2 ring-indigo-400"
                      : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                  }`}
                >
                  {topic.name}
                </button>
              ))}
            </div>
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold rounded-lg transition"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        )}

        {/* Saved tab */}
        {tab === "saved" && (
          <div className="space-y-3">
            {savedArticles.length === 0 && (
              <p className="text-gray-500 text-center py-8">
                No saved articles yet. Tap ☆ on an article to save it.
              </p>
            )}
            {savedArticles.map((article) => (
              <a
                key={article.id}
                href={article.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-gray-900 rounded-lg p-4 hover:bg-gray-800 transition"
              >
                <div className="flex gap-3">
                  {article.imageUrl && (
                    <img
                      src={article.imageUrl}
                      alt=""
                      className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                    />
                  )}
                  <div className="min-w-0">
                    <h3 className="text-white font-semibold text-sm leading-snug mb-1 line-clamp-2">
                      {article.title}
                    </h3>
                    <p className="text-gray-500 text-xs">
                      {article.sourceName} · {timeAgo(article.publishedAt)}
                    </p>
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
