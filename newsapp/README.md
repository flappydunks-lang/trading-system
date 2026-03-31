# NewsSwipe — TikTok-Style News App

A mobile-first web app that shows short, swipeable vertical cards summarizing news stories. Users select interests on signup and get a personalized, ranked feed.

## Tech Stack

| Layer    | Technology                         |
| -------- | ---------------------------------- |
| Frontend | React 19 + TypeScript, Vite, Tailwind CSS |
| Backend  | Node.js + TypeScript, Express 5    |
| Database | PostgreSQL + Prisma ORM            |
| Auth     | JWT (bcryptjs for password hashing) |
| News     | RSS feeds (with NewsAPI option)    |

## Project Structure

```
newsapp/
├── backend/
│   ├── prisma/
│   │   ├── schema.prisma      # Database models
│   │   └── seed.ts            # Test data seeder
│   ├── src/
│   │   ├── index.ts           # Express server entry
│   │   ├── db.ts              # Prisma client instance
│   │   ├── auth.ts            # JWT helpers & middleware
│   │   ├── ranking.ts         # Feed ranking algorithm
│   │   ├── newsFetcher.ts     # RSS/NewsAPI ingestion
│   │   └── routes/
│   │       ├── authRoutes.ts
│   │       ├── topicRoutes.ts
│   │       ├── feedRoutes.ts
│   │       ├── interactionRoutes.ts
│   │       └── adminRoutes.ts
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Router setup
│   │   ├── api.ts             # API client
│   │   ├── context/
│   │   │   └── AuthContext.tsx # Auth state management
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── OnboardingPage.tsx
│   │   │   ├── FeedPage.tsx
│   │   │   └── ProfilePage.tsx
│   │   └── components/
│   │       ├── StoryCard.tsx   # Individual news card
│   │       └── TopicFilterBar.tsx
│   └── index.html
└── README.md
```

## Prerequisites

- **Node.js** v18+ (v20 LTS recommended)
- **PostgreSQL** 14+ running locally or remotely

## Getting Started

### 1. Clone and install dependencies

```bash
cd newsapp

# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configure environment variables

Edit `backend/.env`:

```env
# PostgreSQL connection string — update user/password/host as needed
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/newsapp?schema=public"

# JWT secret — change to a secure random string in production
JWT_SECRET="change-me-to-a-secure-random-string"

# (Optional) NewsAPI key — get one free at https://newsapi.org
# Leave empty to use RSS feeds instead
NEWS_API_KEY=""

# Server port
PORT=4000
```

### 3. Create the database

```bash
# Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE newsapp;"
```

### 4. Run migrations and seed

```bash
cd backend

# Push the Prisma schema to the database
npx prisma db push

# Seed with sample topics and articles
npm run db:seed
```

### 5. Start the development servers

In two separate terminals:

```bash
# Terminal 1: Backend (port 4000)
cd backend
npm run dev

# Terminal 2: Frontend (port 5173, proxies /api to backend)
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

### 6. Test login

A test user is created by the seed script:
- **Email:** test@example.com
- **Password:** password123

## API Endpoints

| Method | Endpoint               | Auth | Description                        |
| ------ | ---------------------- | ---- | ---------------------------------- |
| POST   | `/api/auth/signup`     | No   | Create account                     |
| POST   | `/api/auth/login`      | No   | Login, get JWT token               |
| GET    | `/api/auth/me`         | Yes  | Get current user info              |
| PUT    | `/api/auth/topics`     | Yes  | Update selected topics             |
| GET    | `/api/topics`          | No   | List all topics                    |
| GET    | `/api/feed`            | Yes  | Get ranked article feed            |
| POST   | `/api/interactions`    | Yes  | Record VIEW/LIKE/SAVE/DISMISS      |
| GET    | `/api/interactions/saved` | Yes | Get saved articles              |
| POST   | `/api/admin/fetch-news`| No   | Trigger news ingestion             |

### Feed query parameters

- `page` (default: 1)
- `pageSize` (default: 10, max: 50)
- `topic` — filter by topic slug (e.g., `tech`, `markets`)

## Feed Ranking Algorithm

The ranking function lives in `backend/src/ranking.ts`. Each article gets a score:

```
score = 0.5 × recencyScore + 0.3 × popularityScore + 0.2 × topicMatchScore
```

- **recencyScore** (0–1): Newer articles score higher
- **popularityScore** (0–1): Based on like count (3×) + view count, normalized
- **topicMatchScore** (0 or 1): 1 if article matches user's selected topics

The feed also includes ~15% "explore" articles from non-selected topics.

## News Ingestion

Articles are fetched from:
1. **NewsAPI** (if `NEWS_API_KEY` is set in `.env`) — [newsapi.org](https://newsapi.org)
2. **RSS feeds** (fallback) — NY Times, BBC, CNN, NPR, Reuters, Washington Post

Topics are auto-assigned via keyword matching (see `TOPIC_KEYWORDS` map in `newsFetcher.ts`).

To fetch fresh articles:

```bash
# Via API endpoint
curl -X POST http://localhost:4000/api/admin/fetch-news

# Or via npm script
cd backend
npm run fetch-news
```

## Future Extensions

- **Video support**: The `Article` model includes a `videoUrl` field. When set, `StoryCard` renders an HTML5 video player. Hook up a video CDN or generation API to populate it.
- **Push notifications** for breaking news
- **Social sharing** buttons
- **Full-text search** across articles
- **Cron job** for automatic news ingestion (use `node-cron` or a cloud scheduler)
- **Native mobile app** with React Native using the same API
