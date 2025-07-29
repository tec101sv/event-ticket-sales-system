import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase Configuration
    SUPABASE_URL = "https://kbymmihdkfstrvntuiix.supabase.co"
    SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtieW1taWhka2ZzdHJ2bnR1aWl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1NjczMzcsImV4cCI6MjA2OTE0MzMzN30.kzIqS1ZYKAnmF657aa1F83YOz9cwvNjhvtgYnEooPT8"
    
    # Database Configuration for Supabase PostgreSQL
    SUPABASE_DB_HOST = "db.kbymmihdkfstrvntuiix.supabase.co"
    SUPABASE_DB_PORT = 5432
    SUPABASE_DB_USER = "postgres"
    SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', 'your_db_password')
    SUPABASE_DB_NAME = "postgres"
    
    DATABASE_URL = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # PayPal Configuration
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', 'your_paypal_client_id')
    PAYPAL_SECRET = os.getenv('PAYPAL_SECRET', 'your_paypal_secret')
    PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
    
    # Environment
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # CORS Configuration - Dynamic based on environment
    CORS_ORIGINS = [
        'http://localhost:3000', 
        'http://localhost:8000',
        'https://event-ticketing-app.netlify.app'
    ]
    
    # Add any additional origins from environment variable
    additional_origins = os.getenv('ADDITIONAL_CORS_ORIGINS', '')
    if additional_origins:
        CORS_ORIGINS.extend(additional_origins.split(','))
