import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Building2, MapPin, Edit, Trash2, Eye } from 'lucide-react';
import toast from 'react-hot-toast';
import { hotelsAPI } from '@/api/client';
import type { Hotel } from '@/types';
import Button from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import Loading from '@/components/ui/Loading';

const HotelsPage = () => {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState({ status: '', city: '' });

  useEffect(() => {
    fetchHotels();
  }, [filter]);

  const fetchHotels = async () => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (filter.status) params.status = filter.status;
      if (filter.city) params.city = filter.city;
      
      const data = await hotelsAPI.getAll(params);
      setHotels(data);
    } catch (error) {
      toast.error('Failed to load hotels');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This will also delete all associated room types.`)) {
      return;
    }

    try {
      await hotelsAPI.delete(id);
      toast.success('Hotel deleted successfully');
      fetchHotels();
    } catch (error) {
      toast.error('Failed to delete hotel');
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
    };
    return styles[status as keyof typeof styles] || styles.active;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Loading hotels..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Hotels</h1>
          <p className="text-gray-600 mt-1">Manage your hotel properties</p>
        </div>
        <Link to="/hotels/new">
          <Button variant="primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Hotel
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filter.status}
                onChange={(e) => setFilter({ ...filter, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                value={filter.city}
                onChange={(e) => setFilter({ ...filter, city: e.target.value })}
                placeholder="Filter by city..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Hotels Grid */}
      {hotels.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No hotels found. Create your first hotel to get started.</p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {hotels.map((hotel) => (
            <Card key={hotel.id} hover className="overflow-hidden">
              {/* Hotel Image */}
              <div className="h-48 bg-gradient-to-br from-primary-100 to-primary-200 relative">
                {hotel.images && hotel.images.length > 0 ? (
                  <img
                    src={hotel.images[0]}
                    alt={hotel.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <Building2 className="w-16 h-16 text-primary-400" />
                  </div>
                )}
                <div className={`absolute top-2 right-2 px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(hotel.status)}`}>
                  {hotel.status}
                </div>
              </div>

              <CardBody>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {hotel.name}
                </h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {hotel.description || 'No description available'}
                </p>
                
                {hotel.city && (
                  <div className="flex items-center text-sm text-gray-500 mb-4">
                    <MapPin className="w-4 h-4 mr-1" />
                    {hotel.city}{hotel.country && `, ${hotel.country}`}
                  </div>
                )}

                <div className="flex gap-2">
                  <Link to={`/hotels/${hotel.id}`} className="flex-1">
                    <Button variant="primary" size="sm" fullWidth>
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                  </Link>
                  <Link to={`/hotels/${hotel.id}/edit`}>
                    <Button variant="secondary" size="sm">
                      <Edit className="w-4 h-4" />
                    </Button>
                  </Link>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(hotel.id, hotel.name)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default HotelsPage;
