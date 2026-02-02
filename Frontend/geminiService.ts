import { ResumeData, InterviewQuestion, ConfidenceScore } from "./types";

const API_BASE_URL = "http://localhost:5000/api";

export const geminiService = {
  async generateQuestions(resume: ResumeData, jobRole: string): Promise<InterviewQuestion[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-questions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ resume, jobRole }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const questions = await response.json();
      return questions;
    } catch (error) {
      console.error("Failed to generate questions:", error);
      return [];
    }
  },

  async analyzeAnswer(
    question: string,
    answer: string,
    audioBlob?: string, // base64
    imageFrames?: string[] // base64 snapshots
  ): Promise<{ scores: ConfidenceScore; feedback: any }> {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze-answer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          answer,
          audioBlob,
          imageFrames,
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Failed to analyze answer:", error);
      return {
        scores: { overall: 0, facial: 0, vocal: 0, semantic: 0 },
        feedback: { facial: "", vocal: "", semantic: "", summary: "Error analyzing answer." }
      };
    }
  }
};
