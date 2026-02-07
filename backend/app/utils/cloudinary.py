import cloudinary
import cloudinary.uploader
from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


async def upload_image(file: UploadFile, folder: str = "hotel-management") -> str:
    """
    Upload a single image to Cloudinary.
    
    Args:
        file: The uploaded file object
        folder: Cloudinary folder name
        
    Returns:
        str: The secure URL of the uploaded image
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
            allowed_formats=["jpg", "jpeg", "png", "webp"],
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},  # Limit max size
                {"quality": "auto"},  # Automatic quality optimization
                {"fetch_format": "auto"}  # Automatic format selection
            ]
        )
        
        return result.get("secure_url")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


async def upload_multiple_images(
    files: List[UploadFile],
    folder: str = "hotel-management",
    max_files: int = 3
) -> List[str]:
    """
    Upload multiple images to Cloudinary.
    
    Args:
        files: List of uploaded file objects
        folder: Cloudinary folder name
        max_files: Maximum number of files allowed
        
    Returns:
        List[str]: List of secure URLs of uploaded images
        
    Raises:
        HTTPException: If validation or upload fails
    """
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_files} images allowed"
        )
    
    uploaded_urls = []
    
    for file in files:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not an image"
            )
        
        # Upload the image
        url = await upload_image(file, folder)
        uploaded_urls.append(url)
    
    return uploaded_urls


def delete_image(image_url: str) -> bool:
    """
    Delete an image from Cloudinary using its URL.
    
    Args:
        image_url: The secure URL of the image
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{format}
        parts = image_url.split("/")
        
        if "cloudinary.com" not in image_url:
            return False
        
        # Get the public_id (including folder path)
        public_id_with_ext = "/".join(parts[7:])  # Everything after 'upload/v{version}/'
        public_id = public_id_with_ext.rsplit(".", 1)[0]  # Remove extension
        
        # Delete from Cloudinary
        result = cloudinary.uploader.destroy(public_id)
        
        return result.get("result") == "ok"
        
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False


def delete_multiple_images(image_urls: List[str]) -> int:
    """
    Delete multiple images from Cloudinary.
    
    Args:
        image_urls: List of secure URLs
        
    Returns:
        int: Number of successfully deleted images
    """
    deleted_count = 0
    
    for url in image_urls:
        if delete_image(url):
            deleted_count += 1
    
    return deleted_count
