# ALX Travel App - Payment Integration Guide

## Overview

This project extends the ALX Travel Application (0x02 version) with Chapa Payment Gateway integration. The implementation allows users to securely book travel properties and make payments through the Chapa payment gateway.

## Features

### Payment Integration
- **Secure Payment Initiation**: Initiate payments through Chapa API
- **Payment Verification**: Verify payment status from Chapa
- **Transaction Tracking**: Full payment transaction history and logging
- **Payment Status Management**: Track payment states (pending, completed, failed, cancelled)
- **Email Notifications**: Automated confirmation emails on successful payments

### Models

#### Payment Model
Tracks all payment transactions with the following fields:
- `payment_id`: UUID (Primary Key)
- `booking`: OneToOne relationship with Booking
- `amount`: Decimal amount to be paid
- `currency`: Currency code (default: ETB)
- `status`: Payment status (pending, completed, failed, cancelled)
- `transaction_id`: Unique Chapa transaction ID
- `chapa_reference`: Chapa tx_ref for verification
- `payment_method`: Payment method used (e.g., card, bank transfer)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- `completed_at`: Timestamp when payment was completed
- `error_message`: Error details if payment failed

### API Endpoints

#### Payment Endpoints

**1. List Payments**
```
GET /api/payments/
```
Returns list of payments the user has access to.

**2. Retrieve Payment Details**
```
GET /api/payments/{payment_id}/
```
Returns detailed information about a specific payment.

**3. Initiate Payment for Booking**
```
POST /api/bookings/{booking_id}/initiate_payment/
```
Initiates payment for a booking through Chapa.

**Request:** Empty body (payment already created)

**Response:**
```json
{
    "success": true,
    "checkout_url": "https://checkout.chapa.co/...",
    "payment_id": "uuid-here",
    "amount": "5000.00",
    "currency": "ETB"
}
```

**4. Verify Payment Status**
```
POST /api/payments/{payment_id}/verify_status/
```
Verifies payment status with Chapa and updates local records.

**Response on Success:**
```json
{
    "success": true,
    "status": "completed",
    "message": "Payment completed successfully",
    "amount": "5000.00",
    "received_amount": "5000.00",
    "transaction_id": "chapa-txn-id"
}
```

**5. Payment Callback Verification**
```
POST /api/payments/verify/
```
Endpoint for Chapa to verify payment (webhook callback).

**Request:**
```json
{
    "tx_ref": "payment-uuid"
}
```

### Booking Workflow

When creating a booking, a payment record is automatically created:

```
1. User creates booking
2. Payment record created automatically
3. User initiates payment via POST /api/bookings/{id}/initiate_payment/
4. System returns checkout URL from Chapa
5. User completes payment on Chapa
6. User verifies payment status via POST /api/payments/{id}/verify_status/
7. On success:
   - Booking status updated to 'confirmed'
   - Confirmation email sent to user
   - Payment status updated to 'completed'
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Django 5.2+
- PostgreSQL or MySQL database
- Chapa Account (https://developer.chapa.co/)

### Installation

1. **Clone/Copy the project**
```bash
cd alx_travel_app_0x02
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

Create `.env` file in the project root:
```
# Django Settings
SECRET_KEY=your-django-secret-key
DEBUG=True

# Database
DB_NAME=alx_travel_app
DB_USER=root
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306

# Chapa Payment Gateway
CHAPA_SECRET_KEY=CHASECK_TEST_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHAPA_API_URL=https://api.chapa.co/v1
CHAPA_CALLBACK_URL=http://localhost:8000/api/payments/verify/

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery (Optional - for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Getting Chapa API Keys

1. Create an account at https://developer.chapa.co/
2. Log in to your dashboard
3. Navigate to Settings or API Keys section
4. Copy your Secret Key (starts with CHASECK_TEST_ for sandbox)
5. Add to `.env` as `CHAPA_SECRET_KEY`

5. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## Testing Payment Integration

### Using Sandbox Environment

Chapa provides a sandbox environment for testing:

1. **Test Payment Credentials**
   - Account: Use your sandbox account credentials
   - Test Cards: Chapa provides test card numbers in their documentation

2. **Test Flow**

```bash
# 1. Create a user and list
POST /api/auth/token/
POST /api/listings/

# 2. Create a booking
POST /api/bookings/
# Response includes booking_id

# 3. Initiate payment
POST /api/bookings/{booking_id}/initiate_payment/
# Copy the checkout_url

# 4. Complete payment (visit checkout_url in browser)

# 5. Verify payment
POST /api/payments/{payment_id}/verify_status/
```

### Sample Test Sequence

```python
import requests

