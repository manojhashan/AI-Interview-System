
import React, { useState, useRef, useEffect } from 'react';
import { User, InterviewQuestion, ConfidenceScore, ResumeData, QuestionDetail, InterviewResult } from '../types';
import { geminiService } from '../geminiService';
import { Camera, Mic, Play, Square, Loader2, ArrowRight, VideoOff, PlayCircle, Plus, CheckCircle, X, AlertCircle } from 'lucide-react';

interface InterviewSessionProps {
  user: User;
  onComplete: (resultId?: string) => void;
  onAddResume: () => void;
}

const InterviewSession: React.FC<InterviewSessionProps> = ({ user, onComplete, onAddResume }) => {
  const [step, setStep] = useState<'selection' | 'setup' | 'active' | 'analyzing' | 'finished'>('selection');
  const [selectedResume, setSelectedResume] = useState<ResumeData | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionDetails, setSessionDetails] = useState<QuestionDetail[]>([]);
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [frames, setFrames] = useState<string[]>([]);

  // Text-to-Speech Logic
  useEffect(() => {
    if (step === 'active' && questions[currentQuestionIdx]) {
      const text = questions[currentQuestionIdx].text;
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Optional: Set voice details (can be enhanced later to select specific voices)
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = isMuted ? 0 : 1;

      // Cancel previous speech to prevent overlapping
      window.speechSynthesis.cancel();
      
      // Small delay for natural feel
      const timer = setTimeout(() => {
        if (!isMuted) window.speechSynthesis.speak(utterance);
      }, 500);

      return () => {
        clearTimeout(timer);
        window.speechSynthesis.cancel();
      };
    }
  }, [step, currentQuestionIdx, questions, isMuted]);

  // Clean up speech on component unmount
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  // Ensure camera stream is attached to the video element whenever the step changes
  useEffect(() => {
    if (mediaStreamRef.current && videoRef.current) {
      videoRef.current.srcObject = mediaStreamRef.current;
    }
  }, [step, isRecording]);

  const startSetup = async () => {
    if (!selectedResume) return;
    setStep('setup');
    // 1. Get Camera & Mic
    // We ask permission to use the camera and microphone.
    try {
      // 18. Device Access Validation
      // 24. Capture Audio Input
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 }, 
        audio: true 
      });

      // Explicitly check for audio track
      const audioTracks = stream.getAudioTracks();
      if (audioTracks.length === 0 || !audioTracks[0].enabled) {
          throw new Error("Microphone not detected or disabled.");
      }

      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setIsProcessing(true);
      const generated = await geminiService.generateQuestions(
        selectedResume as any,
        selectedResume.resumeTitle
      );
      // alert(`DEBUG: Received ${generated ? generated.length : 'null'} questions from API`);
      setQuestions(generated);
      setIsProcessing(false);
      // 2. Generate Questions
      // The AI reads the resume and makes up questions.
    } catch (err) {
      console.error("Device Access Error:", err);
      // Fallback for specific mic error if possible to distinguish
      alert("Error: Camera and Microphone are strictly required. Please check permissions and try again.");
      setStep('selection'); // Go back
    }
  };

  const startInterview = () => {
    // 20. Readiness Confirmation Handling
    // 20. Readiness Confirmation Handling
    setStep('active');
  };

  const captureFrame = () => {
    if (videoRef.current && canvasRef.current) {
        // 27. Capture Facial Expressions
      const context = canvasRef.current.getContext('2d');
      if (context) {
        // 27. Capture Facial Expressions
        context.drawImage(videoRef.current, 0, 0, 400, 300);
        const dataUrl = canvasRef.current.toDataURL('image/jpeg', 0.5);
        setFrames(prev => [...prev.slice(-4), dataUrl]); 
      }
    }
  };

  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState(""); // meaningful variable for UI feedback
  const recognitionRef = useRef<any>(null);

  const handleStartRecording = () => {
    setIsRecording(true);
    setTranscript(""); 
    setInterimTranscript("");
    
    // 3. Start Recording
    // This turns on the microphone to listen to the answer.
    
    // Start Video Capture Loop
    const intervalId = setInterval(captureFrame, 2000);
    (window as any)._frameCaptureInterval = intervalId;

    // Start Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
            let final = '';
            let interim = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    final += event.results[i][0].transcript + ' ';
                } else {
                    interim += event.results[i][0].transcript;
                }
            }
            
            if (final) {
                setTranscript(prev => prev + final);
            }
            setInterimTranscript(interim);
        };

        recognition.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            if (event.error === 'not-allowed') {
                alert("Microphone access denied. Please allow permission.");
            }
        };

        recognition.start();
        recognitionRef.current = recognition;
    } else {
        alert("Your browser does not support Speech Recognition. Please use Chrome or Edge.");
    }
  };

  const handleStopRecording = async () => {
    setIsRecording(false);
    clearInterval((window as any)._frameCaptureInterval);
    
    if (recognitionRef.current) {
        recognitionRef.current.stop();
    }
    
    setIsProcessing(true);
    try {
      const question = questions[currentQuestionIdx].text;
      
      // Combine final and any remaining interim transcript
      const fullTranscript = (transcript + interimTranscript).trim();
      
      const answerText = fullTranscript.length > 0 
        ? fullTranscript 
        : "No audio detected. (Please ensure you speak clearly or check microphone permissions)"; 
      
      const analysis = await geminiService.analyzeAnswer(question, answerText, undefined, frames);
      
      const newDetail: QuestionDetail = {
        question: question,
        answer: answerText,
        scores: analysis.scores,
        feedback: analysis.feedback
      };

      setSessionDetails(prev => [...prev, newDetail]);

      if (currentQuestionIdx < questions.length - 1) {
        setCurrentQuestionIdx(prev => prev + 1);
        setFrames([]);
        setTranscript("");
        setInterimTranscript("");
      } else {
        setStep('finished');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const stopTracks = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    if ((window as any)._frameCaptureInterval) {
      clearInterval((window as any)._frameCaptureInterval);
    }
  };

  const saveFullSession = (isIncomplete: boolean = false) => {
    if (sessionDetails.length === 0) return;

    // Helper to calculate average safely
    const avg = (key: keyof ConfidenceScore) => {
        if (sessionDetails.length === 0) return 0;
        return Math.round(sessionDetails.reduce((sum, d) => sum + d.scores[key], 0) / sessionDetails.length);
    };

    const fullResult: InterviewResult = {
      id: Math.random().toString(36).substr(2, 9),
      resumeId: selectedResume?.id || "",
      candidateId: user.id, // Optional now
      candidateName: user.name,
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString(),
      jobRole: selectedResume?.resumeTitle || "Professional",
      scores: {
        overall: isIncomplete ? -1 : avg('overall'), // -1 indicates incomplete/aborted
        facial: avg('facial'),
        vocal: avg('vocal'),
        semantic: avg('semantic'),
      },
      details: sessionDetails
    };

    // 4. Save Everything
    // We send all the answers and scores to the database.

    // Save to Database
    setIsProcessing(true); // Reuse/Show processing state
    geminiService.saveInterviewResult(fullResult).then(savedResult => {
        if (savedResult && savedResult.id) {
            console.log("Session saved to DB");
            stopTracks();
            onComplete(savedResult.id);
        } else {
             alert("Failed to save session to database.");
             setIsProcessing(false);
        }
    });
  };

  const handleExitInterview = () => {
    // 21. Early Interview Termination
    if (sessionDetails.length > 0) {
        // Save partial result
        saveFullSession(true); 
    } else {
        stopTracks();
        onComplete();
    }
  };

  if (step === 'selection') {
    return (
      <div className="max-w-4xl mx-auto py-10 animate-in fade-in slide-in-from-bottom-4">
        <div className="text-center mb-12">
           <h2 className="text-3xl font-bold mb-4 text-white">Choose Your Interview Profile</h2>
           <p className="text-slate-400">Select which resume profile you'd like to use for this session.</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* 17. Candidate Eligibility Verification (Selected Profile) */}
          <div 
            onClick={onAddResume}
            className="bg-slate-900/50 border-2 border-dashed border-slate-800 p-8 rounded-3xl flex flex-col items-center justify-center text-center hover:border-blue-500/50 hover:bg-slate-900 transition-all cursor-pointer group"
          >
             <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Plus size={32} className="text-slate-500 group-hover:text-blue-500" />
             </div>
             <span className="font-bold text-slate-400 group-hover:text-white">Create New Profile</span>
          </div>

          {user.resumes.map(resume => (
            <div 
              key={resume.id} 
              onClick={() => setSelectedResume(resume)}
              className={`p-8 rounded-3xl border-2 transition-all cursor-pointer relative overflow-hidden group ${
                selectedResume?.id === resume.id ? 'bg-blue-600 border-blue-400 shadow-xl shadow-blue-600/20' : 'bg-slate-900 border-slate-800 hover:border-slate-700'
              }`}
            >
               <h3 className={`text-xl font-bold mb-2 ${selectedResume?.id === resume.id ? 'text-white' : 'text-slate-200'}`}>{resume.resumeTitle}</h3>
               <p className={`text-xs uppercase tracking-widest font-bold mb-8 ${selectedResume?.id === resume.id ? 'text-blue-200' : 'text-slate-500'}`}>Professional Profile</p>
               
               <div className={`space-y-2 text-sm ${selectedResume?.id === resume.id ? 'text-blue-100' : 'text-slate-400'}`}>
                  <p>• {resume.skills.length} Skills listed</p>
                  <p>• {resume.experience.length} Roles recorded</p>
               </div>

               {selectedResume?.id === resume.id && (
                  <div className="absolute top-4 right-4 bg-white/20 backdrop-blur-md p-1 rounded-full">
                    <CheckCircle size={20} className="text-white" />
                  </div>
               )}
            </div>
          ))}
        </div>

        {selectedResume && (
          <div className="mt-12 flex justify-center">
             <button 
               onClick={startSetup}
               className="bg-emerald-600 hover:bg-emerald-500 text-white px-12 py-4 rounded-2xl font-bold text-lg transition-all shadow-xl shadow-emerald-600/20 flex items-center gap-3 animate-in zoom-in"
             >
               Confirm & Start Session <ArrowRight size={20} />
             </button>
          </div>
        )}
      </div>
    );
  }

  if (step === 'setup') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-2xl mx-auto text-center animate-in zoom-in duration-300">
        {/* 19. Interview Environment Initialization */}
        <h2 className="text-3xl font-bold mb-2 text-white">Final Check</h2>
        <p className="text-slate-500 mb-8">Role: {selectedResume?.resumeTitle}</p>
        <div className="aspect-video bg-slate-950 rounded-2xl mb-8 overflow-hidden relative flex items-center justify-center border border-slate-800 shadow-inner">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            className="w-full h-full object-cover -scale-x-100" 
          />
          {!mediaStreamRef.current && (
            <div className="absolute inset-0 text-slate-700 flex flex-col items-center justify-center bg-slate-950">
              <VideoOff size={48} className="mb-2" />
              <p>Camera is currently off</p>
            </div>
          )}
        </div>
        
        <div className="flex justify-center gap-4 mb-8">
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg">
            <Camera size={18} className={mediaStreamRef.current ? 'text-emerald-400' : 'text-red-400'} />
            <span className="text-sm">Video Ready</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg">
            <Mic size={18} className={mediaStreamRef.current ? 'text-emerald-400' : 'text-red-400'} />
            <span className="text-sm">Audio Ready</span>
          </div>
        </div>

        {!mediaStreamRef.current ? (
          <button 
            onClick={startSetup}
            className="bg-blue-600 hover:bg-blue-500 text-white px-10 py-4 rounded-xl font-bold transition-all"
          >
            Check Permissions
          </button>
        ) : (
          <div className="flex flex-col gap-4">
            <button 
              onClick={startInterview}
              disabled={isProcessing}
              className="bg-blue-600 hover:bg-blue-500 text-white px-10 py-4 rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2 mx-auto w-full max-w-xs justify-center"
            >
              {isProcessing ? <Loader2 className="animate-spin" /> : 'Begin Interview Session'}
            </button>
            <button 
              onClick={handleExitInterview}
              className="text-slate-500 hover:text-white transition-colors text-sm font-medium"
            >
              Cancel & Return to Dashboard
            </button>
          </div>
        )}
      </div>
    );
  }

  if (step === 'active') {
    const q = questions[currentQuestionIdx];
    return (
      <div className="relative animate-in fade-in duration-500">
        {/* Exit Confirmation Modal */}
        {showExitConfirm && (
          <div className="fixed inset-0 z-[100] bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-6">
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl max-w-sm w-full shadow-2xl animate-in zoom-in duration-200">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-6 mx-auto">
                <AlertCircle className="text-red-500" size={32} />
              </div>
              <h3 className="text-xl font-bold text-white text-center mb-2">Stop Interview?</h3>
              <p className="text-slate-400 text-center text-sm mb-8">Are you sure? Your progress in this session will be lost and camera will be turned off.</p>
              <div className="flex flex-col gap-3">
                <button 
                  onClick={handleExitInterview}
                  className="w-full bg-red-600 hover:bg-red-500 text-white py-3 rounded-xl font-bold transition-all"
                >
                  Yes, End Session
                </button>
                <button 
                  onClick={() => setShowExitConfirm(false)}
                  className="w-full bg-slate-800 hover:bg-slate-700 text-white py-3 rounded-xl font-bold transition-all"
                >
                  No, Continue Interview
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Top Header with Exit */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Recording In Progress</span>
          </div>
          <div className="flex items-center gap-3">
             <button 
              onClick={() => setIsMuted(!isMuted)}
              className="flex items-center gap-2 bg-slate-900/50 hover:bg-slate-800 border border-slate-800 px-4 py-2 rounded-xl text-slate-400 hover:text-white transition-all font-bold text-xs"
            >
              {isMuted ? "🔇 Unmute Question" : "🔊 Mute Question"}
            </button>
            <button 
              onClick={() => setShowExitConfirm(true)}
              className="flex items-center gap-2 bg-slate-900/50 hover:bg-red-500/10 border border-slate-800 hover:border-red-500/30 px-4 py-2 rounded-xl text-slate-400 hover:text-red-500 transition-all font-bold text-xs"
            >
              <X size={16} /> Exit Session
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          <canvas ref={canvasRef} className="hidden" width="400" height="300" />
          
          <div className="lg:col-span-8 space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden relative shadow-2xl">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                muted 
                className="w-full aspect-video object-cover -scale-x-100" 
              />
              <div className="absolute top-4 left-4 flex gap-2">
                <div className="bg-red-500/80 backdrop-blur-md text-white text-[10px] font-bold px-2 py-1 rounded flex items-center gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" /> LIVE
                </div>
                <div className="bg-slate-900/80 backdrop-blur-md text-white text-[10px] font-bold px-2 py-1 rounded">
                  720P HD
                </div>
              </div>
              
              {isRecording && (
                <div className="absolute bottom-4 right-4 flex items-center gap-3">
                  <div className="bg-slate-900/60 backdrop-blur-md rounded-full px-4 py-1.5 flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" />
                      <span className="text-xs font-bold text-white uppercase tracking-widest">Listening</span>
                  </div>
                </div>
              )}
            </div>

            <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl">
              <div className="flex items-center gap-3 mb-4">
                  <span className="bg-blue-600/20 text-blue-400 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest">Question {currentQuestionIdx + 1} of {questions.length}</span>
                  <span className="bg-slate-800 text-slate-400 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest">{q?.category}</span>
              </div>
              <h3 className="text-2xl font-bold text-white leading-relaxed">
                {q?.text || "Generating next question..."}
              </h3>
            </div>
          </div>

          <div className="lg:col-span-4 space-y-6">
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl h-full flex flex-col justify-center text-center space-y-8">
              <p className="text-slate-400 text-sm">Use the controls below to answer. AI analyzes your behavior in real-time.</p>
              
              <div className="flex justify-center gap-6">
                {!isRecording ? (
                   <button
                     onClick={handleStartRecording}
                     disabled={isProcessing}
                     className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-full font-bold flex items-center gap-3 transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
                   >
                     <Mic size={20} />
                     Start Answer
                   </button>
                ) : (
                   <button
                     onClick={handleStopRecording}
                     className="bg-red-500 hover:bg-red-400 text-white px-8 py-3 rounded-full font-bold flex items-center gap-3 transition-all shadow-lg shadow-red-500/20 animate-pulse"
                   >
                     <Square size={20} fill="currentColor" />
                     Stop Answer
                   </button>
                )}
              </div>

              {/* Live Transcript Display */}
              {(transcript || interimTranscript) && (
                  <div className="mt-4 max-w-2xl mx-auto bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                      <p className="text-slate-400 text-sm mb-1">Live Transcript:</p>
                      <p className="text-white text-lg font-medium text-left">
                          {transcript} <span className="text-slate-400 italic">{interimTranscript}</span>
                      </p>
                  </div>
              )}
            
              {isProcessing && (
                <div className="p-4 bg-slate-800 rounded-xl flex items-center justify-center gap-3 animate-pulse">
                  <Loader2 className="animate-spin text-blue-400" />
                  <span className="text-blue-400 font-medium">AI Multimodal Engine Analyzing...</span>
                </div>
              )}
            </div>

            <div className="pt-8 border-t border-slate-800 grid grid-cols-3 gap-2 opacity-50">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mb-2">
                        <Camera size={16} className="text-blue-400" />
                    </div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">Visual</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mb-2">
                        <Mic size={16} className="text-emerald-400" />
                    </div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">Vocal</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mb-2">
                        <PlayCircle size={16} className="text-purple-400" />
                    </div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">Logic</span>
                  </div>
              </div>
            </div>
          </div>
        </div>
    );
  }

  return (
    <div className="max-w-md mx-auto text-center py-20 animate-in fade-in duration-500">
      <div className="w-24 h-24 bg-emerald-500/20 rounded-full mx-auto flex items-center justify-center mb-8">
        <PlayCircle className="text-emerald-500" size={48} />
      </div>
      <h2 className="text-3xl font-bold mb-4 text-white">Session Complete</h2>
      <p className="text-slate-400 mb-10">You have completed all {questions.length} questions for the **{selectedResume?.resumeTitle}** role.</p>
      <button 
        onClick={() => saveFullSession(false)}
        disabled={isProcessing}
        className={`w-full bg-emerald-600 hover:bg-emerald-500 text-white p-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2 shadow-xl shadow-emerald-500/20 ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {isProcessing ? <Loader2 className="animate-spin" /> : <>View Full Analysis <ArrowRight size={20} /></>}
      </button>
    </div>
  );
};

export default InterviewSession;
