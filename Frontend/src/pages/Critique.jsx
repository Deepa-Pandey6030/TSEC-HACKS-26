import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown'; // Import the new library
import { BookOpen, AlertTriangle, CheckCircle, RefreshCw, Feather } from 'lucide-react';

const Critique = () => {
  const [review, setReview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchCritique = async () => {
    setLoading(true);
    setError("");
    setReview("");
    
    try {
      const response = await fetch("http://localhost:8000/critique");
      if (!response.ok) throw new Error("Server error");
      const data = await response.json();
      setReview(data.review);
    } catch (err) {
      setError("Could not connect to the Literary Engine. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans">
      
      {/* --- HEADER --- */}
      <header className="max-w-3xl w-full text-center mb-12">
        <div className="flex justify-center mb-4">
          <div className="bg-stone-900 p-3 rounded-full">
            <Feather className="w-8 h-8 text-stone-100" />
          </div>
        </div>
        <h1 className="text-4xl font-serif font-bold text-stone-900 tracking-tight mb-2">
          NOLAN
        </h1>
        <p className="text-lg text-stone-600 font-light">
          The Autonomous Narrative Critic
        </p>
      </header>

      {/* --- MAIN CONTENT --- */}
      <main className="max-w-4xl w-full">
        
        {/* State: IDLE */}
        {!review && !loading && !error && (
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-10 text-center">
            <BookOpen className="w-12 h-12 text-stone-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-stone-800 mb-2">Ready to Audit Your Manuscript</h2>
            <p className="text-stone-500 mb-8 max-w-md mx-auto">
              NOLAN will read your Neo4j database, check for logic paradoxes, analyze pacing metrics, and generate a 
              professional critique using the persona of an award-winning editor.
            </p>
            <button 
              onClick={fetchCritique}
              className="bg-stone-900 hover:bg-stone-800 text-white font-medium py-3 px-8 rounded-lg transition-all transform hover:scale-105 shadow-lg"
            >
              Generate Forensic Critique
            </button>
          </div>
        )}

        {/* State: LOADING */}
        {loading && (
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-12 text-center animate-pulse">
            <RefreshCw className="w-10 h-10 text-blue-600 mx-auto mb-4 animate-spin" />
            <h3 className="text-lg font-medium text-stone-800">Analyzing Narrative Architecture...</h3>
            <div className="mt-4 space-y-2">
              <p className="text-sm text-stone-500">Querying Neo4j Graph for 'Ghost' Logic Errors...</p>
              <p className="text-sm text-stone-500">Calculating Pacing Tension Scores...</p>
              <p className="text-sm text-stone-500">Consulting Literary Persona (LLM)...</p>
            </div>
          </div>
        )}

        {/* State: ERROR */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r-lg flex items-start">
            <AlertTriangle className="w-6 h-6 text-red-500 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-red-800 font-medium">System Failure</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              <button 
                onClick={fetchCritique}
                className="mt-3 text-sm font-semibold text-red-800 hover:underline"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* State: SUCCESS (The Report) */}
        {review && (
          <div className="bg-white rounded-xl shadow-xl border border-stone-200 overflow-hidden">
            <div className="bg-stone-900 px-8 py-4 flex justify-between items-center">
              <span className="text-stone-100 font-medium tracking-wide text-sm uppercase">Official Editorial Report</span>
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            
            {/* --- IMPROVED VISUALIZATION SECTION --- */}
            <div className="p-10 font-serif text-stone-800 text-lg bg-white">
              <ReactMarkdown
                components={{
                  // Styles H1 (e.g. # Title)
                  h1: ({node, ...props}) => <h1 className="text-3xl font-bold text-stone-900 mt-8 mb-6 border-b pb-2" {...props} />,
                  // Styles H2 (e.g. ## Section)
                  h2: ({node, ...props}) => <h2 className="text-2xl font-bold text-stone-900 mt-8 mb-4" {...props} />,
                  // Styles H3 (e.g. ### 1. The Narrative Arc) - This fixes your specific issue
                  h3: ({node, ...props}) => <h3 className="text-xl font-bold text-stone-800 mt-6 mb-3 uppercase tracking-wide" {...props} />,
                  // Styles Paragraphs
                  p: ({node, ...props}) => <p className="mb-6 leading-loose text-stone-700" {...props} />,
                  // Styles Bold text
                  strong: ({node, ...props}) => <strong className="font-bold text-stone-900" {...props} />,
                  // Styles Lists
                  ul: ({node, ...props}) => <ul className="list-disc list-inside mb-6 space-y-2 pl-4" {...props} />,
                  li: ({node, ...props}) => <li className="text-stone-700" {...props} />,
                  // Styles Blockquotes (if any)
                  blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-stone-300 pl-4 italic my-6 text-stone-500" {...props} />,
                }}
              >
                {review}
              </ReactMarkdown>
            </div>

            <div className="bg-stone-50 px-8 py-4 border-t border-stone-100 flex justify-end">
              <button 
                onClick={fetchCritique}
                className="text-stone-600 hover:text-stone-900 font-medium text-sm flex items-center transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Run New Analysis
              </button>
            </div>
          </div>
        )}

      </main>

      <footer className="mt-12 text-center text-stone-400 text-sm">
        <p>Powered by Neo4j • FastAPI • Groq LLM</p>
      </footer>
    </div>
  );
};

export default Critique;