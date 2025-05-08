import React, { useContext, useState, useEffect, useRef } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { fileApi } from '../services/apiService';
import websocketService from '../services/websocketService';

// Icons
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import FolderIcon from '@mui/icons-material/Folder';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CircularProgress from '@mui/icons-material/CircularProgress';

const SectionContainer = styled(motion.div)`
  background: rgba(10, 10, 26, 0.7);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.3);
  padding: 1.5rem;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-medium), var(--glow-soft);
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(106, 17, 203, 0.3);
`;

const SectionTitle = styled.h2`
  font-family: var(--font-display);
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: var(--glow-soft);
`;

const TabsContainer = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const Tab = styled.button`
  background: ${props => props.active ? 'rgba(106, 17, 203, 0.3)' : 'rgba(10, 10, 26, 0.5)'};
  border: 1px solid ${props => props.active ? 'rgba(106, 17, 203, 0.5)' : 'rgba(106, 17, 203, 0.2)'};
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-speed);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: rgba(106, 17, 203, 0.2);
    border-color: rgba(106, 17, 203, 0.4);
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const UploadArea = styled.div`
  border: 2px dashed rgba(106, 17, 203, 0.3);
  border-radius: var(--border-radius);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-speed);
  background: rgba(10, 10, 26, 0.3);
  margin-bottom: 1.5rem;
  
  &:hover {
    border-color: rgba(106, 17, 203, 0.5);
    background: rgba(10, 10, 26, 0.5);
  }
  
  svg {
    font-size: 3rem;
    color: rgba(106, 17, 203, 0.7);
    margin-bottom: 1rem;
  }
`;

const UploadText = styled.div`
  font-size: 1.1rem;
  color: var(--primary-light);
  margin-bottom: 0.5rem;
`;

const UploadSubtext = styled.div`
  font-size: 0.9rem;
  color: rgba(248, 249, 250, 0.7);
`;

const HiddenInput = styled.input`
  display: none;
`;

const FilesContainer = styled.div`
  overflow-y: auto;
  flex: 1;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(10, 10, 26, 0.3);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(106, 17, 203, 0.5);
    border-radius: 2px;
  }
`;

const FilesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const FileItem = styled(motion.div)`
  background: rgba(10, 10, 26, 0.5);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.2);
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  
  &:hover {
    background: rgba(10, 10, 26, 0.7);
    border-color: rgba(106, 17, 203, 0.3);
  }
`;

const FileIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: ${props => getFileColor(props.type)};
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    color: white;
    font-size: 1.5rem;
  }
`;

const FileInfo = styled.div`
  flex: 1;
`;

const FileName = styled.div`
  font-size: 1rem;
  color: var(--primary-light);
  margin-bottom: 0.25rem;
`;

const FileDetails = styled.div`
  font-size: 0.8rem;
  color: rgba(248, 249, 250, 0.7);
  display: flex;
  gap: 1rem;
`;

const FileStatus = styled.div`
  font-size: 0.8rem;
  color: ${props => {
    switch (props.status) {
      case 'processing':
        return '#f39c12';
      case 'completed':
        return '#2ecc71';
      case 'error':
        return '#e74c3c';
      default:
        return 'rgba(248, 249, 250, 0.7)';
    }
  }};
`;

const FileActions = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const FileActionButton = styled.button`
  background: rgba(10, 10, 26, 0.7);
  border: 1px solid rgba(106, 17, 203, 0.2);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all var(--transition-speed);
  opacity: ${props => props.disabled ? 0.5 : 1};
  
  &:hover {
    background: ${props => props.disabled ? 'rgba(10, 10, 26, 0.7)' : 'rgba(106, 17, 203, 0.2)'};
    border-color: ${props => props.disabled ? 'rgba(106, 17, 203, 0.2)' : 'rgba(106, 17, 203, 0.4)'};
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const GenerateContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const GenerateInput = styled.textarea`
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 1rem;
  font-size: 0.9rem;
  min-height: 150px;
  resize: none;
  
  &:focus {
    outline: none;
    border-color: rgba(106, 17, 203, 0.5);
    box-shadow: 0 0 0 2px rgba(106, 17, 203, 0.2);
  }
  
  &::placeholder {
    color: rgba(248, 249, 250, 0.5);
  }
