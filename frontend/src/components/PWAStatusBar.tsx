/**
 * PWA Status Bar Component
 */
import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Chip,
  IconButton,
  Snackbar,
  Alert,
  Tooltip,
  Fade,
  useTheme,
} from '@mui/material';
import {
  Wifi as OnlineIcon,
  WifiOff as OfflineIcon,
  Update as UpdateIcon,
  GetApp as InstallIcon,
  Sync as SyncIcon,
  CheckCircle as SyncedIcon,
} from '@mui/icons-material';
import { usePWA, useBackgroundSync } from '../hooks/usePWA';
import PWAInstallPrompt from './PWAInstallPrompt';

interface PWAStatusBarProps {
  showInstallPrompt?: boolean;
}

const PWAStatusBar: React.FC<PWAStatusBarProps> = ({ 
  showInstallPrompt = true 
}) => {
  const theme = useTheme();
  const { 
    isOnline, 
    isInstallable, 
    isUpdateAvailable, 
    updateApp,
    isInstalled 
  } = usePWA();
  const { isSupported: isSyncSupported } = useBackgroundSync();
  
  const [installPromptOpen, setInstallPromptOpen] = useState(false);
  const [updateSnackbarOpen, setUpdateSnackbarOpen] = useState(isUpdateAvailable);
  const [offlineSnackbarOpen, setOfflineSnackbarOpen] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'synced' | 'syncing' | 'pending'>('synced');

  // Show offline notification when going offline
  React.useEffect(() => {
    if (!isOnline) {
      setOfflineSnackbarOpen(true);
    }
  }, [isOnline]);

  // Show update notification when update is available
  React.useEffect(() => {
    setUpdateSnackbarOpen(isUpdateAvailable);
  }, [isUpdateAvailable]);

  // Listen for sync events
  React.useEffect(() => {
    const handleSyncStart = () => setSyncStatus('syncing');
    const handleSyncComplete = () => setSyncStatus('synced');
    const handleSyncPending = () => setSyncStatus('pending');

    // Add event listeners for custom sync events
    window.addEventListener('sync-start', handleSyncStart);
    window.addEventListener('sync-complete', handleSyncComplete);
    window.addEventListener('sync-pending', handleSyncPending);

    return () => {
      window.removeEventListener('sync-start', handleSyncStart);
      window.removeEventListener('sync-complete', handleSyncComplete);
      window.removeEventListener('sync-pending', handleSyncPending);
    };
  }, []);

  const handleInstallClick = () => {
    setInstallPromptOpen(true);
  };

  const handleUpdateClick = () => {
    updateApp();
  };

  const getStatusColor = () => {
    if (!isOnline) return 'error';
    if (syncStatus === 'pending') return 'warning';
    return 'success';
  };

  const getStatusIcon = () => {
    if (!isOnline) return <OfflineIcon />;
    if (syncStatus === 'syncing') return <SyncIcon className="rotating" />;
    if (syncStatus === 'pending') return <SyncIcon />;
    return <OnlineIcon />;
  };

  const getStatusText = () => {
    if (!isOnline) return 'Offline';
    if (syncStatus === 'syncing') return 'Syncing...';
    if (syncStatus === 'pending') return 'Sync Pending';
    return 'Online';
  };

  // Don't show status bar on desktop if app is not installed
  if (!isInstalled && window.innerWidth > 768) {
    return null;
  }

  return (
    <>
      {/* Status Bar */}
      <AppBar 
        position="static" 
        elevation={0}
        sx={{
          backgroundColor: 'transparent',
          backgroundImage: 'none',
          borderBottom: `1px solid ${theme.palette.divider}`,
          minHeight: 'auto',
        }}
      >
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          px={2}
          py={0.5}
        >
          {/* Connection Status */}
          <Tooltip title={getStatusText()}>
            <Chip
              icon={getStatusIcon()}
              label={getStatusText()}
              size="small"
              color={getStatusColor()}
              variant="outlined"
              sx={{
                fontSize: '0.75rem',
                height: 24,
                '& .rotating': {
                  animation: 'rotate 1s linear infinite',
                },
                '@keyframes rotate': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }}
            />
          </Tooltip>

          {/* Action Buttons */}
          <Box display="flex" alignItems="center" gap={1}>
            {/* Install Button */}
            {isInstallable && showInstallPrompt && (
              <Fade in={true}>
                <Tooltip title="Install App">
                  <IconButton
                    onClick={handleInstallClick}
                    size="small"
                    sx={{
                      color: theme.palette.primary.main,
                      backgroundColor: theme.palette.primary.main + '20',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.main + '30',
                      },
                    }}
                  >
                    <InstallIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Fade>
            )}

            {/* Update Button */}
            {isUpdateAvailable && (
              <Fade in={true}>
                <Tooltip title="Update Available">
                  <IconButton
                    onClick={handleUpdateClick}
                    size="small"
                    sx={{
                      color: theme.palette.warning.main,
                      backgroundColor: theme.palette.warning.main + '20',
                      '&:hover': {
                        backgroundColor: theme.palette.warning.main + '30',
                      },
                    }}
                  >
                    <UpdateIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Fade>
            )}

            {/* Sync Status Indicator */}
            {isSyncSupported && syncStatus === 'synced' && (
              <Tooltip title="All changes synced">
                <SyncedIcon 
                  fontSize="small" 
                  sx={{ color: theme.palette.success.main, opacity: 0.7 }} 
                />
              </Tooltip>
            )}
          </Box>
        </Box>
      </AppBar>

      {/* Install Prompt Dialog */}
      <PWAInstallPrompt
        open={installPromptOpen}
        onClose={() => setInstallPromptOpen(false)}
      />

      {/* Update Available Snackbar */}
      <Snackbar
        open={updateSnackbarOpen}
        autoHideDuration={null}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity="info"
          action={
            <Box display="flex" gap={1}>
              <IconButton
                size="small"
                onClick={handleUpdateClick}
                sx={{ color: 'white' }}
              >
                <UpdateIcon fontSize="small" />
              </IconButton>
            </Box>
          }
          onClose={() => setUpdateSnackbarOpen(false)}
          sx={{
            '& .MuiAlert-message': {
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            },
          }}
        >
          <UpdateIcon fontSize="small" />
          App update available! Click to refresh.
        </Alert>
      </Snackbar>

      {/* Offline Notification */}
      <Snackbar
        open={offlineSnackbarOpen && !isOnline}
        autoHideDuration={6000}
        onClose={() => setOfflineSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity="warning"
          onClose={() => setOfflineSnackbarOpen(false)}
          sx={{
            '& .MuiAlert-message': {
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            },
          }}
        >
          <OfflineIcon fontSize="small" />
          You're offline. Some features may be limited.
        </Alert>
      </Snackbar>
    </>
  );
};

export default PWAStatusBar;