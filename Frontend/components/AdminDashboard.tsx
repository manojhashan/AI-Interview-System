
import React, { useState, useEffect } from 'react';
import { Users, FileText, Activity, Search, Filter, ExternalLink } from 'lucide-react';

interface AdminDashboardProps {
  onViewResult: (id: string) => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onViewResult }) => {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem('zynergy_results');
    if (saved) setResults(JSON.parse(saved));
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Total Candidates" value="482" icon={<Users className="text-blue-500" />} change="+12%" />
        <StatCard title="Interviews Today" value="24" icon={<Activity className="text-emerald-500" />} change="+5%" />
        <StatCard title="Avg. Confidence" value="76%" icon={<FileText className="text-purple-500" />} change="-2%" />
        <StatCard title="System Status" value="Online" icon={<div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />} />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row justify-between gap-4 items-center">
          <h3 className="text-lg font-bold">Global Interview Logs</h3>
          <div className="flex gap-2 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input 
                placeholder="Search candidates..." 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-300">
              <Filter size={20} />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/50 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                <th className="px-6 py-4">Candidate</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Facial</th>
                <th className="px-6 py-4">Vocal</th>
                <th className="px-6 py-4">Semantic</th>
                <th className="px-6 py-4">Overall</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {results.length > 0 ? results.map((res) => (
                <tr key={res.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-500 font-bold text-xs">
                        {res.candidateName.charAt(0)}
                      </div>
                      <span className="text-sm font-medium">{res.candidateName}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-400">{res.jobRole}</td>
                  <td className="px-6 py-4 text-sm text-slate-400">{res.date}</td>
                  <td className="px-6 py-4">
                    <ScoreBadge value={res.scores.facial} color="blue" />
                  </td>
                  <td className="px-6 py-4">
                    <ScoreBadge value={res.scores.vocal} color="emerald" />
                  </td>
                  <td className="px-6 py-4">
                    <ScoreBadge value={res.scores.semantic} color="purple" />
                  </td>
                  <td className="px-6 py-4 font-bold text-slate-200">{res.scores.overall}%</td>
                  <td className="px-6 py-4">
                    <button 
                      onClick={() => onViewResult(res.id)}
                      className="text-blue-500 hover:text-blue-400 flex items-center gap-1 text-sm font-bold"
                    >
                      Report <ExternalLink size={14} />
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={8} className="px-6 py-20 text-center text-slate-600">
                    No system-wide records available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, change }: any) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl">
    <div className="flex justify-between items-start mb-4">
      <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
        {icon}
      </div>
      {change && (
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${change.startsWith('+') ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
          {change}
        </span>
      )}
    </div>
    <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">{title}</p>
    <p className="text-2xl font-bold mt-1">{value}</p>
  </div>
);

const ScoreBadge = ({ value, color }: { value: number, color: 'blue' | 'emerald' | 'purple' }) => {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    purple: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  };
  return (
    <span className={`px-2 py-1 rounded-md text-[10px] font-bold border ${colors[color]}`}>
      {value}%
    </span>
  );
};

export default AdminDashboard;
