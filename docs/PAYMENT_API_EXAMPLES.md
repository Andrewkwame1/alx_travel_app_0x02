# Payment API Examples

This document provides practical examples for testing the Chapa Payment Gateway integration.

## Prerequisites

- Django server running at `http://localhost:8000`
- User authentication token
- Chapa sandbox account and API key

## Environment Setup

### Get Authentication Token

```bash
# Using curl
curl -X POST http://localhost:8000/api/token/ \
  -d "username=yourusername&password=yourpassword"

# Response:
# {"token": "your_token_here"}

# Save for use in examples
export TOKEN="your_token_here"
```

## Payment API Examples

### 1. Create a Booking (Prerequisite)

```bash
# Using curl
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "your-listing-id",
    "check_in_date": "2025-11-01",
    "check_out_date": "2025-11-05"
  }'

# Response:
{
  "booking_id": "booking-uuid",
  "listing": {...},
  "guest": {...},
  "check_in_date": "2025-11-01",
  "check_out_date": "2025-11-05",
  "total_price": "2000.00",
  "status": "pending",
  "created_at": "2025-10-28T10:30:00Z"
}
```

### 2. Initiate Payment

```bash
# Using curl
curl -X POST http://localhost:8000/api/bookings/{booking_id}/initiate_payment/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response:
{
  "success": true,
  "checkout_url": "https://checkout.chapa.co/checkout/payment-url",
  "payment_id": "payment-uuid",
  "amount": "2000.00",
  "currency": "ETB"
}

# Save payment_id and checkout_url
PAYMENT_ID="payment-uuid"
CHECKOUT_URL="https://checkout.chapa.co/checkout/payment-url"
```

### 3. Get Payment Details

```bash
# Using curl
curl -X GET http://localhost:8000/api/payments/{payment_id}/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response:
{
  "payment_id": "payment-uuid",
  "booking": {
    "booking_id": "booking-uuid",
    "listing": {...},
    "guest": {...},
    "total_price": "2000.00",
    "status": "pending"
  },
  "amount": "2000.00",
  "currency": "ETB",
  "status": "pending",
  "transaction_id": null,
  "chapa_reference": "tx_ref_xxxxx",
  "payment_method": null,
  "created_at": "2025-10-28T10:30:00Z",
  "updated_at": "2025-10-28T10:30:00Z",
  "completed_at": null,
  "error_message": null
}
```

### 4. List User's Payments

```bash
# Using curl
curl -X GET http://localhost:8000/api/payments/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response:
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "payment_id": "payment-uuid-1",
      "booking": {...},
      "amount": "2000.00",
      "currency": "ETB",
      "status": "completed",
      "transaction_id": "chapa-txn-123",
      ...
    },
    {
      "payment_id": "payment-uuid-2",
      "booking": {...},
      "amount": "5000.00",
      "currency": "ETB",
      "status": "pending",
      ...
    }
  ]
}
```

### 5. Filter Payments

```bash
# Filter by status
curl -X GET "http://localhost:8000/api/payments/?status=completed" \
  -H "Authorization: Token $TOKEN"

# Filter by currency
curl -X GET "http://localhost:8000/api/payments/?currency=ETB" \
  -H "Authorization: Token $TOKEN"

# Combine filters
curl -X GET "http://localhost:8000/api/payments/?status=completed&currency=ETB" \
  -H "Authorization: Token $TOKEN"

# Sort by creation date
curl -X GET "http://localhost:8000/api/payments/?ordering=-created_at" \
  -H "Authorization: Token $TOKEN"
```

### 6. Verify Payment Status (After Sandbox Payment)

