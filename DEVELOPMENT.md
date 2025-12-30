# Development Guide

## Setting Up Your Development Environment

### Prerequisites
- Node.js 16+ (download from nodejs.org)
- Git (for version control)
- VS Code (recommended editor)
- MongoDB (for local development)
- OpenAI API key (for AI features)

### Quick Start (5 minutes)

#### 1. Clone and Setup
```bash
# Navigate to project
cd /Users/umeshshetty/REPO/rumee

# Install all dependencies
npm install

# This will install packages for root, backend, and frontend
```

#### 2. Configure Environment Variables

**Backend (.env)**
```bash
cd backend
cp .env.example .env
# Edit .env and add:
# - MongoDB connection string (or use localhost:27017)
# - OpenAI API key
# - JWT secret (any random string)
```

**Frontend (.env.local)**
```bash
cd frontend
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env.local
```

#### 3. Start Development Servers
```bash
# From project root
npm run dev

# This starts both backend (port 5000) and frontend (port 3000)
```

Open http://localhost:3000 in your browser!

---

## Project Structure

### Backend (`/backend`)
```
src/
├── models/        # Database schemas (Note, Person, Meeting, etc)
├── services/      # Business logic (AIService, DataLinkingService)
├── controllers/   # Route handlers
├── routes/        # API route definitions
├── middleware/    # Express middleware
├── config/        # Configuration files
├── utils/         # Helper functions
└── index.ts       # Server entry point
```

### Frontend (`/frontend`)
```
src/
├── components/    # React components (to be built)
├── pages/         # Page components
├── services/      # API integration
├── utils/         # Store and utilities
├── styles/        # CSS and styling
├── App.tsx        # Main app component
└── index.tsx      # React entry point
```

---

## Development Workflow

### Creating a New Note Feature

1. **Backend**:
   - Model exists: `src/models/Note.ts` ✓
   - Create controller: `src/controllers/NoteController.ts`
   - Create service: `src/services/NoteService.ts` (optional)
   - Add routes: `src/routes/notes.ts`
   - Update main router in `src/index.ts`

2. **Frontend**:
   - Create API method in `src/services/api.ts`
   - Create component: `src/components/NoteEditor.tsx`
   - Add to store if needed: `src/utils/store.ts`
   - Add page: `src/pages/NotesPage.tsx`
   - Add route in `src/App.tsx`

### Example: Adding Note Creation Endpoint

**1. Create Controller** (`backend/src/controllers/NoteController.ts`):
```typescript
import { Request, Response } from 'express';
import { Note } from '../models/Note';
import AIService from '../services/AIService';
import DataLinkingService from '../services/DataLinkingService';

export const createNote = async (req: Request, res: Response) => {
  try {
    const { title, content, tags } = req.body;
    const userId = req.user._id; // From JWT middleware

    // Create note
    const note = new Note({
      userId,
      title,
      content,
      tags: tags || [],
    });

    await note.save();

    // Auto-link to entities
    await DataLinkingService.linkNoteToEntities(
      userId.toString(),
      note._id.toString(),
      content
    );

    res.json({ success: true, data: note });
  } catch (error) {
    res.status(500).json({ success: false, error });
  }
};
```

**2. Create Routes** (`backend/src/routes/notes.ts`):
```typescript
import { Router } from 'express';
import { createNote } from '../controllers/NoteController';
import { authenticate } from '../middleware/auth';

const router = Router();

router.post('/', authenticate, createNote);

export default router;
```

**3. Frontend Component** (`frontend/src/components/NoteEditor.tsx`):
```typescript
import React, { useState } from 'react';
import { noteService } from '../services/api';

export const NoteEditor: React.FC = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const handleSave = async () => {
    await noteService.createNote({ title, content });
    setTitle('');
    setContent('');
  };

  return (
    <div className="note-editor">
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        placeholder="Write your note..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <button onClick={handleSave}>Save Note</button>
    </div>
  );
};
```

---

## Running Tests

```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test

# Coverage report
npm test -- --coverage
```

---

## Building for Production

```bash
# Build both frontend and backend
npm run build

# This creates:
# - backend/dist/ (compiled JavaScript)
# - frontend/build/ (optimized React bundle)
```

---

## Common Tasks

### Adding a New Database Model

1. Create file in `backend/src/models/`:
```typescript
import mongoose, { Schema, Document } from 'mongoose';

interface IMyModel extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  createdAt: Date;
}

const schema = new Schema<IMyModel>({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  name: { type: String, required: true },
}, { timestamps: true });

export const MyModel = mongoose.model<IMyModel>('MyModel', schema);
```

2. Use in services:
```typescript
import { MyModel } from '../models/MyModel';

const doc = new MyModel({ userId, name: 'test' });
await doc.save();
```

### Adding a New API Endpoint

1. Add method to controller
2. Create route in routes file
3. Import route in main server file
4. Test with curl or Postman
5. Add API method in frontend
6. Create UI component

### Debugging

**Backend**:
```bash
# Run with debugging
node --inspect backend/dist/index.js

# Then open chrome://inspect
```

**Frontend**:
- Use React Developer Tools extension
- Chrome DevTools for debugging
- Zustand DevTools for state inspection

---

## Database Connection

### Local MongoDB
```bash
# Install MongoDB Compass (GUI tool)
# Or run MongoDB locally:
brew install mongodb-community
brew services start mongodb-community

# Connection: mongodb://localhost:27017/rumee
```

### MongoDB Atlas (Cloud)
```
Get connection string from:
https://cloud.mongodb.com/

Format: mongodb+srv://user:password@cluster.mongodb.net/rumee
```

---

## Environment Setup Checklist

- [ ] Node.js installed (`node --version`)
- [ ] MongoDB running locally or Atlas connection ready
- [ ] Backend `.env` configured with:
  - [ ] MONGODB_URI
  - [ ] OPENAI_API_KEY
  - [ ] JWT_SECRET
- [ ] Frontend `.env.local` configured with:
  - [ ] REACT_APP_API_URL
- [ ] Dependencies installed (`npm install`)
- [ ] Servers starting without errors

---

## Troubleshooting

### "Cannot find module" error
```bash
# Clear node_modules and reinstall
rm -rf node_modules backend/node_modules frontend/node_modules
npm install
```

### MongoDB connection error
- Check MongoDB is running
- Verify connection string in .env
- Check credentials for Atlas

### OpenAI API errors
- Verify API key is valid
- Check API quota/billing
- Ensure OPENAI_API_KEY is set in .env

### Port already in use
```bash
# Backend port 5000 in use:
lsof -i :5000
kill -9 <PID>

# Frontend port 3000 in use:
lsof -i :3000
kill -9 <PID>
```

---

## Additional Resources

- [Express.js Docs](https://expressjs.com)
- [React Docs](https://react.dev)
- [MongoDB Docs](https://docs.mongodb.com)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Mongoose Docs](https://mongoosejs.com)

---

## Getting Help

1. Check the ARCHITECTURE.md for design decisions
2. Look at examples in existing services
3. Check error logs in console
4. Review git history for similar implementations
