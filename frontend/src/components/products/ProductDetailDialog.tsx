import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Typography,
  Box,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardMedia,
} from '@mui/material';
import {
  Close as CloseIcon,
  Image as ImageIcon,
} from '@mui/icons-material';
import { productService } from '../../services/productService';
import { photoService } from '../../services/photoService';
import type { Product, Photo } from '../../types';

interface ProductDetailDialogProps {
  productId: string;
  open: boolean;
  onClose: () => void;
}

const ProductDetailDialog: React.FC<ProductDetailDialogProps> = ({
  productId,
  open,
  onClose,
}) => {
  const { data: product, isLoading, error } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => productService.getProduct(productId),
    enabled: open && !!productId,
  });

  // Fetch photos for the product
  const { data: photos, isLoading: photosLoading } = useQuery({
    queryKey: ['product-photos', productId, product?.photos],
    queryFn: async () => {
      if (!product?.photos || product.photos.length === 0) {
        return [];
      }
      // Fetch all photos in parallel
      const photoPromises = product.photos.map(id => photoService.getPhoto(id));
      return Promise.all(photoPromises);
    },
    enabled: open && !!product && !!product.photos && product.photos.length > 0,
  });

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

  const getTypeLabel = (type: '0' | '1') => {
    return type === '0' ? 'Product' : 'Service';
  };

  const getStatusLabel = (status: '0' | '1') => {
    return status === '1' ? 'Active' : 'Disabled';
  };

  const getStatusColor = (status: '0' | '1') => {
    return status === '1' ? 'success' : 'error';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Product Details</Typography>
          <Button onClick={onClose} color="inherit" size="small">
            <CloseIcon />
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        {isLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">
            Failed to load product: {(error as Error).message}
          </Alert>
        ) : product ? (
          <Grid container spacing={3}>
            {/* Product Photos */}
            {photos && photos.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Photos ({photos.length})
                </Typography>
                <Grid container spacing={2}>
                  {photos.map((photo: Photo, index: number) => (
                    <Grid item xs={12} sm={6} md={4} key={photo.id || index}>
                      <Card>
                        <CardMedia
                          component="img"
                          height="200"
                          image={`data:${photo.content_type};base64,${photo.data}`}
                          alt={photo.filename}
                          sx={{ objectFit: 'contain', bgcolor: '#f5f5f5' }}
                        />
                        {photo.description && (
                          <Box p={1}>
                            <Typography variant="caption" color="text.secondary">
                              {photo.description}
                            </Typography>
                          </Box>
                        )}
                      </Card>
                    </Grid>
                  ))}
                </Grid>
                {photosLoading && (
                  <Box display="flex" justifyContent="center" py={2}>
                    <CircularProgress size={24} />
                  </Box>
                )}
              </Grid>
            )}

            {(!photos || photos.length === 0) && !photosLoading && (
              <Grid item xs={12}>
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  py={3}
                  sx={{ bgcolor: '#f5f5f5', borderRadius: 1 }}
                >
                  <ImageIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    No photos available
                  </Typography>
                </Box>
              </Grid>
            )}

            <Grid item xs={12}>
              <Divider />
            </Grid>

            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Reference
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {product.ref}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Name
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {product.label}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Type
              </Typography>
              <Box mt={0.5}>
                <Chip label={getTypeLabel(product.type)} size="small" variant="outlined" />
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Status
              </Typography>
              <Box mt={0.5}>
                <Chip
                  label={getStatusLabel(product.status)}
                  color={getStatusColor(product.status)}
                  size="small"
                />
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Price
              </Typography>
              <Typography variant="h6" color="primary">
                {formatPrice(product.price)}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Barcode
              </Typography>
              <Typography variant="body1" fontFamily="monospace">
                {product.barcode || '-'}
              </Typography>
            </Grid>

            {product.description && (
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {product.description}
                </Typography>
              </Grid>
            )}

            {/* Stock Information */}
            {product.stock && Object.keys(product.stock).length > 0 && (
              <>
                <Grid item xs={12}>
                  <Divider />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Stock Information
                  </Typography>
                </Grid>
                {Object.entries(product.stock).map(([warehouseId, quantity]) => (
                  <Grid item xs={12} sm={6} key={warehouseId}>
                    <Box
                      sx={{
                        p: 2,
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        Warehouse: {warehouseId}
                      </Typography>
                      <Typography variant="h6">{quantity} units</Typography>
                    </Box>
                  </Grid>
                ))}
              </>
            )}

            {/* Metadata */}
            <Grid item xs={12}>
              <Divider />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Created
              </Typography>
              <Typography variant="body2">
                {product.date_creation
                  ? new Date(product.date_creation).toLocaleString()
                  : '-'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Last Modified
              </Typography>
              <Typography variant="body2">
                {product.date_modification
                  ? new Date(product.date_modification).toLocaleString()
                  : '-'}
              </Typography>
            </Grid>
          </Grid>
        ) : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProductDetailDialog;
