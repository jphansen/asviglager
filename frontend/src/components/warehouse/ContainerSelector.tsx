import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Typography,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import { warehouseService } from '../../services/warehouseService';
import type { Warehouse } from '../../types';

interface ContainerSelectorProps {
  value?: string; // Selected container ref
  onChange: (containerRef: string, containerData: Warehouse | null) => void;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
  showFullPath?: boolean; // Display "Warehouse > Location > Container" format
}

/**
 * Cascading selector for warehouse hierarchy: Warehouse → Location → Container
 * Automatically loads children when parent is selected
 */
const ContainerSelector: React.FC<ContainerSelectorProps> = ({
  value,
  onChange,
  label = 'Container',
  required = false,
  disabled = false,
  error = false,
  helperText,
  showFullPath = true,
}) => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [locations, setLocations] = useState<Warehouse[]>([]);
  const [containers, setContainers] = useState<Warehouse[]>([]);
  
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('');
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [selectedContainer, setSelectedContainer] = useState<string>('');
  
  const [loading, setLoading] = useState(true);
  const [loadingLocations, setLoadingLocations] = useState(false);
  const [loadingContainers, setLoadingContainers] = useState(false);

  // Load warehouses on mount
  useEffect(() => {
    loadWarehouses();
  }, []);

  // If value is provided, load the full hierarchy
  useEffect(() => {
    if (value && warehouses.length > 0 && containers.length > 0) {
      const container = containers.find(c => c.ref === value);
      if (container) {
        setSelectedContainer(container.ref);
      }
    }
  }, [value, warehouses, containers]);

  const loadWarehouses = async () => {
    try {
      setLoading(true);
      const data = await warehouseService.getByType('warehouse');
      setWarehouses(data);
      
      // Auto-select first warehouse if only one
      if (data.length === 1) {
        const warehouseId = data[0]._id || data[0].id!;
        setSelectedWarehouse(warehouseId);
        loadLocations(warehouseId);
      }
    } catch (err) {
      console.error('Failed to load warehouses:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadLocations = async (warehouseId: string) => {
    try {
      setLoadingLocations(true);
      setLocations([]);
      setContainers([]);
      setSelectedLocation('');
      setSelectedContainer('');
      
      const data = await warehouseService.getChildren(warehouseId);
      setLocations(data);
      
      // Auto-select first location if only one
      if (data.length === 1) {
        const locationId = data[0]._id || data[0].id!;
        setSelectedLocation(locationId);
        loadContainers(locationId);
      }
    } catch (err) {
      console.error('Failed to load locations:', err);
    } finally {
      setLoadingLocations(false);
    }
  };

  const loadContainers = async (locationId: string) => {
    try {
      setLoadingContainers(true);
      setContainers([]);
      setSelectedContainer('');
      
      const data = await warehouseService.getChildren(locationId);
      setContainers(data);
    } catch (err) {
      console.error('Failed to load containers:', err);
    } finally {
      setLoadingContainers(false);
    }
  };

  const handleWarehouseChange = (event: SelectChangeEvent) => {
    const warehouseId = event.target.value;
    setSelectedWarehouse(warehouseId);
    setSelectedLocation('');
    setSelectedContainer('');
    onChange('', null);
    
    if (warehouseId) {
      loadLocations(warehouseId);
    }
  };

  const handleLocationChange = (event: SelectChangeEvent) => {
    const locationId = event.target.value;
    setSelectedLocation(locationId);
    setSelectedContainer('');
    onChange('', null);
    
    if (locationId) {
      loadContainers(locationId);
    }
  };

  const handleContainerChange = (event: SelectChangeEvent) => {
    const containerRef = event.target.value;
    setSelectedContainer(containerRef);
    
    const container = containers.find(c => c.ref === containerRef);
    onChange(containerRef, container || null);
  };

  const getFullPath = (): string => {
    if (!selectedContainer) return '';
    
    const warehouse = warehouses.find(w => (w._id || w.id) === selectedWarehouse);
    const location = locations.find(l => (l._id || l.id) === selectedLocation);
    const container = containers.find(c => c.ref === selectedContainer);
    
    const parts = [
      warehouse?.label,
      location?.label,
      container?.label
    ].filter(Boolean);
    
    return parts.join(' > ');
  };

  if (loading) {
    return (
      <Box display="flex" alignItems="center" gap={2}>
        <CircularProgress size={20} />
        <Typography variant="body2" color="text.secondary">
          Loading warehouses...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Warehouse Selector */}
      <FormControl fullWidth margin="normal" required={required} disabled={disabled}>
        <InputLabel>Warehouse</InputLabel>
        <Select
          value={selectedWarehouse}
          onChange={handleWarehouseChange}
          label="Warehouse"
        >
          <MenuItem value="">
            <em>Select warehouse...</em>
          </MenuItem>
          {warehouses.map((warehouse) => (
            <MenuItem key={warehouse._id || warehouse.id} value={warehouse._id || warehouse.id}>
              {warehouse.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Location Selector */}
      {selectedWarehouse && (
        <FormControl fullWidth margin="normal" required={required} disabled={disabled || loadingLocations}>
          <InputLabel>Location</InputLabel>
          <Select
            value={selectedLocation}
            onChange={handleLocationChange}
            label="Location"
            disabled={loadingLocations}
          >
            <MenuItem value="">
              <em>{loadingLocations ? 'Loading...' : 'Select location...'}</em>
            </MenuItem>
            {locations.map((location) => (
              <MenuItem key={location._id || location.id} value={location._id || location.id}>
                {location.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Container Selector */}
      {selectedLocation && (
        <FormControl 
          fullWidth 
          margin="normal" 
          required={required} 
          disabled={disabled || loadingContainers}
          error={error}
        >
          <InputLabel>{label}</InputLabel>
          <Select
            value={selectedContainer}
            onChange={handleContainerChange}
            label={label}
            disabled={loadingContainers}
          >
            <MenuItem value="">
              <em>{loadingContainers ? 'Loading...' : 'Select container...'}</em>
            </MenuItem>
            {containers.map((container) => (
              <MenuItem key={container._id || container.id} value={container.ref}>
                {container.label}
                {container.container_type && ` (${container.container_type})`}
              </MenuItem>
            ))}
          </Select>
          {helperText && (
            <Typography variant="caption" color={error ? 'error' : 'text.secondary'} sx={{ mt: 0.5, ml: 1.5 }}>
              {helperText}
            </Typography>
          )}
        </FormControl>
      )}

      {/* Display full path */}
      {showFullPath && selectedContainer && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, ml: 1.5 }}>
          Path: {getFullPath()}
        </Typography>
      )}
    </Box>
  );
};

export default ContainerSelector;
