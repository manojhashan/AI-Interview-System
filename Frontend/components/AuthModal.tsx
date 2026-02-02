
import React, { useState } from 'react';
import { X, Mail, Lock, User, ArrowRight, ArrowLeft, ShieldCheck } from 'lucide-react';
import { UserRole } from '../types';

interface AuthModalProps {
  initialMode: 'login' | 'signup';
  onClose: () => void;
  onSuccess: (role: UserRole, email: string, name: string) => void;
}

type AuthView = 'login' | 'signup' | 'forgot-password' | 'otp-verify' | 'reset-password';

const AuthModal: React.FC<AuthModalProps> = ({ initialMode, onClose, onSuccess }) => {
  const [view, setView] = useState<AuthView>(initialMode);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [otp, setOtp] = useState(['', '', '', '']);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Determine role based on email suffix
    const role = email.toLowerCase().endsWith('@admin.com') ? UserRole.ADMIN : UserRole.CANDIDATE;
    const nameToUse = fullName || (role === UserRole.ADMIN ? 'System Admin' : 'Candidate User');

    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      onSuccess(role, email, nameToUse);
    }, 1500);
  };

  const handleForgotPassword = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setView('otp-verify');
    }, 1200);
  };

  const handleOtpVerify = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setView('reset-password');
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xl animate-in fade-in duration-300">
      <div className="w-full max-w-md bg-slate-900 border border-white/10 rounded-3xl shadow-2xl relative overflow-hidden">
        <button onClick={onClose} className="absolute top-6 right-6 text-slate-400 hover:text-white">
          <X size={24} />
        </button>

        <div className="p-10">
          <div className="text-center mb-10">
            <div className="w-16 h-16 bg-blue-600 rounded-2xl mx-auto flex items-center justify-center mb-6 shadow-xl shadow-blue-500/20">
              <span className="text-3xl font-bold">Z</span>
            </div>
            <h2 className="text-2xl font-bold">
              {view === 'login' && 'Welcome Back'}
              {view === 'signup' && 'Create Account'}
              {view === 'forgot-password' && 'Reset Password'}
              {view === 'otp-verify' && 'Verify OTP'}
              {view === 'reset-password' && 'New Password'}
            </h2>
            <p className="text-slate-400 text-sm mt-2">
              {view === 'login' && 'Enter your credentials to continue'}
              {view === 'signup' && 'Join Zynergy AI to boost your career'}
              {view === 'forgot-password' && "Enter your email to receive a code"}
              {view === 'otp-verify' && `Code sent to ${email || 'your email'}`}
              {view === 'reset-password' && 'Create a strong new password'}
            </p>
          </div>

          <form onSubmit={
            view === 'login' || view === 'signup' ? handleSubmit : 
            view === 'forgot-password' ? handleForgotPassword :
            view === 'otp-verify' ? handleOtpVerify : handleSubmit
          } className="space-y-5">
            
            {(view === 'signup') && (
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Full Name</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input 
                    required 
                    type="text" 
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-slate-950 border border-white/5 rounded-xl py-3.5 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm" 
                    placeholder="John Doe" 
                  />
                </div>
              </div>
            )}

            {(view === 'login' || view === 'signup' || view === 'forgot-password') && (
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input required value={email} onChange={(e) => setEmail(e.target.value)} type="email" className="w-full bg-slate-950 border border-white/5 rounded-xl py-3.5 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm" placeholder="name@example.com" />
                </div>
              </div>
            )}

            {(view === 'login' || view === 'signup' || view === 'reset-password') && (
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                  <input required type="password" minLength={8} className="w-full bg-slate-950 border border-white/5 rounded-xl py-3.5 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm" placeholder="••••••••" />
                </div>
              </div>
            )}

            {view === 'otp-verify' && (
              <div className="flex justify-center gap-4 py-4">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    type="text"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => {
                      const newOtp = [...otp];
                      newOtp[idx] = e.target.value;
                      setOtp(newOtp);
                      if (e.target.value && e.target.nextSibling) (e.target.nextSibling as HTMLInputElement).focus();
                    }}
                    className="w-14 h-14 bg-slate-950 border border-white/10 rounded-xl text-center text-2xl font-bold focus:border-blue-500 outline-none"
                  />
                ))}
              </div>
            )}

            {view === 'login' && (
              <div className="flex justify-end">
                <button type="button" onClick={() => setView('forgot-password')} className="text-xs font-semibold text-blue-400 hover:text-blue-300">
                  Forgot Password?
                </button>
              </div>
            )}

            <button
              disabled={loading}
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center gap-2 group"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {view === 'login' && 'Sign In Now'}
                  {view === 'signup' && 'Start Free Trial'}
                  {view === 'forgot-password' && 'Send Reset Code'}
                  {view === 'otp-verify' && 'Verify Code'}
                  {view === 'reset-password' && 'Update Password'}
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-white/5 text-center">
            {view === 'login' ? (
              <p className="text-sm text-slate-500">
                Don't have an account?{' '}
                <button onClick={() => setView('signup')} className="text-blue-400 font-bold hover:underline">Sign Up</button>
              </p>
            ) : view === 'signup' ? (
              <p className="text-sm text-slate-500">
                Already have an account?{' '}
                <button onClick={() => setView('login')} className="text-blue-400 font-bold hover:underline">Log In</button>
              </p>
            ) : (
              <button onClick={() => setView('login')} className="flex items-center gap-2 text-sm text-slate-400 mx-auto hover:text-white transition-colors">
                <ArrowLeft size={16} /> Back to login
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
