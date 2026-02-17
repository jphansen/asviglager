import React, { useEffect, useState } from 'react';
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
import type { WarehouseType, ContainerType } from '../../types';

const warehouseSchema = z.object({
  ref: z.string().min(1, 'Reference is required'),
  label: z.string().min(1, 'Name is required'),
  type: z.enum(['warehouse', 'location', 'container']),
  status: z.boolean(),
  short: z.string().optional(),
  description: z.string().optional(),
  address: z.string().optional(),
  zip: z.string().optional(),
  town: z.string().optional(),
  phone: z.string().optional(),
  fax: z.string().optional(),
  fk_parent: z.string().optional(),
  container_type: z.string().optional(),
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
  const [parentOptions, setParentOptions] = useState<Array<{ id: string; label: string; type: WarehouseType }>>([]);
  const [containerTypes, setContainerTypes] = useState<string[]>([]);

  const { data: warehouse, isLoading } = useQuery({
    queryKey: ['warehouse', warehouseId],
    queryFn: () => warehouseService.getWarehouse(warehouseId!),
    enabled: open && !!warehouseId,
  });

  // Load parent options and container types
  useEffect(() => {
    if (open) {
      loadParentOptions();
      loadContainerTypes();
    }
  }, [open]);

  const loadParentOptions = async () => {
    try {
      // Load warehouses for location parents
      const warehouses = await warehouseService.getByType('warehouse');
      // Load locations for container parents
      const locations = await warehouseService.getByType('location');
      
      const options = [
        ...warehouses.map(w => ({ id: w._id || w.id!, label: `${w.label} (Warehouse)`, type: 'warehouse' as WarehouseType })),
        ...locations.map(l => ({ id: l._id || l.id!, label: `${l.label} (Location)`, type: 'location' as WarehouseType })),
      ];
      setParentOptions(options);
    } catch (err) {
      console.error('Failed to load parent options:', err);
    }
  };

  const loadContainerTypes = async () => {
    try {
      const types = await warehouseService.getContainerTypes();
      setContainerTypes(types);
    } catch (err) {
      console.error('Failed to load container types:', err);
    }
  };

  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<WarehouseFormData>({
    resolver: zodResolver(warehouseSchema),
    defaultValues: {
      ref: '',
      label: '',
      type: 'warehouse',
      status: true,
      short: '',
      description: '',
      address: '',
      zip: '',
      town: '',
      phone: '',
      fax: '',
      fk_parent: '',
      container_type: '',
    },
  });

  const watchType = watch('type');
  const watchParent = watch('fk_parent');

  // Reset form when warehouse data loads
  useEffect(() => {
    if (warehouse) {
      reset({
        ref: warehouse.ref,
        label: warehouse.label,
        type: warehouse.type || 'warehouse',
        status: warehouse.status,
        short: warehouse.short || '',
        description: warehouse.description || '',
        address: warehouse.address || '',
        zip: warehouse.zip || '',
        town: warehouse.town || '',
        phone: warehouse.phone || '',
        fax: warehouse.fax || '',
        fk_parent: warehouse.fk_parent || '',
        container_type: warehouse.container_type || '',
      });
    } else if (isCreateMode) {
      reset({
        ref: '',
        label: '',
        type: 'warehouse',
        status: true,
        short: '',
        description: '',
        address: '',
        zip: '',
        town: '',
        phone: '',
        fax: '',
        fk_parent: '',
        container_type: '',
      });
    }
  }, [warehouse, isCreateMode, reset]);

  const createMutation = useMutation({
    mutationFn: (data: WarehouseFormData) => {
      // Clean up data before sending to API
      const cleanedData = {
        ...data,
        // Convert empty strings to undefined for optional fields
        short: data.short || undefined,
        description: data.description || undefined,
        address: data.address || undefined,
        zip: data.zip || undefined,
        town: data.town || undefined,
        phone: data.phone || undefined,
        fax: data.fax || undefined,
        fk_parent: data.fk_parent || undefined,
        container_type: (data.container_type as ContainerType) || undefined,
      };
      return warehouseService.createWarehouse(cleanedData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: WarehouseFormData) => {
      // Clean up data before sending to API
      const cleanedData = {
        ...data,
        // Convert empty strings to undefined for optional fields
        short: data.short || undefined,
        description: data.description || undefined,
        address: data.address || undefined,
        zip: data.zip || undefined,
        town: data.town || undefined,
        phone: data.phone || undefined,
        fax: data.fax || undefined,
        fk_parent: data.fk_parent || undefined,
        container_type: (data.container_type as ContainerType) || undefined,
      };
      return warehouseService.updateWarehouse(warehouseId!, cleanedData);
    },
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

  // Filter parent options based on selected type
  const filteredParentOptions = parentOptions.filter(option => {
    if (watchType === 'location') {
      // Locations can only have warehouse parents
      return option.type === 'warehouse';
    } else if (watchType === 'container') {
      // Containers can only have location parents
      return option.type === 'location';
    }
    return false;
  });

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
                      label="Name *"
                      fullWidth
                      error={!!errors.label}
                      helperText={errors.label?.message}
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
                      <InputLabel>Type *</InputLabel>
                      <Select {...field} label="Type *">
                        <MenuItem value="warehouse">Warehouse</MenuItem>
                        <MenuItem value="location">Location</MenuItem>
                        <MenuItem value="container">Container</MenuItem>
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

              {/* Parent Selection (for locations and containers) */}
              {(watchType === 'location' || watchType === 'container') && (
                <Grid item xs={12}>
                  <Controller
                    name="fk_parent"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.fk_parent}>
                        <InputLabel>
                          {watchType === 'location' ? 'Parent Warehouse' : 'Parent Location'} *
                        </InputLabel>
                        <Select {...field} label={`${watchType === 'location' ? 'Parent Warehouse' : 'Parent Location'} *`}>
                          <MenuItem value="">
                            <em>Select {watchType === 'location' ? 'warehouse' : 'location'}...</em>
                          </MenuItem>
                          {filteredParentOptions.map((option) => (
                            <MenuItem key={option.id} value={option.id}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.fk_parent && (
                          <FormHelperText>{errors.fk_parent.message}</FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />
                </Grid>
              )}

              {/* Container Type (for containers only) */}
              {watchType === 'container' && (
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="container_type"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.container_type}>
                        <InputLabel>Container Type</InputLabel>
                        <Select {...field} label="Container Type">
                          <MenuItem value="">
                            <em>Select container type...</em>
                          </MenuItem>
                          {containerTypes.map((type) => (
                            <MenuItem key={type} value={type}>
                              {type}
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.container_type && (
                          <FormHelperText>{errors.container_type.message}</FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />
                </Grid>
              )}

              <Grid item xs={12} sm={watchType === 'container' ? 6 : 12}>
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

              {/* Address Information (only for warehouses) */}
              {watchType === 'warehouse' && (
                <>
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

                  {/* Contact Information (only for warehouses) */}
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
                </>
              )}
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