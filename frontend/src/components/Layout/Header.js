import React from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Menu,
  Notifications,
  AccountCircle,
  Circle,
} from '@mui/icons-material';

const Header = ({ onSidebarToggle }) => {
  return (
    <AppBar 
      position="static" 
      elevation={1}
      sx={{ 
        bgcolor: 'background.paper', 
        color: 'text.primary',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onSidebarToggle}
          sx={{ mr: 2 }}
        >
          <Menu />
        </IconButton>

        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          WhatsApp MCP Dashboard
        </Typography>

        {/* Status indicators */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mr: 2 }}>
          <Chip
            icon={<Circle sx={{ fontSize: 12, color: '#25D366' }} />}
            label="WhatsApp Connected"
            variant="outlined"
            size="small"
            sx={{ 
              borderColor: '#25D366',
              color: '#25D366',
            }}
          />
        </Box>

        {/* User menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton color="inherit">
            <Notifications />
          </IconButton>
          <IconButton color="inherit">
            <AccountCircle />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;