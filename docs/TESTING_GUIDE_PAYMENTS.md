# Payment Integration Testing Guide

## Overview

This guide provides step-by-step instructions for testing the Chapa payment integration in the ALX Travel Application.

## Prerequisites

- Django project running locally
- Chapa sandbox account (https://developer.chapa.co/)
- Postman or curl for API testing
- Valid Chapa API key

## Testing Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Chapa API credentials verified
- [ ] Payment model created
- [ ] API endpoints working
- [ ] Payment flow tested end-to-end
- [ ] Email notifications working
- [ ] Error handling verified

## Step-by-Step Testing

### 1. Environment Setup

```bash
# Navigate to project directory
cd alx_travel_app_0x02/alx_travel_app_0x02

# Verify .env file has Chapa credentials
cat .env | grep CHAPA

# Expected output:
# CHAPA_SECRET_KEY=CHASECK_TEST_xxxxxxxxxxxxxxxx
# CHAPA_API_URL=https://api.chapa.co/v1
# CHAPA_CALLBACK_URL=http://localhost:8000/api/payments/verify/
```

### 2. Database Setup

```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 3. API Authentication Setup

```bash
# Create a test user and get token
curl -X POST http://localhost:8000/api/token/ \
  -d "username=testuser&password=testpass123"

# Response:
# {
#   "token": "your_api_token_here"
# }

# Save token for subsequent requests
TOKEN="your_api_token_here"
```

### 4. Create Test Data

#### 4.1 Create a Listing

```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beach Resort",
    "description": "Beautiful beachfront property",
    "price_per_night": "1000.00",
    "location": "Addis Ababa",
    "amenities": "WiFi, Pool, Kitchen, AC",
    "is_available": true
  }'

# Response will include listing_id - save it
LISTING_ID="listing-uuid-here"
```

#### 4.2 Create a Booking

```bash
# Calculate dates
CHECK_IN=$(date -u -d "+1 day" +%Y-%m-%d)
CHECK_OUT=$(date -u -d "+5 days" +%Y-%m-%d)

curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"listing_id\": \"$LISTING_ID\",
    \"check_in_date\": \"$CHECK_IN\",
    \"check_out_date\": \"$CHECK_OUT\"
  }"

# Response includes booking_id - save it
BOOKING_ID="booking-uuid-here"
```

### 5. Initiate Payment

```bash
curl -X POST http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response:
# {
#   "success": true,
#   "checkout_url": "https://checkout.chapa.co/...",
#   "payment_id": "payment-uuid-here",
#   "amount": "4000.00",
#   "currency": "ETB"
# }

# Save payment_id and visit checkout_url
PAYMENT_ID="payment-uuid-here"
CHECKOUT_URL="checkout_url_from_response"
```

### 6. Test Sandbox Payment

1. Open the `CHECKOUT_URL` in a browser
2. Select a test payment method
3. Use test card (provided by Chapa):
   - Card Number: 4200 0000 0000 0000
   - Expiry: Any future date
   - CVV: Any 3 digits
4. Complete the payment

### 7. Verify Payment Status

```bash
curl -X POST http://localhost:8000/api/payments/$PAYMENT_ID/verify_status/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response on success:
# {
#   "success": true,
#   "status": "completed",
#   "message": "Payment completed successfully",
#   "amount": "4000.00",
#   "received_amount": "4000.00",
#   "transaction_id": "chapa-txn-id"
# }
```

### 8. Verify Booking Status Updated

```bash
curl -X GET http://localhost:8000/api/bookings/$BOOKING_ID/ \
  -H "Authorization: Token $TOKEN"

# Response should show status: "confirmed"
```

### 9. Check Payment Record

```bash
curl -X GET http://localhost:8000/api/payments/$PAYMENT_ID/ \
  -H "Authorization: Token $TOKEN"

# Response:
# {
#   "payment_id": "uuid",
#   "booking": {...},
#   "amount": "4000.00",
#   "currency": "ETB",
#   "status": "completed",
#   "transaction_id": "chapa-txn-id",
#   "chapa_reference": "tx_ref_from_chapa",
#   "payment_method": "card",
#   "created_at": "2025-10-28T...",
#   "updated_at": "2025-10-28T...",
#   "completed_at": "2025-10-28T..."
# }
```

## Error Testing

### Test Case 1: Missing Chapa Credentials

```bash
# Temporarily remove CHAPA_SECRET_KEY from .env
# Try to initiate payment

curl -X POST http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/ \
  -H "Authorization: Token $TOKEN"

# Expected: 500 error with "Configuration error"
```

### Test Case 2: Invalid Payment Reference

```bash
curl -X GET http://localhost:8000/api/payments/invalid-id/ \
  -H "Authorization: Token $TOKEN"

# Expected: 404 error
```

### Test Case 3: Payment Already Completed

```bash
# Try to initiate payment for already completed payment

curl -X POST http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/ \
  -H "Authorization: Token $TOKEN"

# Expected: 400 error "Cannot initiate payment for completed payment"
```

### Test Case 4: Unauthorized Access

```bash
# Create another user
TOKEN2="another_user_token"

