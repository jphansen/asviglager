import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
} from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

interface DeleteConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  itemName?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting?: boolean;
}

const DeleteConfirmDialog: React.FC<DeleteConfirmDialogProps> = ({
  open,
  title,
  message,
  itemName,
  onConfirm,
  onCancel,
  isDeleting = false,
}) => {
  return (
    <Dialog
      open={open}
      onClose={isDeleting ? undefined : onCancel}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="error" />
          {title}
        </Box>
      </DialogTitle>
      <DialogContent>
        <Alert severity="warning" sx={{ mb: 2 }}>
          This action cannot be undone!
        </Alert>
        <Typography variant="body1" gutterBottom>
          {message}
        </Typography>
        {itemName && (
          <Box
            sx={{
              mt: 2,
              p: 2,
              bgcolor: 'background.default',
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Item to delete:
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {itemName}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button
          onClick={onCancel}
          disabled={isDeleting}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          disabled={isDeleting}
          variant="contained"
          color="error"
          autoFocus
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteConfirmDialog;
