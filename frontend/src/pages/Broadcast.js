import React from 'react';
import { Typography, Box } from '@mui/material';

const Broadcast = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Broadcast Messages
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Send messages to multiple contacts simultaneously.
      </Typography>
    </Box>
  );
};

export default Broadcast;