import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, AlertTriangle, CheckCircle, Edit, Eye, FileText, Zap, Users, Ghost, Activity } from 'lucide-react';
import { useTheme } from '../lib/theme-provider';
import { useGrammarCheck } from '../hooks/useGrammarCheck';
import GrammarOverlay from '../components/Editor/GrammarOverlay';

const ContinuityValidator = () => {
  const { isReducedMotion } = useTheme();
  const [chapterId, setChapterId] = useState(1);
  const [text, setText] = useState(""); 
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("idle");
  const [analytics, setAnalytics] = useState(null);
  const { matches, setMatches } = useGrammarCheck(text);

  useEffect(() => { fetchAnalytics(); }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/analytics');
      setAnalytics(res.data);
    } catch (err) { console.error(err); }
  };

  const handleApplyGrammarFix = (match, replacement) => {
    const prefix = text.slice(0, match.offset);
    const suffix = text.slice(match.offset + match.length);
    setText(prefix + replacement + suffix);
    setMatches(prev => prev.filter(m => m.offset !== match.offset));
  };

  const validateChapter = async () => {
    setStatus("loading");
    setAlerts([]);
    try {
      const payload = { chapter_id: parseInt(chapterId), text_snippet: text };
      const response = await axios.post('http://127.0.0.1:8000/validate', payload);
      
      if (response.data.status === "violation") {
        setAlerts(response.data.alerts);
        setStatus("error");
      } else {
        setStatus("valid");
      }
      fetchAnalytics();
    } catch (error) {
      alert("System Offline: Check Backend Connection");
      setStatus("idle");
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: isReducedMotion ? 0 : 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 140, damping: 20 }
    }
  };

  return (
    <div className="h-screen flex flex-col bg-[#09090b] text-gray-200 font-sans overflow-hidden">
      
      {/* --- HEADER --- */}
      <motion.header 
        className="h-16 px-6 border-b border-white/5 bg-[#0c0c0e] flex items-center justify-between shrink-0 z-20"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div>
          <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Nolan Validator
          </h1>
          <p className="text-xs text-neutral-500">Continuity Engine v2.0</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 bg-neutral-900/50 border border-white/5 px-3 py-1.5 rounded-lg">
             <span className="text-xs font-medium text-neutral-500 uppercase">Chapter</span>
             <input 
                type="number" 
                value={chapterId} 
                onChange={(e) => setChapterId(e.target.value)} 
                className="bg-transparent w-8 text-sm font-bold text-white text-center focus:outline-none"
             />
          </div>
          <motion.button
            onClick={validateChapter}
            disabled={status === "loading"}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              flex items-center gap-2 px-5 py-2 rounded-lg text-xs font-bold transition-all
              ${status === "loading" 
                ? "bg-neutral-800 text-neutral-500 cursor-not-allowed" 
                : "bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-cyan-900/20 hover:shadow-cyan-900/40"
              }
            `}
          >
            {status === "loading" ? <Zap size={14} className="animate-pulse" /> : <Shield size={14} />}
            {status === "loading" ? "Analyzing..." : "Run Checks"}
          </motion.button>
        </div>
      </motion.header>

      {/* --- MAIN CONTENT GRID --- */}
      <motion.div 
        className="flex-1 grid grid-cols-12 overflow-hidden"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        
        {/* === LEFT SIDEBAR: ANALYTICS (Col 3) === */}
        <motion.aside variants={itemVariants} className="col-span-3 bg-[#0c0c0e] border-r border-white/5 flex flex-col min-w-0">
          
          {/* Section 1: Cast Overview */}
          <div className="p-5 border-b border-white/5">
            <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Users size={14} /> Cast Database
            </h3>
            
            {analytics ? (
              <div className="bg-neutral-900/50 rounded-xl p-4 border border-white/5">
                <div className="flex items-end justify-between mb-3">
                  <span className="text-3xl font-light text-white">{analytics.total_characters}</span>
                  <span className="text-[10px] text-neutral-500 uppercase mb-1">Total Entities</span>
                </div>
                
                <div className="space-y-2">
                  <div className="group">
                    <div className="flex justify-between text-[10px] mb-1 text-neutral-400">
                      <span>Active</span>
                      <span>{analytics.active_count}</span>
                    </div>
                    <div className="h-1.5 w-full bg-neutral-800 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${(analytics.active_count / analytics.total_characters) * 100}%` }}
                        className="h-full bg-green-500/80 rounded-full"
                      />
                    </div>
                  </div>
                  
                  <div className="group">
                    <div className="flex justify-between text-[10px] mb-1 text-neutral-400">
                      <span>Inactive</span>
                      <span>{analytics.inactive_count}</span>
                    </div>
                    <div className="h-1.5 w-full bg-neutral-800 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${(analytics.inactive_count / analytics.total_characters) * 100}%` }}
                        className="h-full bg-neutral-600 rounded-full"
                      />
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="animate-pulse h-24 bg-neutral-900 rounded-xl"></div>
            )}
          </div>

          {/* Section 2: Forgotten Characters */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="p-5 pb-2">
              <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest flex items-center gap-2">
                <Ghost size={14} /> Forgotten List
              </h3>
            </div>
            
            <div className="flex-1 overflow-y-auto px-5 pb-5 space-y-2 custom-scrollbar">
              {analytics && analytics.dormant_characters.length > 0 ? (
                analytics.dormant_characters.map((char, i) => (
                  <motion.div 
                    key={i} 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex justify-between items-center p-3 rounded-lg bg-neutral-900/30 border border-white/5 hover:border-purple-500/30 hover:bg-purple-500/5 transition-all group"
                  >
                    <div>
                      <div className="text-sm font-medium text-neutral-300 group-hover:text-purple-300 transition-colors">{char.name}</div>
                      <div className="text-[10px] text-neutral-500">Last seen: Ch {char.last_seen}</div>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-xs font-bold text-purple-400">+{char.gap}</span>
                      <span className="text-[8px] uppercase text-neutral-600">Chapters</span>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-10 opacity-40 text-xs">
                  <CheckCircle size={24} className="mx-auto mb-2 text-neutral-600" />
                  <p>No dormant characters</p>
                </div>
              )}
            </div>
          </div>
        </motion.aside>

        {/* === CENTER: EDITOR (Col 6) === */}
        <motion.main variants={itemVariants} className="col-span-6 bg-[#09090b] relative flex flex-col min-w-0">
           <div className="flex-1 relative overflow-y-auto custom-scrollbar">
             {/* Gradient Glow */}
             <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2/3 h-64 bg-primary-500/5 blur-[100px] pointer-events-none" />
             
             <div className="max-w-3xl mx-auto min-h-full py-10 px-8 relative z-10">
               <GrammarOverlay text={text} matches={matches} onApplyFix={handleApplyGrammarFix} />
               <textarea 
                 className="w-full h-full min-h-[70vh] bg-transparent border-none text-neutral-300 font-serif text-lg leading-loose resize-none focus:ring-0 outline-none placeholder-neutral-800"
                 placeholder="Begin writing your narrative..."
                 value={text}
                 onChange={(e) => setText(e.target.value)}
                 spellCheck="false"
               />
             </div>
           </div>

           {/* Editor Footer */}
           <div className="h-10 border-t border-white/5 bg-[#0c0c0e] flex items-center justify-between px-6 shrink-0 text-[10px] text-neutral-500 uppercase tracking-wider font-medium">
              <span>{text.split(/\s+/).filter(Boolean).length} Words</span>
              <span className={matches.length ? "text-yellow-500" : "text-green-500"}>
                {matches.length ? `${matches.length} Grammar Suggestions` : "Grammar Clean"}
              </span>
           </div>
        </motion.main>

        {/* === RIGHT SIDEBAR: SAFETY CHECK (Col 3) === */}
        <motion.aside variants={itemVariants} className="col-span-3 bg-[#0c0c0e] border-l border-white/5 flex flex-col min-w-0">
          <div className="p-5 border-b border-white/5 flex items-center justify-between">
            <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest flex items-center gap-2">
              <Shield size={14} /> Logic Feed
            </h3>
            {status === 'valid' && <span className="text-[10px] px-2 py-0.5 bg-green-500/10 text-green-400 rounded border border-green-500/20">PASSED</span>}
            {status === 'error' && <span className="text-[10px] px-2 py-0.5 bg-red-500/10 text-red-400 rounded border border-red-500/20">ISSUES</span>}
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar bg-[#0a0a0c]">
            {status === "idle" && (
               <div className="flex flex-col items-center justify-center h-40 text-neutral-700 text-center">
                 <Shield size={32} className="mb-3 opacity-20" />
                 <p className="text-xs font-medium">System Ready</p>
                 <p className="text-[10px] opacity-60">Waiting for text input</p>
               </div>
            )}

            {status === "valid" && (
              <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="p-5 bg-green-500/5 border border-green-500/10 rounded-xl">
                 <div className="flex items-center gap-2 text-green-400 mb-2">
                   <CheckCircle size={16} />
                   <span className="text-xs font-bold uppercase">Plot Integrity Verified</span>
                 </div>
                 <p className="text-[11px] text-green-200/50 leading-relaxed">
                   Narrative flow aligns with established database facts. No timeline or mortality contradictions found.
                 </p>
              </motion.div>
            )}

            <AnimatePresence>
              {alerts.map((alert, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`
                    relative p-4 rounded-xl border
                    ${alert.type === "Critical Error" 
                      ? "bg-red-500/5 border-red-500/20" 
                      : "bg-yellow-500/5 border-yellow-500/20"
                    }
                  `}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {alert.type === "Critical Error" ? <AlertTriangle size={14} className="text-red-500" /> : <AlertTriangle size={14} className="text-yellow-500" />}
                    <span className={`text-[10px] font-bold uppercase ${alert.type === "Critical Error" ? "text-red-400" : "text-yellow-400"}`}>
                      {alert.type}
                    </span>
                  </div>

                  <p className="text-xs text-neutral-300 leading-relaxed mb-3 font-light">
                    {alert.message}
                  </p>

                  <div className="text-[10px] p-3 bg-black/20 rounded-lg border border-white/5">
                    <strong className="block text-neutral-500 uppercase mb-1 text-[9px]">Recommendation</strong>
                    <span className="text-neutral-400">{alert.suggestion}</span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.aside>

      </motion.div>

      {/* --- SCROLLBAR STYLE --- */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 5px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #262626; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #404040; }
      `}</style>
    </div>
  );
};

export default ContinuityValidator;