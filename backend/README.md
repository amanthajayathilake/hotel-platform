# Hotel Management System - Backend

FastAPI backend with PostgreSQL database, JWT authentication, and Cloudinary image storage.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database and Cloudinary credentials
```

### 3. Set Up Database
```bash
# Create PostgreSQL database
createdb hotel_db

# Run migrations
alembic upgrade head

# Seed with sample data
python seed_db.py
```

### 4. Run Server
```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## Seeded Credentials

After running `seed_db.py`:
- Admin: `admin` / `admin123`
- Staff: `staff` / `staff123`

## Environment Variables

Required variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
- `CLOUDINARY_API_KEY`: Your Cloudinary API key
- `CLOUDINARY_API_SECRET`: Your Cloudinary API secret

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API route handlers
│   ├── utils/           # Utilities (auth, cloudinary)
│   ├── config.py        # App configuration
│   ├── database.py      # Database setup
│   ├── main.py          # FastAPI application
│   └── schemas.py       # Pydantic schemas
├── requirements.txt     # Python dependencies
└── seed_db.py          # Database seeding
```
