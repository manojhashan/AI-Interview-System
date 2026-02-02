
import React from 'react';
import { ArrowLeft, CheckCircle2, Info, MessageSquare, Award, Star, User } from 'lucide-react';
import { InterviewResult } from '../types';

interface ResultViewProps {
  resultId: string | null;
  onBack: () => void;
}

const ResultView: React.FC<ResultViewProps> = ({ resultId, onBack }) => {
  const results: InterviewResult[] = JSON.parse(localStorage.getItem('zynergy_results') || '[]');
  const result = results.find(r => r.id === resultId) || results[results.length - 1];

  if (!result) return <div className="text-center py-20 text-white">Result data could not be retrieved.</div>;

  return (
    <div className="space-y-12 animate-in fade-in duration-500">
      <button onClick={onBack} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors group">
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" /> Back to Dashboard
      </button>

      {/* Main Stats Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-12 opacity-5">
           <Award size={200} />
        </div>
        
        <div className="relative z-10 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8 mb-12 pb-12 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-3 mb-3">
               <h2 className="text-4xl font-black text-white">{result.jobRole}</h2>
               <span className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-emerald-500/20">AI Verified</span>
            </div>
            <p className="text-slate-400 font-medium">Session Date: {result.date} • Session ID: #{result.id}</p>
          </div>
          
          <div className="flex items-center gap-8 bg-slate-950/50 p-8 rounded-3xl border border-slate-800/50 backdrop-blur-md">
             <div className="text-center">
                <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Overall Score</p>
                <p className="text-5xl font-black text-blue-500">{result.scores.overall}%</p>
             </div>
             <div className="h-14 w-px bg-slate-800" />
             <div className="text-center">
                <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Proficiency</p>
                <p className="text-2xl font-black text-emerald-400">
                   {result.scores.overall >= 80 ? 'EXPERT' : result.scores.overall >= 60 ? 'ADVANCED' : 'INTERMEDIATE'}
                </p>
             </div>
          </div>
        </div>

        {/* Global Average Breakdown */}
        <div className="grid lg:grid-cols-3 gap-10">
           <ScoreCard 
             title="Facial Confidence" 
             score={result.scores.facial} 
             color="blue" 
             desc="Visual engagement, eye contact stability and micro-expressions."
           />
           <ScoreCard 
             title="Vocal Projection" 
             score={result.scores.vocal} 
             color="emerald" 
             desc="Tone modulation, clarity, pitch variance and speech rate."
           />
           <ScoreCard 
             title="Semantic Logic" 
             score={result.scores.semantic} 
             color="purple" 
             desc="Answer structure, technical alignment and contextual relevance."
           />
        </div>
      </div>

      {/* DETAILED BREAKDOWN BY QUESTION */}
      <div className="space-y-6">
         <div className="flex items-center gap-3 mb-4">
            <div className="w-1.5 h-6 bg-blue-500 rounded-full" />
            <h3 className="text-2xl font-bold text-white">Performance Breakdown by Question</h3>
         </div>

         <div className="grid gap-8">
            {result.details.map((detail, index) => (
               <div key={index} className="bg-slate-900/50 border border-slate-800 rounded-[2rem] overflow-hidden hover:border-slate-700 transition-all group">
                  <div className="p-8 border-b border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                     <div className="flex gap-4 items-start max-w-2xl">
                        <div className="w-10 h-10 bg-slate-800 rounded-xl flex items-center justify-center font-bold text-slate-400 shrink-0">
                           {index + 1}
                        </div>
                        <div>
                           <h4 className="text-lg font-bold text-white mb-2 leading-relaxed">"{detail.question}"</h4>
                           <div className="flex flex-wrap gap-2">
                              <span className="bg-blue-600/10 text-blue-400 text-[10px] font-bold px-2.5 py-1 rounded-lg uppercase tracking-wider border border-blue-500/10">Facial: {detail.scores.facial}%</span>
                              <span className="bg-emerald-600/10 text-emerald-400 text-[10px] font-bold px-2.5 py-1 rounded-lg uppercase tracking-wider border border-emerald-500/10">Vocal: {detail.scores.vocal}%</span>
                              <span className="bg-purple-600/10 text-purple-400 text-[10px] font-bold px-2.5 py-1 rounded-lg uppercase tracking-wider border border-purple-500/10">Semantic: {detail.scores.semantic}%</span>
                           </div>
                        </div>
                     </div>
                     <div className="bg-slate-950 px-6 py-3 rounded-2xl border border-slate-800 flex items-center gap-3">
                        <Star size={16} className="text-amber-400 fill-amber-400" />
                        <span className="font-bold text-white text-xl">{detail.scores.overall}%</span>
                     </div>
                  </div>

                  <div className="p-8 grid lg:grid-cols-2 gap-10">
                     <div className="space-y-4">
                        <div className="flex items-center gap-2 text-slate-500 text-xs font-bold uppercase tracking-widest">
                           <User size={14} /> Your Response
                        </div>
                        <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 italic text-slate-400 text-sm leading-relaxed">
                           "{detail.answer}"
                        </div>
                     </div>
                     <div className="space-y-4">
                        <div className="flex items-center gap-2 text-blue-500 text-xs font-bold uppercase tracking-widest">
                           <MessageSquare size={14} /> AI Expert Feedback
                        </div>
                        <div className="space-y-3">
                           <p className="text-slate-300 text-sm font-medium">{detail.feedback.summary}</p>
                           <div className="flex gap-3 bg-blue-500/5 p-4 rounded-xl border border-blue-500/10">
                              <Info size={16} className="text-blue-400 shrink-0 mt-0.5" />
                              <p className="text-xs text-slate-400 leading-relaxed">
                                 <span className="text-blue-300 font-bold">Observation: </span>
                                 {detail.feedback.semantic}
                              </p>
                           </div>
                        </div>
                     </div>
                  </div>
               </div>
            ))}
         </div>
      </div>
    </div>
  );
};

const ScoreCard = ({ title, score, color, desc }: any) => {
  const colorMap: any = {
    blue: 'text-blue-500 border-blue-500',
    emerald: 'text-emerald-500 border-emerald-500',
    purple: 'text-purple-500 border-purple-500',
  };

  return (
    <div className={`bg-slate-950 p-8 rounded-3xl border-l-4 ${colorMap[color].split(' ')[1]} shadow-lg`}>
       <div className="flex justify-between items-center mb-4">
          <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">{title}</h4>
          <span className={`text-3xl font-black ${colorMap[color].split(' ')[0]}`}>{score}%</span>
       </div>
       <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
       <div className="mt-6 h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-1000 ${color === 'blue' ? 'bg-blue-500' : color === 'emerald' ? 'bg-emerald-500' : 'bg-purple-500'}`}
            style={{ width: `${score}%` }}
          />
       </div>
    </div>
  );
};

export default ResultView;
