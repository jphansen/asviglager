# Photo Management API

## Overview
The photo management system allows storing product images separately from product data, with products maintaining references (IDs) to their photos.

## Architecture

### Collections
- **photos**: Stores photo data (base64 encoded images with metadata)
- **products**: Contains a `photos` field with an array of photo IDs

### Photo Model
```python
{
  "_id": ObjectId,
  "filename": str,
  "content_type": str,  # e.g., "image/jpeg"
  "data": str,  # Base64 encoded image
  "description": str,  # Optional
  "file_size": int,  # In bytes
  "date_creation": datetime,
  "uploaded_by": str
}
```

### Product Photos Field
```python
{
  "photos": ["photo_id_1", "photo_id_2", ...]  # Array of photo IDs
}
```

## API Endpoints

### Photo Endpoints

#### Upload Photo
```http
POST /api/v1/photos
Content-Type: application/json
Authorization: Bearer <token>

{
  "filename": "product_image.jpg",
  "content_type": "image/jpeg",
  "data": "base64_encoded_image_data",
  "description": "Front view"
}
```

#### List Photos (Metadata Only)
```http
GET /api/v1/photos
Authorization: Bearer <token>

Response: List of photos without image data (for performance)
```

#### Get Single Photo (With Data)
```http
GET /api/v1/photos/{photo_id}
Authorization: Bearer <token>

Response: Complete photo with base64 image data
```

#### Delete Photo
```http
DELETE /api/v1/photos/{photo_id}
Authorization: Bearer <token>
```

### Product-Photo Relationship Endpoints

#### Add Photo to Product
```http
POST /api/v1/products/{product_id}/photos/{photo_id}
Authorization: Bearer <token>
```

#### Remove Photo from Product
```http
DELETE /api/v1/products/{product_id}/photos/{photo_id}
Authorization: Bearer <token>
```

#### Get Product's Photos
```http
GET /api/v1/products/{product_id}/photos
Authorization: Bearer <token>

Response: ["photo_id_1", "photo_id_2", ...]
```

## Flutter Integration

### Workflow for Adding Photos to Products

1. **Take/Select Photo in Flutter**
2. **Convert to Base64**
3. **Upload to Photos Endpoint** → Get photo_id
4. **Link to Product** using product_id and photo_id
5. **Display** by fetching photo data

### Example Flutter Flow

```dart
// 1. Take photo
File imageFile = await takePicture();

// 2. Convert to base64
String base64Image = base64Encode(imageFile.readAsBytesSync());

// 3. Upload photo
PhotoResponse photo = await photoService.uploadPhoto(
  filename: "product.jpg",
  contentType: "image/jpeg",
  data: base64Image,
);

// 4. Link to product
await productService.addPhotoToProduct(productId, photo.id);

// 5. Retrieve when needed
List<String> photoIds = await productService.getProductPhotos(productId);
for (String photoId in photoIds) {
  PhotoResponse photo = await photoService.getPhoto(photoId);
  // Decode base64 and display
  Image.memory(base64Decode(photo.data));
}
```

## Benefits of This Design

1. **Separation of Concerns**: Photos are managed independently
2. **Reusability**: Same photo can be referenced by multiple products if needed
3. **Efficient Listing**: Products can be listed without loading heavy image data
4. **Flexible**: Easy to add/remove photos without modifying product core data
5. **Scalable**: Can be migrated to file storage (S3, etc.) later without changing product schema

## Notes

- Images are stored as base64 strings for simplicity
- For production at scale, consider using GridFS or external storage (S3)
- The `photos` array uses `$addToSet` to prevent duplicates
- Deleting a photo doesn't cascade delete it from products (orphan references possible)
