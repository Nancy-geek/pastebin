# Pastebin-Lite Application

A production-ready pastebin service with time-based expiry and view-count limits, built with clean architecture principles.

## Tech Stack

- **Backend**: Python 3.9+, Django 4.x, Django REST Framework
- **Database**: PostgreSQL 12+
- **Frontend**: React.js (Vite)
- **Deployment**: Railway/Render (Backend), Vercel (Frontend)

## Architecture Overview

The application follows **SOLID principles** and **clean architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│              Presentation Layer                  │
│  (Views - Thin controllers, HTTP handling)       │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Service Layer                       │
│  (Business logic, orchestration)                 │
│  - PasteService                                  │
│  - TimeService                                   │
│  - PasteAvailabilityService                      │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Repository Layer                    │
│  (Data access abstraction)                       │
│  - PasteRepository                               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Data Layer                          │
│  (Django ORM, PostgreSQL)                        │
└─────────────────────────────────────────────────┘
```

### Design Decisions

1. **Service Layer Pattern**: Business logic extracted from views into dedicated service classes
   - `PasteService`: Core paste operations (create, fetch, view)
   - `TimeService`: Handles deterministic time for testing
   - `PasteAvailabilityService`: Encapsulates expiry logic

2. **Repository Pattern**: Database operations abstracted into repository
   - Enables easy testing with mocks
   - Single source of truth for data access
   - Supports future database changes

3. **Dependency Injection**: Services accept dependencies via constructor
   - Highly testable
   - Easy to mock for unit tests
   - Follows Dependency Inversion Principle

4. **Single Responsibility Principle**: Each class has one reason to change
   - Views handle HTTP only
   - Services handle business logic
   - Repository handles data access

5. **Atomic Operations**: View count increments use `select_for_update()` within transactions
   - Prevents race conditions
   - Ensures data consistency

## Project Structure

```
backend/
├── config/              # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pastes/              # Main application
│   ├── models.py        # Data models
│   ├── serializers.py   # Input validation
│   ├── views.py         # HTTP handlers (thin)
│   ├── services.py      # Business logic
│   ├── repositories.py  # Data access
│   ├── urls.py          # URL routing
│   └── tests.py         # Unit tests
├── templates/           # HTML templates
├── manage.py
└── requirements.txt

frontend/
├── src/
│   ├── App.jsx         # Main component
│   └── main.jsx
├── package.json
└── vite.config.js
```

## API Specification

### 1. Health Check
```http
GET /api/healthz
```

**Response**: `200 OK`
```json
{
  "ok": true
}
```

### 2. Create Paste
```http
POST /api/pastes
Content-Type: application/json

{
  "content": "string (required, non-empty)",
  "ttl_seconds": 60 (optional, integer >= 1),
  "max_views": 5 (optional, integer >= 1)
}
```

**Response**: `201 Created`
```json
{
  "id": "uuid-string",
  "url": "https://frontend-domain.com/p/uuid-string"
}
```

**Error**: `400 Bad Request` (invalid input)

### 3. Fetch Paste (API)
```http
GET /api/pastes/:id
```

**Response**: `200 OK`
```json
{
  "content": "string",
  "remaining_views": 4 | null,
  "expires_at": "2024-01-01T00:00:00Z" | null
}
```

**Error**: `404 Not Found` (expired, view limit exceeded, or not found)
```json
{
  "error": "Paste not found or no longer available"
}
```

**Note**: Each successful fetch increments view count atomically.

### 4. View Paste (HTML)
```http
GET /p/:id
```

**Response**: `200 OK` (HTML page with escaped content)  
**Error**: `404 Not Found` (HTML error page)

## Persistence Layer

### Database: PostgreSQL

**Paste Model**:
```python
class Paste(models.Model):
    id = UUIDField(primary_key=True)
    content = TextField()
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField(null=True)  # TTL expiry
    max_views = IntegerField(null=True)    # View limit
    view_count = IntegerField(default=0)   # Current views
