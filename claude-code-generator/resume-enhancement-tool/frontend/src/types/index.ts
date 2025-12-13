// API Types
export interface Resume {
  id: string;
  filename: string;
  original_format: string;
  file_path: string;
  extracted_text_path: string;
  upload_date: string;
  file_size_bytes: number;
  word_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  title: string;
  company: string | null;
  description_text: string;
  file_path: string;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface Enhancement {
  id: string;
  resume_id: string;
  job_id: string | null;
  enhancement_type: 'job_tailoring' | 'industry_revamp';
  industry: string | null;
  output_path: string | null;
  pdf_path: string | null;
  status: 'pending' | 'completed' | 'failed';
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  updated_at: string;
}

export interface CreateJobRequest {
  title: string;
  company?: string;
  description_text: string;
  source?: string;
}

export interface CreateTailorEnhancementRequest {
  resume_id: string;
  job_id: string;
  enhancement_type: 'job_tailoring';
}

export interface CreateRevampEnhancementRequest {
  resume_id: string;
  industry: string;
}
