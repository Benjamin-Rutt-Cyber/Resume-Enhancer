import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { resumeApi } from '../services/api';
import { useDarkMode } from '../contexts/DarkModeContext';
import type { Resume } from '../types';

interface ResumeUploadProps {
  onUploadSuccess: (resume: Resume) => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadSuccess }) => {
  const { isDarkMode } = useDarkMode();
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
      'text/plain': ['.txt'],
    },
    multiple: false,
    disabled: uploading,
  });

  const getStyles = () => getStylesWithTheme(isDarkMode);
  const s = getStyles();

  return (
    <div style={s.container}>
      <div
        {...getRootProps()}
        style={{
          ...s.dropzone,
          ...(isDragActive ? s.dropzoneActive : {}),
          ...(uploading ? s.dropzoneDisabled : {}),
        }}
      >
        <input {...getInputProps()} />
        <div style={s.dropzoneContent}>
          {uploading ? (
            <>
              <div style={s.icon}>⏳</div>
              <div style={s.dropzoneTitle}>Uploading...</div>
              <div style={s.dropzoneText}>Please wait</div>
            </>
          ) : isDragActive ? (
            <>
              <div style={s.icon}>📄</div>
              <div style={s.dropzoneTitle}>Drop file here</div>
            </>
          ) : (
            <>
              <div style={s.iconWrapper}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#3b82f6' }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
              </div>
              <div style={s.dropzoneTitle}>Upload Resume</div>
              <div style={s.dropzoneText}>
                Drag and drop or <span style={s.browseText}>browse</span> to choose a file
              </div>
              <div style={s.formats}>PDF, DOCX, DOC, or TXT</div>
            </>
          )}
        </div>
      </div>
      {error && (
        <div style={s.error}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0 }}>
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

const getStylesWithTheme = (isDarkMode: boolean): Record<string, React.CSSProperties> => ({
  container: {
    marginBottom: '2rem',
  },
  dropzone: {
    border: `2px dashed ${isDarkMode ? '#3f3f46' : '#d1d5db'}`,
    borderRadius: '8px',
    padding: '3rem 2rem',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 0.2s',
    backgroundColor: isDarkMode ? '#18181b' : '#f9fafb',
  },
  dropzoneActive: {
    borderColor: '#3b82f6',
    backgroundColor: isDarkMode ? 'rgba(59, 130, 246, 0.05)' : 'rgba(59, 130, 246, 0.05)',
  },
  dropzoneDisabled: {
    cursor: 'not-allowed',
    opacity: 0.6,
  },
  dropzoneContent: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.75rem',
  },
  iconWrapper: {
    marginBottom: '0.5rem',
  },
  icon: {
    fontSize: '3rem',
    marginBottom: '0.5rem',
  },
  dropzoneTitle: {
    fontSize: '1rem',
    fontWeight: '600',
    color: isDarkMode ? '#ffffff' : '#18181b',
  },
  dropzoneText: {
    fontSize: '0.875rem',
    color: isDarkMode ? '#a1a1aa' : '#71717a',
  },
  browseText: {
    color: '#3b82f6',
    fontWeight: '500',
  },
  formats: {
    fontSize: '0.75rem',
    color: isDarkMode ? '#71717a' : '#a1a1aa',
    marginTop: '0.5rem',
  },
  error: {
    marginTop: '1rem',
    padding: '0.75rem 1rem',
    backgroundColor: isDarkMode ? 'rgba(239, 68, 68, 0.1)' : '#fee2e2',
    color: '#ef4444',
    borderRadius: '6px',
    border: `1px solid ${isDarkMode ? 'rgba(239, 68, 68, 0.3)' : '#fecaca'}`,
    fontSize: '0.875rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
});
