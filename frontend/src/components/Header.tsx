import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
} from '@mui/material';
import {
  Print as PrintIcon,
  History as HistoryIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isHomePage = location.pathname === '/';

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <PrintIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI Printer
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {!isHomePage && (
            <Button
              color="inherit"
              startIcon={<HomeIcon />}
              onClick={() => navigate('/')}
            >
              Home
            </Button>
          )}
          
          {isHomePage && (
            <Button
              color="inherit"
              startIcon={<HistoryIcon />}
              onClick={() => navigate('/history')}
            >
              History
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
