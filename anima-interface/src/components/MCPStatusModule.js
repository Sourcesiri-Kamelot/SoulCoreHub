import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Divider, Chip, CircularProgress, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudIcon from '@mui/icons-material/Cloud';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';
import MemoryIcon from '@mui/icons-material/Memory';
import { useHuggingFace } from '../contexts/HuggingFaceContext';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius * 2,
  background: 'rgba(15, 20, 25, 0.85)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  height: '100%',
  display: 'flex',
  flexDirection: 'column'
}));

const StatusItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5),
  borderRadius: theme.shape.borderRadius,
  background: 'rgba(30, 40, 50, 0.6)',
  marginBottom: theme.spacing(1.5),
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(40, 50, 60, 0.6)',
    transform: 'translateY(-2px)'
  }
}));

const StatusIcon = styled(Box)(({ status, theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: status === 'online' ? theme.palette.success.main : 
         status === 'offline' ? theme.palette.error.main : 
         theme.palette.warning.main
}));

const MCPStatusModule = () => {
  const [mcpStatus, setMcpStatus] = useState({
    core: 'checking',
    server: 'checking',
    bridge: 'checking'
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Get Hugging Face context
  const { isConnected: hfConnected, checkConnection: checkHfConnection } = useHuggingFace();
  
  // Check MCP status on mount and periodically
  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 60000); // Check every minute
    
    return () => clearInterval(interval);
  }, []);
  
  const checkStatus = async () => {
    setIsRefreshing(true);
    
    try {
      // Check MCP Core status
      const coreStatus = await fetch('/api/mcp/status/core')
        .then(res => res.ok ? 'online' : 'offline')
        .catch(() => 'offline');
      
      // Check MCP Server status
      const serverStatus = await fetch('/api/mcp/status/server')
        .then(res => res.ok ? 'online' : 'offline')
        .catch(() => 'offline');
      
      // Check MCP Bridge status
      const bridgeStatus = await fetch('/api/mcp/status/bridge')
        .then(res => res.ok ? 'online' : 'offline')
        .catch(() => 'offline');
      
      setMcpStatus({
        core: coreStatus,
        server: serverStatus,
        bridge: bridgeStatus
      });
      
      // Also check Hugging Face connection
      checkHfConnection();
    } catch (error) {
      console.error('Error checking MCP status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };
  
  const getStatusIcon = (status) => {
    if (status === 'checking') {
      return <CircularProgress size={20} />;
    } else if (status === 'online') {
      return <CheckCircleIcon color="success" />;
    } else {
      return <ErrorIcon color="error" />;
    }
  };
  
  return (
    <StyledPaper elevation={6}>
      <Box display="flex" alignItems="center" mb={2}>
        <CloudIcon sx={{ mr: 1 }} />
        <Typography variant="h6" color="primary.light">
          Model Context Protocol
        </Typography>
      </Box>
      
      <Divider sx={{ mb: 2, opacity: 0.3 }} />
      
      <Box flex={1}>
        <StatusItem>
          <Box>
            <Typography variant="subtitle2" color="primary.light">
              MCP Core
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Core processing engine
            </Typography>
          </Box>
          <StatusIcon status={mcpStatus.core}>
            {getStatusIcon(mcpStatus.core)}
          </StatusIcon>
        </StatusItem>
        
        <StatusItem>
          <Box>
            <Typography variant="subtitle2" color="primary.light">
              MCP Server
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Communication server
            </Typography>
          </Box>
          <StatusIcon status={mcpStatus.server}>
            {getStatusIcon(mcpStatus.server)}
          </StatusIcon>
        </StatusItem>
        
        <StatusItem>
          <Box>
            <Typography variant="subtitle2" color="primary.light">
              MCP Bridge
            </Typography>
            <Typography variant="caption" color="text.secondary">
              External model bridge
            </Typography>
          </Box>
          <StatusIcon status={mcpStatus.bridge}>
            {getStatusIcon(mcpStatus.bridge)}
          </StatusIcon>
        </StatusItem>
        
        <StatusItem>
          <Box>
            <Typography variant="subtitle2" color="primary.light">
              Hugging Face
            </Typography>
            <Typography variant="caption" color="text.secondary">
              AI model provider
            </Typography>
          </Box>
          <StatusIcon status={hfConnected ? 'online' : 'offline'}>
            {hfConnected ? <MemoryIcon color="success" /> : <ErrorIcon color="error" />}
          </StatusIcon>
        </StatusItem>
      </Box>
      
      <Button 
        variant="outlined" 
        color="primary" 
        startIcon={isRefreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
        onClick={checkStatus}
        disabled={isRefreshing}
        fullWidth
        sx={{ mt: 2 }}
      >
        {isRefreshing ? 'Checking Status...' : 'Refresh Status'}
      </Button>
    </StyledPaper>
  );
};

export default MCPStatusModule;
