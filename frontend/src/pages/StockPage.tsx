import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  Pagination,
} from '@mui/material';
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { productService } from '../services/productService';
import { warehouseService } from '../services/warehouseService';
import type { Product } from '../types';
import StockEditDialog from '../components/stock/StockEditDialog';

const StockPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [page, setPage] = useState(1);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [containerPaths, setContainerPaths] = useState<Record<string, string>>({});
  
  const itemsPerPage = 50;

  // Debounce search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // Reset to first page when search changes
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  const { data: products, isLoading: productsLoading, error: productsError } = useQuery({
    queryKey: ['products', debouncedSearch, page],
    queryFn: () => productService.getProducts({ 
      search: debouncedSearch || undefined,
      skip: (page - 1) * itemsPerPage,
      limit: itemsPerPage
    }),
  });

  const { data: warehouses, isLoading: warehousesLoading } = useQuery({
    queryKey: ['warehouses'],
    queryFn: () => warehouseService.getWarehouses(),
  });

  // Load hierarchy paths for all containers referenced in products
  React.useEffect(() => {
    const loadContainerPaths = async () => {
      if (!products || !warehouses) return;

      const containerRefs = new Set<string>();
      products.forEach(product => {
        if (product.stock_warehouse) {
          Object.keys(product.stock_warehouse).forEach(ref => containerRefs.add(ref));
        }
      });

      const paths: Record<string, string> = {};
      for (const ref of containerRefs) {
        try {
          const container = warehouses.find(w => w.ref === ref);
          if (container && container.id) {
            const hierarchyPath = await warehouseService.getHierarchyPath(container.id);
            paths[ref] = hierarchyPath.map(item => item.label).join(' > ');
          } else {
            paths[ref] = ref; // Fallback to ref if container not found
          }
        } catch (error) {
          paths[ref] = ref; // Fallback on error
        }
      }
      setContainerPaths(paths);
    };

    loadContainerPaths();
  }, [products, warehouses]);

  const handleEditStock = (product: Product) => {
    setSelectedProduct(product);
    setEditDialogOpen(true);
  };

  const handleCloseEditDialog = () => {
    setEditDialogOpen(false);
    setSelectedProduct(null);
  };

  const getTotalStock = (product: Product): number => {
    if (!product.stock_warehouse) return 0;
    return Object.values(product.stock_warehouse).reduce(
      (sum, stock) => sum + stock.items,
      0
    );
  };

  const getContainerLabel = (warehouseRef: string): string => {
    // Return full hierarchy path if available, otherwise fallback to warehouse label or ref
    return containerPaths[warehouseRef] || getWarehouseLabel(warehouseRef);
  };

  const getWarehouseLabel = (warehouseRef: string): string => {
    const warehouse = warehouses?.find(w => w.ref === warehouseRef);
    return warehouse?.label || warehouseRef;
  };

  if (productsLoading || warehousesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (productsError) {
    return (
      <Alert severity="error">
        Failed to load products: {(productsError as Error).message}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <InventoryIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h4">Stock Management</Typography>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search by reference, name, or barcode..."
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

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Reference</strong></TableCell>
              <TableCell><strong>Product Name</strong></TableCell>
              <TableCell><strong>Barcode</strong></TableCell>
              <TableCell align="center"><strong>Total Stock</strong></TableCell>
              <TableCell><strong>Stock by Location</strong></TableCell>
              <TableCell align="center"><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {!products || products.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="text.secondary" py={4}>
                    {debouncedSearch ? 'No products found matching your search' : 'No products available'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              products.map((product) => {
                const productId = product.id || product._id;
                const totalStock = getTotalStock(product);

                return (
                  <TableRow key={productId} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {product.ref}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{product.label}</Typography>
                      {product.status === '0' && (
                        <Chip label="Disabled" size="small" color="error" sx={{ ml: 1 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {product.barcode || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={totalStock}
                        color={totalStock > 0 ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {product.stock_warehouse && Object.keys(product.stock_warehouse).length > 0 ? (
                        <Box display="flex" flexWrap="wrap" gap={1}>
                          {Object.entries(product.stock_warehouse).map(([warehouseRef, stock]) => (
                            <Chip
                              key={warehouseRef}
                              label={`${getContainerLabel(warehouseRef)}: ${stock.items}`}
                              size="small"
                              variant="outlined"
                              title={`Container: ${warehouseRef}`}
                            />
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No stock locations
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditStock(product)}
                        title="Manage stock"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {products && products.length > 0 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination 
            count={products.length === itemsPerPage ? page + 1 : page}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
      )}

      {selectedProduct && (
        <StockEditDialog
          open={editDialogOpen}
          product={selectedProduct}
          warehouses={warehouses || []}
          onClose={handleCloseEditDialog}
        />
      )}
    </Box>
  );
};

export default StockPage;
