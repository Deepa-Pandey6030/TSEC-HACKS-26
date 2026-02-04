import { useState, useEffect, useRef, useCallback } from 'react';
import { autocompleteService } from '../services/autocompleteService';

export const useAutocomplete = (text, enabled = true) => {
    const [suggestion, setSuggestion] = useState('');
    const lastRequestRef = useRef(null);

    useEffect(() => {
        if (!enabled || !text || text.length < 5) {
            setSuggestion('');
            return;
        }

        // Only suggest if cursor is at the end? 
        // Ideally we'd check cursor position, but for now assuming 'text' is the whole content
        // and we only autocomplete at the end.

        // Clear previous
        if (lastRequestRef.current) {
            lastRequestRef.current.abort();
        }
        setSuggestion('');

        const controller = new AbortController();
        lastRequestRef.current = controller;

        const timeoutId = setTimeout(async () => {
            const result = await autocompleteService.predict(text, controller.signal);
            if (!controller.signal.aborted) {
                setSuggestion(result || '');
            }
        }, 200); // 200ms debounce - faster real-time feel

        return () => {
            clearTimeout(timeoutId);
            controller.abort();
        };
    }, [text, enabled]);

    const acceptSuggestion = useCallback(() => {
        if (suggestion) {
            const toAdd = suggestion;
            setSuggestion('');
            return toAdd;
        }
        return null;
    }, [suggestion]);

    const clearSuggestion = useCallback(() => {
        setSuggestion('');
    }, []);

    return { suggestion, acceptSuggestion, clearSuggestion };
};