BASE_URL = "http://localhost:8000"
headers = {"Authorization": f"Token {your_token}"}

# Create a booking
booking_data = {
    "listing_id": "listing-uuid",
    "check_in_date": "2025-11-01",
    "check_out_date": "2025-11-05"
}
booking = requests.post(f"{BASE_URL}/api/bookings/", json=booking_data, headers=headers).json()

# Initiate payment
payment = requests.post(
    f"{BASE_URL}/api/bookings/{booking['booking_id']}/initiate_payment/",
    headers=headers
).json()

print(f"Checkout URL: {payment['checkout_url']}")
print(f"Payment ID: {payment['payment_id']}")

# After user completes payment on Chapa, verify
verification = requests.post(
    f"{BASE_URL}/api/payments/{payment['payment_id']}/verify_status/",
    headers=headers
).json()

print(f"Status: {verification['status']}")
```

### Testing Email Notifications

By default, emails are logged to console. To test with actual emails:

1. Update `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Use Gmail app password
```

2. Configure Gmail App Password:
   - Enable 2FA on Google Account
   - Go to https://myaccount.google.com/apppasswords
   - Generate password for "Mail" and "Windows Computer"
   - Use this password in .env

## Error Handling

### Common Errors

**CHAPA_SECRET_KEY not set**
```
ValueError: CHAPA_SECRET_KEY environment variable is not set
```
**Solution**: Add CHAPA_SECRET_KEY to .env file

**Payment Already in Non-Pending State**
```json
{
    "detail": "Cannot initiate payment for completed payment."
}
```
**Solution**: Can only initiate payment for pending payments

**Payment Not Found**
```json
{
    "error": "Payment not found"
}
```
**Solution**: Check if payment exists for the booking

## Project Structure

```
alx_travel_app_0x02/
├── alx_travel_app/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── listings/
│   ├── models.py              # Booking, Payment, Review models
│   ├── views.py               # API ViewSets including PaymentViewSet
│   ├── serializers.py         # PaymentSerializer
│   ├── chapa_utils.py         # Chapa API integration
│   ├── email_tasks.py         # Email notification functions
│   ├── urls.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── 0002_payment.py    # Payment model migration
│   └── admin.py
├── .env
├── requirements.txt
└── manage.py
```

## Key Files

### chapa_utils.py
Contains `ChapaAPIClient` class for API interactions:
- `initiate_payment()`: Initiate payment with Chapa
- `verify_payment()`: Verify payment status

Helper functions:
- `create_payment_for_booking()`: Create payment record
- `update_payment_status()`: Update payment status

### email_tasks.py
Email notification functions:
- `send_payment_confirmation_email()`: Send confirmation on success
- `send_payment_failure_email()`: Send notification on failure

## Security Considerations

1. **API Key Management**
   - Store CHAPA_SECRET_KEY in environment variables
   - Never commit .env file to version control
   - Rotate keys periodically

2. **HTTPS**
   - Use HTTPS in production
   - Set SECURE_SSL_REDIRECT = True in production settings

3. **Permission Checks**
   - Only payment owners can access their payments
   - Only booking guest can initiate payment
   - Payment verification checks authentication

4. **Data Validation**
   - Validate all API requests
   - Verify amounts before payment
   - Log all transaction attempts

## Future Enhancements

1. **Celery Integration**
   - Convert email sending to async tasks
   - Background payment status polling

2. **Webhook Handling**
   - Implement Chapa webhook listeners
   - Automatic payment status updates

3. **Admin Dashboard**
   - Payment management interface
   - Transaction reports and analytics

4. **Retry Logic**
   - Automatic retry for failed payments
   - Payment timeout handling

5. **Multi-Currency Support**
   - Support multiple currency conversions
   - Exchange rate management

## Troubleshooting

### Payment Not Going Through
1. Check CHAPA_SECRET_KEY is correct
2. Verify amount format (should be string)
3. Check CHAPA_CALLBACK_URL is accessible
4. Review Chapa logs for detailed errors

### Emails Not Sending
1. Check EMAIL_BACKEND configuration
2. Verify email credentials in .env
3. Check logs for email errors
4. Use console backend for testing

### Database Errors
1. Run migrations: `python manage.py migrate`
2. Check database connection in .env
3. Verify database user permissions

## Support

For issues with:
- **Chapa API**: Visit https://developer.chapa.co/docs
- **Django DRF**: Check https://www.django-rest-framework.org/
- **Project Issues**: Review logs and check error responses

## License

This project is part of the ALX Backend Engineering curriculum.
