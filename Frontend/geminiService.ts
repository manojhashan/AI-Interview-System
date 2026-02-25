import { ResumeData, InterviewQuestion, ConfidenceScore, InterviewResult } from "./types";

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
      alert(`Question Generation Failed: ${String(error)}`);
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
  },

  // Auth Methods
  // These functions handle logging in, signing up, and password resets.
  async login(email: string, password: string): Promise<{ success: boolean; data?: any; error?: string }> {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      // Note: Endpoint is /auth/token, NOT /api/auth/token based on backend routes
      const response = await fetch(`http://localhost:5000/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data.detail || "Login failed" };
      }

      return { success: true, data };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: "Network error or server unreachable" };
    }
  },

  async signup(email: string, password: string, firstName: string, lastName: string): Promise<{ success: boolean; data?: any; error?: string }> {
    // This sends the new user's details to the backend to create an account.
    try {
      const response = await fetch(`http://localhost:5000/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        return { success: false, error: data.detail || "Signup failed" };
      }

      return { success: true, data };
    } catch (error) {
      console.error("Signup error:", error);
      return { success: false, error: "Network error or server unreachable" };
    }
  },

  async forgotPassword(email: string): Promise<{ success: boolean; message?: string; error?: string }> {
      // 1. Request OTP
      // We ask the backend to send a code to this email.
      try {
          const response = await fetch(`http://localhost:5000/auth/forgot-password`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email })
          });
          const data = await response.json();
          if (!response.ok) return { success: false, error: data.detail || "Request failed" };
          return { success: true, message: data.message };
      } catch (e) {
          return { success: false, error: "Network error" };
      }
  },

  async verifyOtp(email: string, otp: string): Promise<{ success: boolean; message?: string; error?: string }> {
      // 2. Check Code
      // We send the code the user typed to see if it's correct.
      try {
          const response = await fetch(`http://localhost:5000/auth/verify-otp`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, otp })
          });
          const data = await response.json();
          if (!response.ok) return { success: false, error: data.detail || "Verification failed" };
          return { success: true, message: data.message };
      } catch (e) {
          return { success: false, error: "Network error" };
      }
  },

  async resetPassword(email: string, otp: string, newPassword: string): Promise<{ success: boolean; message?: string; error?: string }> {
      // 3. New Password
      // If code is correct, we save the new password.
      try {
          const response = await fetch(`http://localhost:5000/auth/reset-password`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, otp, new_password: newPassword })
          });
          const data = await response.json();
          if (!response.ok) return { success: false, error: data.detail || "Reset failed" };
          return { success: true, message: data.message };
      } catch (e) {
          return { success: false, error: "Network error" };
      }
  },

  // Resume Persistence Methods
  async saveResume(resume: ResumeData, userId: string): Promise<{ success: boolean; data?: ResumeData }> {
    try {
        const response = await fetch(`${API_BASE_URL}/resumes?user_id=${userId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(resume)
        });
        if (!response.ok) throw new Error("Failed to save resume");
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error("Save Resume Error:", error);
        return { success: false };
    }
  },

  async getUserResumes(userId: string): Promise<ResumeData[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/resumes/${userId}`);
        if (!response.ok) return [];
        return await response.json();
    } catch (error) {
        console.error("Get Resumes Error:", error);
        return [];
    }
  },

  async deleteResume(resumeId: string): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}`, { method: "DELETE" });
        return response.ok;
    } catch (error) {
         console.error("Delete Resume Error:", error);
         return false;
    }
  },

  // Interview Result Persistence
  async saveInterviewResult(result: InterviewResult): Promise<InterviewResult | null> {
      try {
          const response = await fetch(`${API_BASE_URL}/results`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(result)
          });
          if (!response.ok) return null;
          return await response.json();
      } catch (error) {
          console.error("Save Result Error:", error);
          return null;
      }
  },

  async getUserResults(userId: string): Promise<InterviewResult[]> {
      try {
          const response = await fetch(`${API_BASE_URL}/results/${userId}`);
          if (!response.ok) return [];
          return await response.json();
      } catch (error) {
          console.error("Get Results Error:", error);
          return [];
      }
  },

  async getInterviewResult(resultId: string): Promise<InterviewResult | null> {
      try {
          const response = await fetch(`${API_BASE_URL}/results/detail/${resultId}`);
          if (!response.ok) return null;
          return await response.json();
      } catch (error) {
          console.error("Get Result Detail Error:", error);
          return null;
      }
  },

  async getAllResults(): Promise<InterviewResult[]> {
      try {
          const response = await fetch(`${API_BASE_URL}/admin/results`);
          if (!response.ok) return [];
          return await response.json();
      } catch (error) {
          console.error("Get All Results Error:", error);
          return [];
      }
  },

  async deleteInterviewResult(resultId: string, userId: string): Promise<boolean> {
      try {
          const response = await fetch(`${API_BASE_URL}/results/${resultId}?user_id=${userId}`, {
              method: "DELETE"
          });
          return response.ok;
      } catch (error) {
          console.error("Delete Result Error:", error);
          return false;
      }
  },

  async updateUser(userId: string, data: { first_name?: string, last_name?: string, email?: string, password?: string }) {
      try {
          const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(data)
          });
          if (!response.ok) {
              const error = await response.json();
              return { success: false, error: error.detail || "Update failed" };
          }
          const updatedUser = await response.json();
          return { success: true, data: updatedUser };
      } catch (error) {
          console.error("Update User Error:", error);
          return { success: false, error: "Network error" };
      }
  }
};
