import { useState, FormEvent, useEffect } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { ArrowLeft, Upload, X } from "lucide-react";
import toast from "react-hot-toast";
import { roomTypesAPI, hotelsAPI } from "@/api/client";
import type { Hotel } from "@/types";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import Loading from "@/components/ui/Loading";

const RoomTypeFormPage = () => {
  const navigate = useNavigate();
  const { hotelId, roomTypeId } = useParams<{
    hotelId: string;
    roomTypeId?: string;
  }>();
  const isEditMode = !!roomTypeId;

  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [hotel, setHotel] = useState<Hotel | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    base_rate: "",
    max_occupancy: "2",
    size_sqm: "",
  });
  const [images, setImages] = useState<File[]>([]);
  const [existingImages, setExistingImages] = useState<string[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);

  useEffect(() => {
    fetchData();
  }, [hotelId, roomTypeId]);

  const fetchData = async () => {
    try {
      setIsFetching(true);

      // Fetch hotel
      const hotelData = await hotelsAPI.getById(Number(hotelId));
      setHotel(hotelData);

      // If edit mode, fetch room type
      if (isEditMode && roomTypeId) {
        const roomType = await roomTypesAPI.getById(Number(roomTypeId));
        setFormData({
          name: roomType.name,
          description: roomType.description || "",
          base_rate: roomType.base_rate,
          max_occupancy: String(roomType.max_occupancy),
          size_sqm: roomType.size_sqm ? String(roomType.size_sqm) : "",
        });
        setExistingImages(roomType.images || []);
      }
    } catch (error) {
      toast.error("Failed to load data");
      navigate("/hotels");
    } finally {
      setIsFetching(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const totalImages = existingImages.length + images.length + files.length;

    if (totalImages > 3) {
      toast.error("Maximum 3 images allowed");
      return;
    }

    setImages([...images, ...files]);

    // Create previews
    files.forEach((file) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreviews((prev) => [...prev, reader.result as string]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeNewImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
    setImagePreviews(imagePreviews.filter((_, i) => i !== index));
  };

  const removeExistingImage = (index: number) => {
    setExistingImages(existingImages.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const formDataToSend = new FormData();

      // Append fields
      if (!isEditMode) {
        formDataToSend.append("hotel_id", hotelId!);
      }
      formDataToSend.append("name", formData.name);
      if (formData.description)
        formDataToSend.append("description", formData.description);
      formDataToSend.append("base_rate", formData.base_rate);
      formDataToSend.append("max_occupancy", formData.max_occupancy);
      if (formData.size_sqm)
        formDataToSend.append("size_sqm", formData.size_sqm);

      // Append images
      images.forEach((file) => {
        formDataToSend.append("images", file);
      });

      if (isEditMode) {
        formDataToSend.append("replace_images", "false");
        await roomTypesAPI.update(Number(roomTypeId), formDataToSend);
        toast.success("Room type updated successfully");
      } else {
        await roomTypesAPI.create(formDataToSend);
        toast.success("Room type created successfully");
      }

      navigate(`/hotels/${hotelId}`);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Operation failed";
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  if (isFetching) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading size="lg" text="Loading..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to={`/hotels/${hotelId}`}>
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to {hotel?.name}
        </Button>
      </Link>

      {/* Form Card */}
      <Card>
        <CardHeader>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEditMode ? "Edit Room Type" : "Create New Room Type"}
          </h1>
          <p className="text-gray-600 mt-1">Hotel: {hotel?.name}</p>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Room Type Name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="e.g., Deluxe Suite"
              />

              <Input
                label="Base Rate (USD)"
                name="base_rate"
                type="number"
                step="0.01"
                value={formData.base_rate}
                onChange={handleInputChange}
                required
                placeholder="e.g., 100.00"
              />

              <Input
                label="Maximum Occupancy"
                name="max_occupancy"
                type="number"
                min="1"
                value={formData.max_occupancy}
                onChange={handleInputChange}
                required
                placeholder="e.g., 2"
              />

              <Input
                label="Size (sqm)"
                name="size_sqm"
                type="number"
                min="1"
                value={formData.size_sqm}
                onChange={handleInputChange}
                placeholder="e.g., 35"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Describe the room type..."
              />
            </div>

            {/* Existing Images */}
            {isEditMode && existingImages.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Images
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {existingImages.map((img, index) => (
                    <div key={index} className="relative">
                      <img
                        src={img}
                        alt={`Existing ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={() => removeExistingImage(index)}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Images (Max 3 total)
              </label>

              {imagePreviews.length > 0 && (
                <div className="grid grid-cols-3 gap-4 mb-4">
                  {imagePreviews.map((preview, index) => (
                    <div key={index} className="relative">
                      <img
                        src={preview}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={() => removeNewImage(index)}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {existingImages.length + images.length < 3 && (
                <label className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary-500 transition-colors">
                  <div className="text-center">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      Click to upload images
                    </p>
                    <p className="text-xs text-gray-500">
                      PNG, JPG, WEBP (max 3)
                    </p>
                  </div>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </label>
              )}
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-3 justify-end pt-4 border-t">
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate(`/hotels/${hotelId}`)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" isLoading={isLoading}>
                {isEditMode ? "Update Room Type" : "Create Room Type"}
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>
    </div>
  );
};

export default RoomTypeFormPage;
