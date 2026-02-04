
const GhostOverlay = ({ text, suggestion }) => {
    if (!suggestion) return null;

    return (
        <div
            className="absolute inset-0 pointer-events-none break-words whitespace-pre-wrap overflow-hidden"
            style={{
                fontFamily: 'Georgia, serif',
                fontSize: '1.125rem',
                lineHeight: '1.625',
                padding: '2rem',
                color: 'transparent',
            }}
            aria-hidden="true"
        >
            {text}
            <span className="text-gray-400 dark:text-gray-500 font-medium">
                {suggestion}
            </span>
            {/* Ensure trailing newline is rendered if present in strict matching */}
            {text.endsWith('\n') && <br />}
        </div>
    );
};

export default GhostOverlay;
