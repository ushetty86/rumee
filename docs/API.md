# Rumee Backend API Documentation

## Overview
This document describes the Rumee backend API endpoints, request/response formats, and integration patterns.

## Base URL
```
http://localhost:5000/api
```

## Authentication
All endpoints (except auth endpoints) require JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Notes API

### List Notes
```
GET /notes
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `tags` (optional): Filter by tags (comma-separated)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "_id": "...",
      "title": "Meeting Notes",
      "content": "...",
      "tags": ["meeting", "important"],
      "linkedEntities": ["..."],
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Note
```
POST /notes
```

**Request Body:**
```json
{
  "title": "My Note",
  "content": "Note content here",
  "tags": ["tag1", "tag2"]
}
```

**Response:** Created note object

### Update Note
```
PUT /notes/:id
```

### Delete Note
```
DELETE /notes/:id
```

## People API

### List People
```
GET /people
```

**Response:** Array of person objects

### Create Person
```
POST /people
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "company": "Acme Corp",
  "tags": ["client", "vip"]
}
```

### Get Person Details
```
GET /people/:id
```

Includes linked notes, meetings, and reminders

### Update Person
```
PUT /people/:id
```

### Delete Person
```
DELETE /people/:id
```

## Meetings API

### List Meetings
```
GET /meetings
```

**Query Parameters:**
- `startDate` (optional): Filter from date
- `endDate` (optional): Filter to date

### Create Meeting
```
POST /meetings
```

**Request Body:**
```json
{
  "title": "Team Sync",
  "description": "Weekly team meeting",
  "attendees": ["personId1", "personId2"],
  "date": "2024-01-15T14:00:00Z",
  "duration": 60,
  "location": "Conference Room A",
  "notes": "Meeting notes"
}
```

### Update Meeting
```
PUT /meetings/:id
```

### Delete Meeting
```
DELETE /meetings/:id
```

## Reminders API

### List Reminders
```
GET /reminders
```

**Query Parameters:**
- `completed` (optional): Filter by completion status

### Create Reminder
```
POST /reminders
```

**Request Body:**
```json
{
  "title": "Follow up with John",
  "description": "Check in on project status",
  "dueDate": "2024-01-10T09:00:00Z",
  "type": "followup",
  "priority": "high",
  "linkedEntity": "personId",
  "linkedEntityType": "Person"
}
```

### Mark Reminder Complete
```
PATCH /reminders/:id/complete
```

### Delete Reminder
```
DELETE /reminders/:id
```

## Summaries API

### Get Daily Summary
```
GET /summaries/daily
```

**Query Parameters:**
- `date` (optional): Specific date (YYYY-MM-DD format)

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": "Today's summary text...",
    "generatedAt": "2024-01-01T00:00:00Z"
  }
}
```

### Get Weekly Summary
```
GET /summaries/weekly
```

**Response:** Similar to daily summary

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

### Common Error Codes
- `INVALID_REQUEST` - Malformed request
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication failed
- `FORBIDDEN` - Insufficient permissions
- `CONFLICT` - Resource conflict
- `INTERNAL_ERROR` - Server error

## Rate Limiting
- 100 requests per minute per user
- Responses include `X-RateLimit-*` headers

## Pagination
List endpoints support pagination:
- Default: 20 items per page
- Max: 100 items per page
- Use `page` and `limit` query parameters

## Sorting
Most list endpoints support sorting:
- Use `sort` query parameter
- Format: `field` or `-field` (for descending)
- Example: `GET /notes?sort=-createdAt`

## Data Linking
When creating notes or meetings, the system automatically:
1. Extracts entities (people, dates, topics)
2. Links to mentioned people
3. Finds semantically similar notes
4. Creates action items from meetings
5. Generates follow-up reminders

## Examples

### Create a note and auto-link
```bash
curl -X POST http://localhost:5000/api/notes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Met with John from Acme",
    "content": "Discussed project timeline and deliverables",
    "tags": ["meeting", "acme"]
  }'
```

The system will:
- Extract "John" and "Acme" as entities
- Link to the person record for John
- Link to any previous notes mentioning Acme
- Auto-create tags

### Create a meeting with attendees
```bash
curl -X POST http://localhost:5000/api/meetings \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Kickoff",
    "attendees": ["userId1", "userId2"],
    "date": "2024-01-15T14:00:00Z",
    "duration": 60,
    "notes": "Discussed scope and timeline. Action items: send proposal by Friday"
  }'
```

The system will:
- Extract action items (send proposal)
- Create reminders for assigned tasks
- Link to related notes and people