```

**Indexes**:
- `expires_at` for efficient expiry queries

**Concurrency Safety**:
- View count updates use `select_for_update()` within `transaction.atomic()`
- Row-level locking prevents race conditions
- Availability checks happen inside transaction

**Expiry Logic**:
- Paste expires when: `current_time >= expires_at` OR `view_count >= max_views`
- Both conditions checked atomically on every access
- Expired pastes return 404

## Local Development Setup

### Backend Setup

1. **Prerequisites**: Python 3.9+, PostgreSQL 12+

2. **Install dependencies**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment** (create `backend/.env`):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/pastebin
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173
TEST_MODE=0
```

4. **Run migrations**:
```bash
python manage.py migrate
```

5. **Start server**:
```bash
python manage.py runserver
```

Backend available at: `http://localhost:8000`

### Frontend Setup

1. **Prerequisites**: Node.js 16+

2. **Install dependencies**:
```bash
cd frontend
npm install
```

3. **Configure environment** (create `frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
```

4. **Start dev server**:
```bash
npm run dev
```

Frontend available at: `http://localhost:5173`

## Testing

### Run Unit Tests
```bash
cd backend
python manage.py test pastes
```

### Deterministic Time Testing

Set `TEST_MODE=1` in environment, then use `x-test-now-ms` header:

```bash
# Create paste with 60s TTL
curl -X POST http://localhost:8000/api/pastes \
  -H "Content-Type: application/json" \
  -d '{"content":"test","ttl_seconds":60}'

# Fetch at T=0 (should work)
curl -H "x-test-now-ms: 1700000000000" \
  http://localhost:8000/api/pastes/{id}

# Fetch at T=61s (should fail - expired)
curl -H "x-test-now-ms: 1700000061000" \
  http://localhost:8000/api/pastes/{id}
```

### Test View Limits
```bash
# Create paste with 2 view limit
curl -X POST http://localhost:8000/api/pastes \
  -H "Content-Type: application/json" \
  -d '{"content":"test","max_views":2}'

# First fetch (remaining_views: 1)
curl http://localhost:8000/api/pastes/{id}

# Second fetch (remaining_views: 0)
curl http://localhost:8000/api/pastes/{id}

# Third fetch (404 - limit exceeded)
curl http://localhost:8000/api/pastes/{id}
```

## Deployment

### Backend (Railway/Render)

**Environment Variables**:
```env
DATABASE_URL=<provided-by-platform>
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=your-backend-domain.com
FRONTEND_URL=https://your-frontend-domain.com
TEST_MODE=0
```

**Build Command**: `pip install -r requirements.txt`  
**Start Command**: `python manage.py migrate && gunicorn config.wsgi`

### Frontend (Vercel)

**Environment Variables**:
```env
VITE_API_URL=https://your-backend-domain.com
```

**Build Command**: `npm run build`  
**Output Directory**: `dist`

## Key Features

✅ **Clean Architecture**: Service layer, repository pattern, dependency injection  
✅ **SOLID Principles**: Single responsibility, dependency inversion  
✅ **Atomic Operations**: Race-condition-free view counting  
✅ **Testable**: Unit tests with mocked dependencies  
✅ **XSS Protection**: Django auto-escaping for HTML views  
✅ **Deterministic Testing**: TEST_MODE for time-based tests  
✅ **RESTful API**: Proper HTTP status codes and JSON responses  
✅ **Type Safety**: Clear interfaces and contracts  

## Security Notes

- All HTML rendering uses Django's auto-escaping (XSS protection)
- CORS configured for frontend domain only
- No credentials in repository
- Database credentials via environment variables
- Content Security Policy recommended for production

## Interview Talking Points

1. **Why Service Layer?**
   - Separates business logic from HTTP concerns
   - Easier to test (no HTTP mocking needed)
   - Reusable across different interfaces (API, CLI, etc.)

2. **Why Repository Pattern?**
   - Abstracts data access
   - Easy to mock for testing
   - Single place to change database queries

3. **Why Dependency Injection?**
   - Testability (inject mocks)
   - Flexibility (swap implementations)
   - Follows SOLID principles

4. **Concurrency Handling**:
   - `select_for_update()` locks row during transaction
   - Prevents race conditions on view count
   - Ensures atomic read-modify-write

5. **Trade-offs**:
   - More files/classes (but better organized)
   - Slight performance overhead (negligible)
   - Easier to maintain and extend

## License

MIT
