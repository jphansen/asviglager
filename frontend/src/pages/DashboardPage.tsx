import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActionArea,
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  Warehouse as WarehouseIcon,
  TrendingUp as TrendingUpIcon,
  Category as CategoryIcon,
  ShoppingCart as StockIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface DashboardCardProps {
  title: string;
  icon: React.ReactNode;
  color: string;
  onClick: () => void;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  icon,
  color,
  onClick,
}) => {
  return (
    <Card>
      <CardActionArea onClick={onClick}>
        <CardContent>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: 2,
                bgcolor: color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
              }}
            >
              {icon}
            </Box>
            <Typography variant="h6">{title}</Typography>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.full_name || user?.username}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Asviglager Warehouse Management System
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Products"
            icon={<InventoryIcon sx={{ fontSize: 32 }} />}
            color="primary.main"
            onClick={() => navigate('/products')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Warehouses"
            icon={<WarehouseIcon sx={{ fontSize: 32 }} />}
            color="secondary.main"
            onClick={() => navigate('/warehouses')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Stock"
            icon={<StockIcon sx={{ fontSize: 32 }} />}
            color="success.main"
            onClick={() => navigate('/stock')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2,
                    bgcolor: 'success.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                  }}
                >
                  <TrendingUpIcon sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Stock Value
                  </Typography>
                  <Typography variant="h6">Coming Soon</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2,
                    bgcolor: 'warning.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                  }}
                >
                  <CategoryIcon sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Categories
                  </Typography>
                  <Typography variant="h6">Coming Soon</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Quick Stats
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Dashboard statistics and reports will be displayed here.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default DashboardPage;
