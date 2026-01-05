import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  Stack,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Warehouse as WarehouseIcon,
  LocationOn as LocationIcon,
  Inventory as ContainerIcon,
} from '@mui/icons-material';
import { warehouseService } from '../services/warehouseService';
import WarehouseDetailDialog from '../components/warehouses/WarehouseDetailDialog';
import WarehouseEditDialog from '../components/warehouses/WarehouseEditDialog';
import type { Warehouse } from '../types';

const WarehousesPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedWarehouseId, setSelectedWarehouseId] = useState<string | null>(null);
  const [editWarehouseId, setEditWarehouseId] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Debounce search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  const { data: warehouses, isLoading, error } = useQuery({
    queryKey: ['warehouses', debouncedSearch],
    queryFn: () => warehouseService.getWarehouses({ 
      search: debouncedSearch || undefined,
      limit: 100 
    }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => warehouseService.deleteWarehouse(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
    },
  });

  const getStatusColor = (status: boolean) => {
    return status ? 'success' : 'error';
  };

  const getStatusLabel = (status: boolean) => {
    return status ? 'Active' : 'Disabled';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'warehouse':
        return <WarehouseIcon fontSize="small" />;
      case 'location':
        return <LocationIcon fontSize="small" />;
      case 'container':
        return <ContainerIcon fontSize="small" />;
      default:
        return <ContainerIcon fontSize="small" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'warehouse':
        return 'primary';
      case 'location':
        return 'secondary';
      case 'container':
        return 'default';
      default:
        return 'default';
    }
  };

  const getIndentation = (type: string) => {
    switch (type) {
      case 'warehouse':
        return 0;
      case 'location':
        return 2;
      case 'container':
        return 4;
      default:
        return 0;
    }
  };

  const handleDelete = (id: string, label: string) => {
    if (confirm(`Delete warehouse "${label}"? This will soft delete the warehouse.`)) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Warehouses</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          New Warehouse
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search warehouses by name, reference, or location..."
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
          Failed to load warehouses: {(error as Error).message}
        </Alert>
      )}

      {deleteMutation.isError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to delete warehouse: {(deleteMutation.error as Error).message}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Reference</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Container Type</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : warehouses && warehouses.length > 0 ? (
              warehouses.map((warehouse: Warehouse) => (
                <TableRow key={warehouse.id || warehouse._id} hover>
                  <TableCell>
                    <Chip
                      icon={getTypeIcon(warehouse.type || 'container')}
                      label={warehouse.type || 'container'}
                      color={getTypeColor(warehouse.type || 'container') as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography 
                      variant="body2" 
                      fontWeight="medium"
                      sx={{ pl: getIndentation(warehouse.type || 'container') }}
                    >
                      {warehouse.ref}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography 
                      variant="body2"
                      sx={{ pl: getIndentation(warehouse.type || 'container') }}
                    >
                      {warehouse.label}
                    </Typography>
                    {warehouse.description && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {warehouse.description.substring(0, 50)}
                        {warehouse.description.length > 50 ? '...' : ''}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {warehouse.container_type ? (
                      <Chip
                        label={warehouse.container_type}
                        size="small"
                        variant="outlined"
                      />
                    ) : (
                      <Typography variant="body2" color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {warehouse.town || '-'}
                      {warehouse.zip && ` (${warehouse.zip})`}
                    </Typography>
                    {warehouse.short && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {warehouse.short}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(warehouse.status)}
                      color={getStatusColor(warehouse.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View">
                      <IconButton
                        size="small"
                        onClick={() => setSelectedWarehouseId(warehouse.id || warehouse._id!)}
                      >
                        <ViewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => setEditWarehouseId(warehouse.id || warehouse._id!)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(warehouse.id || warehouse._id!, warehouse.label)}
                        disabled={deleteMutation.isPending}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    {search ? 'No warehouses found matching your search' : 'No warehouses available'}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {warehouses && warehouses.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Showing {warehouses.length} warehouse{warehouses.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
      )}

      {/* Warehouse Detail Dialog */}
      {selectedWarehouseId && (
        <WarehouseDetailDialog
          warehouseId={selectedWarehouseId}
          open={!!selectedWarehouseId}
          onClose={() => setSelectedWarehouseId(null)}
        />
      )}

      {/* Warehouse Edit Dialog */}
      {editWarehouseId && (
        <WarehouseEditDialog
          warehouseId={editWarehouseId}
          open={!!editWarehouseId}
          onClose={() => setEditWarehouseId(null)}
        />
      )}

      {/* Warehouse Create Dialog */}
      {createDialogOpen && (
        <WarehouseEditDialog
          open={createDialogOpen}
          onClose={() => setCreateDialogOpen(false)}
        />
      )}
    </Container>
  );
};

export default WarehousesPage;
