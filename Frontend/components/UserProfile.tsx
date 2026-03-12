import React, { useState } from 'react';
import { User } from '../types';
import { geminiService } from '../geminiService';
import { User as UserIcon, Mail, Lock, Save, ArrowLeft, ShieldCheck, Eye, EyeOff, Globe } from 'lucide-react';

interface UserProfileProps {
  user: User;
  onUpdate: (updatedUser: User) => void;
  onBack: () => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onUpdate, onBack }) => {
  const [firstName, setFirstName] = useState(user.name.split(' ')[0]);
  const [lastName, setLastName] = useState(user.name.split(' ').slice(1).join(' '));
  const [email, setEmail] = useState(user.email);
  const [preferredLanguage, setPreferredLanguage] = useState(user.preferredLanguage || 'en-US');

  const languageOptions = [
    { value: 'en-US', label: 'English (US) — En-US' },
    { value: 'en-GB', label: 'English (UK) — En-GB' },
    { value: 'en-AU', label: 'English (Australia) — En-AU' },
    { value: 'en-IN', label: 'English (India) — En-IN' },
    { value: 'en-ZA', label: 'English (South Africa) — En-ZA' },
    { value: 'en-LK', label: 'English (Sri Lanka) — En-LK' },
  ];
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg(null);
    setLoading(true);

    if (newPassword && newPassword !== confirmPassword) {
        setMsg({ type: 'error', text: "New passwords do not match" });
        setLoading(false);
        return;
    }

    if (newPassword && newPassword.length < 8) {
        setMsg({ type: 'error', text: "Password must be at least 8 characters" });
        setLoading(false);
        return;
    }

    try {
        const updateData: any = {
            first_name: firstName,
            last_name: lastName,
            email: email,
            preferred_language: preferredLanguage
        };
        if (newPassword) {
            updateData.password = newPassword;
        }

        const result = await geminiService.updateUser(user.id, updateData);

        if (result.success) {
            setMsg({ type: 'success', text: "Profile updated successfully" });
            // Construct updated local user object
            const updatedUser: User = {
                ...user,
                name: `${result.data.first_name} ${result.data.last_name}`.trim(),
                email: result.data.email,
                preferredLanguage: result.data.preferred_language || 'en-US'
            };
            onUpdate(updatedUser);
            // Clear password fields
            setNewPassword('');
            setConfirmPassword('');
        } else {
            setMsg({ type: 'error', text: result.error || "Failed to update profile" });
        }
    } catch (err) {
        setMsg({ type: 'error', text: "An unexpected error occurred" });
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center gap-4 mb-6">
        <button onClick={onBack} className="p-2 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors text-slate-400 hover:text-white">
            <ArrowLeft size={20} />
        </button>
        <div>
            <h2 className="text-2xl font-bold text-white">My Profile</h2>
            <p className="text-slate-400 text-sm">Manage your account settings</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-2xl">
         <form onSubmit={handleSave} className="space-y-6">
            
            {/* Name Section */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">First Name</label>
                    <div className="relative">
                        <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input 
                            required value={firstName} onChange={(e) => setFirstName(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm text-slate-200"
                        />
                    </div>
                </div>
                <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Last Name</label>
                    <div className="relative">
                        <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input 
                            value={lastName} onChange={(e) => setLastName(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm text-slate-200"
                        />
                    </div>
                </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Email Address</label>
                <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <input 
                        required type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm text-slate-200"
                    />
                </div>
            </div>

            <div className="h-px bg-slate-800 my-8" />

            {/* Language Preference Section */}
            <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Preferred English Variant</label>
                <p className="text-xs text-slate-500 mb-2">This setting improves speech-to-text accuracy during interviews.</p>
                <div className="relative">
                    <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                    <select 
                        value={preferredLanguage} 
                        onChange={(e) => setPreferredLanguage(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm text-slate-200 appearance-none cursor-pointer"
                    >
                        {languageOptions.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="h-px bg-slate-800 my-8" />

            {/* Password Section */}
            <div>
                <h3 className="text-lg font-bold text-white mb-4">Change Password</h3>
                <p className="text-xs text-slate-500 mb-6">Leave blank if you don't want to change it.</p>
                
                <div className="space-y-4">
                     <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">New Password</label>
                        <div className="relative">
                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                            <input 
                                type={showPassword ? "text" : "password"} 
                                value={newPassword} onChange={(e) => setNewPassword(e.target.value)}
                                minLength={8}
                                placeholder="Min 8 characters"
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-12 outline-none focus:border-blue-500/50 transition-all text-sm text-slate-200"
                            />
                            <button 
                                type="button" onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                            >
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>

                    {newPassword && (
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Confirm Password</label>
                            <div className="relative">
                                <ShieldCheck className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input 
                                    type={showPassword ? "text" : "password"} 
                                    value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-blue-500/50 transition-all text-sm text-slate-200"
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {msg && (
                <div className={`p-3 rounded-xl text-sm font-bold text-center ${msg.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                    {msg.text}
                </div>
            )}

            <div className="pt-4 flex justify-end">
                <button 
                    type="submit" disabled={loading}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2"
                >
                    {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save size={18} />}
                    Save Changes
                </button>
            </div>

         </form>
      </div>
    </div>
  );
};

export default UserProfile;
