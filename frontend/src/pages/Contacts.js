import React from 'react';
import { Typography, Box } from '@mui/material';

const Contacts = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Contacts
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Manage your WhatsApp contacts and their information.
      </Typography>
    </Box>
  );
};

export default Contacts;