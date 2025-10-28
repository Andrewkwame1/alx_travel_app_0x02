# API Testing Guide - ALX Travel App

This document provides step-by-step instructions for testing all API endpoints for the ALX Travel App using Postman, cURL, or Python requests.

## Prerequisites

- Django dev server running: `python manage.py runserver`
- Postman installed (optional, but recommended)
- Database migrated: `python manage.py migrate`
- Superuser created: `python manage.py createsuperuser`

## Quick Start - Setup Test Data

### 1. Create Test Users

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create test users
user1 = User.objects.create_user(username='host1', email='host1@test.com', password='pass123')
user2 = User.objects.create_user(username='guest1', email='guest1@test.com', password='pass123')
user3 = User.objects.create_user(username='host2', email='host2@test.com', password='pass123')

# Create authentication tokens
token1 = Token.objects.create(user=user1)
token2 = Token.objects.create(user=user2)
token3 = Token.objects.create(user=user3)

print(f"Host 1 Token: {token1.key}")
print(f"Guest 1 Token: {token2.key}")
print(f"Host 2 Token: {token3.key}")

# Exit shell
exit()
```

### 2. Create Test Listings

```bash
# Save tokens for later use
export HOST1_TOKEN=<token1_key>
export GUEST_TOKEN=<token2_key>
export HOST2_TOKEN=<token3_key>
```

## Testing with Postman

### Setup Postman Collection

1. **Create Collection**: "ALX Travel API"
2. **Add Variables**:
   - `base_url` = `http://localhost:8000`
   - `host_token` = (Token for host1)
   - `guest_token` = (Token for guest1)
   - `listing_id` = (Will be populated during tests)
   - `booking_id` = (Will be populated during tests)
   - `review_id` = (Will be populated during tests)

### Test Scenarios

#### Scenario 1: Create Listings as Host

**Test 1.1 - Create First Listing**

- **Name**: Create Listing (Downtown Apt)
- **Method**: POST
- **URL**: `{{base_url}}/api/listings/`
- **Headers**:
  - `Authorization: Token {{host_token}}`
  - `Content-Type: application/json`
- **Body**:
```json
{
  "title": "Cozy Downtown Apartment",
  "description": "Beautiful 2-bedroom apartment in the heart of downtown with modern amenities",
  "price_per_night": 150.00,
  "location": "New York",
  "amenities": "WiFi, AC, Kitchen, Laundry",
  "is_available": true
}
```

**Expected Response** (201 Created):
```json
{
  "listing_id": "...",
  "title": "Cozy Downtown Apartment",
  "description": "...",
  "price_per_night": "150.00",
  "location": "New York",
  "host": {
    "id": 1,
    "username": "host1",
    "email": "host1@test.com"
  },
  "is_available": true,
  "reviews": [],
  "average_rating": 0,
  "review_count": 0
}
```

**Post-test Action**: Save `listing_id` to Postman variable

---

**Test 1.2 - Create Second Listing**

- **Name**: Create Listing (Beachfront Villa)
- **Method**: POST
- **URL**: `{{base_url}}/api/listings/`
- **Headers**: Same as above
- **Body**:
```json
{
  "title": "Beachfront Villa",
  "description": "Luxury villa with ocean view, private beach access",
  "price_per_night": 250.00,
  "location": "Miami Beach",
  "amenities": "Pool, WiFi, AC, Kitchen, Parking, Beach Access",
  "is_available": true
}
```

**Expected Response** (201 Created)

---

#### Scenario 2: Retrieve Listings

**Test 2.1 - List All Listings (No Auth Required)**

- **Name**: Get All Listings
- **Method**: GET
- **URL**: `{{base_url}}/api/listings/`
- **Headers**: None required

**Expected Response** (200 OK):
- Returns array of all listings
- Should include both listings created above

---

**Test 2.2 - Get Specific Listing**

- **Name**: Get Listing Details
- **Method**: GET
- **URL**: `{{base_url}}/api/listings/{{listing_id}}/`
- **Headers**: None required

**Expected Response** (200 OK):
- Returns single listing with full details

---

**Test 2.3 - Get User's Listings**

- **Name**: Get My Listings
- **Method**: GET
- **URL**: `{{base_url}}/api/listings/my_listings/`
- **Headers**: `Authorization: Token {{host_token}}`

**Expected Response** (200 OK):
- Returns only listings created by the authenticated user

---

#### Scenario 3: Update & Delete Listings

**Test 3.1 - Update Listing (Owner)**

- **Name**: Update Listing
- **Method**: PUT
- **URL**: `{{base_url}}/api/listings/{{listing_id}}/`
- **Headers**: `Authorization: Token {{host_token}}`
- **Body**:
```json
{
  "title": "Cozy Downtown Apartment - Updated",
  "description": "Updated description",
  "price_per_night": 160.00,
  "location": "New York",
  "amenities": "WiFi, AC, Kitchen, Laundry, Gym",
  "is_available": true
}
```

**Expected Response** (200 OK):
- Listing updated successfully

---

**Test 3.2 - Try Update as Non-Owner (Permission Denied)**

- **Name**: Update Listing (Not Owner)
- **Method**: PUT
- **URL**: `{{base_url}}/api/listings/{{listing_id}}/`
- **Headers**: `Authorization: Token {{guest_token}}`
- **Body**: (Same as above)

**Expected Response** (403 Forbidden):
```json
{
  "detail": "You can only update your own listings."
}
```

---

#### Scenario 4: Filter & Search Listings

**Test 4.1 - Filter by Location**

