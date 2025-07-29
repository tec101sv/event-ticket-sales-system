# Event Ticketing Backend API

Flask backend API for the Event Ticketing System with Supabase integration.

## 🚀 Quick Deploy

### Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Deploy to Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 📋 Environment Variables Required

```env
SUPABASE_DB_PASSWORD=your_supabase_db_password
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
PAYPAL_CLIENT_ID=your_paypal_client_id (optional)
PAYPAL_SECRET=your_paypal_secret (optional)
PAYPAL_MODE=sandbox
```

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env file
cp .env.example .env

# Run the application
python app.py
```

## 📡 API Endpoints

- **Health Check**: `GET /health`
- **Authentication**: `POST /auth/login`, `POST /auth/register`
- **Events**: `GET /api/events`, `GET /api/events/{id}`
- **Cart**: `GET /api/cart`, `POST /api/cart`
- **Admin**: `GET /admin/*` (requires admin authentication)

## 🗄️ Database

Uses Supabase PostgreSQL with the following tables:
- users
- events
- event_types
- venues
- artists
- tickets
- orders
- order_items
- cart_items

## 🔧 Configuration

The application is configured via `config.py` and uses environment variables for sensitive data.

## 📦 Dependencies

- Flask
- Flask-CORS
- Supabase Python Client
- psycopg2-binary
- python-dotenv
- PyJWT
- bcrypt
- paypalrestsdk
