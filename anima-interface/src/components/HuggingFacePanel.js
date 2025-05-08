import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, TextField, Typography, Paper, Grid, CircularProgress, Tabs, Tab, Divider, IconButton, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import ImageIcon from '@mui/icons-material/Image';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SummarizeIcon from '@mui/icons-material/Summarize';
import MemoryIcon from '@mui/icons-material/Memory';
import { useTheme } from '../contexts/ThemeContext';
import { useAnima } from '../contexts/AnimaContext';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius * 2,
  background: 'rgba(15, 20, 25, 0.85)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: '0 12px 48px rgba(0, 0, 0, 0.3)',
    transform: 'translateY(-2px)'
  }
}));

const ResultContainer = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(2),
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  background: 'rgba(30, 40, 50, 0.6)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  maxHeight: '300px',
  overflowY: 'auto',
  fontFamily: 'Roboto Mono, monospace',
  fontSize: '0.9rem',
  lineHeight: '1.5',
  whiteSpace: 'pre-wrap',
  color: theme.palette.primary.light
}));

const ImageResult = styled('img')({
  maxWidth: '100%',
  maxHeight: '300px',
  borderRadius: '8px',
  margin: '10px 0',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
});

const ModelBadge = styled(Box)(({ theme }) => ({
  display: 'inline-block',
  padding: '4px 8px',
  borderRadius: '4px',
  fontSize: '0.7rem',
  fontWeight: 'bold',
  background: theme.palette.primary.dark,
  color: theme.palette.primary.contrastText,
  marginRight: theme.spacing(1),
  marginBottom: theme.spacing(1)
}));

const PulseButton = styled(Button)(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  '&:after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 'inherit',
    boxShadow: `0 0 0 0 ${theme.palette.primary.main}`,
    animation: 'pulse 1.5s infinite',
  },
  '@keyframes pulse': {
    '0%': {
      boxShadow: `0 0 0 0 rgba(${theme.palette.primary.main}, 0.7)`
    },
    '70%': {
      boxShadow: `0 0 0 10px rgba(${theme.palette.primary.main}, 0)`
    },
    '100%': {
      boxShadow: `0 0 0 0 rgba(${theme.palette.primary.main}, 0)`
    }
  }
}));

