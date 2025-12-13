import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { resumeApi } from '../services/api';
import type { Resume } from '../types';

interface ResumeUploadProps {
  onUploadSuccess: (resume: Resume) => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setUploading(true);
      setError(null);

      try {
        const resume = await resumeApi.uploadResume(file);
        onUploadSuccess(resume);
      } catch (err: any) {
        setError(
          err.response?.data?.detail || 'Failed to upload resume. Please try again.'
        );
      } finally {
        setUploading(false);
      }
    },
    [onUploadSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [
        '.docx',
      ],
      'application/msword': ['.doc'],
    },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Upload Your Resume</h2>
      <div
        {...getRootProps()}
        style={{
          ...styles.dropzone,
          ...(isDragActive ? styles.dropzoneActive : {}),
          ...(uploading ? styles.dropzoneDisabled : {}),
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <p>Uploading...</p>
        ) : isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <div style={styles.dropzoneContent}>
            <p style={styles.dropzoneText}>
              Drag & drop your resume here, or click to select
            </p>
            <p style={styles.dropzoneHint}>Supports PDF and DOCX files</p>
          </div>
        )}
      </div>
      {error && <div style={styles.error}>{error}</div>}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginBottom: '2rem',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#333',
  },
  dropzone: {
    border: '2px dashed #ccc',
    borderRadius: '8px',
    padding: '3rem 2rem',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    backgroundColor: '#f9f9f9',
  },
  dropzoneActive: {
    borderColor: '#4CAF50',
    backgroundColor: '#e8f5e9',
  },
  dropzoneDisabled: {
    cursor: 'not-allowed',
    opacity: 0.6,
  },
  dropzoneContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  dropzoneText: {
    fontSize: '1.1rem',
    color: '#555',
    margin: 0,
  },
  dropzoneHint: {
    fontSize: '0.9rem',
    color: '#888',
    margin: 0,
  },
  error: {
    marginTop: '1rem',
    padding: '0.75rem',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px',
    border: '1px solid #ef5350',
  },
};
