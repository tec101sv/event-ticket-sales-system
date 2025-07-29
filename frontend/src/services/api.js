import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  verify: () => api.get('/auth/verify'),
};

// Events API
export const eventsAPI = {
  getEvents: (params = {}) => api.get('/api/events', { params }),
  getEventDetails: (eventId) => api.get(`/api/events/${eventId}`),
  getEventTypes: () => api.get('/api/event-types'),
  getVenues: () => api.get('/api/venues'),
};

// Cart API
export const cartAPI = {
  getCart: () => api.get('/api/cart'),
  addToCart: (item) => api.post('/api/cart', item),
  removeFromCart: (itemId) => api.delete(`/api/cart/${itemId}`),
  checkout: () => api.post('/api/checkout'),
  executePayment: (paymentData) => api.post('/api/payment/execute', paymentData),
};

// Orders API
export const ordersAPI = {
  getUserOrders: () => api.get('/api/orders'),
  getOrderDetails: (orderId) => api.get(`/api/orders/${orderId}`),
};

// Admin API
export const adminAPI = {
  // Dashboard
  getDashboardStats: () => api.get('/admin/dashboard/stats'),
  
  // Events
  getAllEvents: (params = {}) => api.get('/admin/events', { params }),
  getEvent: (eventId) => api.get(`/admin/events/${eventId}`),
  createEvent: (eventData) => api.post('/admin/events', eventData),
  updateEvent: (eventId, eventData) => api.put(`/admin/events/${eventId}`, eventData),
  deleteEvent: (eventId) => api.delete(`/admin/events/${eventId}`),
  
  // Event Types
  getAllEventTypes: () => api.get('/admin/event-types'),
  createEventType: (typeData) => api.post('/admin/event-types', typeData),
  updateEventType: (typeId, typeData) => api.put(`/admin/event-types/${typeId}`, typeData),
  deleteEventType: (typeId) => api.delete(`/admin/event-types/${typeId}`),
  
  // Venues
  getAllVenues: () => api.get('/admin/venues'),
  createVenue: (venueData) => api.post('/admin/venues', venueData),
  updateVenue: (venueId, venueData) => api.put(`/admin/venues/${venueId}`, venueData),
  deleteVenue: (venueId) => api.delete(`/admin/venues/${venueId}`),
  
  // Artists
  getAllArtists: () => api.get('/admin/artists'),
  createArtist: (artistData) => api.post('/admin/artists', artistData),
  updateArtist: (artistId, artistData) => api.put(`/admin/artists/${artistId}`, artistData),
  deleteArtist: (artistId) => api.delete(`/admin/artists/${artistId}`),
  
  // Orders
  getAllOrders: (params = {}) => api.get('/admin/orders', { params }),
};

export default api;
