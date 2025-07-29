import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import authService from './services/auth';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import EventList from './components/EventList';
import EventDetails from './components/EventDetails';
import UserAuth from './components/UserAuth';
import TicketCart from './components/TicketCart';
import AdminDashboard from './components/AdminDashboard';

// Protected Route Component
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  const [isAdmin, setIsAdmin] = useState(authService.isAdmin());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyAuth = async () => {
      if (authService.getToken()) {
        const result = await authService.verifyToken();
        setIsAuthenticated(result.success);
        setIsAdmin(authService.isAdmin());
      } else {
        setIsAuthenticated(false);
        setIsAdmin(false);
      }
      setLoading(false);
    };

    verifyAuth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Public Route Component (redirect if already authenticated)
const PublicRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

function App() {
  const [user, setUser] = useState(authService.getUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      if (authService.getToken()) {
        const result = await authService.verifyToken();
        if (result.success) {
          setUser(result.user);
        } else {
          setUser(null);
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={handleLogout} />
      
      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<EventList />} />
          <Route path="/events/:id" element={<EventDetails />} />
          
          {/* Auth Routes */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <UserAuth mode="login" onLogin={handleLogin} />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute>
                <UserAuth mode="register" onLogin={handleLogin} />
              </PublicRoute>
            } 
          />
          
          {/* Protected Routes */}
          <Route 
            path="/cart" 
            element={
              <ProtectedRoute>
                <TicketCart />
              </ProtectedRoute>
            } 
          />
          
          {/* Admin Routes */}
          <Route 
            path="/admin/*" 
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Payment Routes */}
          <Route 
            path="/payment/success" 
            element={
              <ProtectedRoute>
                <PaymentSuccess />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/payment/cancel" 
            element={
              <ProtectedRoute>
                <PaymentCancel />
              </ProtectedRoute>
            } 
          />
          
          {/* 404 Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      
      <Footer />
    </div>
  );
}

// Payment Success Component
const PaymentSuccess = () => {
  const [processing, setProcessing] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const executePayment = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const paymentId = urlParams.get('paymentId');
        const payerId = urlParams.get('PayerID');

        if (paymentId && payerId) {
          const { cartAPI } = await import('./services/api');
          await cartAPI.executePayment({ payment_id: paymentId, payer_id: payerId });
          setSuccess(true);
        } else {
          setError('Parámetros de pago inválidos');
        }
      } catch (err) {
        setError('Error al procesar el pago');
        console.error('Payment execution error:', err);
      } finally {
        setProcessing(false);
      }
    };

    executePayment();
  }, []);

  if (processing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Procesando pago...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        {success ? (
          <>
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">¡Pago Exitoso!</h2>
            <p className="text-gray-600 mb-6">Tu compra ha sido procesada correctamente.</p>
            <button
              onClick={() => window.location.href = '/'}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition duration-200"
            >
              Volver al Inicio
            </button>
          </>
        ) : (
          <>
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error en el Pago</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.href = '/cart'}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition duration-200"
            >
              Volver al Carrito
            </button>
          </>
        )}
      </div>
    </div>
  );
};

// Payment Cancel Component
const PaymentCancel = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Pago Cancelado</h2>
        <p className="text-gray-600 mb-6">Has cancelado el proceso de pago. Tus artículos siguen en el carrito.</p>
        <div className="space-y-3">
          <button
            onClick={() => window.location.href = '/cart'}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition duration-200"
          >
            Volver al Carrito
          </button>
          <button
            onClick={() => window.location.href = '/'}
            className="w-full bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition duration-200"
          >
            Continuar Navegando
          </button>
        </div>
      </div>
    </div>
  );
};

// 404 Component
const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">Página no encontrada</p>
        <button
          onClick={() => window.location.href = '/'}
          className="bg-primary-600 text-white py-2 px-6 rounded-md hover:bg-primary-700 transition duration-200"
        >
          Volver al Inicio
        </button>
      </div>
    </div>
  );
};

export default App;
