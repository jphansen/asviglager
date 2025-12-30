import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  InputAdornment,
  CircularProgress,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Image as ImageIcon,
} from '@mui/icons-material';
import { productService } from '../services/productService';
import ProductDetailDialog from '../components/products/ProductDetailDialog';
import ProductEditDialog from '../components/products/ProductEditDialog';
import type { Product } from '../types';

const ProductsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);
  const [editProductId, setEditProductId] = useState<string | null>(null);
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  const { data: products, isLoading, error } = useQuery({
    queryKey: ['products', debouncedSearch],
    queryFn: () => productService.getProducts({ 
      search: debouncedSearch || undefined,
      limit: 100 
    }),
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

  const getStatusColor = (status: '0' | '1') => {
    return status === '1' ? 'success' : 'error';
  };

  const getStatusLabel = (status: '0' | '1') => {
    return status === '1' ? 'Active' : 'Disabled';
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Products</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            // TODO: Open create dialog
            alert('Create product dialog - to be implemented');
          }}
        >
          New Product
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search products by name, reference, or barcode..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load products: {(error as Error).message}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Reference</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Barcode</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Photos</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : products && products.length > 0 ? (
              products.map((product: Product) => (
                <TableRow key={product.id || product._id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {product.ref}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{product.label}</Typography>
                    {product.description && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {product.description.substring(0, 50)}
                        {product.description.length > 50 ? '...' : ''}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={getTypeLabel(product.type)} 
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{formatPrice(product.price)}</TableCell>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {product.barcode || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(product.status)}
                      color={getStatusColor(product.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {product.photos && product.photos.length > 0 ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <ImageIcon fontSize="small" color="action" />
                        <Typography variant="body2">{product.photos.length}</Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View">
                      <IconButton
                        size="small"
                        onClick={() => setSelectedProductId(product.id || product._id!)}
                      >
                        <ViewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => setEditProductId(product.id || product._id!)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => {
                          if (confirm(`Delete product ${product.label}?`)) {
                            alert('Delete functionality - to be implemented');
                          }
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    {search ? 'No products found matching your search' : 'No products available'}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {products && products.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Showing {products.length} product{products.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
      )}

      {/* Product Detail Dialog */}
      {selectedProductId && (
        <ProductDetailDialog
          productId={selectedProductId}
          open={!!selectedProductId}
          onClose={() => setSelectedProductId(null)}
        />
      )}

      {/* Product Edit Dialog */}
      {editProductId && (
        <ProductEditDialog
          productId={editProductId}
          open={!!editProductId}
          onClose={() => setEditProductId(null)}
        />
      )}
    </Container>
  );
};

export default ProductsPage;
