import asyncio
from typing import Dict, Any, List
from fastapi import WebSocket

class TextStreamProcessor:
    def __init__(self):
        self.processing_queue = asyncio.Queue()
        # Configuration for "Safe Slicing"
        self.CHUNK_SIZE = 6000  # Characters (approx 1500 tokens)
        self.OVERLAP = 500      # Characters overlap to maintain context

    def _chunk_text(self, text: str) -> List[str]:
        """Slices large text into overlapping chunks for safe AI consumption."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            # Try to find a sentence ending to break cleanly
            if end < len(text):
                last_period = text.rfind('.', start, end)
                if last_period != -1:
                    end = last_period + 1
            
            chunk = text[start:end]
            chunks.append(chunk)
            # Move forward, but backstep by overlap to keep context
            start = end - self.OVERLAP if end < len(text) else end
        return chunks

    async def add_to_stream(self, websocket: WebSocket, text: str, metadata: Dict[str, Any]):
        if not text or not text.strip():
            return

        # 1. SMART CHUNKING
        # If text is huge, break it down. If small, keep as is.
        if len(text) > self.CHUNK_SIZE:
            print(f"📚 Large Input Detected ({len(text)} chars). Slicing...")
            chunks = self._chunk_text(text)
        else:
            chunks = [text]

        # 2. SEQUENTIAL QUEUEING
        # We preserve the paragraph number but add a "chunk_index" metadata
        base_para = metadata.get('paragraph', 0)
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata['paragraph'] = f"{base_para}_{i}" # Unique ID for graph
            chunk_metadata['is_chunk'] = True
            
            print(f"📥 Queuing Chunk {i+1}/{len(chunks)}")
            await self.processing_queue.put({
                "websocket": websocket,
                "text": chunk,
                "metadata": chunk_metadata
            })

processor = TextStreamProcessor()