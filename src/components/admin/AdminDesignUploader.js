import React, { useState } from 'react';
import { useUserPlanContext } from '../../context/UserPlanContext';

export function AdminDesignUploader() {
  const { userPlan, loading, canUploadImages } = useUserPlanContext();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadSuccess(false);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      
      // Simulate upload process
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // In a real implementation, you would upload the file to your server or cloud storage
      console.log('File uploaded:', selectedFile.name);
      
      setUploadSuccess(true);
      setSelectedFile(null);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="design-uploader loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!canUploadImages()) {
    return (
      <div className="upgrade-prompt">
        <h3>Upgrade to Pro</h3>
        <p>You need a Pro plan or higher to upload custom designs.</p>
        <p>Your current plan: <strong>{userPlan}</strong></p>
        <button className="upgrade-button">Upgrade Now</button>
      </div>
    );
  }

  return (
    <div className="design-uploader">
      <h2>Upload Custom Design</h2>
      <p>Your current plan: <strong>{userPlan}</strong></p>
      
      <div className="upload-form">
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleFileChange}
          disabled={uploading}
        />
        
        <button 
          onClick={handleUpload} 
          disabled={!selectedFile || uploading}
          className={uploading ? 'uploading' : ''}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      {uploadSuccess && <div className="success-message">File uploaded successfully!</div>}
      
      {userPlan === 'enterprise' && (
        <div className="enterprise-features">
          <h3>Enterprise Features</h3>
          <div className="enterprise-buttons">
            <button>Bulk Upload</button>
            <button>AI Enhancement</button>
            <button>Team Sharing</button>
          </div>
        </div>
      )}
    </div>
  );
}
