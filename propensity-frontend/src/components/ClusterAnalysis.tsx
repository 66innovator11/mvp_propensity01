import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Box,
  Container,
  Chip,
  CircularProgress,
  Alert,
  Button
} from '@mui/material';

interface ClusterResult {
  product_id: number;
  product_name: string;
  business_use: string;
  cluster_count: number;
  image_path: string;
  high_propensity_customers: number;
  conversion_potential: string;
}

interface PipelineResponse {
  status: string;
  message: string;
  cluster_results: ClusterResult[];
  total_products_analyzed: number;
  execution_time: string;
}

const ClusterAnalysis: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [clusterData, setClusterData] = useState<ClusterResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());

  // Handle image loading errors
  const handleImageError = (productId: number) => {
    setImageErrors(prev => new Set(prev).add(productId));
  };

  // Handle cluster card click
  const handleClusterClick = (productName: string) => {
    // Convert product name to URL-friendly format
    const urlProductName = productName.toLowerCase().replace(' ', '-');
    navigate(`/cluster-details/${urlProductName}`);
  };

  useEffect(() => {
    const loadClusterData = async () => {
      try {
        setLoading(true);
        
        // Try to get data from navigation state first
        if (location.state && location.state.clusterData) {
          setClusterData(location.state.clusterData);
        } else {
          // Fallback to insurance product data if no navigation state
          const insuranceData: ClusterResult[] = [
            {
              product_id: 1,
              product_name: "Term Life",
              business_use: "Identify customers needing pure life protection coverage for income replacement",
              cluster_count: 4,
              image_path: "/clusters/term_life_clusters.jpg",
              high_propensity_customers: 2156,
              conversion_potential: "High"
            },
            {
              product_id: 2,
              product_name: "Critical Illness",
              business_use: "Target customers for critical illness coverage and health protection plans",
              cluster_count: 5,
              image_path: "/clusters/critical_illness_clusters.jpg",
              high_propensity_customers: 1834,
              conversion_potential: "High"
            },
            {
              product_id: 3,
              product_name: "Annuity",
              business_use: "Find customers interested in retirement income and pension solutions",
              cluster_count: 3,
              image_path: "/clusters/annuity_clusters.jpg",
              high_propensity_customers: 923,
              conversion_potential: "Medium"
            },
            {
              product_id: 4,
              product_name: "Endowment",
              business_use: "Identify customers for savings-oriented life insurance with maturity benefits",
              cluster_count: 4,
              image_path: "/clusters/endowment_clusters.jpg",
              high_propensity_customers: 1456,
              conversion_potential: "Medium"
            },
            {
              product_id: 5,
              product_name: "Unit Linked",
              business_use: "Target customers for investment-linked insurance with market-linked returns",
              cluster_count: 6,
              image_path: "/clusters/unit_linked_clusters.jpg",
              high_propensity_customers: 789,
              conversion_potential: "High"
            },
            {
              product_id: 6,
              product_name: "Whole Life",
              business_use: "Find customers seeking lifelong protection with cash value accumulation",
              cluster_count: 4,
              image_path: "/clusters/whole_life_clusters.jpg",
              high_propensity_customers: 1123,
              conversion_potential: "Medium"
            }
          ];
          setClusterData(insuranceData);
        }
      } catch (err) {
        setError('Failed to load cluster analysis data');
      } finally {
        setLoading(false);
      }
    };

    loadClusterData();
  }, [location.state]);

  const getConversionPotentialColor = (potential: string) => {
    switch (potential) {
      case 'High': return 'success';
      case 'Medium': return 'warning';
      case 'Low': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'center' }}>
              Cluster Data Analysis
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 8, textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading cluster analysis...
          </Typography>
        </Container>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'center' }}>
              Cluster Data Analysis
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 8 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button variant="contained" onClick={() => window.location.href = '/'}>
            Back to Upload
          </Button>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'center' }}>
            Cluster Data Analysis
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Insurance Product Customer Clusters
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Analysis of {clusterData.length} insurance products showing customer segments with high propensity to buy
          </Typography>
        </Box>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
          {clusterData.map((cluster) => (
            <Box key={cluster.product_id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6
                  }
                }}
                onClick={() => handleClusterClick(cluster.product_name)}
              >
                <CardMedia
                  component="img"
                  image={imageErrors.has(cluster.product_id) ? "/cluster graph.jpg" : cluster.image_path}
                  alt={`${cluster.product_name} Cluster Analysis`}
                  onError={() => handleImageError(cluster.product_id)}
                  sx={{ 
                    height: 200,
                    objectFit: 'cover',
                    bgcolor: 'primary.main'
                  }}
                />
                
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {cluster.product_name}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {cluster.business_use}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Clusters Found:
                    </Typography>
                    <Typography variant="h6" color="primary.main">
                      {cluster.cluster_count}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      High Propensity Customers:
                    </Typography>
                    <Typography variant="h6" color="primary.main">
                      {cluster.high_propensity_customers.toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Conversion Potential:
                    </Typography>
                    <Chip 
                      label={cluster.conversion_potential}
                      color={getConversionPotentialColor(cluster.conversion_potential) as any}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button 
            variant="outlined" 
            onClick={() => window.location.href = '/'}
            sx={{ mr: 2 }}
          >
            Back to Upload
          </Button>
          <Button 
            variant="contained"
            onClick={() => window.location.reload()}
          >
            Refresh Analysis
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default ClusterAnalysis;