curl -X GET http://localhost:8000/api/payments/$PAYMENT_ID/ \
  -H "Authorization: Token $TOKEN2"

# Expected: 404 or 403 error (user should not have access)
```

## Email Notification Testing

### Console Backend (Default)

Emails are logged to console. Check terminal output:

```
[Email Details]
To: guest@example.com
Subject: Payment Confirmation - Your Travel Booking
Message: (HTML and plain text versions shown)
```

### SMTP Backend Testing

1. Update .env:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

2. Complete payment flow
3. Check email inbox for confirmation

## Django Admin Testing

1. Navigate to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Click "Payments" in the admin panel
4. Verify payment records are displayed
5. Click on a payment to view details
6. Verify all fields are populated correctly

## Database Testing

```bash
# Access Django shell
python manage.py shell

# Query payments
from listings.models import Payment

# Get all payments
Payment.objects.all()

# Get payment by ID
payment = Payment.objects.get(payment_id='your-payment-id')

# Check payment status
print(payment.status)
print(payment.booking.guest.email)
print(payment.amount)

# Filter by status
completed = Payment.objects.filter(status='completed')
print(f"Completed payments: {completed.count()}")

# Check booking relationship
booking = payment.booking
print(f"Booking: {booking.listing.title}")
print(f"Guest: {booking.guest.username}")
```

## Performance Testing

### Test Multiple Concurrent Payments

```python
# test_concurrent_payments.py
import concurrent.futures
import requests

TOKEN = "your_token"
BASE_URL = "http://localhost:8000"
LISTING_ID = "listing-uuid"

def create_booking_and_initiate_payment():
    # Create booking
    booking = requests.post(
        f"{BASE_URL}/api/bookings/",
        headers={"Authorization": f"Token {TOKEN}"},
        json={
            "listing_id": LISTING_ID,
            "check_in_date": "2025-11-01",
            "check_out_date": "2025-11-05"
        }
    ).json()
    
    # Initiate payment
    payment = requests.post(
        f"{BASE_URL}/api/bookings/{booking['booking_id']}/initiate_payment/",
        headers={"Authorization": f"Token {TOKEN}"}
    ).json()
    
    return payment

# Run 10 concurrent payment initiations
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(create_booking_and_initiate_payment, range(10)))
    
    print(f"Successful: {sum(1 for r in results if r.get('success'))}")
    print(f"Failed: {sum(1 for r in results if not r.get('success'))}")
```

## Logging and Debugging

### Enable Detailed Logging

Add to Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'listings': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Check Logs

```bash
# View recent logs
tail -f debug.log | grep -i payment

# Check for errors
tail -f debug.log | grep -i error
```

## Unit Tests

```bash
# Run all tests
python manage.py test listings

# Run specific test
python manage.py test listings.tests_payment.PaymentIntegrationTestCase

# Run with verbosity
python manage.py test listings -v 2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test listings
coverage report
```

## Integration Test Scenario

```
1. Create User Account
   ✓ Register new user
   ✓ Get authentication token

2. Create Property Listing
   ✓ Create listing as host
   ✓ Verify listing appears in listings API

3. Create Booking
   ✓ Book a property as guest
   ✓ Verify booking status is 'pending'
   ✓ Verify payment created automatically

4. Initiate Payment
   ✓ Get checkout URL
   ✓ Verify payment status is still 'pending'

5. Complete Payment (Sandbox)
   ✓ Visit checkout URL
   ✓ Enter test card details
   ✓ Complete payment on Chapa

6. Verify Payment
   ✓ Call verify_status endpoint
   ✓ Verify payment status updated to 'completed'
   ✓ Verify booking status updated to 'confirmed'
   ✓ Verify confirmation email sent

7. Check Records
   ✓ Admin: Payment record shows all details
   ✓ Admin: Booking status is confirmed
   ✓ API: Payment detail shows transaction ID
```

## Troubleshooting

### Issue: "CHAPA_SECRET_KEY not set"

**Solution:**
```bash
# Verify .env file
cat .env | grep CHAPA_SECRET_KEY

# Should show: CHAPA_SECRET_KEY=CHASECK_TEST_xxxxx

# If missing, add it and restart server
```

### Issue: "Payment not found" when verifying

**Solution:**
```bash
# Check if payment exists in database
python manage.py shell
from listings.models import Payment
Payment.objects.filter(payment_id='your-id').exists()

# If not exists, create a test payment
```

### Issue: Emails not sending

**Solution:**
```bash
# Check EMAIL_BACKEND
python manage.py shell
from django.conf import settings
print(settings.EMAIL_BACKEND)

# Should be console for testing
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Success Indicators

- ✓ All HTTP endpoints return 200/201 on successful requests
- ✓ Payment records created in database
- ✓ Payment status transitions correctly
- ✓ Booking status updated on successful payment
- ✓ Emails sent with proper formatting
- ✓ No database errors in logs
- ✓ No API authentication errors
- ✓ Transaction IDs stored correctly

## Next Steps

1. Deploy to staging environment
2. Test with real Chapa API keys (production account)
3. Set up webhook handlers
4. Configure production email service
5. Implement monitoring and alerting
6. Set up automated testing in CI/CD pipeline