```bash
# IMPORTANT: First complete payment on Chapa using checkout_url
# Then verify the payment status

curl -X POST http://localhost:8000/api/payments/{payment_id}/verify_status/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response on success:
{
  "success": true,
  "status": "completed",
  "message": "Payment completed successfully",
  "amount": "2000.00",
  "received_amount": "2000.00",
  "transaction_id": "chapa-transaction-id"
}

# Response on failure:
{
  "success": false,
  "status": "failed",
  "message": "Payment failed"
}

# Response still pending:
{
  "success": true,
  "status": "pending",
  "message": "Payment is still pending"
}
```

## PowerShell Examples

### 1. Create Booking (PowerShell)

```powershell
$headers = @{
    "Authorization" = "Token $env:TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    listing_id = "your-listing-id"
    check_in_date = "2025-11-01"
    check_out_date = "2025-11-05"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/bookings/" `
    -Method Post `
    -Headers $headers `
    -Body $body

$booking = $response.Content | ConvertFrom-Json
$bookingId = $booking.booking_id
Write-Host "Booking ID: $bookingId"
```

### 2. Initiate Payment (PowerShell)

```powershell
$headers = @{
    "Authorization" = "Token $env:TOKEN"
    "Content-Type" = "application/json"
}

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/bookings/$bookingId/initiate_payment/" `
    -Method Post `
    -Headers $headers

$payment = $response.Content | ConvertFrom-Json
$paymentId = $payment.payment_id
$checkoutUrl = $payment.checkout_url

Write-Host "Payment ID: $paymentId"
Write-Host "Checkout URL: $checkoutUrl"
Write-Host "Open this URL to complete payment"
```

### 3. Verify Payment (PowerShell)

```powershell
$headers = @{
    "Authorization" = "Token $env:TOKEN"
    "Content-Type" = "application/json"
}

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/payments/$paymentId/verify_status/" `
    -Method Post `
    -Headers $headers

$verification = $response.Content | ConvertFrom-Json

if ($verification.success) {
    Write-Host "Payment Status: $($verification.status)"
    Write-Host "Amount: $($verification.amount)"
    Write-Host "Transaction ID: $($verification.transaction_id)"
} else {
    Write-Host "Verification failed: $($verification.message)"
}
```

## Complete Test Sequence (Bash Script)

```bash
#!/bin/bash

# Configuration
API_URL="http://localhost:8000"
TOKEN="your_token_here"
LISTING_ID="your-listing-id"

echo "=== Payment Integration Test ==="
echo ""

# Step 1: Create booking
echo "1. Creating booking..."
BOOKING=$(curl -s -X POST "$API_URL/api/bookings/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "'$LISTING_ID'",
    "check_in_date": "2025-11-01",
    "check_out_date": "2025-11-05"
  }')

BOOKING_ID=$(echo $BOOKING | jq -r '.booking_id')
TOTAL_PRICE=$(echo $BOOKING | jq -r '.total_price')
echo "✓ Booking created: $BOOKING_ID"
echo "  Total price: $TOTAL_PRICE ETB"
echo ""

# Step 2: Initiate payment
echo "2. Initiating payment..."
PAYMENT=$(curl -s -X POST "$API_URL/api/bookings/$BOOKING_ID/initiate_payment/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json")

PAYMENT_ID=$(echo $PAYMENT | jq -r '.payment_id')
CHECKOUT_URL=$(echo $PAYMENT | jq -r '.checkout_url')
SUCCESS=$(echo $PAYMENT | jq -r '.success')

if [ "$SUCCESS" = "true" ]; then
    echo "✓ Payment initiated: $PAYMENT_ID"
    echo "  Checkout URL: $CHECKOUT_URL"
    echo ""
    echo "  📌 NEXT STEPS:"
    echo "  1. Open the checkout URL in a browser"
    echo "  2. Use test card: 4200000000000000"
    echo "  3. Complete payment on Chapa"
    echo "  4. Run verification command:"
    echo ""
    echo "  curl -X POST '$API_URL/api/payments/$PAYMENT_ID/verify_status/' \\"
    echo "    -H \"Authorization: Token $TOKEN\""
    echo ""
else
    echo "✗ Payment initiation failed"
    echo $PAYMENT | jq .
    exit 1
fi

# Step 3: Get payment details
echo "3. Getting payment details..."
PAYMENT_DETAIL=$(curl -s -X GET "$API_URL/api/payments/$PAYMENT_ID/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json")

STATUS=$(echo $PAYMENT_DETAIL | jq -r '.status')
AMOUNT=$(echo $PAYMENT_DETAIL | jq -r '.amount')
echo "✓ Payment details retrieved"
echo "  Status: $STATUS"
echo "  Amount: $AMOUNT ETB"
echo ""

echo "=== Test Complete ==="
echo "Now complete payment and verify with the command shown above."
```

