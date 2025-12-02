# MangaRec Frontend

A Next.js 16 frontend application for the MangaRec manga and novel recommendation system with Thai/English bilingual support.

## Features

- **Next.js 16 App Router**: Modern React Server Components architecture
- **Bilingual Support**: Thai and English language switching (i18n)
- **Firebase Authentication**: Google Sign-in integration
- **Responsive Design**: Mobile-first with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **SEO Optimized**: Static generation for public pages

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── admin/             # Admin dashboard
│   ├── book/[id]/         # Book detail page (dynamic)
│   ├── favorites/         # User favorites
│   ├── login/             # Authentication
│   ├── search/            # Search with filters
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── providers.tsx      # Context providers
├── components/            # Reusable components
│   ├── books/             # Book-related components
│   ├── common/            # Shared components
│   └── layout/            # Layout components
├── contexts/              # React Context providers
│   ├── AuthContext.tsx    # Authentication state
│   └── I18nContext.tsx    # Language/translation
├── hooks/                 # Custom React hooks
│   └── useBooks.ts        # Book data fetching
├── lib/                   # Utilities and config
│   ├── api.ts             # API client (axios)
│   ├── firebase.ts        # Firebase config
│   ├── i18n.ts            # Translations
│   └── types.ts           # TypeScript types
└── public/                # Static assets
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (Python FastAPI)

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
```

### Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Building

```bash
# Create production build
npm run build

# Run production server
npm start
```

### Linting

```bash
npm run lint
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home page with popular and recent books |
| `/search` | Search with filters (type, status, tags, rating) |
| `/book/[id]` | Book detail with reviews and recommendations |
| `/login` | Google Sign-in |
| `/favorites` | User's book lists (reading, completed, etc.) |
| `/admin` | Admin dashboard (books, authors, publishers, reviews) |

## API Integration

The frontend communicates with the Python FastAPI backend at `NEXT_PUBLIC_API_URL`. All authenticated requests include a JWT token in the Authorization header.

## Internationalization

The app supports Thai (default) and English. Language preference is stored in localStorage and can be toggled from the header.

```typescript
// Using translations
import { useI18n } from '@/contexts/I18nContext';

const { t, language, toggleLanguage } = useI18n();
<h1>{t('home.welcome')}</h1>
```

## Authentication

Firebase Auth with Google provider. After Firebase authentication, the frontend exchanges the Firebase token for a JWT from the backend.

```typescript
import { useAuth } from '@/contexts/AuthContext';

const { user, isAuthenticated, loginWithGoogle, logout } = useAuth();
```

## Deploy on Vercel

The easiest way to deploy is using [Vercel](https://vercel.com):

1. Push your code to GitHub
2. Import the repository in Vercel
3. Set environment variables
4. Deploy

For other platforms, see [Next.js deployment docs](https://nextjs.org/docs/app/building-your-application/deploying).
