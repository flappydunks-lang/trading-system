import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getTopics, updateTopics, type Topic } from "../api";
import { useAuth } from "../context/AuthContext";

export default function OnboardingPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const { updateUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    getTopics().then(setTopics);
  }, []);

  function toggleTopic(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleContinue() {
    if (selected.size === 0) return;
    setLoading(true);
    try {
      const res = await updateTopics([...selected]);
      updateUser({ selectedTopics: res.selectedTopics });
      navigate("/");
    } catch (err) {
      console.error("Failed to save topics:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-dvh bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-white text-center mb-2">
          What interests you?
        </h1>
        <p className="text-gray-400 text-center mb-8">
          Select topics to personalize your feed. You can change these later.
        </p>

        <div className="flex flex-wrap gap-3 justify-center mb-8">
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
          onClick={handleContinue}
          disabled={selected.size === 0 || loading}
          className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition"
        >
          {loading
            ? "Saving..."
            : `Continue (${selected.size} selected)`}
        </button>

        <button
          onClick={() => navigate("/")}
          className="w-full py-3 mt-3 text-gray-500 hover:text-gray-300 text-sm transition"
        >
          Skip for now
        </button>
      </div>
    </div>
  );
}
