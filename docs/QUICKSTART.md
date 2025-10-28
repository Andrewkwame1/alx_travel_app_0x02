# Quick Start Guide - ALX Travel App API

Get the ALX Travel App API running in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- MySQL server running (or use SQLite for development)
- Git installed

## Step 1: Clone and Navigate

```bash
git clone https://github.com/Andrewkwame1/alx_travel_app_0x01.git
cd alx_travel_app_0x01/alx_travel_app
```

## Step 2: Create Virtual Environment

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r ../requirements.txt
```

## Step 4: Configure Database

### Option A: MySQL (Production)

Create `.env` file:
```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
DB_NAME=alx_travel_app
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### Option B: SQLite (Development - Default)

Skip `.env` creation. Update `alx_travel_app/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Step 5: Run Migrations

```bash
python manage.py migrate
```

## Step 6: Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Step 7: Start Development Server

```bash
python manage.py runserver
```

Server will start at `http://localhost:8000`

## Step 8: Access API Documentation

### Swagger UI
Visit: http://localhost:8000/api/swagger/

### ReDoc
Visit: http://localhost:8000/api/redoc/

### Admin Panel
Visit: http://localhost:8000/admin/

## Step 9: Get Authentication Token

### Option A: Via Django Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.create_user(username='testuser', email='test@test.com', password='testpass123')
token = Token.objects.create(user=user)
print(f"Your token: {token.key}")
exit()
```

### Option B: Via Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Go to Tokens and create a new token for your user

## Step 10: Test API Endpoints

### Using Swagger (Easiest)

1. Go to http://localhost:8000/api/swagger/
2. Click "Authorize" and enter: `Token YOUR_TOKEN_HERE`
3. Try out endpoints!

### Using PowerShell

```powershell
# Get all listings
Invoke-WebRequest -Uri "http://localhost:8000/api/listings/" -Method Get

# Create a listing (requires auth)
$headers = @{
    "Authorization" = "Token YOUR_TOKEN_HERE"
    "Content-Type" = "application/json"
}

$body = @{
    title = "My Listing"
    description = "Beautiful property"
    price_per_night = 100
    location = "New York"
    amenities = "WiFi, Kitchen"
    is_available = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/listings/" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

### Using cURL

```bash
# Get all listings
curl http://localhost:8000/api/listings/

# Create a listing
curl -X POST http://localhost:8000/api/listings/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Listing","description":"Beautiful","price_per_night":100,"location":"NYC","amenities":"WiFi","is_available":true}'
```

## Common Tasks

### Create Test Data

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from listings.models import Listing

# Create users
host = User.objects.create_user(username='host1', password='pass123')
guest = User.objects.create_user(username='guest1', password='pass123')

# Create listing
listing = Listing.objects.create(
    title="Test Apartment",
    description="A test listing",
    price_per_night=150.00,
    location="New York",
    amenities="WiFi, Kitchen, AC",
    host=host
)

print(f"Listing ID: {listing.listing_id}")
exit()
```

### Run Tests

```bash
python manage.py test
```

### Make Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Reset Database

```bash
python manage.py flush
```

## Troubleshooting

### ModuleNotFoundError

**Solution**: Ensure virtual environment is activated

```bash
# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### Database Connection Error

**Solution**: Check `.env` file and MySQL connection

```bash
# Test connection
python manage.py dbshell
```

### Port 8000 Already in Use

```bash
python manage.py runserver 8001
```

### Token Authentication Not Working

1. Ensure header format: `Authorization: Token YOUR_TOKEN`
2. Check token exists: `python manage.py shell` → `Token.objects.all()`

## Project Structure

```
alx_travel_app/
├── alx_travel_app/          # Django project config
│   ├── settings.py          # Configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # Production server
├── listings/                # Main app
│   ├── models.py            # Database models
│   ├── views.py             # API ViewSets
│   ├── serializers.py       # Data serialization
│   ├── urls.py              # App routes
│   └── tests.py             # Tests
├── manage.py                # Django CLI
├── requirements.txt         # Dependencies
└── .env                     # Configuration (create manually)
```

## Next Steps

- Explore full [README.md](README.md) for detailed documentation
- Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing scenarios
- Review [API Documentation](http://localhost:8000/api/swagger/)

## Useful Commands

| Command | Purpose |
|---------|---------|
| `python manage.py shell` | Interactive Python shell with Django |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py check` | Verify project setup |
| `python manage.py makemigrations` | Create migrations |
| `python manage.py migrate` | Apply migrations |
| `python manage.py test` | Run tests |
| `python manage.py runserver` | Start dev server |

## Support

For issues, check the [README.md](README.md) or open an issue on GitHub.

Happy coding! 🚀
