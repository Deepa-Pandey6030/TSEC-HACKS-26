import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const autocompleteService = {
    predict: async (text, signal) => {
        try {
            const response = await axios.post(
                `${API_URL}/api/v1/autocomplete/predict`,
                { text, max_words: 5 },
                { signal }
            );
            return response.data.suggestion;
        } catch (error) {
            // Autocomplete should be silent on error
            return "";
        }
    }
};