## Complete Test Sequence (PowerShell Script)

```powershell
# Configuration
$ApiUrl = "http://localhost:8000"
$Token = $env:TOKEN
$ListingId = "your-listing-id"

Write-Host "=== Payment Integration Test ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create booking
Write-Host "1. Creating booking..." -ForegroundColor Yellow
$bookingHeaders = @{
    "Authorization" = "Token $Token"
    "Content-Type" = "application/json"
}

$bookingBody = @{
    listing_id = $ListingId
    check_in_date = "2025-11-01"
    check_out_date = "2025-11-05"
} | ConvertTo-Json

$bookingResponse = Invoke-WebRequest -Uri "$ApiUrl/api/bookings/" `
    -Method Post `
    -Headers $bookingHeaders `
    -Body $bookingBody

$booking = $bookingResponse.Content | ConvertFrom-Json
$bookingId = $booking.booking_id
$totalPrice = $booking.total_price

Write-Host "✓ Booking created: $bookingId" -ForegroundColor Green
Write-Host "  Total price: $totalPrice ETB"
Write-Host ""

# Step 2: Initiate payment
Write-Host "2. Initiating payment..." -ForegroundColor Yellow
$paymentResponse = Invoke-WebRequest -Uri "$ApiUrl/api/bookings/$bookingId/initiate_payment/" `
    -Method Post `
    -Headers $bookingHeaders

$payment = $paymentResponse.Content | ConvertFrom-Json
$paymentId = $payment.payment_id
$checkoutUrl = $payment.checkout_url
$success = $payment.success

if ($success) {
    Write-Host "✓ Payment initiated: $paymentId" -ForegroundColor Green
    Write-Host "  Checkout URL: $checkoutUrl"
    Write-Host ""
    Write-Host "  📌 NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Open the checkout URL in a browser"
    Write-Host "  2. Use test card: 4200000000000000"
    Write-Host "  3. Complete payment on Chapa"
    Write-Host "  4. Run verification command:"
    Write-Host ""
    Write-Host "  `$headers = @{ 'Authorization' = 'Token $Token' }"
    Write-Host "  Invoke-WebRequest -Uri '$ApiUrl/api/payments/$paymentId/verify_status/' `\"
    Write-Host "    -Method Post -Headers `$headers"
    Write-Host ""
} else {
    Write-Host "✗ Payment initiation failed" -ForegroundColor Red
    Write-Host ($payment | ConvertTo-Json)
    exit 1
}

# Step 3: Get payment details
Write-Host "3. Getting payment details..." -ForegroundColor Yellow
$detailResponse = Invoke-WebRequest -Uri "$ApiUrl/api/payments/$paymentId/" `
    -Method Get `
    -Headers $bookingHeaders

$paymentDetail = $detailResponse.Content | ConvertFrom-Json
$status = $paymentDetail.status
$amount = $paymentDetail.amount

Write-Host "✓ Payment details retrieved" -ForegroundColor Green
Write-Host "  Status: $status"
Write-Host "  Amount: $amount ETB"
Write-Host ""

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Now complete payment and verify with the command shown above."
```

## Testing Different Scenarios

### Scenario 1: Successful Payment

```bash
# 1. Create booking and initiate payment (as shown above)
# 2. Visit checkout URL and complete payment with test card
# 3. Verify payment

