import axios from 'axios';

// Align with the port used in creative-assistant.jsx or main backend
const API_URL = 'http://localhost:8000';

export const grammarService = {
    checkGrammar: async (text, language = 'en-US', signal) => {
        try {
            const response = await axios.post(
                `${API_URL}/api/v1/grammar/check`,
                { text, language },
                { signal } // For aborting requests
            );
            return response.data;
        } catch (error) {
            if (axios.isCancel(error)) {
                // Request cancelled, ignore
                return null;
            }
            console.error('Grammar check failed:', error);
            return { matches: [] };
        }
    }
};
