
import React from 'react';
import { Play, Shield, Zap, BarChart3, ChevronRight } from 'lucide-react';

interface LandingPageProps {
  isLoggedIn: boolean;
  onGetStarted: (mode: 'login' | 'signup') => void;
  onGoToDashboard: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ isLoggedIn, onGetStarted, onGoToDashboard }) => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-blue-500/30">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div 
            className="flex items-center gap-3 cursor-pointer group" 
            onClick={scrollToTop}
            title="Zynergy AI Home"
          >
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-110 transition-transform">
              <span className="font-bold text-xl text-white">Z</span>
            </div>
            <span className="font-bold text-xl tracking-tight hidden sm:block text-white group-hover:text-blue-400 transition-colors">Zynergy AI</span>
          </div>
          <div className="flex items-center gap-4">
            {isLoggedIn ? (
              <button 
                onClick={onGoToDashboard}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-full text-sm font-bold transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2"
              >
                Go to Dashboard <ChevronRight size={16} />
              </button>
            ) : (
              <>
                <button 
                  onClick={() => onGetStarted('login')}
                  className="px-5 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                >
                  Sign In
                </button>
                <button 
                  onClick={() => onGetStarted('signup')}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-full text-sm font-bold transition-all shadow-lg shadow-blue-600/20"
                >
                  Sign Up Free
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-40 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold mb-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
            <Zap size={14} /> POWERED BY GEMINI 2.5
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold mb-8 tracking-tight bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent leading-tight">
            Master Your Next <br /> <span className="text-blue-500">Interview with AI</span>
          </h1>
          <p className="max-w-2xl mx-auto text-slate-400 text-lg mb-12 leading-relaxed">
            Real-time multimodal confidence estimation. We analyze your voice, facial cues, and semantic logic to give you explainable feedback.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            {isLoggedIn ? (
               <button 
                onClick={onGoToDashboard}
                className="w-full sm:w-auto px-10 py-5 bg-white text-slate-950 rounded-2xl font-bold text-lg hover:bg-slate-200 transition-all flex items-center justify-center gap-2 group"
              >
                Continue to Dashboard <ChevronRight className="group-hover:translate-x-1 transition-transform" />
              </button>
            ) : (
              <button 
                onClick={() => onGetStarted('signup')}
                className="w-full sm:w-auto px-10 py-5 bg-white text-slate-950 rounded-2xl font-bold text-lg hover:bg-slate-200 transition-all flex items-center justify-center gap-2 group"
              >
                Start Free Trial <ChevronRight className="group-hover:translate-x-1 transition-transform" />
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<Shield className="text-blue-500" />} 
            title="Privacy First" 
            desc="Your data is encrypted and used only for your personalized analysis."
          />
          <FeatureCard 
            icon={<Zap className="text-emerald-500" />} 
            title="Real-time Analysis" 
            desc="Get instant feedback on your confidence levels as you speak."
          />
          <FeatureCard 
            icon={<BarChart3 className="text-purple-500" />} 
            title="Multimodal Insight" 
            desc="Deep learning analysis of facial, vocal and semantic expressions."
          />
        </div>
      </section>
      
      <footer className="py-12 border-t border-white/5 text-center text-slate-500 text-sm">
        <p>© 2025 Zynergy AI System. All rights reserved.</p>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, desc }: any) => (
  <div className="p-8 bg-slate-900/50 border border-white/5 rounded-3xl hover:border-blue-500/30 transition-all group">
    <div className="w-12 h-12 bg-slate-950 rounded-xl flex items-center justify-center mb-6 border border-white/10 group-hover:border-blue-500/50 transition-colors">
      {icon}
    </div>
    <h3 className="text-xl font-bold mb-4">{title}</h3>
    <p className="text-slate-400 leading-relaxed">{desc}</p>
  </div>
);

export default LandingPage;
