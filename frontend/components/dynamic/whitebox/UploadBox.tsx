/**
 * UploadBox component for whitebox scanning
 */

import React, { useState, useRef } from 'react';
import '@/styles/dynamic/whitebox/UploadBox.css';

interface UploadBoxProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export const UploadBox: React.FC<UploadBoxProps> = ({ onUpload, isUploading }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const zipFile = files.find(file => file.name.toLowerCase().endsWith('.zip'));

    if (zipFile) {
      onUpload(zipFile);
    } else {
      alert('Please upload a ZIP file');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.zip')) {
        alert('Please select a ZIP file');
        return;
      }
      onUpload(file);
    }
  };

  const handleClick = () => {
    if (!isUploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="upload-box">
      <div
        className={`upload-area ${isDragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        {isUploading ? (
          <div className="uploading-content">
            <div className="spinner"></div>
            <p>Uploading and scanning...</p>
          </div>
        ) : (
          <>
            <div className="upload-icon">📦</div>
            <h3>Upload ZIP File</h3>
            <p>Drag and drop your ZIP file here, or click to browse</p>
            <p className="file-types">Supports: .zip (max 10MB)</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              onChange={handleFileSelect}
              className="file-input"
              disabled={isUploading}
            />
          </>
        )}
      </div>
    </div>
  );
};
