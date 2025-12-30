import React, { useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
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
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { warehouseService } from '../../services/warehouseService';

const warehouseSchema = z.object({
  ref: z.string().min(1, 'Reference is required'),
  label: z.string().min(1, 'Name is required'),
  status: z.boolean(),
  short: z.string().optional(),
  description: z.string().optional(),
  address: z.string().optional(),
  zip: z.string().optional(),
  town: z.string().optional(),
  phone: z.string().optional(),
  fax: z.string().optional(),
});

type WarehouseFormData = z.infer<typeof warehouseSchema>;

interface WarehouseEditDialogProps {
  warehouseId?: string;
  open: boolean;
  onClose: () => void;
}

const WarehouseEditDialog: React.FC<WarehouseEditDialogProps> = ({
  warehouseId,
  open,
  onClose,
}) => {
  const queryClient = useQueryClient();
  const isCreateMode = !warehouseId;

  const { data: warehouse, isLoading } = useQuery({
    queryKey: ['warehouse', warehouseId],
    queryFn: () => warehouseService.getWarehouse(warehouseId!),
    enabled: open && !!warehouseId,
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<WarehouseFormData>({
    resolver: zodResolver(warehouseSchema),
    defaultValues: {
      ref: '',
      label: '',
      status: true,
      short: '',
      description: '',
      address: '',
      zip: '',
      town: '',
      phone: '',
      fax: '',
    },
  });

  // Reset form when warehouse data loads
  useEffect(() => {
    if (warehouse) {
      reset({
        ref: warehouse.ref,
        label: warehouse.label,
        status: warehouse.status,
        short: warehouse.short || '',
        description: warehouse.description || '',
        address: warehouse.address || '',
        zip: warehouse.zip || '',
        town: warehouse.town || '',
        phone: warehouse.phone || '',
        fax: warehouse.fax || '',
      });
    } else if (isCreateMode) {
      reset({
        ref: '',
        label: '',
        status: true,
        short: '',
        description: '',
        address: '',
        zip: '',
        town: '',
        phone: '',
        fax: '',
      });
    }
  }, [warehouse, isCreateMode, reset]);

  const createMutation = useMutation({
    mutationFn: (data: WarehouseFormData) =>
      warehouseService.createWarehouse(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: WarehouseFormData) =>
      warehouseService.updateWarehouse(warehouseId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      queryClient.invalidateQueries({ queryKey: ['warehouse', warehouseId] });
      onClose();
    },
  });

  const onSubmit = (data: WarehouseFormData) => {
    if (isCreateMode) {
      createMutation.mutate(data);
    } else {
      updateMutation.mutate(data);
    }
  };

  const isPending = createMutation.isPending || updateMutation.isPending;
  const error = createMutation.error || updateMutation.error;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {isCreateMode ? 'Create Warehouse' : 'Edit Warehouse'}
          </Typography>
          <Button onClick={onClose} color="inherit" size="small">
            <CloseIcon />
          </Button>
        </Box>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent dividers>
          {isLoading && !isCreateMode ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Basic Information
                </Typography>
              </Grid>

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
                      label="Warehouse Name *"
                      fullWidth
                      error={!!errors.label}
                      helperText={errors.label?.message}
                    />
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
                      <Select 
                        {...field} 
                        value={field.value ? 'true' : 'false'}
                        onChange={(e) => field.onChange(e.target.value === 'true')}
                        label="Status"
                      >
                        <MenuItem value="true">Active</MenuItem>
                        <MenuItem value="false">Disabled</MenuItem>
                      </Select>
                      {errors.status && (
                        <FormHelperText>{errors.status.message}</FormHelperText>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="short"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Short Location Code"
                      fullWidth
                      error={!!errors.short}
                      helperText={errors.short?.message || 'E.g., HED01 for Hedensted01'}
                    />
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
                      rows={2}
                      error={!!errors.description}
                      helperText={errors.description?.message}
                    />
                  )}
                />
              </Grid>

              {/* Address Information */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Address
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <Controller
                  name="address"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Street Address"
                      fullWidth
                      error={!!errors.address}
                      helperText={errors.address?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="zip"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Postal Code"
                      fullWidth
                      error={!!errors.zip}
                      helperText={errors.zip?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="town"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Town/City"
                      fullWidth
                      error={!!errors.town}
                      helperText={errors.town?.message}
                    />
                  )}
                />
              </Grid>

              {/* Contact Information */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Contact Information
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="phone"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Phone"
                      fullWidth
                      error={!!errors.phone}
                      helperText={errors.phone?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="fax"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Fax"
                      fullWidth
                      error={!!errors.fax}
                      helperText={errors.fax?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending}
          >
            {isPending ? (
              <CircularProgress size={24} />
            ) : isCreateMode ? (
              'Create'
            ) : (
              'Save Changes'
            )}
          </Button>
        </DialogActions>
      </form>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          Failed to {isCreateMode ? 'create' : 'update'} warehouse:{' '}
          {(error as Error).message}
        </Alert>
      )}
    </Dialog>
  );
};

export default WarehouseEditDialog;