curl -X POST http://localhost:8000/api/payments/$PAYMENT_ID/verify_status/ \
  -H "Authorization: Token $TOKEN"

# Expected response:
# {
#   "success": true,
#   "status": "completed",
#   "message": "Payment completed successfully"
# }
```

### Scenario 2: Pending Payment

```bash
# Before completing payment on Chapa, verify:

curl -X POST http://localhost:8000/api/payments/$PAYMENT_ID/verify_status/ \
  -H "Authorization: Token $TOKEN"

# Expected response:
# {
#   "success": true,
#   "status": "pending",
#   "message": "Payment is still pending"
# }
```

### Scenario 3: Failed Payment

```bash
# Use invalid test card on Chapa
# Then verify:

curl -X POST http://localhost:8000/api/payments/$PAYMENT_ID/verify_status/ \
  -H "Authorization: Token $TOKEN"

# Expected response:
# {
#   "success": false,
#   "status": "failed",
#   "message": "Payment failed"
# }
```

## Error Scenarios

### Missing Authorization

```bash
curl -X GET http://localhost:8000/api/payments/

# Response: 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid Payment ID

```bash
curl -X GET http://localhost:8000/api/payments/invalid-id/ \
  -H "Authorization: Token $TOKEN"

# Response: 404 Not Found
{
  "detail": "Not found."
}
```

### Unauthorized Access

```bash
# User1 tries to access User2's payment

curl -X GET http://localhost:8000/api/payments/$OTHER_USER_PAYMENT_ID/ \
  -H "Authorization: Token $USER1_TOKEN"

# Response: 404 Not Found (or filtered out)
```

### Duplicate Payment Initiation

```bash
# Try to initiate payment for already completed payment

curl -X POST http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/ \
  -H "Authorization: Token $TOKEN"

# Response: 400 Bad Request
{
  "detail": "Cannot initiate payment for completed payment."
}
```

## Tips and Tricks

### 1. Save Payment ID to Variable

```bash
PAYMENT_ID=$(curl -s -X POST "http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/" \
  -H "Authorization: Token $TOKEN" | jq -r '.payment_id')

echo $PAYMENT_ID
```

### 2. Chain Commands

```bash
# Create booking, initiate payment, and open checkout URL in one sequence
BOOKING=$(curl -s -X POST "http://localhost:8000/api/bookings/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"listing_id":"id","check_in_date":"2025-11-01","check_out_date":"2025-11-05"}')

BOOKING_ID=$(echo $BOOKING | jq -r '.booking_id')

PAYMENT=$(curl -s -X POST "http://localhost:8000/api/bookings/$BOOKING_ID/initiate_payment/" \
  -H "Authorization: Token $TOKEN")

CHECKOUT_URL=$(echo $PAYMENT | jq -r '.checkout_url')

# Open in browser (on macOS)
open $CHECKOUT_URL

# On Linux
xdg-open $CHECKOUT_URL

# On Windows
start $CHECKOUT_URL
```

### 3. Format JSON Output Nicely

```bash
curl -s -X GET http://localhost:8000/api/payments/$PAYMENT_ID/ \
  -H "Authorization: Token $TOKEN" | jq . -C
```

## Monitoring

### Check Django Logs

```bash
# Monitor Django console for payment processing
tail -f django.log | grep -i payment
```

### Check Database

```bash
# Connect to Django shell
python manage.py shell

# Check payments
from listings.models import Payment
Payment.objects.all()

# Check specific payment
payment = Payment.objects.get(payment_id='your-id')
print(f"Status: {payment.status}")
print(f"Amount: {payment.amount}")
print(f"Transaction: {payment.transaction_id}")
```

---

**Last Updated:** October 28, 2025  
**Version:** 1.0.0
