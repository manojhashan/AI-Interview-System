
import React, { useState, useEffect } from 'react';
import { User, InterviewResult } from '../types';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { Plus, ArrowUpRight, Clock, Award } from 'lucide-react';

interface DashboardProps {
  user: User;
  onStartInterview: () => void;
  onViewResult: (id: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ user, onStartInterview, onViewResult }) => {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem('zynergy_results');
    if (saved) setResults(JSON.parse(saved).reverse());
  }, []);

  const latestResult = results[0];
  const chartData = latestResult ? [
    { subject: 'Facial', A: latestResult.scores.facial, fullMark: 100 },
    { subject: 'Vocal', A: latestResult.scores.vocal, fullMark: 100 },
    { subject: 'Semantic', A: latestResult.scores.semantic, fullMark: 100 },
    { subject: 'Engage', A: (latestResult.scores.facial + latestResult.scores.vocal) / 2, fullMark: 100 },
    { subject: 'Logic', A: latestResult.scores.semantic, fullMark: 100 },
  ] : [];

  // Circumference = 2 * PI * r (for r = 54, it's ~339.3)
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const score = latestResult?.scores.overall || 0;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-gradient-to-br from-blue-600 to-indigo-700 p-8 rounded-3xl text-white relative overflow-hidden shadow-2xl shadow-blue-500/20">
           <div className="relative z-10">
              <h2 className="text-2xl font-bold mb-2">Ready to shine, {user.name.split(' ')[0]}?</h2>
              <p className="text-blue-100 mb-8 max-w-md">Our AI multimodal engine analyzes over 50 data points from your voice and face to estimate confidence.</p>
              <button 
                onClick={onStartInterview}
                className="bg-white text-blue-600 px-6 py-3 rounded-xl font-bold hover:bg-blue-50 transition-all flex items-center gap-2"
              >
                <Plus size={20} /> New Interview
              </button>
           </div>
           <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
           <Award className="absolute right-8 top-8 opacity-20" size={120} />
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl flex flex-col items-center justify-center text-center">
            <h3 className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-4">Overall Level</h3>
            <div className="relative w-32 h-32 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90 origin-center" viewBox="0 0 128 128">
                    {/* Background circle */}
                    <circle 
                      cx="64" 
                      cy="64" 
                      r={radius} 
                      stroke="currentColor" 
                      strokeWidth="10" 
                      fill="transparent" 
                      className="text-slate-800" 
                    />
                    {/* Progress circle */}
                    <circle 
                      cx="64" 
                      cy="64" 
                      r={radius} 
                      stroke="currentColor" 
                      strokeWidth="10" 
                      fill="transparent" 
                      strokeDasharray={circumference}
                      style={{ 
                        strokeDashoffset: offset,
                        transition: 'stroke-dashoffset 1s ease-out'
                      }}
                      strokeLinecap="round"
                      className="text-blue-500" 
                    />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-bold text-white">{score}%</span>
                </div>
            </div>
            <p className="mt-4 text-xs text-slate-500">Based on your latest session</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <section className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2"><Clock size={20} className="text-blue-400" /> Recent Activity</h3>
          <div className="space-y-4">
            {results.length > 0 ? results.map((res) => (
              <div key={res.id} className="group bg-slate-950/50 hover:bg-slate-800 border border-slate-800/50 p-4 rounded-2xl flex items-center justify-between transition-all cursor-pointer" onClick={() => onViewResult(res.id)}>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-500 font-bold group-hover:bg-blue-500 group-hover:text-white transition-all">
                    {res.scores.overall}
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-200">{res.jobRole} Interview</h4>
                    <p className="text-xs text-slate-500">{res.date}</p>
                  </div>
                </div>
                <ArrowUpRight className="text-slate-600 group-hover:text-white transition-all" size={20} />
              </div>
            )) : (
              <div className="text-center py-10">
                <p className="text-slate-500">No interviews completed yet.</p>
              </div>
            )}
          </div>
        </section>

        <section className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2"><Award size={20} className="text-emerald-400" /> Multimodal Breakdown</h3>
          <div className="h-64">
            {results.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Radar name="Zynergy" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-600">
                Complete an interview to see metrics
              </div>
            )}
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="text-center">
                  <span className="text-blue-400 font-bold block">{latestResult?.scores.facial || 0}%</span>
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Facial</span>
              </div>
              <div className="text-center border-x border-slate-800">
                  <span className="text-emerald-400 font-bold block">{latestResult?.scores.vocal || 0}%</span>
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Vocal</span>
              </div>
              <div className="text-center">
                  <span className="text-purple-400 font-bold block">{latestResult?.scores.semantic || 0}%</span>
                  <span className="text-[10px] text-slate-500 uppercase font-bold">Semantic</span>
              </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
