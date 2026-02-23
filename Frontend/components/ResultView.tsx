
import React from 'react';
import { ArrowLeft, CheckCircle2, Info, MessageSquare, Award, Star, User, Loader2 } from 'lucide-react';
import { InterviewResult } from '../types';
import { geminiService } from '../geminiService';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface ResultViewProps {
  resultId: string | null;
  onBack: () => void;
  isAdmin?: boolean;
}

const ResultView: React.FC<ResultViewProps> = ({ resultId, onBack, isAdmin = false }) => {
  const [result, setResult] = React.useState<InterviewResult | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchResult = async () => {
        if (!resultId) {
            setLoading(false);
            return;
        }
        // 33. Retrieve Detailed Report
        const data = await geminiService.getInterviewResult(resultId);
        setResult(data);
        setLoading(false);
    };
    fetchResult();
  }, [resultId]);

  if (loading) return (
      <div className="flex items-center justify-center min-h-[50vh]">
          <Loader2 className="animate-spin text-blue-500" size={48} />
      </div>
  );

  if (!result) return <div className="text-center py-20 text-white">Result data could not be retrieved.</div>;

  return (
    // 34. Display Results Securely
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
            <p className="text-slate-400 font-medium">Session: {result.date} at {result.time || ''} • ID: #{result.id}</p>
          </div>
          
          <div className="flex items-center gap-8 bg-slate-950/50 p-8 rounded-3xl border border-slate-800/50 backdrop-blur-md">
             <div className="text-center">
                <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Overall Score</p>
                {result.scores.overall === -1 ? (
                    <p className="text-3xl font-black text-amber-500">INCOMPLETE</p>
                ) : (
                    <p className="text-5xl font-black text-blue-500">{result.scores.overall}%</p>
                )}
             </div>
             <div className="h-14 w-px bg-slate-800" />
             <div className="text-center">
                <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Proficiency</p>
                 <p className="text-2xl font-black text-emerald-400">
                    {result.scores.overall === -1 ? 'N/A' : (result.scores.overall >= 80 ? 'EXPERT' : result.scores.overall >= 60 ? 'ADVANCED' : 'INTERMEDIATE')}
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

      {/* MULTIMODAL ANALYSIS CHARTS — Admin Only */}
      {isAdmin && <MultimodalCharts result={result} />}


      {/* XAI — EXPLAINABLE AI FEEDBACK */}
      {result.xai && (
        <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10 shadow-2xl space-y-8">
          {/* Header */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="w-1.5 h-6 bg-emerald-500 rounded-full" />
            <h3 className="text-2xl font-bold text-white">Overall Explainable AI Feedback</h3>
            <span className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-emerald-500/20">
              XAI · SHAP Analysis
            </span>
          </div>

          {/* Summary */}
          <div className="bg-emerald-900/20 border border-emerald-500/20 rounded-2xl p-5">
            <p className="text-emerald-300 font-semibold text-sm mb-1">Overall Explanation</p>
            <p className="text-slate-300 text-sm leading-relaxed">{result.xai.summary_xai}</p>
          </div>

          {/* SHAP Contribution Bars */}
          <div className="space-y-4">
            <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">SHAP Contribution per Modality</p>
            {[
              { label: 'Vocal',    phi: result.xai.contributions.vocal,    color: 'bg-emerald-500' },
              { label: 'Facial',   phi: result.xai.contributions.facial,   color: 'bg-blue-500' },
              { label: 'Semantic', phi: result.xai.contributions.semantic,  color: 'bg-purple-500' },
            ].map(({ label, phi, color }) => (
              <div key={label} className="flex items-center gap-4">
                <span className="w-20 text-xs font-bold text-slate-400 text-right">{label}</span>
                <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${phi >= 0 ? color : 'bg-red-500'}`}
                    style={{ width: `${Math.min(100, Math.abs(phi) * 5 + 10)}%` }}
                  />
                </div>
                <span className={`text-xs font-bold w-16 ${phi >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {phi >= 0 ? '+' : ''}{phi.toFixed(1)} pts
                </span>
              </div>
            ))}
          </div>

          {/* Per-Modality XAI Explanations */}
          <div className="grid lg:grid-cols-3 gap-6">
            {[
              { label: '🎙 Vocal',    text: result.xai.vocal_xai,    border: 'border-emerald-500/20', bg: 'bg-emerald-500/5' },
              { label: '👁 Facial',  text: result.xai.facial_xai,   border: 'border-blue-500/20',   bg: 'bg-blue-500/5' },
              { label: '💬 Semantic', text: result.xai.semantic_xai, border: 'border-purple-500/20', bg: 'bg-purple-500/5' },
            ].map(({ label, text, border, bg }) => (
              <div key={label} className={`${bg} border ${border} rounded-2xl p-5`}>
                <p className="text-slate-300 font-bold text-xs mb-2">{label}</p>
                <p className="text-slate-400 text-xs leading-relaxed">
                  {text.replace('[+XAI] ', '')}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

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
                                 <span className="text-blue-300 font-bold">Analysis: </span>
                                 {detail.feedback.semantic.split('|').map((part, i) => (
                                     <span key={i} className="block mt-1">
                                        {part.trim()}
                                     </span>
                                 ))}
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

/* ─────────────────────────────────────────────
   Multimodal Charts Component
───────────────────────────────────────────── */
const MultimodalCharts = ({ result }: { result: InterviewResult }) => {
  // Radar data: session-level scores
  const radarData = [
    { subject: 'Vocal',    score: result.scores.vocal },
    { subject: 'Facial',   score: result.scores.facial },
    { subject: 'Semantic', score: result.scores.semantic },
    { subject: 'Overall',  score: result.scores.overall },
  ];

  // Bar data: per-question breakdown
  const barData = result.details.map((d, i) => ({
    name: `Q${i + 1}`,
    Vocal:    d.scores.vocal,
    Facial:   d.scores.facial,
    Semantic: d.scores.semantic,
    Overall:  d.scores.overall,
  }));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10 shadow-2xl space-y-10">
      {/* Section header */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="w-1.5 h-6 bg-purple-500 rounded-full" />
        <h3 className="text-2xl font-bold text-white">Multimodal vs Single Modality Analysis</h3>
        <span className="bg-purple-500/10 text-purple-400 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-purple-500/20">
          Research Insight
        </span>
      </div>
      <p className="text-slate-400 text-sm leading-relaxed -mt-4">
        The <span className="text-purple-400 font-semibold">Overall (Multimodal)</span> score integrates all three modalities,
        providing a more balanced and reliable assessment than any single modality alone.
      </p>

      <div className="grid lg:grid-cols-2 gap-10">
        {/* ── Radar Chart ── */}
        <div className="bg-slate-950/60 rounded-3xl border border-slate-800 p-6">
          <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6 text-center">
            Session Score Balance
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 700 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#a855f7"
                fill="#a855f7"
                fillOpacity={0.25}
                strokeWidth={2}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }}
                formatter={(v: any) => [`${v}%`, 'Score']}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* ── Grouped Bar Chart ── */}
        <div className="bg-slate-950/60 rounded-3xl border border-slate-800 p-6">
          <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6 text-center">
            Per‑Question Modality Comparison
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', color: '#e2e8f0' }}
                formatter={(v: any, name: string) => [`${v}%`, name]}
              />
              <Legend wrapperStyle={{ paddingTop: '12px', fontSize: '11px', color: '#94a3b8' }} />
              <Bar dataKey="Vocal"    fill="#10b981" radius={[4,4,0,0]} />
              <Bar dataKey="Facial"   fill="#3b82f6" radius={[4,4,0,0]} />
              <Bar dataKey="Semantic" fill="#8b5cf6" radius={[4,4,0,0]} />
              <Bar dataKey="Overall"  fill="#f59e0b" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Research callout */}
      <div className="bg-purple-900/20 border border-purple-500/20 rounded-2xl p-5 flex items-start gap-4">
        <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
          <span className="text-purple-400 text-sm font-black">💡</span>
        </div>
        <div>
          <p className="text-purple-300 font-semibold text-sm mb-1">Multimodal Advantage</p>
          <p className="text-slate-400 text-xs leading-relaxed">
            Relying on a single modality can miss key signals — e.g., a candidate may score low on Semantic but
            show high confidence via Facial &amp; Vocal cues. The combined multimodal score (Vocal 40% + Facial 40% + Semantic 20%)
            captures a richer, more reliable picture of interview performance.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResultView;
