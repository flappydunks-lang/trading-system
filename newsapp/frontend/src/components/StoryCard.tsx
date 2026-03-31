import { type Article, sendInteraction } from "../api";

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

interface Props {
  article: Article;
  onInteraction: (articleId: string, type: string) => void;
}

export default function StoryCard({ article, onInteraction }: Props) {
  async function handleAction(type: "LIKE" | "SAVE" | "DISMISS") {
    try {
      await sendInteraction(article.id, type);
      onInteraction(article.id, type);
    } catch (err) {
      console.error("Interaction error:", err);
    }
  }

  const hasVideo = !!article.videoUrl;
  const hasImage = !!article.imageUrl;

  return (
    <div className="snap-item relative flex flex-col justify-end bg-gray-950">
      {/* Background image or video */}
      {hasVideo ? (
        <video
          src={article.videoUrl!}
          className="absolute inset-0 w-full h-full object-cover"
          autoPlay
          loop
          muted
          playsInline
        />
      ) : hasImage ? (
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${article.imageUrl})` }}
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900" />
      )}

      {/* Gradient overlay for text readability */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />

      {/* Content */}
      <div className="relative z-10 p-6 pb-8 max-w-lg mx-auto w-full">
        {/* Topic tags */}
        <div className="flex flex-wrap gap-2 mb-3">
          {article.topics.map((topic) => (
            <span
              key={topic.id}
              className="px-2.5 py-0.5 bg-white/15 backdrop-blur-sm rounded-full text-xs text-white/80 font-medium"
            >
              {topic.name}
            </span>
          ))}
        </div>

        {/* Title */}
        <h2 className="text-2xl md:text-3xl font-bold text-white leading-tight mb-3">
          {article.title}
        </h2>

        {/* Summary */}
        <p className="text-gray-300 text-base leading-relaxed mb-4 line-clamp-3">
          {article.summary}
        </p>

        {/* Source and time */}
        <p className="text-gray-400 text-sm mb-5">
          {article.sourceName} · {timeAgo(article.publishedAt)}
        </p>

        {/* Action buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleAction("LIKE")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all ${
              article.userLiked
                ? "bg-red-500 text-white"
                : "bg-white/15 backdrop-blur-sm text-white hover:bg-white/25"
            }`}
          >
            <span>{article.userLiked ? "♥" : "♡"}</span>
            <span>{article.likeCount}</span>
          </button>

          <button
            onClick={() => handleAction("SAVE")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all ${
              article.userSaved
                ? "bg-indigo-500 text-white"
                : "bg-white/15 backdrop-blur-sm text-white hover:bg-white/25"
            }`}
          >
            <span>{article.userSaved ? "★" : "☆"}</span>
            <span>Save</span>
          </button>

          <button
            onClick={() => handleAction("DISMISS")}
            className="px-4 py-2 rounded-full text-sm font-medium bg-white/15 backdrop-blur-sm text-white hover:bg-white/25 transition-all"
          >
            ✕ Hide
          </button>

          <a
            href={article.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-auto px-4 py-2 rounded-full text-sm font-medium bg-white text-gray-900 hover:bg-gray-200 transition-all"
          >
            Read →
          </a>
        </div>
      </div>
    </div>
  );
}
