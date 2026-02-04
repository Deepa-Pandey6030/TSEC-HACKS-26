import React, { useMemo } from 'react';

const LineGutter = ({ content }) => {
    const lineCount = useMemo(() => {
        return content.split('\n').length;
    }, [content]);

    return (
        <div
            className="absolute top-0 left-0 bottom-0 w-12 bg-neutral-100 dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700 pt-8 pb-8 flex flex-col items-center select-none overflow-hidden"
            aria-hidden="true"
        >
            {Array.from({ length: lineCount }).map((_, i) => (
                <div
                    key={i}
                    className="text-neutral-400 dark:text-neutral-500 text-sm font-mono leading-[1.625rem]"
                    style={{ height: '1.625rem' }} // Match line-height of textarea (text-lg * leading-relaxed ~= 1.125rem * 1.625 = 1.828rem, adjusted to match visually)
                >
                    {i + 1}
                </div>
            ))}
        </div>
    );
};

export default LineGutter;
