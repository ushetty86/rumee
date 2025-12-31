# Mobile App Architecture

## Overview
The Rumee backend is fully compatible with mobile applications (iOS, Android, React Native, Flutter) via REST API.

## API Compatibility

### REST API Design
- **Stateless**: Each request contains all necessary authentication
- **JSON Format**: All responses in mobile-friendly JSON
- **HTTP Methods**: Standard GET, POST, PUT, DELETE
- **Status Codes**: Proper HTTP status codes for error handling

### Authentication
```typescript
// JWT Token in Authorization header
Authorization: Bearer <jwt-token>

// Token obtained from login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
// Returns: { token: "jwt-token", user: {...} }
```

### Mobile-Optimized Endpoints

#### Pagination
```
GET /api/notes?page=1&limit=20
GET /api/people?page=1&limit=20
```

#### Filtering
```
GET /api/notes?tags=important,work
GET /api/meetings?startDate=2024-01-01&endDate=2024-01-31
```

#### Efficient Data Loading
```
// Get summary with counts (lightweight)
GET /api/dashboard/summary

// Get full data when needed
GET /api/notes
```

## Mobile SDK Examples

### React Native
```typescript
// services/api.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://your-api.com/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const noteService = {
  getNotes: () => apiClient.get('/notes'),
  createNote: (data) => apiClient.post('/notes', data),
  updateNote: (id, data) => apiClient.put(`/notes/${id}`, data),
  deleteNote: (id) => apiClient.delete(`/notes/${id}`),
};
```

### Swift (iOS)
```swift
import Foundation

class APIService {
    let baseURL = "https://your-api.com/api"
    
    func getNotes(completion: @escaping ([Note]) -> Void) {
        guard let token = UserDefaults.standard.string(forKey: "authToken"),
              let url = URL(string: "\(baseURL)/notes") else { return }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data else { return }
            let notes = try? JSONDecoder().decode([Note].self, from: data)
            completion(notes ?? [])
        }.resume()
    }
}
```

### Kotlin (Android)
```kotlin
import retrofit2.http.*

interface RumeeAPI {
    @GET("notes")
    suspend fun getNotes(): List<Note>
    
    @POST("notes")
    suspend fun createNote(@Body note: NoteRequest): Note
    
    @PUT("notes/{id}")
    suspend fun updateNote(@Path("id") id: String, @Body note: NoteRequest): Note
}

// Retrofit setup
val retrofit = Retrofit.Builder()
    .baseUrl("https://your-api.com/api/")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val api = retrofit.create(RumeeAPI::class.java)
```

## Mobile-Specific Features

### Offline Support
```typescript
// Backend supports offline-first
POST /api/notes/sync
{
  "notes": [
    { "id": "local-1", "title": "...", "offline": true },
    { "id": "local-2", "title": "...", "offline": true }
  ]
}
// Returns: { synced: [...], conflicts: [...] }
```

### Push Notifications
```typescript
// Register device token
POST /api/devices/register
{
  "deviceToken": "fcm-token-here",
  "platform": "ios" | "android"
}

// Backend sends notifications for:
// - New reminders due
// - Daily summary ready
// - New connections discovered
```

### Image Upload
```typescript
// Upload images from mobile camera
POST /api/notes/{id}/images
Content-Type: multipart/form-data

{
  image: File
}
```

## Data Sync Strategy

### Pull-to-Refresh
```typescript
GET /api/sync?lastSync=2024-01-01T12:00:00Z
// Returns only items updated since lastSync
```

### Real-time Updates (WebSocket)
```typescript
// Optional WebSocket for real-time sync
ws://your-api.com/ws?token=jwt-token

// Receive events:
{
  "event": "note.created",
  "data": { ... }
}
```

## Performance Optimization

### Image Optimization
- Backend automatically resizes images
- Serves thumbnails for list views
- Full resolution on demand

### Caching Headers
```
Cache-Control: max-age=3600
ETag: "abc123"
```

### Compression
- All responses GZIP compressed
- Reduces mobile data usage

## Security

### HTTPS Only
- All mobile apps must use HTTPS
- Certificate pinning recommended

### Token Refresh
```typescript
POST /api/auth/refresh
{
  "refreshToken": "..."
}
// Returns new access token
```

### Rate Limiting
- Per-user limits protect server
- Mobile apps handle 429 responses

## App Store Deployment

### Backend Requirements
✅ HTTPS with valid SSL
✅ Privacy policy endpoint: `/api/privacy`
✅ Terms of service: `/api/terms`
✅ Account deletion: `DELETE /api/users/me`

## Recommended Mobile Stack

### React Native (Cross-platform)
```json
{
  "dependencies": {
    "react-native": "^0.72.0",
    "axios": "^1.6.0",
    "@react-navigation/native": "^6.1.0",
    "zustand": "^4.4.0",
    "react-query": "^3.39.0"
  }
}
```

### Native
- **iOS**: SwiftUI + Combine
- **Android**: Jetpack Compose + Kotlin Coroutines

## Testing

### API Testing
```bash
# Test from mobile network
curl -H "Authorization: Bearer token" \
  https://your-api.com/api/notes
```

### Load Testing
- Test with multiple concurrent mobile clients
- Monitor response times (target: <200ms)

## Deployment Checklist

- [ ] Backend deployed to cloud (Heroku, AWS, etc.)
- [ ] HTTPS enabled
- [ ] CORS configured for mobile domains
- [ ] Database indexed for mobile queries
- [ ] API documentation published
- [ ] Mobile SDK examples provided
- [ ] Push notification service setup
- [ ] Image CDN configured
- [ ] Rate limiting enabled
- [ ] Monitoring and logging active

## Mobile App Features

All backend features work on mobile:
- ✅ Note creation with voice input
- ✅ People management with camera
- ✅ Meeting scheduling with calendar sync
- ✅ Reminders with notifications
- ✅ Daily summaries
- ✅ Knowledge graph visualization
- ✅ Offline mode
- ✅ Biometric authentication

The REST API is 100% mobile-ready!
