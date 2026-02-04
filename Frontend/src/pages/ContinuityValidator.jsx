import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useGrammarCheck } from '../hooks/useGrammarCheck';
import GrammarOverlay from '../components/Editor/GrammarOverlay';

// --- VISUAL ICONS ---
const Icons = {
  Shield: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  Alert: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  Check: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  Users: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  Ghost: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 22v-2a3 3 0 0 1 3-3h.01a3 3 0 0 1 3 3v2"/><path d="M12 2a7 7 0 0 0-7 7v13l2.5-1.5L10 22l2.5-1.5L15 22l2.5-1.5L20 22V9a7 7 0 0 0-7-7z"/><path d="M10 10h.01"/><path d="M14 10h.01"/></svg>,
  Play: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>,
  X: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
};

const ContinuityValidator = () => {
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

  return (
    <div className="flex flex-col h-screen w-full bg-[#000000] text-gray-200 font-sans overflow-hidden">
      
      {/* --- TOP HEADER --- */}
      <nav className="flex items-center justify-between h-16 px-6 border-b border-gray-800 bg-[#09090b] shrink-0 z-50">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded bg-blue-600 text-white font-bold tracking-tight shadow-lg shadow-blue-900/50">N</div>
          <div>
            <h1 className="text-base font-bold text-white tracking-wide">Nolan Editor <span className="text-blue-500 text-xs uppercase ml-1">Studio</span></h1>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3 bg-gray-900 px-4 py-1.5 rounded-full border border-gray-800">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Chapter</span>
            <input 
              type="number" 
              value={chapterId} 
              onChange={(e) => setChapterId(e.target.value)} 
              className="bg-transparent w-8 text-sm font-bold text-white text-center focus:outline-none"
            />
          </div>
          <button 
            onClick={validateChapter}
            disabled={status === "loading"}
            className={`
              flex items-center gap-2 px-6 py-2 rounded-full text-sm font-bold transition-all shadow-md
              ${status === "loading" 
                ? "bg-gray-800 text-gray-500 cursor-not-allowed" 
                : "bg-white text-black hover:bg-gray-200 hover:shadow-white/10"
              }
            `}
          >
            {status === "loading" ? "Scanning..." : <><Icons.Play /> Run Safety Check</>}
          </button>
        </div>
      </nav>

      {/* --- MAIN WORKSPACE --- */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* === LEFT PANEL: REFERENCE (Cast & Forgotten) === */}
        <aside className="w-[300px] flex flex-col border-r border-gray-800 bg-[#0c0c0e] shrink-0">
          
          {/* Section 1: Cast Overview */}
          <div className="p-6 border-b border-gray-800">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Icons.Users /> Cast Database
            </h3>
            {analytics ? (
              <div className="bg-[#18181b] rounded-xl p-4 border border-gray-800">
                <div className="flex justify-between items-end mb-2">
                  <span className="text-3xl font-light text-white">{analytics.total_characters}</span>
                  <span className="text-[10px] text-gray-500 uppercase mb-1">Total Entities</span>
                </div>
                {/* Visual Bar */}
                <div className="flex h-2 w-full rounded-full overflow-hidden bg-gray-800">
                  <div className="bg-green-500" style={{ width: `${(analytics.active_count / analytics.total_characters) * 100}%` }}></div>
                </div>
                <div className="flex justify-between mt-2 text-[10px] uppercase font-bold text-gray-500">
                  <span>{analytics.active_count} Active</span>
                  <span>{analytics.inactive_count} Inactive</span>
                </div>
              </div>
            ) : <div className="h-20 bg-gray-800 animate-pulse rounded-xl"></div>}
          </div>

          {/* Section 2: Forgotten Characters */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="px-6 py-4 bg-[#0c0c0e]">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                <Icons.Ghost /> Forgotten List
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-3 custom-scrollbar">
              {analytics && analytics.dormant_characters.length > 0 ? (
                analytics.dormant_characters.map((char, i) => (
                  <div key={i} className="flex justify-between items-center p-3 rounded-lg bg-[#18181b] border border-gray-800/50 hover:border-purple-500/50 transition-colors group">
                    <div>
                      <div className="text-sm font-medium text-gray-200 group-hover:text-purple-300 transition-colors">{char.name}</div>
                      <div className="text-[10px] text-gray-500">Last: Ch {char.last_seen}</div>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-xs font-bold text-purple-400">Not seen since:{char.gap}</span>
                      <span className="text-[8px] uppercase text-gray-600">Chapters</span>
                    </div>
                  </div>
                ))
              ) : (
                 <div className="text-center py-10 opacity-50 text-xs">No dormant characters.</div>
              )}
            </div>
          </div>
        </aside>

        {/* === CENTER PANEL: EDITOR === */}
        <main className="flex-1 flex flex-col min-w-0 bg-[#09090b] relative z-0">
          <div className="flex-1 relative overflow-y-auto custom-scrollbar">
            <div className="max-w-3xl mx-auto min-h-full py-12 px-10 relative z-10">
              <GrammarOverlay text={text} matches={matches} onApplyFix={handleApplyGrammarFix} />
              <textarea 
                className="w-full h-full min-h-[70vh] bg-transparent border-none text-gray-300 font-serif text-xl leading-loose resize-none focus:ring-0 outline-none placeholder-gray-800"
                placeholder="Start writing your scene here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                spellCheck="false"
              />
            </div>
          </div>
          <div className="h-8 border-t border-gray-800 bg-[#09090b] flex items-center justify-between px-4 text-[10px] text-gray-600 uppercase font-mono tracking-wider">
             <span>Words: {text.split(/\s+/).filter(Boolean).length}</span>
             <span className={matches.length ? "text-yellow-500" : "text-green-500"}>Grammar: {matches.length ? "Review Needed" : "Clean"}</span>
          </div>
        </main>

        {/* === RIGHT PANEL: SAFETY CHECK (Logic Feed) === */}
        {/* WIDENED to 400px for maximum readability */}
        <aside className="w-[400px] flex flex-col border-l border-gray-800 bg-[#111113] shrink-0 shadow-2xl z-10">
          
          {/* Header Area */}
          <div className="h-16 flex items-center justify-between px-6 border-b border-gray-800 bg-[#18181b]">
            <span className="text-sm font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <Icons.Shield /> Safety Check
            </span>
            {/* Quick Status Pill */}
            {status === "valid" && <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-[10px] font-bold uppercase rounded border border-green-500/20">Passed</span>}
            {status === "error" && <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-[10px] font-bold uppercase rounded border border-red-500/20">Failed</span>}
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar bg-[#111113]">
            {status === "idle" && (
              <div className="flex flex-col items-center justify-center h-64 text-gray-600 opacity-60">
                 <div className="mb-4 p-4 bg-gray-800/50 rounded-full"><Icons.Shield /></div>
                 <p className="text-xs uppercase tracking-widest font-bold">System Ready</p>
                 <p className="text-[10px] mt-2">Waiting for text analysis...</p>
              </div>
            )}

            {status === "valid" && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="p-6 bg-green-500/5 border border-green-500/20 rounded-xl">
                 <div className="flex items-center gap-3 mb-3">
                   <div className="p-2 bg-green-500/20 rounded-full text-green-400"><Icons.Check /></div>
                   <h4 className="text-base font-bold text-white">All Systems Go</h4>
                 </div>
                 <p className="text-sm text-green-200/70 leading-relaxed">
                   No logical contradictions found. Timeline and character mortality are consistent.
                 </p>
              </motion.div>
            )}

            <AnimatePresence>
              {alerts.map((alert, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`
                    relative p-5 rounded-xl border-l-4 shadow-lg
                    ${alert.type === "Critical Error" 
                      ? "bg-[#1f1212] border-l-red-500 border-y border-r border-red-500/20" 
                      : "bg-[#1f1a12] border-l-yellow-500 border-y border-r border-yellow-500/20"
                    }
                  `}
                >
                  {/* Card Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                       {alert.type === "Critical Error" ? <span className="text-red-500"><Icons.X /></span> : <span className="text-yellow-500"><Icons.Alert /></span>}
                       <span className={`text-xs font-bold uppercase tracking-wider ${alert.type === "Critical Error" ? "text-red-400" : "text-yellow-400"}`}>
                         {alert.type}
                       </span>
                    </div>
                  </div>

                  {/* Message Body - Larger Text */}
                  <p className="text-sm text-gray-200 leading-relaxed mb-4 font-light">
                    {alert.message}
                  </p>

                  {/* Suggestion Box */}
                  <div className="text-xs p-3 bg-black/40 rounded-lg border border-white/5">
                    <strong className="block text-gray-500 uppercase text-[10px] mb-1">Recommended Fix</strong>
                    <span className="text-gray-300">{alert.suggestion}</span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </aside>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #444; }
      `}</style>
    </div>
  );
};

export default ContinuityValidator;