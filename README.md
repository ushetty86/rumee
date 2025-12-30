# Rumee - AI-Powered Assistant

A comprehensive AI-driven assistant application designed to help users manage notes, meetings, people, and reminders with automatic data linking and intelligent summarization.

## Features

### 📝 **Smart Note-Taking**
- Create and organize notes with automatic tagging
- AI-powered entity extraction (people, dates, topics, locations)
- Automatic linking to related notes, people, and meetings
- Full-text search capabilities
- Note embeddings for semantic similarity

### 👥 **People Management**
- Track people you meet and interact with
- Store contact information and meeting history
- Automatic linking to relevant notes and conversations
- Company and role tracking
- Custom tags for organization

### 📅 **Meeting Scheduler**
- Schedule and document meetings
- Automatic action item extraction
- Attendee management with linking to person profiles
- Meeting notes with AI-powered summarization
- Integration with reminders system

### 🔔 **Smart Reminders**
- Task reminders with priority levels
- Meeting preparation reminders
- Follow-up reminders linked to people
- Automatic reminder generation from meeting action items
- Daily digest of upcoming tasks

### 📊 **Daily & Weekly Summaries**
- AI-generated daily summaries of activities
- Weekly reports with key topics and action items
- Aggregated insights from notes, meetings, and tasks
- Email digest support
- Customizable summary preferences

### 🔗 **Automatic Data Linking**
- AI analyzes all content to find connections
- Links notes to people mentioned in them
- Connects meetings to related notes
- Creates reminders from meeting action items
- Semantic similarity matching using embeddings
- One-click access to related information

### 🤖 **AI Engine**
- GPT-3.5/GPT-4 integration for content analysis
- Entity extraction from unstructured text
- Semantic similarity and connection finding
- Automatic summarization
- Action item generation

## Architecture

### Backend
- **Framework**: Express.js with TypeScript
- **Database**: MongoDB
- **AI Integration**: OpenAI API
- **Authentication**: JWT
- **Logging**: Winston

### Frontend
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Data Fetching**: React Query

### Core Services
- **AIService**: LLM integrations for analysis and generation
- **DataLinkingService**: Automatic connection finding
- **SummaryService**: Daily and weekly report generation

## Project Structure

```
rumee/
├── backend/
│   ├── src/
│   │   ├── models/          # MongoDB models
│   │   ├── routes/          # API routes
│   │   ├── controllers/      # Route handlers
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Express middleware
│   │   ├── config/          # Configuration
│   │   ├── utils/           # Utilities
│   │   └── index.ts         # Entry point
│   ├── package.json
│   └── tsconfig.json
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── utils/           # Utilities & stores
│   │   ├── styles/          # Global styles
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── shared/
│   └── types/               # Shared TypeScript types
└── docs/
    └── API.md              # API documentation
```

## Getting Started

### Prerequisites
- Node.js 16+
- MongoDB (local or Atlas)
- OpenAI API key

### Backend Setup

1. Install dependencies:
```bash
cd backend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start development server:
```bash
npm run dev
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## API Endpoints

### Notes
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create note
- `PUT /api/notes/:id` - Update note
- `DELETE /api/notes/:id` - Delete note

### People
- `GET /api/people` - Get all people
- `POST /api/people` - Add person
- `PUT /api/people/:id` - Update person
- `DELETE /api/people/:id` - Delete person

### Meetings
- `GET /api/meetings` - Get all meetings
- `POST /api/meetings` - Create meeting
- `PUT /api/meetings/:id` - Update meeting
- `DELETE /api/meetings/:id` - Delete meeting

### Reminders
- `GET /api/reminders` - Get reminders
- `POST /api/reminders` - Create reminder
- `PUT /api/reminders/:id` - Update reminder
- `DELETE /api/reminders/:id` - Delete reminder

### Summaries
- `GET /api/summaries/daily` - Get daily summary
- `GET /api/summaries/weekly` - Get weekly summary

## Configuration

### Environment Variables

#### Backend (.env)
- `NODE_ENV` - Development/production mode
- `PORT` - Server port (default: 5000)
- `MONGODB_URI` - MongoDB connection string
- `JWT_SECRET` - JWT signing secret
- `OPENAI_API_KEY` - OpenAI API key
- `CORS_ORIGIN` - CORS allowed origin

#### Frontend (.env)
- `REACT_APP_API_URL` - Backend API URL

## Data Linking Algorithm

The app uses a multi-step approach to link data:

1. **Entity Extraction**: AI extracts people, dates, topics, and locations
2. **Direct Matching**: Links to matching person/entity names
3. **Semantic Similarity**: Uses embeddings to find conceptually related items
4. **Scoring**: Connections above 0.6 similarity threshold are linked
5. **Bidirectional Linking**: Links are created in both directions for easy navigation

## Development Workflow

### Adding a New Feature

1. Create models in `backend/src/models/`
2. Create services in `backend/src/services/`
3. Create controllers in `backend/src/controllers/`
4. Add routes in `backend/src/routes/`
5. Create frontend components in `frontend/src/components/`
6. Add API methods in `frontend/src/services/api.ts`
7. Create store state in `frontend/src/utils/store.ts` if needed

### Building

```bash
# Backend
cd backend
npm run build

# Frontend
cd frontend
npm run build
```

## Deployment

### Backend
Deploy to Heroku, AWS, or any Node.js hosting platform
```bash
npm run build
npm start
```

### Frontend
Build static files and deploy to Vercel, Netlify, or similar
```bash
npm run build
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT

## Support

For issues and feature requests, please create an issue on the repository.
