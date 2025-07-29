import React, { useState, useEffect } from 'react';
import { eventsAPI } from '../services/api';

const SearchBar = ({ onSearch, onFiltersChange }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedVenue, setSelectedVenue] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [eventTypes, setEventTypes] = useState([]);
  const [venues, setVenues] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    loadFilters();
  }, []);

  const loadFilters = async () => {
    try {
      const [typesResponse, venuesResponse] = await Promise.all([
        eventsAPI.getEventTypes(),
        eventsAPI.getVenues()
      ]);
      
      setEventTypes(typesResponse.data);
      setVenues(venuesResponse.data);
    } catch (error) {
      console.error('Error loading filters:', error);
    }
  };

  const handleSearch = () => {
    const filters = {
      search: searchTerm,
      type: selectedType,
      venue: selectedVenue,
      date: selectedDate
    };
    
    onSearch(filters);
    if (onFiltersChange) {
      onFiltersChange(filters);
    }
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setSelectedType('');
    setSelectedVenue('');
    setSelectedDate('');
    
    const emptyFilters = {
      search: '',
      type: '',
      venue: '',
      date: ''
    };
    
    onSearch(emptyFilters);
    if (onFiltersChange) {
      onFiltersChange(emptyFilters);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
      {/* Main Search Bar */}
      <div className="flex flex-col md:flex-row gap-4 mb-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Buscar eventos, artistas, lugares..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 flex items-center"
          >
            <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
            </svg>
            Filtros
          </button>
          
          <button
            onClick={handleSearch}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition duration-200 flex items-center"
          >
            <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Buscar
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      {isExpanded && (
        <div className="border-t pt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* Event Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Evento
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todos los tipos</option>
                {eventTypes.map((type) => (
                  <option key={type.id} value={type.name}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Venue Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lugar
              </label>
              <select
                value={selectedVenue}
                onChange={(e) => setSelectedVenue(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todos los lugares</option>
                {venues.map((venue) => (
                  <option key={venue.id} value={venue.name}>
                    {venue.name} - {venue.city}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fecha
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filter Actions */}
          <div className="flex justify-between items-center">
            <button
              onClick={handleClearFilters}
              className="text-gray-600 hover:text-gray-800 transition duration-200"
            >
              Limpiar filtros
            </button>
            
            <div className="flex gap-2">
              <button
                onClick={() => setIsExpanded(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200"
              >
                Cerrar
              </button>
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition duration-200"
              >
                Aplicar Filtros
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Display */}
      {(searchTerm || selectedType || selectedVenue || selectedDate) && (
        <div className="border-t pt-4 mt-4">
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-600">Filtros activos:</span>
            
            {searchTerm && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                Búsqueda: {searchTerm}
                <button
                  onClick={() => {
                    setSearchTerm('');
                    handleSearch();
                  }}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  ×
                </button>
              </span>
            )}
            
            {selectedType && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                Tipo: {selectedType}
                <button
                  onClick={() => {
                    setSelectedType('');
                    handleSearch();
                  }}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  ×
                </button>
              </span>
            )}
            
            {selectedVenue && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                Lugar: {selectedVenue}
                <button
                  onClick={() => {
                    setSelectedVenue('');
                    handleSearch();
                  }}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  ×
                </button>
              </span>
            )}
            
            {selectedDate && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                Fecha: {new Date(selectedDate).toLocaleDateString('es-ES')}
                <button
                  onClick={() => {
                    setSelectedDate('');
                    handleSearch();
                  }}
                  className="ml-2 text-primary-600 hover:text-primary-800"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
