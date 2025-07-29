import React, { useState, useEffect } from 'react';
import { eventsAPI } from '../services/api';
import SearchBar from './SearchBar';
import EventCard from './EventCard';

const EventList = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 12,
    total: 0,
    pages: 0
  });
  const [filters, setFilters] = useState({
    search: '',
    type: '',
    venue: '',
    date: ''
  });

  useEffect(() => {
    loadEvents();
  }, [pagination.page, filters]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      };

      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await eventsAPI.getEvents(params);
      setEvents(response.data.events);
      setPagination(prev => ({
        ...prev,
        ...response.data.pagination
      }));
    } catch (err) {
      console.error('Error loading events:', err);
      setError('Error al cargar los eventos. Por favor, intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (newFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderPagination = () => {
    if (pagination.pages <= 1) return null;

    const pages = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, pagination.page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(pagination.pages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    // Previous button
    if (pagination.page > 1) {
      pages.push(
        <button
          key="prev"
          onClick={() => handlePageChange(pagination.page - 1)}
          className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-md hover:bg-gray-50"
        >
          Anterior
        </button>
      );
    }

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`px-3 py-2 text-sm font-medium border ${
            i === pagination.page
              ? 'bg-primary-600 text-white border-primary-600'
              : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-50'
          }`}
        >
          {i}
        </button>
      );
    }

    // Next button
    if (pagination.page < pagination.pages) {
      pages.push(
        <button
          key="next"
          onClick={() => handlePageChange(pagination.page + 1)}
          className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50"
        >
          Siguiente
        </button>
      );
    }

    return (
      <div className="flex justify-center items-center mt-8">
        <nav className="flex" aria-label="Pagination">
          {pages}
        </nav>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              Encuentra tu Evento Perfecto
            </h1>
            <p className="text-xl md:text-2xl text-primary-100 max-w-3xl mx-auto">
              Descubre los mejores conciertos, obras de teatro, eventos deportivos y más. 
              Compra tus entradas de forma segura y fácil.
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} onFiltersChange={setFilters} />

        {/* Results Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Próximos Eventos
            </h2>
            {pagination.total > 0 && (
              <p className="text-gray-600 mt-1">
                Mostrando {((pagination.page - 1) * pagination.per_page) + 1} - {Math.min(pagination.page * pagination.per_page, pagination.total)} de {pagination.total} eventos
              </p>
            )}
          </div>

          {/* Sort Options */}
          <div className="hidden md:block">
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="date">Ordenar por fecha</option>
              <option value="price">Ordenar por precio</option>
              <option value="name">Ordenar por nombre</option>
            </select>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-16">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Cargando eventos...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-red-800 mb-2">Error al cargar eventos</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={loadEvents}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              Intentar de nuevo
            </button>
          </div>
        )}

        {/* No Events State */}
        {!loading && !error && events.length === 0 && (
          <div className="text-center py-16">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h3 className="text-xl font-medium text-gray-900 mb-2">No se encontraron eventos</h3>
            <p className="text-gray-600 mb-4">
              {Object.values(filters).some(filter => filter) 
                ? 'Intenta ajustar tus filtros de búsqueda'
                : 'No hay eventos disponibles en este momento'
              }
            </p>
            {Object.values(filters).some(filter => filter) && (
              <button
                onClick={() => handleSearch({ search: '', type: '', venue: '', date: '' })}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Limpiar filtros
              </button>
            )}
          </div>
        )}

        {/* Events Grid */}
        {!loading && !error && events.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>

            {/* Pagination */}
            {renderPagination()}
          </>
        )}

        {/* Featured Categories */}
        {!loading && !error && Object.values(filters).every(filter => !filter) && (
          <div className="mt-16">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Explora por Categoría
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { name: 'Conciertos', icon: '🎵', color: 'bg-purple-500' },
                { name: 'Teatro', icon: '🎭', color: 'bg-red-500' },
                { name: 'Deportes', icon: '⚽', color: 'bg-green-500' },
                { name: 'Festivales', icon: '🎪', color: 'bg-yellow-500' }
              ].map((category) => (
                <button
                  key={category.name}
                  onClick={() => handleSearch({ ...filters, type: category.name })}
                  className={`${category.color} text-white p-6 rounded-lg hover:opacity-90 transition duration-200 text-center`}
                >
                  <div className="text-3xl mb-2">{category.icon}</div>
                  <div className="font-medium">{category.name}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EventList;
