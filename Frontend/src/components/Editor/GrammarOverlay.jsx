import React, { useMemo } from 'react';

// Maps issues to positions
const GrammarOverlay = ({ text, matches, onApplyFix }) => {

    // Determine error type color based on rule category
    const getErrorStyle = (match) => {
        const category = match.rule?.category;
        const categoryId = typeof category === 'object' ? category?.id : category;
        const issueType = match.rule?.issueType;

        // Grammar/Spelling errors - RED
        if (categoryId === 'CASING' || categoryId === 'TYPOS' || categoryId === 'GRAMMAR' || issueType === 'misspelling' || issueType === 'grammar') {
            return {
                underline: 'decoration-red-500',
                hover: 'hover:bg-red-500/10'
            };
        }
        // Style/Suggestion - BLUE
        else if (categoryId === 'STYLE' || categoryId === 'TONE' || issueType === 'style') {
            return {
                underline: 'decoration-blue-500',
                hover: 'hover:bg-blue-500/10'
            };
        }
        // Warning/Clarity - YELLOW
        else if (categoryId === 'CONFUSED_WORDS' || categoryId === 'CLARITY' || issueType === 'warning' || issueType === 'clarity') {
            return {
                underline: 'decoration-yellow-500',
                hover: 'hover:bg-yellow-500/10'
            };
        }
        // Default to BLUE for unknown types
        return {
            underline: 'decoration-blue-500',
            hover: 'hover:bg-blue-500/10'
        };
    };

    // Create segments for rendering text + highlights
    const segments = useMemo(() => {
        if (!matches || matches.length === 0) {
            return [{ text, isError: false }];
        }

        const sortedMatches = [...matches].sort((a, b) => a.offset - b.offset);
        const result = [];
        let lastIndex = 0;

        sortedMatches.forEach(match => {
            // Add text before match
            if (match.offset > lastIndex) {
                result.push({
                    text: text.slice(lastIndex, match.offset),
                    isError: false
                });
            }

            // Add match text
            result.push({
                text: text.slice(match.offset, match.offset + match.length),
                isError: true,
                match: match
            });

            lastIndex = match.offset + match.length;
        });

        // Add remaining text
        if (lastIndex < text.length) {
            result.push({
                text: text.slice(lastIndex),
                isError: false
            });
        }

        return result;
    }, [text, matches]);

    const handleFix = (match) => {
        if (match.replacements && match.replacements.length > 0) {
            const replacement = match.replacements[0].value;
            onApplyFix(match, replacement);
        }
    };

    // Render text segments
    // We use whitespace-pre-wrap to match textarea
    return (
        <div
            className="absolute inset-0 pointer-events-none break-words whitespace-pre-wrap overflow-hidden"
            style={{
                fontFamily: 'Georgia, serif', // Match textarea styling
                fontSize: '1.125rem',         // text-lg
                lineHeight: '1.625',          // leading-relaxed
                padding: '2rem',              // p-8 match
                color: 'transparent',
            }}
            aria-hidden="true"
        >
            {segments.map((segment, index) => (
                <span key={index}>
                    {segment.isError ? (
                        <span
                            className={`relative group pointer-events-auto cursor-pointer decoration-wavy underline ${getErrorStyle(segment.match).underline} decoration-2 underline-offset-4 ${getErrorStyle(segment.match).hover} transition-colors rounded`}
                            onClick={() => handleFix(segment.match)}
                        >
                            {segment.text}
                            {/* Tooltip */}
                            <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-2 bg-neutral-900 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none">
                                <span className="block font-semibold mb-1">{segment.match.message}</span>
                                <span className="block text-xs text-gray-300 mb-1">
                                    {typeof segment.match.rule?.category === 'object' 
                                        ? segment.match.rule.category.name 
                                        : segment.match.rule?.category || 'Issue'}
                                </span>
                                {segment.match.replacements && segment.match.replacements.length > 0 && (
                                    <span className="block text-green-400">Click to fix: {segment.match.replacements[0].value}</span>
                                )}
                            </span>
                        </span>
                    ) : (
                        segment.text
                    )}
                </span>
            ))}
            {/* Ensure trailing newline is rendered if present */}
            {text.endsWith('\n') && <br />}
        </div>
    );
};

export default GrammarOverlay;
