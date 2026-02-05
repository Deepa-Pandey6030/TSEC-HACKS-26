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
    } catch (err) {
      console.error(err);
    }
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
    } catch {
      alert("Backend not running");
      setStatus("idle");
    }
  };

  return (
    <div className="h-screen flex flex-col bg-white text-neutral-800 dark:bg-[#09090b] dark:text-gray-200 overflow-hidden">

      {/* HEADER */}
      <motion.header
        className="h-16 px-6 border-b border-neutral-200 bg-neutral-50 
                   dark:border-white/5 dark:bg-[#0c0c0e]
                   flex items-center justify-between"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div>
          <h1 className="text-lg font-bold bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">
            Nolan Validator
          </h1>
          <p className="text-xs text-neutral-500">Continuity Engine</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-neutral-100 dark:bg-neutral-900 px-3 py-1.5 rounded-lg border border-neutral-200 dark:border-white/5">
            <span className="text-xs text-neutral-500 uppercase">Chapter</span>
            <input
              type="number"
              value={chapterId}
              onChange={e => setChapterId(e.target.value)}
              className="bg-transparent w-8 text-center font-bold focus:outline-none"
            />
          </div>

          <motion.button
            onClick={validateChapter}
            disabled={status === "loading"}
            className="px-5 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-blue-600 to-cyan-600 text-white"
          >
            {status === "loading" ? "Analyzing..." : "Run Checks"}
          </motion.button>
        </div>
      </motion.header>

      {/* GRID */}
      <div className="flex-1 grid grid-cols-12 overflow-hidden">

        {/* LEFT SIDEBAR */}
        <aside className="col-span-3 bg-neutral-50 border-r border-neutral-200 
                          dark:bg-[#0c0c0e] dark:border-white/5 overflow-hidden flex flex-col">

          <div className="p-5 border-b border-neutral-200 dark:border-white/5">
            <h3 className="text-xs font-bold text-neutral-600 dark:text-neutral-500 uppercase mb-4 flex items-center gap-2">
              <Users size={14}/> Cast Database
            </h3>

            {analytics && (
              <div className="bg-neutral-100 dark:bg-neutral-900/50 p-4 rounded-xl border border-neutral-200 dark:border-white/5">
                <div className="text-3xl font-light">{analytics.total_characters}</div>
                <div className="text-xs text-neutral-500 mt-1">Total Characters</div>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-2">
            {analytics?.dormant_characters?.map((char,i)=>(
              <div key={i} className="p-3 bg-neutral-100 dark:bg-neutral-900/40 rounded-lg border border-neutral-200 dark:border-white/5">
                <div className="font-medium">{char.name}</div>
                <div className="text-xs text-neutral-500">Last seen: Ch {char.last_seen}</div>
              </div>
            ))}
          </div>
        </aside>

        {/* EDITOR */}
        <main className="col-span-6 bg-white dark:bg-[#09090b] flex flex-col">

          <div className="flex-1 overflow-y-auto px-8 py-10">
            <GrammarOverlay
              text={text}
              matches={matches}
              onApplyFix={handleApplyGrammarFix}
            />

            <textarea
              className="w-full min-h-[70vh] bg-transparent text-lg leading-loose outline-none resize-none
                         text-neutral-800 dark:text-neutral-300 placeholder-neutral-400 dark:placeholder-neutral-700"
              placeholder="Begin writing your narrative..."
              value={text}
              onChange={e=>setText(e.target.value)}
            />
          </div>

          <div className="h-10 border-t border-neutral-200 dark:border-white/5 
                          bg-neutral-50 dark:bg-[#0c0c0e] flex justify-between px-6 text-xs text-neutral-500">
            <span>{text.split(/\s+/).filter(Boolean).length} Words</span>
            <span>{matches.length ? `${matches.length} Suggestions` : "Grammar Clean"}</span>
          </div>
        </main>

        {/* RIGHT SIDEBAR */}
        <aside className="col-span-3 bg-neutral-50 border-l border-neutral-200 
                          dark:bg-[#0c0c0e] dark:border-white/5 overflow-y-auto p-5">

          {status === "idle" && (
            <div className="text-center text-neutral-400 mt-20">
              <Shield size={32} className="mx-auto mb-3"/>
              System Ready
            </div>
          )}

          {status === "valid" && (
            <div className="bg-green-100 dark:bg-green-500/5 border border-green-300 dark:border-green-500/20 p-4 rounded-xl text-green-600 dark:text-green-400">
              Plot Integrity Verified
            </div>
          )}

          <AnimatePresence>
            {alerts.map((alert,i)=>(
              <motion.div
                key={i}
                initial={{ opacity:0, x:20 }}
                animate={{ opacity:1, x:0 }}
                exit={{ opacity:0 }}
                className="mt-4 p-4 rounded-xl border bg-yellow-100 dark:bg-yellow-500/5 border-yellow-300 dark:border-yellow-500/20"
              >
                <p className="font-semibold text-xs mb-2">{alert.type}</p>
                <p className="text-sm">{alert.message}</p>
                <p className="text-xs mt-2 text-neutral-500">{alert.suggestion}</p>
              </motion.div>
            ))}
          </AnimatePresence>

        </aside>

      </div>
    </div>
  );
};

export default ContinuityValidator;
