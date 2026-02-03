import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { ArrowBack, Email, Visibility } from '@mui/icons-material';
import { apiService, EmailDraft } from '../services/api';
import EmailDialog from './EmailDialog';

const ReviewEmailsPage: React.FC = () => {
  const navigate = useNavigate();
  const [emails, setEmails] = useState<EmailDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<EmailDraft | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isSendingEmails, setIsSendingEmails] = useState(false);
  const [emailsSent, setEmailsSent] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(0);

  useEffect(() => {
    const loadEmails = async () => {
      try {
        setLoading(true);
        console.log('Loading draft emails for review...');
        
        const response = await apiService.reviewEmails();
        
        setEmails(response.emails);
        console.log(`Loaded ${response.total_emails} draft emails`);
        
      } catch (err) {
        console.error('Failed to load emails:', err);
        setError(err instanceof Error ? err.message : 'Failed to load emails');
      } finally {
        setLoading(false);
      }
    };

    loadEmails();
  }, []);

  const handleReviewEmail = (email: EmailDraft) => {
    setSelectedEmail(email);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedEmail(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Email Sent': return 'success';
      case 'Draft': return 'primary';
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
    setIsSendingEmails(true);
    try {
      console.log('Sending emails to all customers...');
      const response = await apiService.finalizeEmails();
      
      console.log(`Successfully sent ${response.total_emails} emails`);
      console.log('Updated emails:', response.emails[0]); // Log first email to check status
      console.log('First email status:', response.emails[0].status); // Check status specifically
      
      // Update the emails list with new status
      setEmails(response.emails);
      setEmailsSent(true); // Set emails sent state
      
      // Force a re-render by updating the key
      setForceUpdate(prev => prev + 1);
      console.log('Emails state updated, forcing re-render');
      
      // Additional force update after a short delay
      setTimeout(() => {
        setForceUpdate(prev => prev + 1);
        console.log('Additional force update applied');
      }, 100);
      
      alert(`Successfully sent ${response.total_emails} emails to customers!`);
      
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
              Loading Emails...
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 8, textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading draft emails for review...
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
            Review Customer Emails
          </Typography>
          <Box sx={{ width: 48 }} /> {/* Spacer for centering */}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Customer Email Drafts
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Review and approve personalized email drafts for {emails.length} customers
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<Email />}
            onClick={handleSendEmails}
            disabled={isSendingEmails || emailsSent}
            sx={{ mb: 3 }}
          >
            {isSendingEmails ? 'Sending Emails...' : emailsSent ? 'All Emails Sent' : 'Click here to send emails to customers'}
          </Button>
        </Box>

        <TableContainer component={Paper} sx={{ boxShadow: 3 }} key={`${emails.length}-${forceUpdate}-${Date.now()}`}>
          <Table sx={{ minWidth: 800 }} aria-label="email review table">
            <TableHead sx={{ bgcolor: 'primary.main' }}>
              <TableRow>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Customer ID</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Customer Name</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Product</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Propensity Score</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Agent</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Generated Date</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody key={`tbody-${forceUpdate}`}>
              {emails.map((email, index) => (
                <TableRow
                  key={`${email.customer_id}-${forceUpdate}`}
                  sx={{ '&:nth-of-type(odd)': { bgcolor: 'action.hover' } }}
                >
                  <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                    {email.customer_id}
                  </TableCell>
                  <TableCell>{email.customer_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={email.product_name}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={email.propensity_score.toFixed(3)}
                      color={getPropensityScoreColor(email.propensity_score) as any}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{email.agent_name}</TableCell>
                  <TableCell>
                    {new Date(email.generated_date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={email.status}
                      color={getStatusColor(email.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Review Email">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleReviewEmail(email)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
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
          <Button variant="contained" color="primary">
            Send Approved Emails
          </Button>
        </Box>
      </Container>

      {/* Email Review Dialog */}
      <EmailDialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        email={selectedEmail}
      />
    </Box>
  );
};

export default ReviewEmailsPage;
