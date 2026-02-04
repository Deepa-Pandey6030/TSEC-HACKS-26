import { useCallback, useEffect } from 'react';
import { useStoryStore } from '../store';

const API_BASE_URL = 'http://localhost:8000';

export const useWebSocket = (manuscriptId) => {
    const { setEntities, setProcessing, setConnected } = useStoryStore();

    // Check backend connection on mount
    useEffect(() => {
        const checkConnection = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/health`);
                setConnected(response.ok);
            } catch (error) {
                console.error('❌ Backend connection failed:', error);
                setConnected(false);
            }
        };

        checkConnection();
        const interval = setInterval(checkConnection, 30000); // Check every 30s

        return () => clearInterval(interval);
    }, [setConnected]);

    const sendParagraph = useCallback(
        async (text, chapter, paragraph) => {
            if (!text || !text.trim()) {
                console.warn('⚠️ Empty text, skipping NLP extraction');
                return;
            }

            setProcessing(true);
            console.log('📤 Sending to NLP API:', { text: text.substring(0, 50) + '...', chapter, paragraph });

            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/nlp/extract`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text,
                        manuscript_id: manuscriptId || 'default_manuscript',
                        chapter,
                        paragraph,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                console.log('✅ NLP Response:', data);

                // Extract entities from response
                const extractedEntities = [];

                // Add characters
                if (data.characters && data.characters.length > 0) {
                    data.characters.forEach((char) => {
                        extractedEntities.push({
                            text: char.name,
                            type: 'character',
                            properties: {
                                archetype: char.archetype,
                                goal: char.goal,
                                emotion: char.emotion,
                            },
                        });
                    });
                }

                // Add locations
                if (data.locations && data.locations.length > 0) {
                    data.locations.forEach((loc) => {
                        extractedEntities.push({
                            text: loc.name,
                            type: 'location',
                            properties: {
                                atmosphere: loc.atmosphere,
                                type: loc.type,
                            },
                        });
                    });
                }

                // Add scenes
                if (data.scenes && data.scenes.length > 0) {
                    data.scenes.forEach((scene) => {
                        extractedEntities.push({
                            text: scene.description || 'Scene',
                            type: 'event',
                            properties: {
                                setting: scene.setting,
                                mood: scene.mood,
                            },
                        });
                    });
                }

                console.log(`📊 Extracted ${extractedEntities.length} entities`);
                setEntities(extractedEntities);
            } catch (error) {
                console.error('❌ NLP extraction failed:', error);
                setConnected(false);
            } finally {
                setProcessing(false);
            }
        },
        [manuscriptId, setEntities, setProcessing, setConnected]
    );

    return { sendParagraph };
};
