import { create } from 'zustand';

export const useStoryStore = create((set) => ({
    // Manuscript state
    manuscript: {
        title: 'Untitled Story',
        content: '',
        chapter: 1,
        paragraph: 1,
    },

    // Extracted entities from NLP
    entities: [],

    // Processing state
    processing: false,

    // Connection state (for UI feedback)
    isConnected: true,

    // Saved manuscript state (persisted to backend)
    savedManuscript: {
        id: null,
        title: '',
        content: '',
        summary: '',
        savedAt: null,
    },

    // Actions
    updateContent: (content) =>
        set((state) => ({
            manuscript: { ...state.manuscript, content },
        })),

    setTitle: (title) =>
        set((state) => ({
            manuscript: { ...state.manuscript, title },
        })),

    setChapter: (chapter) =>
        set((state) => ({
            manuscript: { ...state.manuscript, chapter },
        })),

    setParagraph: (paragraph) =>
        set((state) => ({
            manuscript: { ...state.manuscript, paragraph },
        })),

    setEntities: (entities) => set({ entities }),

    addEntities: (newEntities) =>
        set((state) => ({
            entities: [...state.entities, ...newEntities],
        })),

    setProcessing: (processing) => set({ processing }),

    setSavedManuscript: (data) => set({ savedManuscript: data }),

    setConnected: (isConnected) => set({ isConnected }),

    reset: () =>
        set({
            manuscript: {
                title: 'Untitled Story',
                content: '',
                chapter: 1,
                paragraph: 1,
            },
            entities: [],
            processing: false,
        }),
}));
