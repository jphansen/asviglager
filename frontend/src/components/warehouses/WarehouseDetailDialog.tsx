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
} from '@mui/material';
import {
  Close as CloseIcon,
  LocationOn as LocationIcon,
  Phone as PhoneIcon,
  Fax as FaxIcon,
} from '@mui/icons-material';
import { warehouseService } from '../../services/warehouseService';

interface WarehouseDetailDialogProps {
  warehouseId: string;
  open: boolean;
  onClose: () => void;
}

const WarehouseDetailDialog: React.FC<WarehouseDetailDialogProps> = ({
  warehouseId,
  open,
  onClose,
}) => {
  const { data: warehouse, isLoading, error } = useQuery({
    queryKey: ['warehouse', warehouseId],
    queryFn: () => warehouseService.getWarehouse(warehouseId),
    enabled: open && !!warehouseId,
  });

  const getStatusLabel = (status: boolean) => {
    return status ? 'Active' : 'Disabled';
  };

  const getStatusColor = (status: boolean) => {
    return status ? 'success' : 'error';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Warehouse Details</Typography>
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
            Failed to load warehouse: {(error as Error).message}
          </Alert>
        ) : warehouse ? (
          <Grid container spacing={3}>
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
                {warehouse.ref}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Name
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {warehouse.label}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Status
              </Typography>
              <Box mt={0.5}>
                <Chip
                  label={getStatusLabel(warehouse.status)}
                  color={getStatusColor(warehouse.status)}
                  size="small"
                />
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Short Location Code
              </Typography>
              <Typography variant="body1">
                {warehouse.short || '-'}
              </Typography>
            </Grid>

            {warehouse.description && (
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {warehouse.description}
                </Typography>
              </Grid>
            )}

            {/* Address Information */}
            <Grid item xs={12}>
              <Divider />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                <LocationIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                Address
              </Typography>
            </Grid>

            {warehouse.address && (
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">
                  Street Address
                </Typography>
                <Typography variant="body2">{warehouse.address}</Typography>
              </Grid>
            )}

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Postal Code
              </Typography>
              <Typography variant="body2">{warehouse.zip || '-'}</Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Town/City
              </Typography>
              <Typography variant="body2">{warehouse.town || '-'}</Typography>
            </Grid>

            {/* Contact Information */}
            {(warehouse.phone || warehouse.fax) && (
              <>
                <Grid item xs={12}>
                  <Divider />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Contact Information
                  </Typography>
                </Grid>

                {warehouse.phone && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">
                      <PhoneIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                      Phone
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {warehouse.phone}
                    </Typography>
                  </Grid>
                )}

                {warehouse.fax && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">
                      <FaxIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                      Fax
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {warehouse.fax}
                    </Typography>
                  </Grid>
                )}
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
                {warehouse.date_creation
                  ? new Date(warehouse.date_creation).toLocaleString()
                  : '-'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">
                Last Modified
              </Typography>
              <Typography variant="body2">
                {warehouse.date_modification
                  ? new Date(warehouse.date_modification).toLocaleString()
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

export default WarehouseDetailDialog;
