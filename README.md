# Pastebin Application

A **production-grade** pastebin service with time-based expiry and view-count limits, built with **clean architecture** and **SOLID principles**.

## 🎯 Key Highlights

- ✅ **Clean Architecture**: Service layer, repository pattern, dependency injection
- ✅ **SOLID Principles**: Single responsibility, dependency inversion
- ✅ **Highly Testable**: Unit tests with mocked dependencies
- ✅ **Concurrency Safe**: Atomic operations with row-level locking
- ✅ **Production Ready**: Proper error handling, validation, security
- ✅ **Interview Ready**: Well-documented, easy to explain

## Tech Stack

- **Backend**: Python Django + Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: React.js (Vite)
- **Deployment**: Railway or Render

## Features

- Create text pastes with shareable URLs
- Optional time-based expiry (TTL in seconds)
- Optional view-count limits
- Atomic concurrency-safe operations
- Server-rendered HTML views with XSS protection
- RESTful API with proper HTTP status codes

## Architecture

The application follows **clean architecture** with clear separation of concerns:

```
Views (HTTP) → Services (Business Logic) → Repository (Data Access) → Database
```

**Key Components**:
- **Views**: Thin controllers handling HTTP only
- **Services**: Business logic (PasteService, TimeService, AvailabilityService)
- **Repository**: Database abstraction (PasteRepository)
- **Models**: Data structure (Paste model)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed explanation.

## Project Structure

```
pastebin/
├── backend/
│   ├── config/           # Django settings
│   ├── pastes/
│   │   ├── models.py       # Data models
│   │   ├── views.py        # HTTP handlers (thin)
│   │   ├── services.py     # Business logic ⭐
│   │   ├── repositories.py # Data access ⭐
│   │   ├── serializers.py  # Input validation
│   │   ├── tests.py        # Unit tests
│   │   └── urls.py
│   ├── templates/       # HTML templates
│   └── requirements.txt
├── frontend/         # React application
├── ARCHITECTURE.md   # Architecture documentation
├── REFACTORING_SUMMARY.md  # What changed
├── INTERVIEW_GUIDE.md      # Interview prep
└── README.md
```

⭐ = New files added during refactoring

## Backend Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+

### Installation

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file in backend directory
DATABASE_URL=postgresql://user:password@localhost:5432/pastebin
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173
TEST_MODE=0  # Set to 1 for deterministic time testing
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start development server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
# Create .env file in frontend directory
VITE_API_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Documentation

### Health Check
```
GET /api/healthz
Response: 200 OK
{
  "ok": true,
  "database": "connected"
}
```

### Create Paste
```
POST /api/pastes
Content-Type: application/json

{
  "content": "string (required)",
  "ttl_seconds": 60 (optional, integer >= 1),
  "max_views": 5 (optional, integer >= 1)
}

Response: 201 Created
{
  "id": "uuid-string",
  "url": "https://domain.com/p/uuid-string"
}
```

### Fetch Paste (API)
```
GET /api/pastes/:id
Response: 200 OK
{
  "content": "string",
  "remaining_views": 4 (or null if unlimited),
  "expires_at": "ISO8601 timestamp" (or null if no expiry)
}

Response: 404 Not Found (if expired, view limit exceeded, or not found)
{
  "error": "Paste not found or no longer available"
}
```

### View Paste (HTML)
```
GET /p/:id
Response: 200 OK (HTML page with paste content)
Response: 404 Not Found (if expired, view limit exceeded, or not found)
```

## Persistence Layer

The application uses PostgreSQL for persistent storage with the following data model:

**Paste Model**:
- `id`: UUID (primary key)
- `content`: Text field (paste content)
- `created_at`: DateTime (creation timestamp)
- `expires_at`: DateTime (nullable, expiry timestamp)
- `max_views`: Integer (nullable, maximum view count)
- `view_count`: Integer (default 0, current view count)

**Concurrency Safety**:
- View count increments use `select_for_update()` within `transaction.atomic()`
- Constraints are re-checked inside the transaction before serving content
- Prevents race conditions during concurrent access

**Expiry Logic**:
- Paste becomes unavailable when `expires_at` is reached OR `view_count >= max_views`
- Both constraints are checked atomically on every access
- In `TEST_MODE=1`, expiry checks use `x-test-now-ms` header for deterministic testing

## Testing

### Deterministic Time Testing

Set `TEST_MODE=1` in environment variables, then include the `x-test-now-ms` header in requests:

```bash
curl -H "x-test-now-ms: 1700000000000" http://localhost:8000/api/pastes/:id
```

The application will treat the header value as the current time for expiry calculations.

## Deployment

### Backend Deployment (Railway/Render)

1. Set environment variables:
   - `DATABASE_URL` (provided by platform)
   - `SECRET_KEY` (generate secure key)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.com`
   - `FRONTEND_URL=https://your-frontend-domain.com`

2. The application automatically runs migrations on startup

### Frontend Deployment

1. Set build environment variable:
   - `VITE_API_URL=https://your-backend-domain.com`

2. Build command: `npm run build`
3. Output directory: `dist`

## Security Notes

- All HTML rendering uses Django's auto-escaping to prevent XSS
- CORS configured to allow frontend domain only
- No secrets or credentials in repository
- Database credentials via environment variables only
- Content Security Policy headers recommended for production

## License

MIT