// Main component
const HuggingFacePanel = () => {
  const { theme } = useTheme();
  const { sendMessage } = useAnima();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [modelStats, setModelStats] = useState(null);
  
  // Input states
  const [textPrompt, setTextPrompt] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [sentimentText, setSentimentText] = useState('');
  const [summarizeText, setSummarizeText] = useState('');
  const [agentTask, setAgentTask] = useState('');
  
  // Refs for animation
  const resultRef = useRef(null);
  
  // Fetch model stats on mount
  useEffect(() => {
    fetchModelStats();
    
    // Set up interval to refresh stats
    const interval = setInterval(fetchModelStats, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Scroll to result when it changes
  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [result]);
  
  const fetchModelStats = async () => {
    try {
      const response = await fetch('/api/stats');
      if (response.ok) {
        const data = await response.json();
        setModelStats(data);
      }
    } catch (err) {
      console.error('Error fetching model stats:', err);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setResult(null);
    setError(null);
    setImageUrl(null);
  };
  
  const handleGenerateText = async () => {
    if (!textPrompt.trim()) return;
    
    setLoading(true);
    setResult(null);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: textPrompt })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResult(data.result);
        // Also send to Anima for awareness
        sendMessage(`Generated text from Hugging Face: "${textPrompt}" -> ${data.result.substring(0, 100)}...`);
      } else {
        setError(data.error || 'Failed to generate text');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchModelStats();
    }
  };
  
  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) return;
    
    setLoading(true);
    setResult(null);
    setError(null);
    setImageUrl(null);
    
    try {
      const response = await fetch('/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: imagePrompt })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setImageUrl(data.imagePath);
        sendMessage(`Generated image from Hugging Face with prompt: "${imagePrompt}"`);
      } else {
        setError(data.error || 'Failed to generate image');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchModelStats();
    }
  };
  
  const handleAnalyzeSentiment = async () => {
    if (!sentimentText.trim()) return;
    
    setLoading(true);
    setResult(null);
    setError(null);
    
    try {
      const response = await fetch('/api/analyze-sentiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: sentimentText })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResult(JSON.stringify(data, null, 2));
      } else {
        setError(data.error || 'Failed to analyze sentiment');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchModelStats();
    }
  };
  
  const handleSummarizeText = async () => {
    if (!summarizeText.trim()) return;
    
    setLoading(true);
    setResult(null);
    setError(null);
    
    try {
      const response = await fetch('/api/summarize-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: summarizeText })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResult(data.summary);
      } else {
        setError(data.error || 'Failed to summarize text');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchModelStats();
    }
  };
  
  const handleExecuteTask = async () => {
    if (!agentTask.trim()) return;
    
    setLoading(true);
    setResult(null);
    setError(null);
    
    try {
      const response = await fetch('/api/execute-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task: agentTask })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResult(JSON.stringify(data.result, null, 2));
        sendMessage(`Executed Hugging Face agent task: "${agentTask}"`);
      } else {
        setError(data.error || 'Failed to execute task');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchModelStats();
    }
  };
  
  const renderTabContent = () => {
    switch (activeTab) {
      case 0: // Text Generation
        return (
          <Box>
            <Typography variant="subtitle1" color="primary.light" gutterBottom>
              Generate text with state-of-the-art language models
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              placeholder="Enter your prompt here..."
              value={textPrompt}
              onChange={(e) => setTextPrompt(e.target.value)}
              sx={{ mb: 2, background: 'rgba(0,0,0,0.2)' }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleGenerateText}
              disabled={loading || !textPrompt.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <TextFieldsIcon />}
              fullWidth
            >
              Generate Text
            </Button>
          </Box>
        );
        
      case 1: // Image Generation
        return (
          <Box>
            <Typography variant="subtitle1" color="primary.light" gutterBottom>
              Create images from text descriptions
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              placeholder="Describe the image you want to generate..."
              value={imagePrompt}
              onChange={(e) => setImagePrompt(e.target.value)}
              sx={{ mb: 2, background: 'rgba(0,0,0,0.2)' }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleGenerateImage}
              disabled={loading || !imagePrompt.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <ImageIcon />}
              fullWidth
            >
              Generate Image
            </Button>
          </Box>
        );
        
      case 2: // Sentiment Analysis
        return (
          <Box>
            <Typography variant="subtitle1" color="primary.light" gutterBottom>
              Analyze the sentiment and emotion in text
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              placeholder="Enter text to analyze sentiment..."
              value={sentimentText}
              onChange={(e) => setSentimentText(e.target.value)}
              sx={{ mb: 2, background: 'rgba(0,0,0,0.2)' }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleAnalyzeSentiment}
              disabled={loading || !sentimentText.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <SentimentSatisfiedAltIcon />}
              fullWidth
            >
              Analyze Sentiment
            </Button>
          </Box>
        );
        
      case 3: // Text Summarization
        return (
          <Box>
            <Typography variant="subtitle1" color="primary.light" gutterBottom>
              Summarize long text into concise content
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              placeholder="Enter long text to summarize..."
              value={summarizeText}
              onChange={(e) => setSummarizeText(e.target.value)}
              sx={{ mb: 2, background: 'rgba(0,0,0,0.2)' }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleSummarizeText}
              disabled={loading || !summarizeText.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <SummarizeIcon />}
              fullWidth
            >
              Summarize Text
            </Button>
          </Box>
        );
        
      case 4: // Agent Tasks
        return (
          <Box>
            <Typography variant="subtitle1" color="primary.light" gutterBottom>
              Execute complex tasks with Hugging Face agents
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              placeholder="Describe the task you want the agent to perform..."
              value={agentTask}
              onChange={(e) => setAgentTask(e.target.value)}
              sx={{ mb: 2, background: 'rgba(0,0,0,0.2)' }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleExecuteTask}
              disabled={loading || !agentTask.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <MemoryIcon />}
              fullWidth
            >
              Execute Task
            </Button>
          </Box>
        );
        
      default:
        return null;
    }
  };
  
  const renderResult = () => {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" p={3}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (error) {
      return (
        <ResultContainer sx={{ color: 'error.main' }} ref={resultRef}>
          Error: {error}
        </ResultContainer>
      );
    }
    
    if (activeTab === 1 && imageUrl) {
      return (
        <Box textAlign="center" ref={resultRef}>
          <ImageResult src={imageUrl} alt="Generated image" />
        </Box>
      );
    }
    
    if (result) {
      return (
        <ResultContainer ref={resultRef}>
          {result}
        </ResultContainer>
      );
    }
    
    return null;
  };
  
  const renderModelStats = () => {
    if (!modelStats) return null;
    
    return (
      <Box mt={3} pt={2} borderTop="1px solid rgba(255,255,255,0.1)">
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="subtitle2" color="primary.light">
            Model Usage Statistics
          </Typography>
          <Tooltip title="Refresh Stats">
            <IconButton size="small" onClick={fetchModelStats}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Grid container spacing={1}>
          <Grid item xs={12}>
            <Typography variant="caption" color="text.secondary">
              Total API Calls: {modelStats.totalCalls || 0}
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="caption" color="text.secondary" component="div">
              Recently Used Models:
            </Typography>
            <Box mt={0.5}>
              {modelStats.lastUsedModels && modelStats.lastUsedModels.map((model, index) => (
                <ModelBadge key={index}>{model}</ModelBadge>
              ))}
            </Box>
          </Grid>
        </Grid>
      </Box>
    );
  };
  
  return (
    <StyledPaper elevation={6}>
      <Typography variant="h6" color="primary.light" gutterBottom sx={{ 
        display: 'flex', 
        alignItems: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        pb: 1,
        mb: 2
      }}>
        <MemoryIcon sx={{ mr: 1 }} /> Hugging Face Integration
      </Typography>
      
      <Tabs 
        value={activeTab} 
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ 
          mb: 3,
          '& .MuiTab-root': {
            minWidth: 'auto',
            px: 2
          }
        }}
      >
        <Tab icon={<TextFieldsIcon />} label="Text" />
        <Tab icon={<ImageIcon />} label="Image" />
        <Tab icon={<SentimentSatisfiedAltIcon />} label="Sentiment" />
        <Tab icon={<SummarizeIcon />} label="Summarize" />
        <Tab icon={<MemoryIcon />} label="Agent" />
      </Tabs>
      
      {renderTabContent()}
      
      {(result || error || (activeTab === 1 && imageUrl) || loading) && (
        <Box mt={3}>
          <Divider sx={{ mb: 2, opacity: 0.3 }} />
          <Typography variant="subtitle2" color="primary.light" gutterBottom>
            Result:
          </Typography>
          {renderResult()}
        </Box>
      )}
      
      {renderModelStats()}
    </StyledPaper>
  );
};

export default HuggingFacePanel;
