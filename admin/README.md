# Myestro Admin Panel

**AI-powered English Learning Platform Admin Panel**

Built with:
- Next.js 14 + TypeScript
- Tailwind CSS + shadcn/ui components
- TanStack React Query
- React Hook Form + Zod validation
- Recharts for data visualization
- Sonner for notifications

## Features

- ✅ **Dashboard** - Stats cards, activity chart, CEFR distribution
- ✅ **User Management** - List, search, edit, delete users
- ✅ **Direct Messaging** - Send messages to users via Telegram
- ✅ **Responsive Design** - Mobile, tablet, desktop layouts
- ✅ **Orange Theme** - Custom color scheme
- ✅ **Dark Sidebar** - Professional UI

## Local Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

```bash
# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local

# Edit .env.local with your API URL
nano .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Login

- Email: `admin@example.com`
- Password: `password`

## Build

```bash
npm run build
npm start
```

## Docker

### Build Image

```bash
docker build -t myestro-admin .
```

### Run Container

```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://myestroeco-backend-production.up.railway.app \
  myestro-admin
```

### Docker Compose

From project root:

```bash
docker compose up --build admin
```

Admin panel will be available at `http://localhost:3002`

## API Integration

The admin panel connects to the backend API at:
- Local: `https://myestroeco-backend-production.up.railway.app`
- Docker: `http://backend:8000`

Required endpoints:
- `POST /auth/login`
- `GET /stats`
- `GET /stats/activity?days=7`
- `GET /stats/cefr`
- `GET /users?skip=0&limit=50`
- `PUT /users/{id}`
- `DELETE /users/{id}`
- `POST /admin/send-message`

## Project Structure

```
admin/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Redirect to login
│   ├── login/             # Login page
│   ├── dashboard/         # Dashboard page & layout
│   └── users/             # Users page & layout
├── components/            # Reusable components
│   ├── ui/                # Base UI components
│   ├── layout/            # Layout components
│   ├── dashboard/         # Dashboard components
│   ├── users/             # Users components
│   └── common/            # Common components
├── context/               # React Context
├── hooks/                 # Custom hooks
├── lib/                   # Utilities
│   ├── api.ts            # Axios instance
│   ├── types.ts          # TypeScript types
│   ├── validations.ts    # Zod schemas
│   └── utils.ts          # Helper functions
├── providers/             # Providers
├── tailwind.config.ts     # Tailwind config
├── next.config.js         # Next.js config
└── package.json
```

## License

Copyright © 2025 Myestro
