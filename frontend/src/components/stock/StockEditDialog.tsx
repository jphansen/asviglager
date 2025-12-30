import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import {
  Close as CloseIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { productService } from '../../services/productService';
import type { Product, Warehouse } from '../../types';

interface StockEditDialogProps {
  open: boolean;
  product: Product;
  warehouses: Warehouse[];
  onClose: () => void;
}

const StockEditDialog: React.FC<StockEditDialogProps> = ({
  open,
  product,
  warehouses,
  onClose,
}) => {
  const queryClient = useQueryClient();
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('');
  const [stockAmount, setStockAmount] = useState<string>('');
  const [error, setError] = useState<string>('');

  const productId = product.id || product._id || '';

  const updateStockMutation = useMutation({
    mutationFn: ({ warehouseRef, items }: { warehouseRef: string; items: number }) =>
      productService.updateStock(productId, warehouseRef, { items }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['product', productId] });
      setSelectedWarehouse('');
      setStockAmount('');
      setError('');
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update stock');
    },
  });

  const removeStockMutation = useMutation({
    mutationFn: (warehouseRef: string) =>
      productService.removeStock(productId, warehouseRef),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['product', productId] });
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to remove stock location');
    },
  });

  const handleAddStock = () => {
    if (!selectedWarehouse) {
      setError('Please select a warehouse');
      return;
    }

    const items = parseFloat(stockAmount);
    if (isNaN(items) || items < 0) {
      setError('Please enter a valid stock amount (0 or greater)');
      return;
    }

    updateStockMutation.mutate({
      warehouseRef: selectedWarehouse,
      items,
    });
  };

  const handleRemoveStock = (warehouseRef: string) => {
    if (confirm(`Remove stock location: ${getWarehouseLabel(warehouseRef)}?`)) {
      removeStockMutation.mutate(warehouseRef);
    }
  };

  const getWarehouseLabel = (warehouseRef: string): string => {
    const warehouse = warehouses.find(w => w.ref === warehouseRef);
    return warehouse?.label || warehouseRef;
  };

  const getAvailableWarehouses = () => {
    return warehouses.filter(w => w.status === true);
  };

  const currentStock = product.stock_warehouse || {};

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Manage Stock - {product.label}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {product.ref}
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Current Stock */}
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            <strong>Current Stock Locations</strong>
          </Typography>
          {Object.keys(currentStock).length === 0 ? (
            <Alert severity="info">No stock locations configured</Alert>
          ) : (
            <List>
              {Object.entries(currentStock).map(([warehouseRef, stock]) => (
                <ListItem
                  key={warehouseRef}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                  }}
                >
                  <ListItemText
                    primary={getWarehouseLabel(warehouseRef)}
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.secondary">
                          Ref: {warehouseRef}
                        </Typography>
                        <br />
                        <Typography component="span" variant="body2" fontWeight="bold">
                          Stock: {stock.items} items
                        </Typography>
                      </>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      color="error"
                      onClick={() => handleRemoveStock(warehouseRef)}
                      disabled={removeStockMutation.isPending}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Add/Update Stock */}
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            <strong>Add or Update Stock</strong>
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Warehouse</InputLabel>
                <Select
                  value={selectedWarehouse}
                  onChange={(e) => setSelectedWarehouse(e.target.value)}
                  label="Warehouse"
                >
                  {getAvailableWarehouses().map((warehouse) => (
                    <MenuItem key={warehouse.ref} value={warehouse.ref}>
                      {warehouse.label} ({warehouse.ref})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Stock Amount"
                value={stockAmount}
                onChange={(e) => setStockAmount(e.target.value)}
                inputProps={{ min: 0, step: 1 }}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddStock}
                disabled={updateStockMutation.isPending}
                sx={{ height: '56px' }}
              >
                {currentStock[selectedWarehouse] ? 'Update' : 'Add'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default StockEditDialog;
