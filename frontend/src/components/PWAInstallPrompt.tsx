/**
 * PWA Install Prompt Component
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Slide,
  Alert,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Close as CloseIcon,
  GetApp as InstallIcon,
  PhoneAndroid as MobileIcon,
  Computer as DesktopIcon,
  Wifi as OnlineIcon,
  WifiOff as OfflineIcon,
  Update as UpdateIcon,
} from '@mui/icons-material';
import { TransitionProps } from '@mui/material/transitions';
import { usePWA } from '../hooks/usePWA';

const Transition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

interface PWAInstallPromptProps {
  open: boolean;
  onClose: () => void;
}

const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { promptInstall, isOnline } = usePWA();
  const [installing, setInstalling] = useState(false);
  const [error, setError] = useState<string>('');

  const handleInstall = async () => {
    setInstalling(true);
    setError('');

    try {
      await promptInstall();
      onClose();
    } catch (err) {
      setError('Installation failed. Please try again.');
      console.error('Install failed:', err);
    } finally {
      setInstalling(false);
    }
  };

  const features = [
    {
      icon: isMobile ? <MobileIcon /> : <DesktopIcon />,
      title: 'Offline Access',
      description: 'Use AI Printer even without internet connection'
    },
    {
      icon: <InstallIcon />,
      title: 'Native Experience',
      description: 'Runs like a native app on your device'
    },
    {
      icon: isOnline ? <OnlineIcon /> : <OfflineIcon />,
      title: 'Background Sync',
      description: 'Automatically sync when connection is restored'
    }
  ];

  return (
    <Dialog
      open={open}
      TransitionComponent={Transition}
      keepMounted
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          backgroundImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            <InstallIcon />
            <Typography variant="h6" fontWeight="bold">
              Install AI Printer
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
            sx={{ color: 'white' }}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
          Get the full AI Printer experience by installing our app on your device.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 3 }}>
          {features.map((feature, index) => (
            <Box
              key={index}
              display="flex"
              alignItems="center"
              gap={2}
              sx={{ mb: 2 }}
            >
              <Box
                sx={{
                  p: 1,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {feature.icon}
              </Box>
              <Box>
                <Typography variant="subtitle1" fontWeight="600">
                  {feature.title}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  {feature.description}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>

        <Typography variant="body2" sx={{ opacity: 0.7, textAlign: 'center' }}>
          The app will be added to your home screen and work offline.
        </Typography>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button
          onClick={onClose}
          sx={{
            color: 'white',
            borderColor: 'rgba(255, 255, 255, 0.5)',
            '&:hover': {
              borderColor: 'white',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            }
          }}
          variant="outlined"
        >
          Maybe Later
        </Button>
        <Button
          onClick={handleInstall}
          disabled={installing}
          variant="contained"
          startIcon={installing ? <UpdateIcon /> : <InstallIcon />}
          sx={{
            backgroundColor: 'white',
            color: theme.palette.primary.main,
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
            },
            '&:disabled': {
              backgroundColor: 'rgba(255, 255, 255, 0.6)',
            }
          }}
        >
          {installing ? 'Installing...' : 'Install App'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PWAInstallPrompt;