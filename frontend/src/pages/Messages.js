import React from 'react';
import { Typography, Box } from '@mui/material';

const Messages = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Messages
      </Typography>
      <Typography variant="body1" color="text.secondary">
        View and manage all WhatsApp conversations here.
      </Typography>
    </Box>
  );
};

export default Messages;