`;

const GenerateButton = styled.button`
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  border: none;
  color: white;
  border-radius: var(--border-radius);
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all var(--transition-speed);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: ${props => props.disabled ? 0.7 : 1};
  
  &:hover {
    opacity: ${props => props.disabled ? 0.7 : 0.9};
    transform: ${props => props.disabled ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => props.disabled ? 'none' : '0 5px 15px rgba(106, 17, 203, 0.3)'};
  }
  
  &:active {
    transform: ${props => props.disabled ? 'none' : 'translateY(0)'};
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const GeneratedContent = styled.div`
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 1rem;
  font-size: 0.9rem;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(10, 10, 26, 0.3);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(106, 17, 203, 0.5);
    border-radius: 2px;
  }
`;

const GeneratedActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(248, 249, 250, 0.5);
  text-align: center;
  padding: 2rem;
`;

const LoadingSpinner = styled(CircularProgress)`
  color: ${props => props.color || 'var(--accent-1)'};
  animation: spin 1.5s linear infinite;
  
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: rgba(10, 10, 26, 0.5);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.5rem;
`;

const ProgressFill = styled.div`
  height: 100%;
  width: ${props => props.progress}%;
  background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
  border-radius: 2px;
  transition: width 0.3s ease;
`;

// Helper function to get file color based on type
function getFileColor(type) {
  switch (type) {
    case 'pdf':
      return '#e74c3c';
    case 'doc':
    case 'docx':
      return '#3498db';
    case 'xls':
    case 'xlsx':
      return '#2ecc71';
    case 'ppt':
    case 'pptx':
      return '#f39c12';
    case 'txt':
      return '#95a5a6';
    case 'img':
    case 'png':
    case 'jpg':
    case 'jpeg':
      return '#9b59b6';
    default:
      return '#7f8c8d';
  }
}

// Helper function to format file size
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

const FileInteractionSection = () => {
  const { addNotification } = useContext(AnimaContext);
  const [activeTab, setActiveTab] = useState('files');
  const [files, setFiles] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingFiles, setProcessingFiles] = useState(new Set());
  const fileInputRef = useRef(null);
  
  // Load files on component mount
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const fileList = await fileApi.getAll();
        setFiles(fileList);
      } catch (error) {
        console.error('Failed to load files:', error);
        addNotification('error', 'File Loading Failed', 'Could not load files.');
      }
    };
    
    loadFiles();
    
    // Set up WebSocket listener for file updates
    websocketService.connect().catch(error => {
      console.error('Failed to connect to WebSocket:', error);
    });
    
    const handleFileUpdate = (data) => {
      // Reload files when a file is updated
      loadFiles();
      
      // Update processing status
      if (data.fileId && data.status === 'completed') {
        setProcessingFiles(prev => {
          const newSet = new Set(prev);
          newSet.delete(data.fileId);
          return newSet;
        });
        
        addNotification('success', 'File Processing Complete', `File ${data.fileName} has been processed.`);
      }
    };
    
    websocketService.on('file_update', handleFileUpdate);
    
    // Clean up listener when component unmounts
    return () => {
      websocketService.off('file_update', handleFileUpdate);
    };
  }, [addNotification]);
  
  // Handle file upload
  const handleFileUpload = async (event) => {
    const uploadedFiles = Array.from(event.target.files);
    if (uploadedFiles.length === 0) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      // Create form data
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      // Upload files
      const result = await fileApi.upload(formData, progress => {
        setUploadProgress(progress);
      });
      
      // Add uploaded files to processing set
      const newProcessingFiles = new Set(processingFiles);
      result.files.forEach(file => {
        newProcessingFiles.add(file.id);
      });
      setProcessingFiles(newProcessingFiles);
      
      // Update files list
      setFiles(prev => [...prev, ...result.files]);
      
      addNotification('success', 'Files Uploaded', `${result.files.length} files uploaded successfully.`);
      
      // Process each file
      result.files.forEach(async file => {
        try {
          await fileApi.process(file.id);
        } catch (error) {
          console.error(`Failed to process file ${file.id}:`, error);
          
          // Remove from processing set
          setProcessingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(file.id);
            return newSet;
          });
          
          addNotification('error', 'Processing Failed', `Could not process file ${file.name}.`);
        }
      });
    } catch (error) {
      console.error('Failed to upload files:', error);
      addNotification('error', 'Upload Failed', 'Could not upload files.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      
      // Clear input
      if (fileInputRef.current) {
        fileInputRef.current.value = null;
      }
    }
  };
  
  // Handle file delete
  const handleFileDelete = async (fileId) => {
    try {
      await fileApi.delete(fileId);
      
      // Update files list
      setFiles(prev => prev.filter(file => file.id !== fileId));
      
      addNotification('success', 'File Deleted', 'File deleted successfully.');
    } catch (error) {
      console.error('Failed to delete file:', error);
      addNotification('error', 'Deletion Failed', 'Could not delete file.');
    }
  };
  
  // Handle file download
  const handleFileDownload = async (fileId, fileName) => {
    try {
      const blob = await fileApi.download(fileId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      addNotification('success', 'File Downloaded', 'File downloaded successfully.');
    } catch (error) {
      console.error('Failed to download file:', error);
      addNotification('error', 'Download Failed', 'Could not download file.');
    }
  };
  
  // Handle file processing
  const handleFileProcess = async (fileId) => {
    try {
      // Add to processing set
      setProcessingFiles(prev => new Set([...prev, fileId]));
      
      await fileApi.process(fileId);
      
      addNotification('info', 'Processing Started', 'File processing has started.');
    } catch (error) {
      console.error('Failed to process file:', error);
      
      // Remove from processing set
      setProcessingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
      
      addNotification('error', 'Processing Failed', 'Could not process file.');
    }
  };
  
  // Handle generate content
  const handleGenerateContent = async () => {
    if (!prompt) return;
    
    setIsGenerating(true);
    
    try {
      const result = await fileApi.generateContent(prompt);
      setGeneratedContent(result.content);
      
      addNotification('success', 'Content Generated', 'Content generated successfully.');
    } catch (error) {
      console.error('Failed to generate content:', error);
      addNotification('error', 'Generation Failed', 'Could not generate content.');
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Handle copy generated content
  const handleCopyContent = () => {
    navigator.clipboard.writeText(generatedContent);
    addNotification('info', 'Content Copied', 'Generated content copied to clipboard.');
  };
  
  // Handle download generated content
  const handleDownloadContent = () => {
    const element = document.createElement('a');
    const file = new Blob([generatedContent], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `generated-content-${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    addNotification('success', 'Content Downloaded', 'Generated content downloaded successfully.');
  };
  
  // Format date
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString();
  };
  
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        duration: 0.5,
        when: "beforeChildren",
        staggerChildren: 0.1
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3 }
    }
  };
  
  return (
    <SectionContainer
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <SectionHeader>
        <SectionTitle>File Interaction</SectionTitle>
      </SectionHeader>
      
      <TabsContainer>
        <Tab 
          active={activeTab === 'files'} 
          onClick={() => setActiveTab('files')}
        >
          <InsertDriveFileIcon />
          Files
        </Tab>
        <Tab 
          active={activeTab === 'generate'} 
          onClick={() => setActiveTab('generate')}
        >
          <AutoAwesomeIcon />
          Generate
        </Tab>
      </TabsContainer>
      
      {activeTab === 'files' && (
        <>
          <HiddenInput 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload}
            multiple
          />
          
          <UploadArea 
            onClick={() => fileInputRef.current.click()}
            style={{ cursor: isUploading ? 'not-allowed' : 'pointer' }}
          >
            {isUploading ? (
              <>
                <LoadingSpinner />
                <UploadText>Uploading...</UploadText>
                <ProgressBar>
                  <ProgressFill progress={uploadProgress} />
                </ProgressBar>
              </>
            ) : (
              <>
                <CloudUploadIcon />
                <UploadText>Click to upload files</UploadText>
                <UploadSubtext>or drag and drop files here</UploadSubtext>
              </>
            )}
          </UploadArea>
          
          <FilesContainer>
            {files.length > 0 ? (
              <FilesList>
                {files.map((file) => (
                  <FileItem 
                    key={file.id}
                    variants={itemVariants}
                  >
                    <FileIcon type={file.type}>
                      <DescriptionIcon />
                    </FileIcon>
                    <FileInfo>
                      <FileName>{file.name}</FileName>
                      <FileDetails>
                        <span>{formatFileSize(file.size)}</span>
                        <span>{formatDate(file.lastModified)}</span>
                        {processingFiles.has(file.id) && (
                          <FileStatus status="processing">Processing...</FileStatus>
                        )}
                        {file.status === 'completed' && (
                          <FileStatus status="completed">Processed</FileStatus>
                        )}
                        {file.status === 'error' && (
                          <FileStatus status="error">Error</FileStatus>
                        )}
                      </FileDetails>
                    </FileInfo>
                    <FileActions>
                      <FileActionButton 
                        onClick={() => handleFileDownload(file.id, file.name)}
                        disabled={processingFiles.has(file.id)}
                      >
                        <DownloadIcon />
                      </FileActionButton>
                      <FileActionButton 
                        onClick={() => handleFileDelete(file.id)}
                        disabled={processingFiles.has(file.id)}
                      >
                        <DeleteIcon />
                      </FileActionButton>
                      <FileActionButton 
                        onClick={() => handleFileProcess(file.id)}
                        disabled={processingFiles.has(file.id) || file.status === 'completed'}
                      >
                        {processingFiles.has(file.id) ? (
                          <LoadingSpinner size={16} />
                        ) : (
                          <AutoAwesomeIcon />
                        )}
                      </FileActionButton>
                    </FileActions>
                  </FileItem>
                ))}
              </FilesList>
            ) : (
              <EmptyState>
                <FolderIcon style={{ fontSize: '3rem', marginBottom: '1rem' }} />
                <p>No files uploaded</p>
                <p>Upload files to process them with Anima</p>
              </EmptyState>
            )}
          </FilesContainer>
        </>
      )}
      
      {activeTab === 'generate' && (
        <GenerateContainer>
          <GenerateInput 
            placeholder="Enter a prompt to generate content..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isGenerating}
          />
          
          <GenerateButton 
            onClick={handleGenerateContent}
            disabled={isGenerating || !prompt}
          >
            {isGenerating ? (
              <>
                <LoadingSpinner size={20} />
                Generating...
              </>
            ) : (
              <>
                <AutoAwesomeIcon />
                Generate Content
              </>
            )}
          </GenerateButton>
          
          {generatedContent && (
            <>
              <GeneratedContent>
                {generatedContent}
              </GeneratedContent>
              
              <GeneratedActions>
                <FileActionButton onClick={handleCopyContent}>
                  <ContentCopyIcon />
                </FileActionButton>
                <FileActionButton onClick={handleDownloadContent}>
                  <DownloadIcon />
                </FileActionButton>
              </GeneratedActions>
            </>
          )}
        </GenerateContainer>
      )}
    </SectionContainer>
  );
};

export default FileInteractionSection;
