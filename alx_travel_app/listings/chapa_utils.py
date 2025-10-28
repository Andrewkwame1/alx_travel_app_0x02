"""
Utility functions for Chapa API integration
"""
import os
import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)


class ChapaAPIClient:
    """Client for interacting with Chapa Payment Gateway API"""

    def __init__(self):
        """Initialize Chapa API client with configuration"""
        self.secret_key = os.getenv('CHAPA_SECRET_KEY')
        self.api_url = os.getenv('CHAPA_API_URL', 'https://api.chapa.co/v1')
        self.callback_url = os.getenv('CHAPA_CALLBACK_URL', 'http://localhost:8000/api/payments/verify/')
        
        if not self.secret_key:
            raise ValueError("CHAPA_SECRET_KEY environment variable is not set")
        
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }

    def initiate_payment(self, payment_obj, booking_obj):
        """
        Initiate a payment with Chapa API
        
        Args:
            payment_obj: Payment model instance
            booking_obj: Booking model instance
            
        Returns:
            dict: Response from Chapa API containing checkout_url and reference
        """
        try:
            payload = {
                'amount': str(float(payment_obj.amount)),
                'currency': payment_obj.currency,
                'email': booking_obj.guest.email,
                'first_name': booking_obj.guest.first_name or booking_obj.guest.username,
                'last_name': booking_obj.guest.last_name or '',
                'phone_number': '',  # Add phone if available in User model
                'tx_ref': str(payment_obj.payment_id),  # Use payment_id as reference
                'callback_url': self.callback_url,
                'return_url': self.callback_url,
                'customization[title]': f'Travel Booking - {booking_obj.listing.title}',
                'customization[description]': f'Booking from {booking_obj.check_in_date} to {booking_obj.check_out_date}',
            }

            response = requests.post(
                f'{self.api_url}/transaction/initialize',
                json=payload,
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'success':
                logger.info(f"Payment initiated successfully for payment {payment_obj.payment_id}")
                return {
                    'success': True,
                    'checkout_url': data.get('data', {}).get('checkout_url'),
                    'reference': data.get('data', {}).get('tx_ref'),
                }
            else:
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"Payment initiation failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during payment initiation: {str(e)}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
            }
        except Exception as e:
            logger.error(f"Unexpected error during payment initiation: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
            }

    def verify_payment(self, transaction_reference):
        """
        Verify a payment status with Chapa API
        
        Args:
            transaction_reference: The transaction reference/payment_id from Chapa
            
        Returns:
            dict: Payment status information
        """
        try:
            response = requests.get(
                f'{self.api_url}/transaction/verify/{transaction_reference}',
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'success':
                transaction_data = data.get('data', {})
                logger.info(f"Payment verification successful for {transaction_reference}")
                
                return {
                    'success': True,
                    'status': transaction_data.get('status'),  # success, failed, pending
                    'amount': transaction_data.get('amount'),
                    'currency': transaction_data.get('currency'),
                    'reference': transaction_data.get('reference'),
                    'tx_ref': transaction_data.get('tx_ref'),
                    'charge': transaction_data.get('charge'),
                    'method': transaction_data.get('method'),
                    'received_amount': transaction_data.get('received_amount'),
                }
            else:
                error_msg = data.get('message', 'Verification failed')
                logger.error(f"Payment verification error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during payment verification: {str(e)}")
            return {
                'success': False,
                'error': f'Verification request failed: {str(e)}',
            }
        except Exception as e:
            logger.error(f"Unexpected error during payment verification: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
            }


def create_payment_for_booking(booking_obj):
    """
    Create a Payment record for a booking
    
    Args:
        booking_obj: Booking model instance
        
    Returns:
        Payment: The created Payment instance
    """
    from .models import Payment
    
    payment = Payment.objects.create(
        booking=booking_obj,
        amount=booking_obj.total_price,
        currency='ETB'  # Default to Ethiopian Birr
    )
    
    logger.info(f"Payment created for booking {booking_obj.booking_id}")
    return payment


def update_payment_status(payment_obj, status, transaction_id=None, 
                         chapa_reference=None, payment_method=None, error_message=None):
    """
    Update payment status and related information
    
    Args:
        payment_obj: Payment model instance
        status: New payment status
        transaction_id: Chapa transaction ID
        chapa_reference: Chapa reference/tx_ref
        payment_method: Payment method used
        error_message: Error message if payment failed
    """
    from .models import Booking
    
    payment_obj.status = status
    
    if transaction_id:
        payment_obj.transaction_id = transaction_id
    
    if chapa_reference:
        payment_obj.chapa_reference = chapa_reference
    
    if payment_method:
        payment_obj.payment_method = payment_method
    
    if error_message:
        payment_obj.error_message = error_message
    
    if status == 'completed':
        payment_obj.completed_at = timezone.now()
        # Update booking status to confirmed when payment is completed
        payment_obj.booking.status = 'confirmed'
        payment_obj.booking.save()
    
    payment_obj.save()
    logger.info(f"Payment {payment_obj.payment_id} status updated to {status}")

