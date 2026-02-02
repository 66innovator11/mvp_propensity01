import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  CircularProgress,
  Alert,
  Button,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { ArrowBack, Email, Phone } from '@mui/icons-material';
import { apiService, Customer, ClusterDetailsResponse } from '../services/api';

const ClusterDetailsPage: React.FC = () => {
  const { productName } = useParams<{ productName: string }>();
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [productTitle, setProductTitle] = useState<string>('');
  const [isSendingEmails, setIsSendingEmails] = useState(false);

  useEffect(() => {
    const loadClusterDetails = async () => {
      if (!productName) {
        setError('Product name not specified');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        console.log(`Loading cluster details for: ${productName}`);
        
        const response: ClusterDetailsResponse = await apiService.getClusterDetails(productName);
        
        setCustomers(response.customers);
        setProductTitle(response.product_name);
        console.log(`Loaded ${response.total_customers} customers for ${response.product_name}`);
        
      } catch (err) {
        console.error('Failed to load cluster details:', err);
        setError(err instanceof Error ? err.message : 'Failed to load cluster details');
      } finally {
        setLoading(false);
      }
    };

    loadClusterDetails();
  }, [productName]);

  const getRiskProfileColor = (profile: string) => {
    switch (profile) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  const getPropensityScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const handleBack = () => {
    navigate('/cluster-analysis');
  };

  const handleSendEmails = async () => {
    if (!productName) {
      setError('Product name not specified');
      return;
    }

    setIsSendingEmails(true);
    try {
      console.log(`Sending emails for product: ${productName}`);
      const response = await apiService.sendEmails(productName);
      
      console.log(`Emails generated successfully: ${response.total_emails} emails`);
      
      // Navigate to review emails page
      navigate('/review-emails');
      
    } catch (err) {
      console.error('Failed to send emails:', err);
      setError(err instanceof Error ? err.message : 'Failed to send emails');
    } finally {
      setIsSendingEmails(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <AppBar position="static">
          <Toolbar>
            <IconButton color="inherit" onClick={handleBack} sx={{ mr: 2 }}>
              <ArrowBack />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Loading Customer Details...
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 8, textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading customer details...
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
            <IconButton color="inherit" onClick={handleBack} sx={{ mr: 2 }}>
              <ArrowBack />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Error
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 8 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button variant="contained" onClick={handleBack}>
            Back to Cluster Analysis
          </Button>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton color="inherit" onClick={handleBack} sx={{ mr: 2 }}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'center' }}>
            Customer Details for {productTitle}
          </Typography>
          <Box sx={{ width: 48 }} /> {/* Spacer for centering */}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {productTitle} - Customer Details
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Showing {customers.length} high-propensity customers with detailed information
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<Email />}
            onClick={handleSendEmails}
            disabled={isSendingEmails}
            sx={{ mb: 3 }}
          >
            {isSendingEmails ? 'Generating Emails...' : 'Send Emails'}
          </Button>
        </Box>

        <TableContainer component={Paper} sx={{ boxShadow: 3 }}>
          <Table sx={{ minWidth: 1200 }} aria-label="customer details table">
            <TableHead sx={{ bgcolor: 'primary.main' }}>
              <TableRow>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Customer ID</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Name</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Address</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Propensity Score</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Insurance Product</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Existing Products</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Age</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Annual Income</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Risk Profile</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Contact</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers.map((customer) => (
                <TableRow
                  key={customer.customer_id}
                  sx={{ '&:nth-of-type(odd)': { bgcolor: 'action.hover' } }}
                >
                  <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                    {customer.customer_id}
                  </TableCell>
                  <TableCell>{customer.name}</TableCell>
                  <TableCell sx={{ maxWidth: 200, wordBreak: 'break-word' }}>
                    {customer.address}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={customer.propensity_score.toFixed(3)}
                      color={getPropensityScoreColor(customer.propensity_score) as any}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{customer.insurance_product}</TableCell>
                  <TableCell>
                    {customer.existing_products.length > 0 ? (
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {customer.existing_products.map((product, index) => (
                          <Chip
                            key={index}
                            label={product}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.75rem' }}
                          />
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        None
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{customer.age}</TableCell>
                  <TableCell>{customer.annual_income}</TableCell>
                  <TableCell>
                    <Chip
                      label={customer.risk_profile}
                      color={getRiskProfileColor(customer.risk_profile) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Tooltip title={customer.email}>
                        <IconButton size="small" color="primary">
                          <Email fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={customer.phone}>
                        <IconButton size="small" color="primary">
                          <Phone fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button variant="outlined" onClick={handleBack} sx={{ mr: 2 }}>
            Back to Cluster Analysis
          </Button>
          <Button variant="contained" onClick={() => window.print()}>
            Print Report
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default ClusterDetailsPage;
