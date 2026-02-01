# Deployment Guide

## Railway Deployment

### Backend

1. Create new project on Railway
2. Add PostgreSQL database
3. Connect GitHub repository
4. Set root directory to `backend`
5. Configure environment variables:
   - `SECRET_KEY` (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.railway.app`
   - `FRONTEND_URL=https://your-frontend-domain.com`
   - `TEST_MODE=0`
6. Railway will automatically detect Django and run migrations

### Frontend

1. Create new project on Railway (or use Vercel/Netlify)
2. Connect GitHub repository
3. Set root directory to `frontend`
4. Set build command: `npm run build`
5. Set output directory: `dist`
6. Configure environment variable:
   - `VITE_API_URL=https://your-backend-domain.railway.app`

## Render Deployment

### Backend

1. Create new Web Service
2. Connect GitHub repository
3. Set root directory to `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn config.wsgi:application`
6. Add PostgreSQL database
7. Configure environment variables (same as Railway)

### Frontend

1. Create new Static Site
2. Connect GitHub repository
3. Set root directory to `frontend`
4. Build command: `npm run build`
5. Publish directory: `dist`
6. Configure environment variable: `VITE_API_URL`

## Local Development

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with backend URL
npm run dev
```

## Testing

Run the test script:
```bash
./test_api.sh
```

Or test manually:
```bash
# Health check
curl http://localhost:8000/api/healthz

# Create paste
curl -X POST http://localhost:8000/api/pastes \
  -H "Content-Type: application/json" \
  -d '{"content": "Test", "ttl_seconds": 60, "max_views": 5}'

# Fetch paste
curl http://localhost:8000/api/pastes/{paste-id}

# View HTML
open http://localhost:8000/p/{paste-id}
```

## Deterministic Time Testing

Set `TEST_MODE=1` in backend `.env`, then:

```bash
# Create paste
PASTE_ID=$(curl -X POST http://localhost:8000/api/pastes \
  -H "Content-Type: application/json" \
  -d '{"content": "Test", "ttl_seconds": 60}' | jq -r '.id')

# Fetch with custom time (before expiry)
curl -H "x-test-now-ms: 1700000000000" \
  http://localhost:8000/api/pastes/$PASTE_ID

# Fetch with custom time (after expiry)
curl -H "x-test-now-ms: 1700000100000" \
  http://localhost:8000/api/pastes/$PASTE_ID
```
