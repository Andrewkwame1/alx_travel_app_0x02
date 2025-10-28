# Quick Start Guide - Payment Integration

## 5-Minute Setup

### Step 1: Environment Configuration (1 minute)

```bash
# Edit .env file
# Add Chapa credentials:
CHAPA_SECRET_KEY=CHASECK_TEST_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHAPA_API_URL=https://api.chapa.co/v1
CHAPA_CALLBACK_URL=http://localhost:8000/api/payments/verify/
```

### Step 2: Database Setup (2 minutes)

```bash
cd alx_travel_app_0x02/alx_travel_app_0x02

# Run migrations
python manage.py migrate
```

### Step 3: Start Server (1 minute)

```bash
python manage.py runserver
```

### Step 4: Test Payment Flow (1 minute)

Use this curl script:

```bash
#!/bin/bash

# 1. Create user and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/token/ \
  -d "username=testuser&password=testpass" | jq -r '.token')

echo "Token: $TOKEN"

# 2. Create listing
LISTING=$(curl -s -X POST http://localhost:8000/api/listings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Place",
    "description": "Test",
    "price_per_night": "500",
    "location": "Addis",
    "amenities": "WiFi"
  }')

LISTING_ID=$(echo $LISTING | jq -r '.listing_id')
echo "Listing: $LISTING_ID"

# 3. Create booking
BOOKING=$(curl -s -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "'$LISTING_ID'",
    "check_in_date": "2025-11-01",
    "check_out_date": "2025-11-05"
  }')

BOOKING_ID=$(echo $BOOKING | jq -r '.booking_id')
echo "Booking: $BOOKING_ID"

# 4. Initiate payment
PAYMENT=$(curl -s -X POST http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/ \
  -H "Authorization: Token $TOKEN")

echo "Payment Response:"
echo $PAYMENT | jq .

# Extract payment ID
PAYMENT_ID=$(echo $PAYMENT | jq -r '.payment_id')
CHECKOUT_URL=$(echo $PAYMENT | jq -r '.checkout_url')

echo ""
echo "==== NEXT STEPS ===="
echo "1. Visit checkout URL:"
echo "$CHECKOUT_URL"
echo ""
echo "2. Complete payment with test card: 4200000000000000"
echo ""
echo "3. Verify payment status:"
echo "curl -X POST http://localhost:8000/api/payments/$PAYMENT_ID/verify_status/ \\"
echo "  -H \"Authorization: Token $TOKEN\""
```

## File Structure

Key files for payment integration:

```
listings/
├── models.py              # Payment model
├── views.py              # PaymentViewSet, payment endpoints
├── serializers.py        # PaymentSerializer
├── chapa_utils.py        # ChapaAPIClient, payment utilities
├── email_tasks.py        # Email notifications
├── admin.py              # Admin interface
└── migrations/
    └── 0002_payment.py   # Payment migration
```

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/bookings/{id}/initiate_payment/` | Start payment |
| POST | `/api/payments/{id}/verify_status/` | Check payment status |
| GET | `/api/payments/` | List payments |
| GET | `/api/payments/{id}/` | Get payment details |
| POST | `/api/payments/verify/` | Webhook callback |

## Testing Checklist

- [ ] Chapa API key configured
- [ ] Can create bookings
- [ ] Can initiate payments
- [ ] Checkout URL generated
- [ ] Can verify payment status
- [ ] Booking status updated on success
- [ ] Email notifications working

## Common Issues

**Issue: "CHAPA_SECRET_KEY not set"**
- Solution: Add to .env and restart server

**Issue: Payment verification fails**
- Solution: Ensure CHAPA_API_URL is correct in .env

**Issue: Emails not sending**
- Solution: Check EMAIL_BACKEND in settings.py

## Next Steps

1. Read `PAYMENT_INTEGRATION.md` for detailed documentation
2. Follow `TESTING_GUIDE_PAYMENTS.md` for comprehensive testing
3. Configure production settings for deployment
4. Set up webhook handlers for real-time updates

## Support

- Chapa API Docs: https://developer.chapa.co/docs
- Django REST Framework: https://www.django-rest-framework.org/
- Project README: See PROJECT_COMPLETION.md

