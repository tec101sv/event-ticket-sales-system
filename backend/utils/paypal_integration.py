import requests
import json
from config import Config

class PayPalIntegration:
    def __init__(self):
        self.client_id = Config.PAYPAL_CLIENT_ID
        self.secret = Config.PAYPAL_SECRET
        self.mode = Config.PAYPAL_MODE
        
        if self.mode == 'sandbox':
            self.base_url = 'https://api.sandbox.paypal.com'
        else:
            self.base_url = 'https://api.paypal.com'
    
    def get_access_token(self):
        """Get PayPal access token"""
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
            }
            
            data = 'grant_type=client_credentials'
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.secret)
            )
            
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                print(f"Error getting PayPal access token: {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal access token error: {e}")
            return None
    
    def create_payment(self, amount, currency='USD', return_url=None, cancel_url=None):
        """Create a PayPal payment"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            url = f"{self.base_url}/v1/payments/payment"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url or "http://localhost:3000/payment/success",
                    "cancel_url": cancel_url or "http://localhost:3000/payment/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Event Tickets",
                            "sku": "tickets",
                            "price": str(amount),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "currency": currency,
                        "total": str(amount)
                    },
                    "description": "Event ticket purchase"
                }]
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payment_data))
            
            if response.status_code == 201:
                payment = response.json()
                # Find the approval URL
                for link in payment['links']:
                    if link['rel'] == 'approval_url':
                        payment['approval_url'] = link['href']
                        break
                return payment
            else:
                print(f"Error creating PayPal payment: {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal payment creation error: {e}")
            return None
    
    def execute_payment(self, payment_id, payer_id):
        """Execute a PayPal payment"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            url = f"{self.base_url}/v1/payments/payment/{payment_id}/execute"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            execute_data = {
                "payer_id": payer_id
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(execute_data))
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error executing PayPal payment: {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal payment execution error: {e}")
            return None
    
    def get_payment_details(self, payment_id):
        """Get PayPal payment details"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            url = f"{self.base_url}/v1/payments/payment/{payment_id}"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting PayPal payment details: {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal payment details error: {e}")
            return None

# Global PayPal instance
paypal = PayPalIntegration()