- **Name**: Filter Listings by Location
- **Method**: GET
- **URL**: `{{base_url}}/api/listings/?location=Miami+Beach`

**Expected Response** (200 OK):
- Returns only listings in Miami Beach

---

**Test 4.2 - Filter by Availability**

- **Name**: Filter Available Listings
- **Method**: GET
- **URL**: `{{base_url}}/api/listings/?is_available=true`

**Expected Response** (200 OK):
- Returns only available listings

---

**Test 4.3 - Search by Title**

- **Name**: Search Listings
- **Method**: GET
- **URL**: `{{base_url}}/api/listings/?search=Beachfront`

**Expected Response** (200 OK):
- Returns listings matching search term

---

#### Scenario 5: Create & Manage Bookings

**Test 5.1 - Create Booking**

- **Name**: Create Booking
- **Method**: POST
- **URL**: `{{base_url}}/api/bookings/`
- **Headers**: `Authorization: Token {{guest_token}}`
- **Body**:
```json
{
  "listing_id": "{{listing_id}}",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-05",
  "total_price": 600.00
}
```

**Expected Response** (201 Created)

---

**Test 5.2 - Invalid Dates (Check-out before Check-in)**

- **Name**: Create Booking - Invalid Dates
- **Method**: POST
- **URL**: `{{base_url}}/api/bookings/`
- **Headers**: `Authorization: Token {{guest_token}}`
- **Body**:
```json
{
  "listing_id": "{{listing_id}}",
  "check_in_date": "2025-12-05",
  "check_out_date": "2025-12-01",
  "total_price": 600.00
}
```

**Expected Response** (400 Bad Request):
```json
{
  "non_field_errors": ["Check-out date must be after check-in date."]
}
```

---

**Test 5.3 - Cancel Booking**

- **Name**: Cancel Booking
- **Method**: PATCH
- **URL**: `{{base_url}}/api/bookings/{{booking_id}}/cancel/`
- **Headers**: `Authorization: Token {{guest_token}}`

**Expected Response** (200 OK):
```json
{
  "booking_id": "...",
  "status": "cancelled",
  "..."
}
```

---

#### Scenario 6: Reviews

**Test 6.1 - Create Review**

- **Name**: Create Review
- **Method**: POST
- **URL**: `{{base_url}}/api/reviews/`
- **Headers**: `Authorization: Token {{guest_token}}`
- **Body**:
```json
{
  "listing_id": "{{listing_id}}",
  "rating": 5,
  "comment": "Amazing property! The location is perfect and the host was very responsive."
}
```

**Expected Response** (201 Created)

---

## Testing with cURL / PowerShell

### Create Listing

```powershell
$headers = @{
    "Authorization" = "Token YOUR_HOST_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    title = "Ocean View Apartment"
    description = "Beautiful apartment with ocean view"
    price_per_night = 200.00
    location = "Los Angeles"
    amenities = "WiFi, Parking, Kitchen, Balcony"
    is_available = $true
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/listings/" `
    -Method Post `
    -Headers $headers `
    -Body $body

$response | ConvertFrom-Json
```

### Get All Listings

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/listings/" -Method Get
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Create Booking

```powershell
$headers = @{
    "Authorization" = "Token YOUR_GUEST_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    listing_id = "550e8400-e29b-41d4-a716-446655440000"
    check_in_date = "2025-12-15"
    check_out_date = "2025-12-20"
    total_price = 1000.00
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/bookings/" `
    -Method Post `
    -Headers $headers `
    -Body $body

$response | ConvertFrom-Json
```

## Using Swagger/ReDoc

1. Navigate to `http://localhost:8000/api/swagger/`
2. Click "Authorize" button in top right
3. Enter Token: `Token YOUR_AUTH_TOKEN`
4. Explore all endpoints with auto-generated documentation
5. Try out endpoints directly from the browser

## Common Test Cases Checklist

### Authentication
- [ ] Request without token returns 401 for protected endpoints
- [ ] Request with invalid token returns 401
- [ ] Request with valid token succeeds

### Listing CRUD
- [ ] Create listing as authenticated user
- [ ] Read all listings without authentication
- [ ] Read specific listing
- [ ] Update own listing succeeds
- [ ] Update others' listing returns 403
- [ ] Delete own listing succeeds
- [ ] Delete others' listing returns 403

### Booking CRUD
- [ ] Create booking as guest
- [ ] Cannot create booking without authentication
- [ ] Update own booking
- [ ] Cannot update others' booking
- [ ] Cancel pending/confirmed booking
- [ ] Cannot cancel completed booking
- [ ] Host can confirm pending booking
- [ ] Guest cannot confirm booking

### Filtering & Search
- [ ] Filter listings by location
- [ ] Filter listings by availability
- [ ] Search listings by title
- [ ] Sort listings by price
- [ ] Filter bookings by status

### Reviews
- [ ] Create review (authenticated)
- [ ] Get reviews for listing
- [ ] Update own review
- [ ] Cannot update others' review
- [ ] Delete own review
- [ ] Cannot delete others' review

### Edge Cases
- [ ] Check-out date before check-in date returns error
- [ ] Empty required fields return validation errors
- [ ] Invalid UUIDs return 404
- [ ] Duplicate review (unique constraint) returns error

## Summary

This comprehensive testing guide covers:
- ✅ Authentication and token usage
- ✅ CRUD operations for all models
- ✅ Permission checking
- ✅ Filtering and search
- ✅ Edge cases and error handling
- ✅ Testing tools and methods

All tests should pass with the implemented API endpoints!
