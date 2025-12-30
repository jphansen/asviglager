import React, { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Card,
  CardMedia,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Close as CloseIcon,
  Delete as DeleteIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { productService } from '../../services/productService';
import { photoService } from '../../services/photoService';
import type { Product, Photo } from '../../types';

const productSchema = z.object({
  ref: z.string().min(1, 'Reference is required'),
  label: z.string().min(1, 'Name is required'),
  price: z.coerce.number().min(0, 'Price must be positive'),
  type: z.enum(['0', '1']),
  status: z.enum(['0', '1']),
  barcode: z.string().optional(),
  description: z.string().optional(),
});

type ProductFormData = z.infer<typeof productSchema>;

interface ProductEditDialogProps {
  productId: string;
  open: boolean;
  onClose: () => void;
}

const ProductEditDialog: React.FC<ProductEditDialogProps> = ({
  productId,
  open,
  onClose,
}) => {
  const queryClient = useQueryClient();
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  const { data: product, isLoading, error } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => productService.getProduct(productId),
    enabled: open && !!productId,
  });

  // Fetch photos for the product
  const { data: photos, refetch: refetchPhotos } = useQuery({
    queryKey: ['product-photos', productId, product?.photos],
    queryFn: async () => {
      if (!product?.photos || product.photos.length === 0) {
        return [];
      }
      const photoPromises = product.photos.map(id => photoService.getPhoto(id));
      return Promise.all(photoPromises);
    },
    enabled: open && !!product && !!product.photos && product.photos.length > 0,
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      ref: '',
      label: '',
      price: 0,
      type: '0',
      status: '1',
      barcode: '',
      description: '',
    },
  });

  // Reset form when product data loads
  useEffect(() => {
    if (product) {
      reset({
        ref: product.ref,
        label: product.label,
        price: product.price,
        type: product.type,
        status: product.status,
        barcode: product.barcode || '',
        description: product.description || '',
      });
    }
  }, [product, reset]);

  const updateMutation = useMutation({
    mutationFn: (data: ProductFormData) =>
      productService.updateProduct(productId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['product', productId] });
      onClose();
    },
  });

  const unlinkPhotoMutation = useMutation({
    mutationFn: (photoId: string) =>
      productService.unlinkPhoto(productId, photoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product', productId] });
      refetchPhotos();
    },
  });

  const onDrop = async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      try {
        setUploadingPhoto(true);
        // Convert to base64
        const base64 = await photoService.fileToBase64(file);
        
        // Upload photo
        const uploadedPhoto = await photoService.uploadPhoto({
          filename: file.name,
          data: base64,
          content_type: file.type,
          description: `Photo for ${product?.label}`,
        });

        // Link to product
        await productService.linkPhoto(productId, uploadedPhoto.id!);
        
        // Refresh product data
        queryClient.invalidateQueries({ queryKey: ['product', productId] });
        refetchPhotos();
      } catch (error) {
        console.error('Photo upload failed:', error);
        alert('Failed to upload photo. Please try again.');
      } finally {
        setUploadingPhoto(false);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    multiple: true,
  });

  const onSubmit = (data: ProductFormData) => {
    updateMutation.mutate(data);
  };

  const handleDeletePhoto = (photoId: string) => {
    if (confirm('Remove this photo from the product?')) {
      unlinkPhotoMutation.mutate(photoId);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Edit Product</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent dividers>
          {isLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">
              Failed to load product: {(error as Error).message}
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {/* Photos Section */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Photos
                </Typography>
                
                {/* Existing Photos */}
                {photos && photos.length > 0 && (
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    {photos.map((photo: Photo) => (
                      <Grid item xs={12} sm={6} md={4} key={photo.id}>
                        <Card sx={{ position: 'relative' }}>
                          <CardMedia
                            component="img"
                            height="150"
                            image={`data:${photo.content_type};base64,${photo.data}`}
                            alt={photo.filename}
                            sx={{ objectFit: 'contain', bgcolor: '#f5f5f5' }}
                          />
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeletePhoto(photo.id!)}
                            sx={{
                              position: 'absolute',
                              top: 4,
                              right: 4,
                              bgcolor: 'rgba(255,255,255,0.9)',
                              '&:hover': { bgcolor: 'rgba(255,255,255,1)' },
                            }}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}

                {/* Upload New Photos */}
                <Box
                  {...getRootProps()}
                  sx={{
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'divider',
                    borderRadius: 1,
                    p: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <input {...getInputProps()} />
                  <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    {isDragActive
                      ? 'Drop photos here...'
                      : 'Drag & drop photos here, or click to select'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Supports JPEG and PNG
                  </Typography>
                </Box>
                {uploadingPhoto && (
                  <Box display="flex" justifyContent="center" mt={2}>
                    <CircularProgress size={24} />
                  </Box>
                )}
              </Grid>

              {/* Form Fields */}
              <Grid item xs={12} sm={6}>
                <Controller
                  name="ref"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Reference *"
                      fullWidth
                      error={!!errors.ref}
                      helperText={errors.ref?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="label"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Product Name *"
                      fullWidth
                      error={!!errors.label}
                      helperText={errors.label?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="price"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Price *"
                      type="number"
                      fullWidth
                      error={!!errors.price}
                      helperText={errors.price?.message}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">€</InputAdornment>,
                      }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="barcode"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Barcode"
                      fullWidth
                      error={!!errors.barcode}
                      helperText={errors.barcode?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.type}>
                      <InputLabel>Type</InputLabel>
                      <Select {...field} label="Type">
                        <MenuItem value="0">Product</MenuItem>
                        <MenuItem value="1">Service</MenuItem>
                      </Select>
                      {errors.type && (
                        <FormHelperText>{errors.type.message}</FormHelperText>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="status"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.status}>
                      <InputLabel>Status</InputLabel>
                      <Select {...field} label="Status">
                        <MenuItem value="1">Active</MenuItem>
                        <MenuItem value="0">Disabled</MenuItem>
                      </Select>
                      {errors.status && (
                        <FormHelperText>{errors.status.message}</FormHelperText>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Description"
                      fullWidth
                      multiline
                      rows={3}
                      error={!!errors.description}
                      helperText={errors.description?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={updateMutation.isPending}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </form>

      {updateMutation.isError && (
        <Alert severity="error" sx={{ m: 2 }}>
          Failed to update product: {(updateMutation.error as Error).message}
        </Alert>
      )}
    </Dialog>
  );
};

export default ProductEditDialog;
