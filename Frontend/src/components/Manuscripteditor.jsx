import React, { useCallback } from "react";
import { useStoryStore } from "../store";
import { useWebSocket } from "../hooks/useWebSocket";

export const ManuscriptEditor = ({ manuscriptId }) => {
    const { manuscript, updateContent, processing, isConnected, entities, setSavedManuscript, setProcessing } = useStoryStore();
    const { sendParagraph } = useWebSocket(manuscriptId);

    const handleChange = useCallback(
        (e) => {
            updateContent(e.target.value);
        },
        [updateContent]
    );

    const handleSave = useCallback(async () => {
        const currentText = manuscript.content.trim();

        // Safety check: Don't send if empty or already processing
        if (!currentText || processing) return;

        console.log("📤 Saving and analyzing manuscript...");
        setProcessing(true);

        try {
            // Get token from localStorage (AuthContext stores it there)
            const token = localStorage.getItem('sessionToken');

            const headers = {
                'Content-Type': 'application/json',
            };

            // Add auth header if token exists
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch('http://localhost:8000/api/v1/manuscript/save-and-analyze', {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    title: manuscript.title,
                    text: currentText,
                    chapter: manuscript.chapter,
                    paragraph: manuscript.paragraph,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log("✅ Manuscript saved and analyzed:", data);

            // Update saved manuscript state
            setSavedManuscript({
                id: data.id,
                title: data.title,
                content: currentText,
                summary: data.summary,
                savedAt: new Date().toISOString(),
            });

            // Also trigger NLP extraction for entity sidebar
            sendParagraph(
                currentText,
                manuscript.chapter,
                manuscript.paragraph
            );

        } catch (error) {
            console.error("❌ Save and analyze failed:", error);
        } finally {
            setProcessing(false);
        }
    }, [manuscript, processing, setSavedManuscript, setProcessing, sendParagraph]);


    return (
        <div className="manuscript-editor bg-white p-6 rounded-lg shadow-sm h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold text-gray-800">{manuscript.title}</h1>
                <div className="flex items-center gap-3">
                    {/* Connection Status Indicator */}
                    <div className="flex items-center gap-2 px-3 py-1 bg-gray-50 rounded-full border border-gray-200">
                        <div
                            className={`w-2 h-2 rounded-full transition-colors duration-300 ${isConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]" : "bg-red-500"
                                }`}
                        />
                        <span className="text-xs font-medium text-gray-600">
                            {isConnected ? "Live" : "Offline"}
                        </span>
                    </div>

                    {/* Processing Status */}
                    {processing ? (
                        <span className="text-xs text-blue-600 font-medium animate-pulse flex items-center gap-1">
                            <span className="inline-block w-2 h-2 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></span>
                            Analyzing...
                        </span>
                    ) : entities.length > 0 ? (
                        <span className="text-xs text-green-600 font-medium transition-opacity duration-500">
                            ✓ {entities.length} entities
                        </span>
                    ) : null}
                </div>
            </div>

            <div className="flex gap-2 mb-4">
                <div className="relative group">
                    <span className="absolute -top-2 left-2 px-1 bg-white text-[10px] text-gray-400">Chapter</span>
                    <input
                        type="number"
                        min="1"
                        value={manuscript.chapter}
                        className="w-20 px-3 py-2 border border-gray-200 rounded text-sm bg-gray-50 text-gray-500 focus:outline-none cursor-not-allowed"
                        readOnly
                    />
                </div>
                <div className="relative group">
                    <span className="absolute -top-2 left-2 px-1 bg-white text-[10px] text-gray-400">Para</span>
                    <input
                        type="number"
                        min="1"
                        value={manuscript.paragraph}
                        className="w-20 px-3 py-2 border border-gray-200 rounded text-sm bg-gray-50 text-gray-500 focus:outline-none cursor-not-allowed"
                        readOnly
                    />
                </div>
            </div>

            <textarea
                value={manuscript.content}
                onChange={handleChange}
                placeholder="Start writing your story here..."
                className="editor-input flex-1 w-full p-4 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none transition-all font-serif text-lg leading-relaxed text-gray-800 placeholder-gray-300"
            />

            <div className="flex justify-end mt-4">
                <button
                    onClick={handleSave}
                    disabled={processing || !isConnected}
                    className={`
            px-6 py-2 rounded-md font-medium text-sm transition-all duration-200
            ${processing || !isConnected
                            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                            : "bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md active:transform active:scale-95"}
          `}
                >
                    {processing ? "Processing..." : "Save & Analyze"}
                </button>
            </div>
        </div>
    );
};