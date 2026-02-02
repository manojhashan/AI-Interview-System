
import React, { useState, useEffect } from 'react';
import { User, UserRole, ResumeData } from './types';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ResumeForm from './components/ResumeForm';
import InterviewSession from './components/InterviewSession';
import ResultView from './components/ResultView';
import AdminDashboard from './components/AdminDashboard';
import LandingPage from './components/LandingPage';
import AuthModal from './components/AuthModal';
import HistoryView from './components/HistoryView';
import { Trash2, PlusCircle, Briefcase } from 'lucide-react';

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<string>('landing');
  const [showAuth, setShowAuth] = useState<{ mode: 'login' | 'signup' } | null>(null);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
  const [editingResumeId, setEditingResumeId] = useState<string | null>(null);

  // Load user resumes from localStorage on login or initialization
  useEffect(() => {
    if (user && user.role === UserRole.CANDIDATE) {
      const savedResumes = localStorage.getItem(`resumes_${user.id}`);
      if (savedResumes) {
        const parsedResumes = JSON.parse(savedResumes);
        if (JSON.stringify(parsedResumes) !== JSON.stringify(user.resumes)) {
          setUser(prev => prev ? { ...prev, resumes: parsedResumes } : null);
        }
      }
    }
  }, [user?.id]);

  const handleLoginSuccess = (role: UserRole, email: string, name: string) => {
    // We can use the email hash or a simple ID strategy
    const userId = role === UserRole.ADMIN ? 'admin-id' : `user-${btoa(email).substring(0, 8)}`;
    const savedResumes = localStorage.getItem(`resumes_${userId}`);
    
    setUser({
      id: userId,
      name: name,
      email: email,
      role: role,
      resumes: savedResumes ? JSON.parse(savedResumes) : [] 
    });
    setShowAuth(null);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage('landing');
  };

  const saveResume = (resume: ResumeData) => {
    if (!user) return;
    
    const exists = user.resumes.find(r => r.id === resume.id);
    const updatedResumes = exists 
      ? user.resumes.map(r => r.id === resume.id ? resume : r)
      : [...user.resumes, resume];
    
    localStorage.setItem(`resumes_${user.id}`, JSON.stringify(updatedResumes));
    setUser({ ...user, resumes: updatedResumes });

    setEditingResumeId(null);
    setCurrentPage('profile');
  };

  const deleteResume = (id: string) => {
    if (!user) return;
    
    if (window.confirm('Are you sure you want to delete this resume profile? This action cannot be undone.')) {
      const updatedResumes = user.resumes.filter(r => r.id !== id);
      localStorage.setItem(`resumes_${user.id}`, JSON.stringify(updatedResumes));
      setUser({ ...user, resumes: updatedResumes });
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

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-500/30">
      <Sidebar 
        role={user.role} 
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
               user.role === UserRole.ADMIN && currentPage === 'dashboard' ? 'Admin Overview' :
               currentPage.charAt(0).toUpperCase() + currentPage.slice(1).replace('-', ' ')}
            </h1>
            <p className="text-slate-400 text-sm">Welcome back, {user.name}</p>
          </div>
        </header>

        <div className="max-w-6xl mx-auto">
          {currentPage === 'dashboard' && user.role === UserRole.CANDIDATE && (
            <Dashboard user={user} onStartInterview={() => setCurrentPage('interview')} onViewResult={(id) => { setSelectedResultId(id); setCurrentPage('view-result'); }} />
          )}
          {currentPage === 'dashboard' && user.role === UserRole.ADMIN && (
            <AdminDashboard onViewResult={(id) => { setSelectedResultId(id); setCurrentPage('view-result'); }} />
          )}
          
          {currentPage === 'profile' && (
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

          {currentPage === 'interview' && (
            <InterviewSession 
              user={user} 
              onComplete={() => setCurrentPage('dashboard')} 
              onAddResume={() => { setEditingResumeId('new'); setCurrentPage('profile'); }}
            />
          )}
          
          {currentPage === 'view-result' && <ResultView resultId={selectedResultId} onBack={() => setCurrentPage('dashboard')} />}
          {currentPage === 'history' && <HistoryView onViewResult={(id) => { setSelectedResultId(id); setCurrentPage('view-result'); }} />}
        </div>
      </main>
    </div>
  );
};

export default App;
