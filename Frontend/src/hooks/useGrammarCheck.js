import { useState, useEffect, useRef, useCallback } from 'react';
import { grammarService } from '../services/grammarService';

export const useGrammarCheck = (text) => {
    const [matches, setMatches] = useState([]);
    const [isChecking, setIsChecking] = useState(false);
    const abortControllerRef = useRef(null);

    // Debounce logic
    useEffect(() => {
        // Limits: Start checking at 10+ characters for real-time feedback
        if (!text || text.length < 10) {
            setMatches([]);
            return;
        }

        // Cancel previous request if it exists
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        // Create new abort controller
        abortControllerRef.current = new AbortController();
        const { signal } = abortControllerRef.current;

        const timeoutId = setTimeout(async () => {
            setIsChecking(true);
            try {
                const result = await grammarService.checkGrammar(text, 'en-US', signal);
                if (result && result.matches) {
                    setMatches(result.matches);
                }
            } catch (error) {
                // Error handling is mostly silent for grammar check generally
            } finally {
                // Only set checking to false if this specific request finished (and wasn't aborted)
                if (!signal.aborted) {
                    setIsChecking(false);
                }
            }
        }, 300); // 300ms debounce - real-time checking

        return () => {
            clearTimeout(timeoutId);
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [text]);

    const ignoreMatch = useCallback((matchId) => {
        setMatches(prev => prev.filter(m => m.msgId !== matchId && m.rule.id !== matchId));
    }, []);

    return { matches, isChecking, ignoreMatch, setMatches };
};
