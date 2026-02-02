
import React from 'react';
import { UserRole } from '../types';

interface LoginProps {
  onLogin: (role: UserRole) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-blue-600 rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-2xl shadow-blue-500/20">
            <span className="text-4xl font-bold text-white">Z</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Zynergy AI</h1>
          <p className="text-slate-400">Multimodal Confidence Estimation System</p>
        </div>

        <div className="bg-slate-900 p-8 rounded-2xl border border-slate-800 shadow-xl space-y-6">
          <h2 className="text-xl font-semibold text-center mb-6">Choose Entry Point</h2>
          
          <button
            onClick={() => onLogin(UserRole.CANDIDATE)}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-3"
          >
            <span>Candidate Portal</span>
          </button>

          <button
            onClick={() => onLogin(UserRole.ADMIN)}
            className="w-full bg-slate-800 hover:bg-slate-700 text-white font-semibold py-4 rounded-xl transition-all flex items-center justify-center gap-3"
          >
            <span>Administrator Access</span>
          </button>

          <div className="pt-4 border-t border-slate-800 text-center">
            <p className="text-xs text-slate-500">Real-Time Explainable Multimodal Confidence Estimation in AI-Powered Interview Systems</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
