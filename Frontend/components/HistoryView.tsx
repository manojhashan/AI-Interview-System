
import React, { useState, useEffect } from 'react';
import { InterviewResult } from '../types';
import { Calendar, Briefcase, ChevronRight, Award, Trash2, Search } from 'lucide-react';

interface HistoryViewProps {
  onViewResult: (id: string) => void;
}

const HistoryView: React.FC<HistoryViewProps> = ({ onViewResult }) => {
  const [history, setHistory] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const saved = localStorage.getItem('zynergy_results');
    if (saved) {
      // Sorting by date descending (newest first)
      const parsed = JSON.parse(saved);
      setHistory(parsed.reverse());
    }
  }, []);

  const deleteRecord = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm('Delete this interview record permanently?')) {
      const updated = history.filter(item => item.id !== id);
      setHistory(updated);
      localStorage.setItem('zynergy_results', JSON.stringify(updated.reverse()));
    }
  };

  const filteredHistory = history.filter(item => 
    item.jobRole.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-900/50 p-6 rounded-3xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold">Your Interview Archive</h2>
          <p className="text-sm text-slate-500">You have completed {history.length} sessions</p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input 
            type="text" 
            placeholder="Search by role..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:border-blue-500 outline-none transition-all"
          />
        </div>
      </div>

      {filteredHistory.length > 0 ? (
        <div className="grid gap-4">
          {filteredHistory.map((item) => (
            <div 
              key={item.id}
              onClick={() => onViewResult(item.id)}
              className="bg-slate-900 border border-slate-800 p-6 rounded-3xl hover:border-blue-500/50 transition-all group cursor-pointer flex flex-col md:flex-row items-center justify-between gap-6"
            >
              <div className="flex items-center gap-5 w-full md:w-auto">
                <div className="w-14 h-14 bg-blue-600/10 rounded-2xl flex items-center justify-center text-blue-500 group-hover:bg-blue-600 group-hover:text-white transition-all shrink-0">
                  <Award size={28} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">{item.jobRole}</h3>
                  <div className="flex items-center gap-4 mt-1 text-sm text-slate-500">
                    <span className="flex items-center gap-1.5"><Calendar size={14} /> {item.date}</span>
                    <span className="flex items-center gap-1.5"><Briefcase size={14} /> Interview ID: {item.id}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-8 w-full md:w-auto justify-between border-t md:border-t-0 border-slate-800 pt-4 md:pt-0">
                <div className="flex gap-6">
                  <div className="text-center">
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Score</p>
                    <p className="text-xl font-bold text-blue-500">{item.scores.overall}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Facial</p>
                    <p className="text-lg font-bold text-slate-300">{item.scores.facial}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Vocal</p>
                    <p className="text-lg font-bold text-slate-300">{item.scores.vocal}%</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button 
                    onClick={(e) => deleteRecord(e, item.id)}
                    className="p-2.5 text-slate-500 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                    title="Delete Record"
                  >
                    <Trash2 size={20} />
                  </button>
                  <div className="p-2.5 bg-slate-800 group-hover:bg-blue-600 rounded-xl transition-all">
                    <ChevronRight size={20} className="text-white" />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-32 bg-slate-900/30 border-2 border-dashed border-slate-800 rounded-3xl">
          <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-6 text-slate-600">
            <Briefcase size={40} />
          </div>
          <h3 className="text-xl font-bold text-slate-400">No records found</h3>
          <p className="text-slate-500 mt-2">Start an interview session to see your results here.</p>
        </div>
      )}
    </div>
  );
};

export default HistoryView;
