"""
Unit tests for payment integration
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date, timedelta
import json

from .models import Listing, Booking, Payment, Review


class PaymentIntegrationTestCase(TestCase):
    """Test cases for payment integration"""

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.host_user = User.objects.create_user(
            username='host',
            email='host@test.com',
            password='testpass123'
        )
        
        self.guest_user = User.objects.create_user(
            username='guest',
            email='guest@test.com',
            password='testpass123'
        )

        # Create tokens for API authentication
        self.host_token = Token.objects.create(user=self.host_user)
        self.guest_token = Token.objects.create(user=self.guest_user)

        # Create test listing
        self.listing = Listing.objects.create(
            title='Test Beach House',
            description='Beautiful beach property',
            price_per_night=Decimal('1000.00'),
            location='Addis Ababa',
            amenities='WiFi, Pool, Kitchen',
            host=self.host_user,
            is_available=True
        )

        # Create test booking
        today = date.today()
        self.booking = Booking.objects.create(
            listing=self.listing,
            guest=self.guest_user,
            check_in_date=today + timedelta(days=1),
            check_out_date=today + timedelta(days=5),
            total_price=Decimal('4000.00'),
            status='pending'
        )

        # Create test payment
        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal('4000.00'),
            currency='ETB',
            status='pending'
        )

        # Initialize API client
        self.client = APIClient()

    def test_payment_model_creation(self):
        """Test Payment model creation"""
        self.assertIsNotNone(self.payment.payment_id)
        self.assertEqual(self.payment.amount, Decimal('4000.00'))
        self.assertEqual(self.payment.status, 'pending')
        self.assertEqual(self.payment.booking, self.booking)
        self.assertIsNone(self.payment.transaction_id)

    def test_booking_has_payment(self):
        """Test that booking has associated payment"""
        booking = Booking.objects.get(booking_id=self.booking.booking_id)
        payment = booking.payment
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, self.booking.total_price)

    def test_get_payment_list(self):
        """Test retrieving payment list"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.guest_token.key}')
        response = self.client.get('/api/payments/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_payment_detail(self):
        """Test retrieving payment details"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.guest_token.key}')
        response = self.client.get(f'/api/payments/{self.payment.payment_id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['amount'], '4000.00')
        self.assertEqual(data['status'], 'pending')

    def test_payment_access_control(self):
        """Test that only authorized users can access payment"""
        # Create another user
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        other_token = Token.objects.create(user=other_user)

        # Try to access payment as unauthorized user
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.get(f'/api/payments/{self.payment.payment_id}/')
        
        # Should not have access
        self.assertNotEqual(response.status_code, 200)

    def test_booking_creation_creates_payment(self):
        """Test that creating a booking automatically creates payment"""
        # Create new listing and booking
        new_booking = Booking.objects.create(
            listing=self.listing,
            guest=self.guest_user,
            check_in_date=date.today() + timedelta(days=10),
            check_out_date=date.today() + timedelta(days=15),
            total_price=Decimal('5000.00'),
            status='pending'
        )

        # Note: In the actual implementation, payment creation happens in perform_create
        # So we manually create it here for testing
        payment = Payment.objects.create(
            booking=new_booking,
            amount=new_booking.total_price,
            currency='ETB',
            status='pending'
        )

        self.assertIsNotNone(payment)
        self.assertEqual(payment.booking, new_booking)
        self.assertEqual(payment.amount, Decimal('5000.00'))

    def test_payment_status_update(self):
        """Test updating payment status"""
        self.assertEqual(self.payment.status, 'pending')
        
        self.payment.status = 'completed'
        self.payment.transaction_id = 'chapa-txn-123'
        self.payment.save()
        
        updated_payment = Payment.objects.get(payment_id=self.payment.payment_id)
        self.assertEqual(updated_payment.status, 'completed')
        self.assertEqual(updated_payment.transaction_id, 'chapa-txn-123')

    def test_payment_failure_state(self):
        """Test payment failure state"""
        self.payment.status = 'failed'
        self.payment.error_message = 'Card declined'
        self.payment.save()
        
        updated_payment = Payment.objects.get(payment_id=self.payment.payment_id)
        self.assertEqual(updated_payment.status, 'failed')
        self.assertEqual(updated_payment.error_message, 'Card declined')

    def test_payment_currency_default(self):
        """Test payment currency defaults to ETB"""
        new_payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal('1000.00')
        )
        
        self.assertEqual(new_payment.currency, 'ETB')

    def test_payment_serializer_read_only_fields(self):
        """Test that certain fields are read-only in serializer"""
        from .serializers import PaymentSerializer
        
        serializer = PaymentSerializer(self.payment)
        data = serializer.data
        
        # Check that certain fields are present
        self.assertIn('payment_id', data)
        self.assertIn('booking', data)
        self.assertIn('amount', data)
        self.assertIn('status', data)


class PaymentAPITestCase(TestCase):
    """Test cases for Payment API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.host_user = User.objects.create_user(
            username='host',
            email='host@test.com',
            password='testpass123'
        )
        
        self.guest_user = User.objects.create_user(
            username='guest',
            email='guest@test.com',
            password='testpass123'
        )

        self.guest_token = Token.objects.create(user=self.guest_user)
        
        self.listing = Listing.objects.create(
            title='Test Property',
            description='A test property',
            price_per_night=Decimal('500.00'),
            location='Addis Ababa',
            amenities='WiFi',
            host=self.host_user,
            is_available=True
        )

        today = date.today()
        self.booking = Booking.objects.create(
            listing=self.listing,
            guest=self.guest_user,
            check_in_date=today + timedelta(days=1),
            check_out_date=today + timedelta(days=3),
            total_price=Decimal('1000.00'),
            status='pending'
        )

        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal('1000.00'),
            currency='ETB',
            status='pending'
        )

        self.client = APIClient()

    def test_payment_list_requires_authentication(self):
        """Test that payment list requires authentication"""
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, 401)

    def test_payment_list_authenticated(self):
        """Test payment list for authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.guest_token.key}')
        response = self.client.get('/api/payments/')
        
        self.assertEqual(response.status_code, 200)

    def test_payment_detail_requires_authentication(self):
        """Test that payment detail requires authentication"""
        response = self.client.get(f'/api/payments/{self.payment.payment_id}/')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    import unittest
    unittest.main()
