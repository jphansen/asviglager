import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Paper,
} from '@mui/material';
import {
  Search as SearchIcon,
  QrCode as BarcodeIcon,
  Inventory as InventoryIcon,
  Description as DescriptionIcon,
  AttachMoney as PriceIcon,
} from '@mui/icons-material';
import { productService } from '../services/productService';

const BarcodeLookupPage: React.FC = () => {
  const [barcode, setBarcode] = useState<string>('');
  const [searchBarcode, setSearchBarcode] = useState<string>('');

  const {
    data: product,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['productByBarcode', searchBarcode],
    queryFn: () => productService.getProductByBarcode(searchBarcode),
    enabled: !!searchBarcode,
    retry: false,
  });

  const handleSearch = () => {
    if (barcode.trim()) {
      setSearchBarcode(barcode.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleClear = () => {
    setBarcode('');
    setSearchBarcode('');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        <BarcodeIcon sx={{ verticalAlign: 'middle', mr: 2, fontSize: 36 }} />
        Barcode Lookup
      </Typography>

      {/* Search Section */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Enter Barcode
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Enter a barcode to lookup product information. Example: 6921815628880 (OnePlus Pad 3)
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={8} md={9}>
              <TextField
                fullWidth
                label="Barcode"
                value={barcode}
                onChange={(e) => setBarcode(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter barcode (e.g., 6921815628880)"
                InputProps={{
                  startAdornment: <BarcodeIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
                disabled={isLoading}
              />
            </Grid>
            <Grid item xs={12} sm={4} md={3}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleSearch}
                disabled={!barcode.trim() || isLoading}
                startIcon={isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                sx={{ height: '56px' }}
              >
                {isLoading ? 'Searching...' : 'Lookup'}
              </Button>
            </Grid>
          </Grid>

          {searchBarcode && (
            <Box sx={{ mt: 2 }}>
              <Chip
                label={`Searching for: ${searchBarcode}`}
                onDelete={handleClear}
                color="primary"
                variant="outlined"
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Results Section */}
      {isLoading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={handleClear}>
              Clear
            </Button>
          }
        >
          Product not found for barcode: {searchBarcode}
        </Alert>
      )}

      {product && !isLoading && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <InventoryIcon sx={{ mr: 1 }} />
              Product Found
            </Typography>
            
            <Divider sx={{ my: 2 }} />

            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                  <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
                    Basic Information
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Product Name
                    </Typography>
                    <Typography variant="body1" fontWeight="medium" gutterBottom>
                      {product.label}
                    </Typography>

                    <Typography variant="caption" color="text.secondary" display="block">
                      Reference
                    </Typography>
                    <Typography variant="body1" fontFamily="monospace" gutterBottom>
                      {product.ref}
                    </Typography>

                    <Typography variant="caption" color="text.secondary" display="block">
                      Barcode
                    </Typography>
                    <Typography variant="body1" fontFamily="monospace" gutterBottom>
                      {searchBarcode}
                    </Typography>

                    <Typography variant="caption" color="text.secondary" display="block">
                      Type
                    </Typography>
                    <Chip
                      label={product.type === '0' ? 'Product' : 'Service'}
                      size="small"
                      color={product.type === '0' ? 'primary' : 'secondary'}
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </Paper>
              </Grid>

              {/* Price & Description */}
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                  <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <PriceIcon fontSize="small" sx={{ mr: 1 }} />
                    Pricing
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Price
                    </Typography>
                    <Typography variant="h5" color="primary" gutterBottom>
                      ${product.price.toFixed(2)}
                    </Typography>

                    {product.price_ttc && (
                      <>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Price (TTC)
                        </Typography>
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                          ${product.price_ttc.toFixed(2)}
                        </Typography>
                      </>
                    )}
                  </Box>

                  {product.description && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        <DescriptionIcon fontSize="small" sx={{ mr: 1 }} />
                        Description
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {product.description}
                      </Typography>
                    </>
                  )}
                </Paper>
              </Grid>

              {/* Stock Information */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Stock Information
                  </Typography>
                  
                  {product.stock_warehouse && Object.keys(product.stock_warehouse).length > 0 ? (
                    <Grid container spacing={2}>
                      {Object.entries(product.stock_warehouse).map(([warehouseRef, stock]) => (
                        <Grid item xs={12} sm={6} md={4} key={warehouseRef}>
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Warehouse
                            </Typography>
                            <Typography variant="body2" fontWeight="medium" gutterBottom>
                              {warehouseRef}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Stock Quantity
                            </Typography>
                            <Typography variant="h6" color={stock.items > 0 ? 'success.main' : 'error.main'}>
                              {stock.items} items
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  ) : (
                    <Alert severity="info">
                      No stock information available for this product.
                    </Alert>
                  )}
                </Paper>
              </Grid>

              {/* Status & Metadata */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Status & Metadata
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Status
                      </Typography>
                      <Chip
                        label={product.status === '1' ? 'Enabled' : 'Disabled'}
                        color={product.status === '1' ? 'success' : 'error'}
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Buy Status
                      </Typography>
                      <Chip
                        label={product.status_buy === '1' ? 'Can Buy' : 'Cannot Buy'}
                        color={product.status_buy === '1' ? 'info' : 'default'}
                        size="small"
                      />
                    </Grid>
                    {product.date_creation && (
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Created
                        </Typography>
                        <Typography variant="body2">
                          {new Date(product.date_creation).toLocaleDateString()}
                        </Typography>
                      </Grid>
                    )}
                    {product.date_modification && (
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Last Modified
                        </Typography>
                        <Typography variant="body2">
                          {new Date(product.date_modification).toLocaleDateString()}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </Paper>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button variant="outlined" onClick={handleClear}>
                Clear Search
              </Button>
              <Button variant="contained" onClick={() => refetch()}>
                Refresh
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      {!product && !isLoading && !error && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              How to Use Barcode Lookup
            </Typography>
            <Typography variant="body2" paragraph>
              1. Enter a barcode in the search field above (e.g., 6921815628880)
            </Typography>
            <Typography variant="body2" paragraph>
              2. Press Enter or click the "Lookup" button to search
            </Typography>
            <Typography variant="body2" paragraph>
              3. The system will display product information including name, description, price, and stock levels
            </Typography>
            <Typography variant="body2">
              4. Use this feature to quickly find product details by scanning or entering barcodes
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default BarcodeLookupPage;