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
  selected_style: string | null;  // User's selected writing style
  style_previews_generated: boolean;  // Whether style previews have been generated
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
  docx_path: string | null;

  // Cover letter fields
  cover_letter_path: string | null;
  cover_letter_pdf_path: string | null;
  cover_letter_docx_path: string | null;
  cover_letter_status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  cover_letter_error: string | null;

  run_analysis: boolean;
  job_match_score: number | null;
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
  run_analysis?: boolean;
}

export interface CreateRevampEnhancementRequest {
  resume_id: string;
  industry: string;
}

// Style Preview Types
export interface StylePreviewItem {
  style: string;
  name: string;
  description: string;
  preview_text: string;
}

export interface StylePreviewsResponse {
  resume_id: string;
  previews: StylePreviewItem[];
}

export interface StyleSelectionRequest {
  style: string;
}

export interface StyleSelectionResponse {
  message: string;
  selected_style: string;
}

// Analysis Types
export interface KeywordCategory {
  technical_skills: string[];
  soft_skills: string[];
  action_verbs: string[];
  certifications: string[];
}

export interface MatchAnalysis {
  match_score: number;
  total_job_keywords: number;
  matched_keywords: number;
  missing_keywords: number;
  keywords_found: string[];
  keywords_missing: string[];
}

export interface ATSAnalysis {
  resume_keywords: KeywordCategory;
  job_keywords: KeywordCategory;
  match_analysis: MatchAnalysis;
  recommendations: string[];
}

export interface AnalysisResponse {
  enhancement_id: string;
  ats_analysis: ATSAnalysis;
  job_match_score: number;
  cached: boolean;
}

export interface AchievementSuggestion {
  achievement: string;
  verb: string;
  location: string;
  suggested_metrics: string[];
  already_quantified: boolean;
  achievement_type: string;
}

export interface AchievementSuggestionsResponse {
  total_achievements: number;
  unquantified_count: number;
  suggestions: AchievementSuggestion[];
  summary: string;
  breakdown_by_type?: Record<string, number>;
}

export interface ComparisonData {
  enhancement_id: string;
  original_text: string;
  enhanced_text: string;
  enhancement_type: string;
  status: string;
}

// Authentication Types
export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  role: string;  // SECURITY: For frontend authorization checks
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;  // Token expiration in seconds
  user: User;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  email: string;
  password: string;
  full_name?: string;
  accept_terms: boolean;  // COMPLIANCE: Required for registration
}
