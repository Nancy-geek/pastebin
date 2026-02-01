#!/bin/bash

echo "🚀 Setting up Pastebin locally..."
echo ""

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL not found. Please install PostgreSQL first."
    exit 1
fi

# Create database
echo "📦 Creating database..."
psql -U postgres -c "CREATE DATABASE pastebin;" 2>/dev/null || echo "Database already exists"

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create .env
cat > .env << EOF
DATABASE_URL=postgresql://postgres@localhost:5432/pastebin
SECRET_KEY=django-insecure-local-dev-key-$(date +%s)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173
TEST_MODE=0
EOF

# Install dependencies
echo "📥 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

# Run migrations
echo "🗄️  Running migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd frontend

# Create .env
cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF

# Install dependencies
echo "📥 Installing Node dependencies..."
npm install --silent

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate  # if using venv"
echo "  python3 manage.py runserver"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:5173"
