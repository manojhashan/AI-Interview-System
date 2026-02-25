import React, { useState, useEffect } from 'react';
import { User, InterviewResult } from '../types';
import { geminiService } from '../geminiService';
import { Search, Calendar, Briefcase, Award, ChevronRight, User as UserIcon, LogOut } from 'lucide-react';

interface AdminDashboardProps {
  user: User;
  onViewResult: (id: string) => void;
  onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user, onViewResult, onLogout }) => {
  const [results, setResults] = useState<InterviewResult[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllResults = async () => {
      // 32. Retrieve Candidate Results (Admin)
      const data = await geminiService.getAllResults();
      setResults(data);
      setLoading(false);
    };
    fetchAllResults();
  }, []);

  const filteredResults = results.filter(item => 
    item.candidateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.jobRole.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-3xl gap-4 shadow-xl">
        <div className="flex items-center gap-4">
             <div className="w-12 h-12 bg-purple-600/20 rounded-xl flex items-center justify-center text-purple-400">
                <UserIcon size={24} />
             </div>
             <div>
                <h2 className="text-xl font-bold text-white">Admin Portal</h2>
                <p className="text-sm text-slate-400">Welcome back, {user.name}</p>
             </div>
        </div>
        <button 
            onClick={onLogout}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-bold text-xs flex items-center gap-2 transition-all"
        >
            <LogOut size={14} /> Sign Out
        </button>
      </div>

      {/* Stats/Search */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl flex flex-col justify-center text-center">
            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Total</h3>
            <p className="text-4xl font-black text-white">{results.length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl flex flex-col justify-center text-center">
            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Completed</h3>
            <p className="text-4xl font-black text-emerald-400">{results.filter(r => r.scores.overall !== -1).length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl flex flex-col justify-center text-center">
            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Incomplete</h3>
            <p className="text-4xl font-black text-amber-400">{results.filter(r => r.scores.overall === -1).length}</p>
        </div>
        <div className="md:col-span-1 relative">
           <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
           <input 
             type="text" 
             placeholder="Search candidates or roles..."
             value={searchTerm}
             onChange={(e) => setSearchTerm(e.target.value)}
             className="w-full h-full bg-slate-950 border border-slate-800 rounded-3xl pl-12 pr-6 text-sm focus:border-purple-500 outline-none transition-all py-6 md:py-0"
           />
        </div>
      </div>

      {/* List */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden p-6">
         <h3 className="text-lg font-bold text-white mb-6 pl-2">All Candidate Sessions</h3>
         
         <div className="space-y-4">
            {loading ? (
                <div className="text-center py-20 text-slate-500">Loading records...</div>
            ) : filteredResults.length > 0 ? (
                filteredResults.map((item) => (
                    <div 
                      key={item.id}
                      onClick={() => onViewResult(item.id)}
                      className="group bg-slate-950/50 hover:bg-slate-800 border border-slate-800/50 p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 transition-all cursor-pointer"
                    >
                       <div className="flex items-center gap-4 w-full md:w-auto">
                          <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center font-bold text-slate-400 group-hover:bg-purple-600 group-hover:text-white transition-all shrink-0">
                             {item.candidateName.charAt(0)}
                          </div>
                          <div>
                             <h4 className="font-bold text-white text-lg">{item.candidateName}</h4>
                             <div className="flex items-center gap-3 text-sm text-slate-500 mt-1">
                                <span className="flex items-center gap-1.5"><Briefcase size={12} /> {item.jobRole}</span>
                                <span className="flex items-center gap-1.5"><Calendar size={12} /> {item.date}</span>
                             </div>
                          </div>
                       </div>

                       <div className="flex items-center gap-8 w-full md:w-auto justify-between border-t md:border-t-0 border-slate-800 pt-4 md:pt-0">
                          <div className="flex gap-8">
                             <div className="text-center">
                                <p className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Score</p>
                                <p className={`text-xl font-bold ${item.scores.overall >= 70 ? 'text-emerald-400' : item.scores.overall >= 50 ? 'text-blue-400' : 'text-amber-400'}`}>
                                    {item.scores.overall}%
                                </p>
                             </div>
                             <div className="hidden md:block w-px h-10 bg-slate-800" />
                              <div className="text-center">
                                <p className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Status</p>
                                {item.userDeleted ? (
                                  <span className="px-2 py-0.5 text-xs font-bold bg-red-500/20 text-red-400 rounded-full border border-red-500/30">
                                    Deleted by User
                                  </span>
                                ) : (
                                  <p className="text-sm font-bold text-slate-300">Completed</p>
                                )}
                             </div>
                          </div>
                          <div className="bg-slate-800 p-2 rounded-xl group-hover:bg-purple-600 transition-colors">
                             <ChevronRight className="text-white" size={20} />
                          </div>
                       </div>
                    </div>
                ))
            ) : (
                <div className="text-center py-20 text-slate-500">No records found matching your search.</div>
            )}
         </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
