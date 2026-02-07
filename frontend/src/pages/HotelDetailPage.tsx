import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Plus,
  DollarSign,
  Calendar,
  TrendingUp,
  Edit,
  Trash2,
} from "lucide-react";
import toast from "react-hot-toast";
import { format } from "date-fns";
import { hotelsAPI, roomTypesAPI, rateAdjustmentsAPI } from "@/api/client";
import type { Hotel, RoomType, RateAdjustment } from "@/types";
import Button from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Loading from "@/components/ui/Loading";
import Modal from "@/components/ui/Modal";
import Input from "@/components/ui/Input";

const HotelDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [hotel, setHotel] = useState<Hotel | null>(null);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Rate adjustment modal state
  const [showAdjustmentModal, setShowAdjustmentModal] = useState(false);
  const [selectedRoomType, setSelectedRoomType] = useState<RoomType | null>(
    null
  );
  const [adjustmentHistory, setAdjustmentHistory] = useState<RateAdjustment[]>(
    []
  );
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  // Form state for rate adjustment
  const [adjustmentForm, setAdjustmentForm] = useState({
    adjustment_amount: "",
    effective_date: format(new Date(), "yyyy-MM-dd"),
    reason: "",
  });

  console.log(id);

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [id]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [hotelData, roomTypesData] = await Promise.all([
        hotelsAPI.getById(Number(id)),
        roomTypesAPI.getAll(Number(id)),
      ]);
      setHotel(hotelData);
      setRoomTypes(roomTypesData);
    } catch (error) {
      toast.error("Failed to load hotel details");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddAdjustment = (roomType: RoomType) => {
    setSelectedRoomType(roomType);
    setAdjustmentForm({
      adjustment_amount: "",
      effective_date: format(new Date(), "yyyy-MM-dd"),
      reason: "",
    });
    setShowAdjustmentModal(true);
  };

  const handleSubmitAdjustment = async () => {
    if (!selectedRoomType) return;

    try {
      await rateAdjustmentsAPI.create({
        room_type_id: selectedRoomType.id,
        adjustment_amount: parseFloat(adjustmentForm.adjustment_amount),
        effective_date: adjustmentForm.effective_date,
        reason: adjustmentForm.reason,
      });

      toast.success("Rate adjustment added successfully");
      setShowAdjustmentModal(false);
      fetchData(); // Refresh data to show updated effective rates
    } catch (error) {
      toast.error("Failed to add rate adjustment");
    }
  };

  const handleViewHistory = async (roomType: RoomType) => {
    try {
      const history = await rateAdjustmentsAPI.getHistory(roomType.id);
      setAdjustmentHistory(history);
      setSelectedRoomType(roomType);
      setShowHistoryModal(true);
    } catch (error) {
      toast.error("Failed to load rate history");
    }
  };

  const handleDeleteRoomType = async (roomTypeId: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await roomTypesAPI.delete(roomTypeId);
      toast.success("Room type deleted successfully");
      fetchData();
    } catch (error) {
      toast.error("Failed to delete room type");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Loading hotel details..." />
      </div>
    );
  }

  if (!hotel) {
    return <div>Hotel not found</div>;
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to="/hotels">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Hotels
        </Button>
      </Link>

      {/* Hotel Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{hotel.name}</h1>
              <p className="text-gray-600 mt-1">
                {hotel.city}, {hotel.country}
              </p>
            </div>
            <Link to={`/hotels/${hotel.id}/edit`}>
              <Button variant="secondary">
                <Edit className="w-4 h-4 mr-2" />
                Edit Hotel
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-gray-700">{hotel.description}</p>
              <div className="mt-4 space-y-2">
                {hotel.address && (
                  <p className="text-sm text-gray-600">
                    <strong>Address:</strong> {hotel.address}
                  </p>
                )}
                {hotel.phone && (
                  <p className="text-sm text-gray-600">
                    <strong>Phone:</strong> {hotel.phone}
                  </p>
                )}
                {hotel.email && (
                  <p className="text-sm text-gray-600">
                    <strong>Email:</strong> {hotel.email}
                  </p>
                )}
              </div>
            </div>
            {hotel.images && hotel.images.length > 0 && (
              <div className="grid grid-cols-3 gap-2">
                {hotel.images.map((img, idx) => (
                  <img
                    key={idx}
                    src={img}
                    alt={`${hotel.name} ${idx + 1}`}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                ))}
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Room Types Section */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Room Types</h2>
        <Link to={`/hotels/${hotel.id}/room-types/new`}>
          <Button variant="primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Room Type
          </Button>
        </Link>
      </div>

      {roomTypes.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <p className="text-gray-600">
              No room types yet. Add your first room type to get started.
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {roomTypes.map((roomType) => (
            <Card key={roomType.id} hover>
              {/* Room Type Images */}
              {roomType.images && roomType.images.length > 0 ? (
                <div className="h-48 bg-gradient-to-br from-primary-100 to-primary-200 relative">
                  <img
                    src={roomType.images[0]}
                    alt={roomType.name}
                    className="w-full h-full object-cover"
                  />
                  {roomType.images.length > 1 && (
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
                      +{roomType.images.length - 1} more
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gray-300 rounded-lg mx-auto mb-2 flex items-center justify-center">
                      <span className="text-gray-500 text-2xl">🛏️</span>
                    </div>
                    <p className="text-sm text-gray-500">No images</p>
                  </div>
                </div>
              )}

              <CardBody>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {roomType.name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {roomType.description}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewHistory(roomType)}
                    >
                      <TrendingUp className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() =>
                        handleDeleteRoomType(roomType.id, roomType.name)
                      }
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Image Gallery (if multiple images) */}
                {roomType.images && roomType.images.length > 1 && (
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    {roomType.images.slice(0, 3).map((img, idx) => (
                      <img
                        key={idx}
                        src={img}
                        alt={`${roomType.name} ${idx + 1}`}
                        className="w-full h-16 object-cover rounded cursor-pointer hover:opacity-75 transition-opacity"
                        onClick={() => window.open(img, "_blank")}
                      />
                    ))}
                  </div>
                )}

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Base Rate:</span>
                    <span className="font-medium">${roomType.base_rate}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Current Rate:</span>
                    <span className="font-semibold text-primary-600 text-lg">
                      ${roomType.effective_rate || roomType.base_rate}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Max Occupancy:</span>
                    <span>{roomType.max_occupancy} guests</span>
                  </div>
                  {roomType.size_sqm && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Size:</span>
                      <span>{roomType.size_sqm} sqm</span>
                    </div>
                  )}
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  fullWidth
                  className="mt-4"
                  onClick={() => handleAddAdjustment(roomType)}
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Add Rate Adjustment
                </Button>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Rate Adjustment Modal */}
      <Modal
        isOpen={showAdjustmentModal}
        onClose={() => setShowAdjustmentModal(false)}
        title={`Add Rate Adjustment - ${selectedRoomType?.name}`}
        footer={
          <div className="flex gap-3 justify-end">
            <Button
              variant="ghost"
              onClick={() => setShowAdjustmentModal(false)}
            >
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmitAdjustment}>
              Add Adjustment
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Input
            label="Adjustment Amount ($)"
            type="number"
            step="0.01"
            placeholder="e.g., 20.00 or -10.00"
            value={adjustmentForm.adjustment_amount}
            onChange={(e) =>
              setAdjustmentForm({
                ...adjustmentForm,
                adjustment_amount: e.target.value,
              })
            }
            required
          />
          <Input
            label="Effective Date"
            type="date"
            value={adjustmentForm.effective_date}
            onChange={(e) =>
              setAdjustmentForm({
                ...adjustmentForm,
                effective_date: e.target.value,
              })
            }
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reason <span className="text-red-500">*</span>
            </label>
            <textarea
              value={adjustmentForm.reason}
              onChange={(e) =>
                setAdjustmentForm({ ...adjustmentForm, reason: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows={3}
              placeholder="e.g., Holiday season pricing, Conference event, Maintenance discount"
              required
            />
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-900">
              Current base rate: <strong>${selectedRoomType?.base_rate}</strong>
            </p>
            <p className="text-sm text-blue-700 mt-1">
              New effective rate will be calculated as: base rate + adjustment
              amount
            </p>
          </div>
        </div>
      </Modal>

      {/* Rate History Modal */}
      <Modal
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
        title={`Rate History - ${selectedRoomType?.name}`}
        size="lg"
      >
        {adjustmentHistory.length === 0 ? (
          <p className="text-gray-600 text-center py-8">
            No rate adjustments yet.
          </p>
        ) : (
          <div className="space-y-3">
            {adjustmentHistory.map((adjustment) => (
              <div
                key={adjustment.id}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-primary-600" />
                      <span
                        className={`font-semibold ${parseFloat(adjustment.adjustment_amount) >= 0 ? "text-green-600" : "text-red-600"}`}
                      >
                        {parseFloat(adjustment.adjustment_amount) >= 0
                          ? "+"
                          : ""}
                        ${adjustment.adjustment_amount}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {adjustment.reason}
                    </p>
                  </div>
                  <div className="text-right text-sm">
                    <p className="text-gray-600">
                      Effective:{" "}
                      {format(
                        new Date(adjustment.effective_date),
                        "MMM dd, yyyy"
                      )}
                    </p>
                    <p className="text-gray-500 text-xs mt-1">
                      By: {adjustment.created_by}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default HotelDetailPage;
