import React from 'react';
import { Typography, Box } from '@mui/material';

const Settings = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Configure your dashboard preferences and integrations.
      </Typography>
    </Box>
  );
};

export default Settings;