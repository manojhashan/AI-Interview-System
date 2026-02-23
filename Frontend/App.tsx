
import React, { useState, useEffect } from 'react';
import { User, UserRole, ResumeData } from './types';
import { geminiService } from './geminiService';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ResumeForm from './components/ResumeForm';
import InterviewSession from './components/InterviewSession';
import ResultView from './components/ResultView';
import AdminDashboard from './components/AdminDashboard';
import LandingPage from './components/LandingPage';
import AuthModal from './components/AuthModal';
import HistoryView from './components/HistoryView';
import { Trash2, PlusCircle, Briefcase, User as UserIcon } from 'lucide-react';
import UserProfile from './components/UserProfile';

import { Toaster } from 'react-hot-toast';

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<string>('landing');
  const [showAuth, setShowAuth] = useState<{ mode: 'login' | 'signup' } | null>(null);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
  const [editingResumeId, setEditingResumeId] = useState<string | null>(null);

  // Load user resumes from localStorage on login or initialization
  // Load user resumes from API on login or initialization
  // Load user resumes from API on login or initialization
  useEffect(() => {
    // Check for saved user on mount
    /* 
    // AUTO-LOGIN DISABLED BY USER REQUEST
    const savedUser = localStorage.getItem('zynergy_user');
    if (savedUser && !user) {
        try {
            const parsedUser = JSON.parse(savedUser);
            // Ensure compatibility if we change User shape
            setUser(parsedUser);
        } catch (e) {
            console.error("Failed to parse saved user", e);
            localStorage.removeItem('zynergy_user');
        }
    }
    */

    if (user && user.role === UserRole.CANDIDATE) {
      const loadResumes = async () => {
         // Optimization: If resumes are already in savedUser, maybe skip? 
         // But better to fetch fresh.
         const resumes = await geminiService.getUserResumes(user.id);
         setUser(prev => prev ? { ...prev, resumes } : null);
      };
      loadResumes();
    }
  }, [user?.id]); // Depend on ID to re-fetch resumes if user changes

  const handleLoginSuccess = async (role: UserRole, email: string, name: string, userId: string) => {
    const newUser: User = {
      id: userId,
      name: name,
      email: email,
      role: role,
      resumes: [] 
    };
    setUser(newUser);
    localStorage.setItem('zynergy_user', JSON.stringify(newUser));
    setShowAuth(null);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('zynergy_user');
    setCurrentPage('landing');
  };

  const saveResume = async (resume: ResumeData) => {
    if (!user) return;
    
    const result = await geminiService.saveResume(resume, user.id);
    if (result.success && result.data) {
        // Update local state with returned data (useful for real DB ID)
        const updatedResume = result.data;
        const exists = user.resumes.find(r => r.id === updatedResume.id);
        const updatedResumes = exists 
          ? user.resumes.map(r => r.id === updatedResume.id ? updatedResume : r)
          : [...user.resumes, updatedResume];
        
        setUser({ ...user, resumes: updatedResumes });
        setEditingResumeId(null);
        setCurrentPage('profile');
    } else {
        alert("Failed to save resume. Please try again.");
    }
  };

  const deleteResume = async (id: string) => {
    if (!user) return;
    
    if (window.confirm('Are you sure you want to delete this resume profile? This action cannot be undone.')) {
      const success = await geminiService.deleteResume(id);
      if (success) {
          const updatedResumes = user.resumes.filter(r => r.id !== id);
          setUser({ ...user, resumes: updatedResumes });
      } else {
          alert("Failed to delete resume.");
      }
    }
  };

  if (currentPage === 'landing') {
    return (
      <>
        <LandingPage 
          isLoggedIn={!!user} 
          onGetStarted={(mode) => setShowAuth({ mode })} 
          onGoToDashboard={() => setCurrentPage('dashboard')}
        />
        {showAuth && !user && (
          <AuthModal 
            initialMode={showAuth.mode} 
            onClose={() => setShowAuth(null)} 
            onSuccess={handleLoginSuccess}
          />
        )}
      </>
    );
  }

  if (!user) {
    setCurrentPage('landing');
    return null;
  }

  // Helper to check if admin
  const isAdmin = user && user.role && user.role.toString().toUpperCase() === 'ADMIN';

  console.log("Current User:", user);
  console.log("Is Admin?", isAdmin);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-500/30">
      <Toaster position="top-right" toastOptions={{
        style: {
          background: '#1e293b',
          color: '#e2e8f0',
          border: '1px solid rgba(255,255,255,0.1)',
        },
      }} />
      {/* Admin Logic */}
      {isAdmin && (
          <div className="max-w-6xl mx-auto p-6 md:p-12">
               {currentPage === 'dashboard' && (
                  <AdminDashboard 
                    user={user} 
                    onViewResult={(id) => { setSelectedResultId(id); setCurrentPage('view-result'); }}
                    onLogout={handleLogout}
                  />
               )}
               {currentPage === 'view-result' && <ResultView resultId={selectedResultId} onBack={() => setCurrentPage('dashboard')} isAdmin={true} />}
          </div>
      )}

      {/* Candidate Logic - Render if NOT admin */}
      {(!user || !isAdmin) && (
        <div className="flex min-h-screen">
          <Sidebar 
            role={user?.role || UserRole.CANDIDATE} 
            activePage={currentPage} 
            onNavigate={(page) => {
              setCurrentPage(page);
              setEditingResumeId(null);
            }} 
            onLogout={handleLogout} 
          />
          
          <main className="flex-1 overflow-y-auto p-4 md:p-8">
            <header className="mb-8 flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                  {currentPage === 'profile' && editingResumeId ? (editingResumeId === 'new' ? 'Create Profile' : 'Edit Profile') : 
                   currentPage === 'profile' ? 'My Career Profiles' :
                   currentPage === 'history' ? 'Interview History' :
                   currentPage.charAt(0).toUpperCase() + currentPage.slice(1).replace('-', ' ')}
                </h1>
                <p className="text-slate-400 text-sm">Welcome back, {user?.name || 'Guest'}</p>
              </div>
              
              <div onClick={() => setCurrentPage('user-profile')} className="flex items-center gap-3 cursor-pointer group hover:opacity-80 transition-opacity">
                  <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center border border-slate-700 group-hover:border-blue-500/50 transition-colors">
                      <UserIcon className="text-slate-400 group-hover:text-blue-400" size={20} />
                  </div>
                  <div className="text-right hidden sm:block">
                        <p className="text-slate-200 text-sm font-bold">{user?.name || 'Guest'}</p>
                        <p className="text-slate-500 text-xs">{user?.email}</p>
                  </div>
              </div>
            </header>

            <div className="max-w-6xl mx-auto">
              {(currentPage === 'dashboard' || currentPage === 'landing') && user && (
                <Dashboard user={user} onStartInterview={() => setCurrentPage('interview')} onViewResult={(id) => { setSelectedResultId(id); setCurrentPage('view-result'); }} />
              )}
              
              {currentPage === 'profile' && user && (
                editingResumeId ? (
                  <ResumeForm 
                    existingResume={user.resumes.find(r => r.id === editingResumeId)} 
                    onSave={saveResume} 
                    onCancel={() => setEditingResumeId(null)}
                  />
                ) : (
                  <div className="space-y-6 animate-in fade-in duration-500">
                    <div className="flex justify-between items-center">
                      <h2 className="text-xl font-bold text-white">Manage your career profiles</h2>
                      <button 
                        onClick={() => setEditingResumeId('new')} 
                        className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2"
                      >
                        <PlusCircle size={18} /> Add New Profile
                      </button>
                    </div>

                    {user.resumes.length > 0 ? (
                      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {user.resumes.map(resume => (
                          <div key={resume.id} className="bg-slate-900 border border-slate-800 p-6 rounded-3xl hover:border-blue-500/50 transition-all group relative animate-in zoom-in duration-300">
                             <button 
                               onClick={(e) => { 
                                 e.preventDefault();
                                 e.stopPropagation(); 
                                 deleteResume(resume.id); 
                               }}
                               className="absolute top-4 right-4 p-2.5 text-slate-500 hover:text-red-500 bg-slate-950/50 hover:bg-red-500/10 rounded-xl transition-all z-10"
                               title="Delete Profile"
                             >
                               <Trash2 size={18} />
                             </button>
                             <h3 className="text-lg font-bold mb-1 text-white pr-10">{resume.resumeTitle}</h3>
                             <p className="text-xs text-slate-500 mb-6 uppercase tracking-widest font-bold">Resume Profile</p>
                             <div className="space-y-2 mb-8 text-sm text-slate-400">
                                <p>• {resume.skills.length} Skills</p>
                                <p>• {resume.projects.length} Projects</p>
                             </div>
                             <button 
                               onClick={() => { setEditingResumeId(resume.id); }}
                               className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-bold text-sm transition-all border border-slate-700 hover:border-blue-500/30"
                             >
                               Edit Profile
                             </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-24 bg-slate-900/30 border-2 border-dashed border-slate-800 rounded-[2.5rem] flex flex-col items-center">
                        <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 text-slate-600">
                          <Briefcase size={40} />
                        </div>
                        <h3 className="text-xl font-bold text-slate-400">No career profiles found</h3>
                        <p className="text-slate-500 mt-2 mb-8">Create a profile to get customized interview questions.</p>
                        <button 
                          onClick={() => setEditingResumeId('new')} 
                          className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20"
                        >
                          Create Your First Profile
                        </button>
                      </div>
                    )}
                  </div>
                )
              )}

              {currentPage === 'interview' && user && (
                <InterviewSession 
                  user={user} 
                  onComplete={(resultId) => {
                    if (resultId) {
                      setSelectedResultId(resultId);
                      setCurrentPage('view-result');
                    } else {
                      setCurrentPage('dashboard');
                    }
                  }} 
                  onAddResume={() => { setEditingResumeId('new'); setCurrentPage('profile'); }}
                />
              )}
              
              {currentPage === 'view-result' && <ResultView resultId={selectedResultId} onBack={() => setCurrentPage('dashboard')} isAdmin={false} />}
              {currentPage === 'user-profile' && user && (
                <UserProfile 
                   user={user} 
                   onUpdate={(updatedUser) => {
                       setUser(updatedUser);
                       localStorage.setItem('zynergy_user', JSON.stringify(updatedUser));
                   }}
                   onBack={() => setCurrentPage('dashboard')}
                />
              )}
              {currentPage === 'history' && user && <HistoryView userId={user.id} onViewResult={(id) => { setSelectedResultId(id); setCurrentPage('view-result'); }} />}
            </div>
          </main>
        </div>
      )}
    </div>
  );
};

export default App;
