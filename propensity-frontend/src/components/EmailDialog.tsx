import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Paper
} from '@mui/material';
import { Close, Email, Person } from '@mui/icons-material';
import { EmailDraft } from '../services/api';

interface EmailDialogProps {
  open: boolean;
  onClose: () => void;
  email: EmailDraft | null;
}

const EmailDialog: React.FC<EmailDialogProps> = ({ open, onClose, email }) => {
  if (!email) return null;

  const getPropensityScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: {
          minHeight: '600px',
          maxHeight: '80vh'
        }
      }}
    >
      <DialogTitle sx={{ 
        bgcolor: 'primary.main', 
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Box>
          <Typography variant="h6" component="div">
            Email Review
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {email.customer_name} - {email.product_name}
          </Typography>
        </Box>
        <IconButton onClick={onClose} sx={{ color: 'white' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {/* Email Header Information */}
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Person color="primary" />
              <Typography variant="body1" fontWeight="bold">
                {email.customer_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ({email.customer_id})
              </Typography>
            </Box>
            <Chip
              label={`Score: ${email.propensity_score.toFixed(3)}`}
              color={getPropensityScoreColor(email.propensity_score) as any}
              size="small"
            />
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Email color="primary" />
              <Typography variant="body2" color="text.secondary">
                Subject: {email.subject}
              </Typography>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Generated: {email.generated_date}
            </Typography>
          </Box>
        </Paper>

        {/* Email Content */}
        <Paper sx={{ p: 3, bgcolor: 'white' }}>
          <Typography variant="h6" gutterBottom>
            Email Content
          </Typography>
          <Box 
            sx={{ 
              bgcolor: 'grey.50', 
              p: 3, 
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'grey.200'
            }}
          >
            <Typography 
              variant="body1" 
              component="pre" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                fontFamily: 'inherit',
                fontSize: 'inherit',
                lineHeight: 1.6
              }}
            >
              {email.email_content}
            </Typography>
          </Box>
        </Paper>

        {/* Agent Information */}
        <Paper sx={{ p: 2, mt: 3, bgcolor: 'info.light' }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Assigned Agent:</strong> {email.agent_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Contact:</strong> {email.agent_contact}
          </Typography>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ p: 3, bgcolor: 'grey.50' }}>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
        <Button onClick={onClose} variant="contained" color="primary">
          Approve Email
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EmailDialog;
