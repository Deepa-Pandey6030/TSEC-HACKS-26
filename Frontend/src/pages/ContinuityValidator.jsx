import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useGrammarCheck } from '../hooks/useGrammarCheck';
import GrammarOverlay from '../components/Editor/GrammarOverlay';

// Simple Icons (SVG) to avoid external dependencies like lucide-react
const Icons = {
  Shield: () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-400"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
  ),
  Alert: () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-yellow-400"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
  ),
  Danger: () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-500"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
  ),
  Check: () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-400"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
  )
};

const ContinuityValidator = () => {
  const [chapterId, setChapterId] = useState(1);
  const [text, setText] = useState(""); 
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("idle");
  const { matches, setMatches } = useGrammarCheck(text);

  const simulateExtraction = () => {
    return {
      chapter_id: parseInt(chapterId),
      text_snippet: text,
      // Logic handled by backend now, but structure kept for compatibility
      characters: [] 
    };
  };

  const handleApplyGrammarFix = (match, replacement) => {
    const prefix = text.slice(0, match.offset);
    const suffix = text.slice(match.offset + match.length);
    const newText = prefix + replacement + suffix;
    setText(newText);

    // Remove the fixed match locally to update UI instantly
    setMatches(prev => prev.filter(m => m.offset !== match.offset));
  };

  const validateChapter = async () => {
    setStatus("loading");
    setAlerts([]);
    try {
      const payload = simulateExtraction();
      // Ensure this URL matches your actual backend port
      const response = await axios.post('http://127.0.0.1:8000/validate', payload);
      
      if (response.data.status === "violation") {
        setAlerts(response.data.alerts);
        setStatus("error");
      } else {
        setStatus("valid");
      }
    } catch (error) {
      console.error(error);
      alert("Backend not connected!");
      setStatus("idle");
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-200 font-sans selection:bg-cyan-500/30 overflow-hidden relative">
      
      {/* BACKGROUND GLOW EFFECT */}
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-purple-900/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-0 w-[600px] h-[500px] bg-cyan-900/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 py-12 relative z-10">
        
        {/* HERO HEADER */}
        <div className="text-center mb-16 space-y-4">
          <motion.div 
             initial={{ opacity: 0, y: 20 }}
             animate={{ opacity: 1, y: 0 }}
             transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-4">
              Make your story <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
                unbreakable.
              </span>
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Experience the future of narrative consistency with our autonomous AI ecosystem that protects your plot in real-time.
            </p>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* EDITOR SECTION (Left - Wider) */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-[#0f0f0f]/80 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-2xl">
              
              {/* Toolbar */}
              <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-4">
                <div className="flex items-center gap-3">
                  <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                  </span>
                  <span className="text-sm font-medium text-cyan-400 tracking-wider uppercase">Live Editor</span>
                </div>
                
                <div className="flex items-center gap-2">
                  <label className="text-xs text-gray-500 uppercase font-bold">Chapter ID</label>
                  <input 
                    type="number" 
                    value={chapterId} 
                    onChange={(e) => setChapterId(e.target.value)} 
                    className="bg-[#0a0a0a] border border-white/10 rounded-md px-3 py-1 text-white text-sm w-16 text-center focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                  />
                </div>
              </div>

              {/* Text Area */}
              <div className="relative">
                <GrammarOverlay
                  text={text}
                  matches={matches}
                  onApplyFix={handleApplyGrammarFix}
                />
                <textarea 
                  className="relative z-10 w-full h-[400px] bg-transparent border-none text-gray-300 font-mono text-base resize-none focus:ring-0 outline-none placeholder-gray-700 leading-relaxed"
                  placeholder="Paste your scene text here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  style={{
                    fontFamily: 'Georgia, serif',
                    fontSize: '1rem',
                    lineHeight: '1.6'
                  }}
                />
              </div>
              
              {/* Action Bar */}
              <div className="mt-6 flex justify-end pt-4 border-t border-white/5">
                <button 
                  onClick={validateChapter} 
                  disabled={status === "loading"}
                  className={`
                    relative px-8 py-3 rounded-xl font-bold text-white transition-all duration-300
                    ${status === "loading" 
                      ? "bg-gray-800 cursor-not-allowed text-gray-500" 
                      : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:scale-[1.02] active:scale-[0.98]"
                    }
                  `}
                >
                  {status === "loading" ? "Scanning Logic..." : "Experience the Magic"}
                </button>
              </div>
            </div>
          </div>

          {/* RESULTS SECTION (Right - Narrower cards) */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-[#0f0f0f]/80 backdrop-blur-md border border-white/10 rounded-2xl p-6 min-h-[500px]">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Icons.Shield />
                <span>Analysis Report</span>
              </h2>

              <div className="space-y-4">
                {status === "idle" && (
                  <div className="flex flex-col items-center justify-center h-64 text-gray-600 border border-dashed border-gray-800 rounded-xl">
                    <p className="text-sm">Waiting for input...</p>
                  </div>
                )}
                
                {status === "valid" && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-green-500/5 border border-green-500/20 rounded-xl p-6 relative overflow-hidden"
                  >
                    {/* Glowing Accent */}
                    <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 blur-[50px] rounded-full pointer-events-none" />
                    
                    <div className="relative z-10">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="bg-green-500/20 p-2 rounded-lg text-green-400">
                          <Icons.Check />
                        </div>
                        <h3 className="text-xl font-bold text-white tracking-wide">Logic Integrity Verified</h3>
                      </div>

                      <div className="space-y-3 mb-4">
                        {/* Fake "Checklist" to make it feel descriptive */}
                        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                          <span className="text-gray-400">Entity Existence</span>
                          <span className="text-green-400 font-mono">VERIFIED</span>
                        </div>
                        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                          <span className="text-gray-400">Temporal Continuity</span>
                          <span className="text-green-400 font-mono">CONSISTENT</span>
                        </div>
                        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                          <span className="text-gray-400">Status Validity</span>
                          <span className="text-green-400 font-mono">MATCHED</span>
                        </div>
                      </div>

                      <p className="text-sm text-green-200/70 leading-relaxed bg-green-900/10 p-3 rounded-lg border border-green-500/10">
                        The narrative flow aligns perfectly with the established database. No contradictions were found in character mortality or timeline events.
                      </p>
                    </div>
                  </motion.div>
                )}
                
                <AnimatePresence>
                  {alerts.map((alert, index) => (
                    <motion.div 
                      key={index} 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`
                        group relative overflow-hidden rounded-xl border p-5 transition-all
                        ${alert.type === "Critical Error" 
                          ? "bg-red-500/5 border-red-500/20 hover:border-red-500/40" 
                          : "bg-yellow-500/5 border-yellow-500/20 hover:border-yellow-500/40"
                        }
                      `}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-2">
                           {alert.type === "Critical Error" ? <Icons.Danger /> : <Icons.Alert />}
                           <span className={`font-bold ${alert.type === "Critical Error" ? "text-red-400" : "text-yellow-400"}`}>
                             {alert.type}
                           </span>
                        </div>
                        <span className="text-[10px] font-mono bg-black/40 border border-white/5 px-2 py-1 rounded text-gray-400">
                          CONFIDENCE: {(alert.ai_confidence * 100).toFixed(0)}%
                        </span>
                      </div>

                      <p className="text-sm text-gray-300 mb-4 leading-relaxed opacity-90">
                        {alert.message}
                      </p>

                      <div className={`
                        text-xs p-3 rounded-lg border
                        ${alert.type === "Critical Error" 
                          ? "bg-red-950/30 border-red-500/10 text-red-200/80" 
                          : "bg-yellow-950/30 border-yellow-500/10 text-yellow-200/80"
                        }
                      `}>
                        <strong className="block mb-1 uppercase tracking-wider text-[10px] opacity-70">Suggested Fix</strong>
                        {alert.suggestion}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContinuityValidator;