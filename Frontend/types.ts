
export enum UserRole {
  CANDIDATE = 'CANDIDATE',
  ADMIN = 'ADMIN'
}

export interface ExperienceEntry {
  job_role: string;
  startYear: string;
  endYear: string;
}

export interface ResumeData {
  id: string;
  resumeTitle: string;
  skills: string[];
  certificates: string[];
  education: string[];
  projects: string[];
  experience: ExperienceEntry[];
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  resumes: ResumeData[];
}

export interface InterviewQuestion {
  id: string;
  text: string;
  category: 'Common' | 'Technical' | 'Situational';
}

export interface ConfidenceScore {
  overall: number;
  facial: number;
  vocal: number;
  semantic: number;
}

export interface QuestionDetail {
  question: string;
  answer: string;
  scores: ConfidenceScore;
  feedback: {
    facial: string;
    vocal: string;
    semantic: string;
    summary: string;
  };
}

export interface XaiExplanation {
  contributions: { vocal: number; facial: number; semantic: number };
  strongest: string;
  weakest: string;
  vocal_xai: string;
  facial_xai: string;
  semantic_xai: string;
  summary_xai: string;
}

export interface InterviewResult {
  id: string;
  resumeId: string;
  candidateId?: string;
  candidateName: string;
  date: string;
  time: string;
  jobRole: string;
  scores: ConfidenceScore;
  feedback?: string;
  details: QuestionDetail[];
  xai?: XaiExplanation;
}
