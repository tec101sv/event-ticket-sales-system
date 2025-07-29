import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { eventsAPI, cartAPI } from '../services/api';
import authService from '../services/auth';

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTickets, setSelectedTickets] = useState({});
  const [addingToCart, setAddingToCart] = useState(false);
  const [cartMessage, setCartMessage] = useState('');

  useEffect(() => {
    loadEventDetails();
  }, [id]);

  const loadEventDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await eventsAPI.getEventDetails(id);
      setEvent(response.data);
    } catch (err) {
      console.error('Error loading event details:', err);
      setError('Error al cargar los detalles del evento');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const handleTicketQuantityChange = (ticketId, quantity) => {
    setSelectedTickets(prev => ({
      ...prev,
      [ticketId]: Math.max(0, quantity)
    }));
  };

  const getTotalPrice = () => {
    if (!event || !event.tickets) return 0;
    
    return event.tickets.reduce((total, ticket) => {
      const quantity = selectedTickets[ticket.id] || 0;
      return total + (ticket.price * quantity);
    }, 0);
  };

  const getTotalTickets = () => {
    return Object.values(selectedTickets).reduce((total, quantity) => total + quantity, 0);
  };

  const handleAddToCart = async () => {
    if (!authService.isAuthenticated()) {
      navigate('/login');
      return;
    }

    const totalTickets = getTotalTickets();
    if (totalTickets === 0) {
      setCartMessage('Selecciona al menos un ticket');
      setTimeout(() => setCartMessage(''), 3000);
      return;
    }

    try {
      setAddingToCart(true);
      setCartMessage('');

      // Add each selected ticket type to cart
      for (const [ticketId, quantity] of Object.entries(selectedTickets)) {
        if (quantity > 0) {
          await cartAPI.addToCart({
            ticket_id: parseInt(ticketId),
            quantity: quantity
          });
        }
      }

      setCartMessage('¡Tickets agregados al carrito exitosamente!');
      setSelectedTickets({});
      
      setTimeout(() => {
        setCartMessage('');
      }, 3000);

    } catch (err) {
      console.error('Error adding to cart:', err);
      setCartMessage(err.response?.data?.error || 'Error al agregar al carrito');
      setTimeout(() => setCartMessage(''), 3000);
    } finally {
      setAddingToCart(false);
    }
  };

  const handleBuyNow = async () => {
    await handleAddToCart();
    if (getTotalTickets() > 0) {
      navigate('/cart');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando detalles del evento...</p>
        </div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Evento no encontrado</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition duration-200"
          >
            Volver a Eventos
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Button */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition duration-200"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
            </svg>
            Volver a Eventos
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Event Details */}
          <div className="lg:col-span-2">
            {/* Event Image */}
            <div className="bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg overflow-hidden mb-6">
              {event.image_url ? (
                <img
                  src={event.image_url}
                  alt={event.title}
                  className="w-full h-64 md:h-80 object-cover"
                />
              ) : (
                <div className="w-full h-64 md:h-80 flex items-center justify-center text-white">
                  <div className="text-center">
                    <svg className="w-24 h-24 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="text-xl font-medium">{event.event_type}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Event Info */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                  {event.event_type}
                </span>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Fecha</div>
                  <div className="font-semibold">{formatDate(event.event_date)}</div>
                  <div className="text-sm text-gray-600">{formatTime(event.event_time)}</div>
                </div>
              </div>

              <h1 className="text-3xl font-bold text-gray-900 mb-4">{event.title}</h1>

              {event.artist_name && (
                <div className="flex items-center mb-4">
                  <svg className="w-5 h-5 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span className="text-lg font-medium text-gray-900">{event.artist_name}</span>
                </div>
              )}

              <div className="flex items-center mb-6">
                <svg className="w-5 h-5 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <div>
                  <div className="font-medium">{event.venue_name}</div>
                  <div className="text-sm text-gray-600">{event.venue_address}, {event.venue_city}</div>
                </div>
              </div>

              {event.description && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Descripción</h3>
                  <p className="text-gray-700 leading-relaxed">{event.description}</p>
                </div>
              )}
            </div>

            {/* Artist Info */}
            {event.artist_bio && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Sobre el Artista</h3>
                <p className="text-gray-700 leading-relaxed">{event.artist_bio}</p>
              </div>
            )}
          </div>

          {/* Ticket Selection */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
              <h3 className="text-xl font-semibold mb-4">Seleccionar Tickets</h3>

              {event.tickets && event.tickets.length > 0 ? (
                <>
                  <div className="space-y-4 mb-6">
                    {event.tickets.map((ticket) => (
                      <div key={ticket.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-medium">{ticket.location}</h4>
                            <p className="text-2xl font-bold text-primary-600">
                              {formatPrice(ticket.price)}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-600">Disponibles</div>
                            <div className="font-medium">{ticket.available}</div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Cantidad:</span>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleTicketQuantityChange(ticket.id, (selectedTickets[ticket.id] || 0) - 1)}
                              disabled={!selectedTickets[ticket.id] || selectedTickets[ticket.id] <= 0}
                              className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              -
                            </button>
                            <span className="w-8 text-center font-medium">
                              {selectedTickets[ticket.id] || 0}
                            </span>
                            <button
                              onClick={() => handleTicketQuantityChange(ticket.id, (selectedTickets[ticket.id] || 0) + 1)}
                              disabled={selectedTickets[ticket.id] >= ticket.available}
                              className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              +
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Total */}
                  <div className="border-t pt-4 mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">Total de tickets:</span>
                      <span className="font-medium">{getTotalTickets()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold">Total:</span>
                      <span className="text-2xl font-bold text-primary-600">
                        {formatPrice(getTotalPrice())}
                      </span>
                    </div>
                  </div>

                  {/* Cart Message */}
                  {cartMessage && (
                    <div className={`p-3 rounded-lg mb-4 text-sm ${
                      cartMessage.includes('exitosamente') 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {cartMessage}
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="space-y-3">
                    <button
                      onClick={handleBuyNow}
                      disabled={addingToCart || getTotalTickets() === 0}
                      className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 font-medium"
                    >
                      {addingToCart ? 'Procesando...' : 'Comprar Ahora'}
                    </button>
                    
                    <button
                      onClick={handleAddToCart}
                      disabled={addingToCart || getTotalTickets() === 0}
                      className="w-full border border-primary-600 text-primary-600 py-3 px-4 rounded-lg hover:bg-primary-50 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 font-medium"
                    >
                      {addingToCart ? 'Agregando...' : 'Agregar al Carrito'}
                    </button>
                  </div>

                  {!authService.isAuthenticated() && (
                    <p className="text-sm text-gray-600 text-center mt-4">
                      <button
                        onClick={() => navigate('/login')}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        Inicia sesión
                      </button>
                      {' '}para comprar tickets
                    </p>
                  )}
                </>
              ) : (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" />
                  </svg>
                  <p className="text-gray-600">No hay tickets disponibles para este evento</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventDetails;
