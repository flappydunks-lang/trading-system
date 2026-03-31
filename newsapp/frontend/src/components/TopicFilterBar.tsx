import { type Topic } from "../api";

interface Props {
  topics: Topic[];
  activeTopic: string | null;
  onSelect: (slug: string | null) => void;
}

export default function TopicFilterBar({
  topics,
  activeTopic,
  onSelect,
}: Props) {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-md border-b border-white/10">
      <div className="max-w-lg mx-auto px-4 py-3">
        <div className="flex gap-2 overflow-x-auto no-scrollbar">
          <button
            onClick={() => onSelect(null)}
            className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
              activeTopic === null
                ? "bg-indigo-600 text-white"
                : "bg-white/10 text-white/70 hover:bg-white/20"
            }`}
          >
            For You
          </button>
          {topics.map((topic) => (
            <button
              key={topic.id}
              onClick={() =>
                onSelect(activeTopic === topic.slug ? null : topic.slug)
              }
              className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                activeTopic === topic.slug
                  ? "bg-indigo-600 text-white"
                  : "bg-white/10 text-white/70 hover:bg-white/20"
              }`}
            >
              {topic.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
