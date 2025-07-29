import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';

const ManageArtists = () => {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingArtist, setEditingArtist] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    bio: '',
    image_url: ''
  });

  useEffect(() => {
    loadArtists();
  }, []);

  const loadArtists = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await adminAPI.getAllArtists();
      setArtists(response.data);
    } catch (err) {
      console.error('Error loading artists:', err);
      setError('Error al cargar los artistas');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('El nombre es requerido');
      return;
    }

    try {
      setError('');
      
      if (editingArtist) {
        await adminAPI.updateArtist(editingArtist.id, formData);
      } else {
        await adminAPI.createArtist(formData);
      }

      setFormData({ name: '', bio: '', image_url: '' });
      setShowForm(false);
      setEditingArtist(null);
      await loadArtists();
    } catch (err) {
      console.error('Error saving artist:', err);
      setError(err.response?.data?.error || 'Error al guardar el artista');
    }
  };

  const handleEdit = (artist) => {
    setEditingArtist(artist);
    setFormData({
      name: artist.name,
      bio: artist.bio || '',
      image_url: artist.image_url || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (artistId) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este artista?')) {
      return;
    }

    try {
      await adminAPI.deleteArtist(artistId);
      await loadArtists();
    } catch (err) {
      console.error('Error deleting artist:', err);
      setError('Error al eliminar el artista');
    }
  };

  const handleCancel = () => {
    setFormData({ name: '', bio: '', image_url: '' });
    setShowForm(false);
    setEditingArtist(null);
    setError('');
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando artistas...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Artistas</h1>
          <p className="text-gray-600">Gestiona los artistas y anfitriones de eventos</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition duration-200 flex items-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
          Nuevo Artista
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">
            {editingArtist ? 'Editar Artista' : 'Nuevo Artista'}
          </h3>
          
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Ej: Banda Rock Nacional, DJ Internacional"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL de Imagen
                </label>
                <input
                  type="url"
                  name="image_url"
                  value={formData.image_url}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="https://ejemplo.com/imagen.jpg"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Biografía
                </label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Información sobre el artista, su trayectoria, logros, etc."
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition duration-200"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition duration-200"
              >
                {editingArtist ? 'Actualizar' : 'Crear'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Artists Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {artists.map((artist) => (
          <div key={artist.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Artist Image */}
            <div className="h-48 bg-gradient-to-br from-primary-400 to-primary-600">
              {artist.image_url ? (
                <img
                  src={artist.image_url}
                  alt={artist.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-white">
                  <svg className="w-16 h-16 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              )}
            </div>

            {/* Artist Info */}
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{artist.name}</h3>
              
              {artist.bio && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {artist.bio}
                </p>
              )}

              <div className="text-xs text-gray-500 mb-4">
                Creado: {new Date(artist.created_at).toLocaleDateString('es-ES')}
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => handleEdit(artist)}
                  className="px-3 py-1 text-sm text-primary-600 hover:text-primary-900 border border-primary-600 rounded hover:bg-primary-50 transition duration-200"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(artist.id)}
                  className="px-3 py-1 text-sm text-red-600 hover:text-red-900 border border-red-600 rounded hover:bg-red-50 transition duration-200"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {artists.length === 0 && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay artistas registrados</h3>
            <p className="text-gray-600 mb-6">Comienza agregando artistas para tus eventos</p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition duration-200"
            >
              Crear el primer artista
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManageArtists;
