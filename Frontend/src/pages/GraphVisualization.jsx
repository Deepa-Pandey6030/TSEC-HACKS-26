import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import ForceGraph2D from 'react-force-graph-2d';

const API_BASE_URL = 'http://localhost:8000';

export default function GraphVisualization() {

  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [manuscripts, setManuscripts] = useState([]);
  const [manuscriptId, setManuscriptId] = useState('');

  const graphRef = useRef();

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/graph/manuscripts`)
      .then(r => r.json())
      .then(d => {
        setManuscripts(d.manuscripts || []);
        if (d.manuscripts?.length) setManuscriptId(d.manuscripts[0].manuscript_id);
      });
  }, []);

  const fetchGraphData = async (mid) => {
    if (!mid) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/graph?manuscript_id=${mid}`);
      const data = await res.json();

      const nodes = data.nodes.map(n => ({
        id: n.id,
        name: n.name,
        type: n.type,
        properties: n.properties || {},
        color: n.type === 'Character' ? '#3b82f6' :
               n.type === 'Location'  ? '#10b981' :
               '#f59e0b',
        size: n.type === 'Character' ? 8 : 6
      }));

      const map = Object.fromEntries(nodes.map(n => [n.name, n.id]));

      const links = data.edges.map(e => ({
        source: map[e.source],
        target: map[e.target],
        type: e.type
      }));

      setGraphData({ nodes, links });
    } catch {
      setError('Failed loading graph');
    } finally {
      setLoading(false);
    }
  };

  const handleZoomIn = () => graphRef.current?.zoom(1.2, 400);
  const handleZoomOut = () => graphRef.current?.zoom(0.8, 400);
  const handleFitView = () => graphRef.current?.zoomToFit(400);

  return (
    <div className="min-h-screen bg-neutral-900 p-6">

      <div className="flex gap-3 mb-4">
      <select
  value={manuscriptId}
  onChange={e => setManuscriptId(e.target.value)}
  className="bg-neutral-800 text-white px-3 py-2 rounded"
>
  <option value="">Select manuscript</option>

  {manuscripts.map(m => (
    <option key={m.manuscript_id} value={m.manuscript_id}>
      {m.manuscript_id} — 👤 {m.characters} chars • 📍 {m.locations} locs • 🔗 {m.relationships} rels
    </option>
  ))}
</select>


        <Button onClick={() => fetchGraphData(manuscriptId)}>
          {loading ? 'Loading...' : 'Load Graph'}
        </Button>
      </div>

      {error && (
        <div className="text-red-400 mb-3 flex gap-2">
          <AlertCircle size={18} /> {error}
        </div>
      )}

      <div className="relative h-[600px] bg-neutral-800 rounded-xl">

        <div className="absolute top-3 right-3 flex flex-col gap-2 z-10">
          <Button size="sm" onClick={handleZoomIn}><ZoomIn size={16} /></Button>
          <Button size="sm" onClick={handleZoomOut}><ZoomOut size={16} /></Button>
          <Button size="sm" onClick={handleFitView}><Maximize2 size={16} /></Button>
        </div>

        {graphData.nodes.length > 0 && (
         <ForceGraph2D
         ref={graphRef}
         graphData={graphData}
         backgroundColor="#111827"
       
         linkColor={() => '#a855f7'}
         linkWidth={2}
         linkDirectionalArrowLength={6}
         linkDirectionalArrowRelPos={0.9}
         linkCurvature={0.15}
       
         onNodeClick={setSelectedNode}
       
         nodeCanvasObjectMode={() => "after"}
         linkCanvasObjectMode={() => "after"}
       
         nodeCanvasObject={(node, ctx, scale) => {
           const fontSize = 12 / scale;
           ctx.font = `${fontSize}px Sans-Serif`;
       
           // draw node
           ctx.fillStyle = node.color;
           ctx.beginPath();
           ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
           ctx.fill();
       
           // draw node label (NO background)
           ctx.fillStyle = "#ffffff";
           ctx.textAlign = "left";
           ctx.textBaseline = "middle";
           ctx.fillText(
             node.name,
             node.x + node.size + 2,
             node.y
           );
         }}
       
         linkCanvasObject={(link, ctx, scale) => {
           if (typeof link.source !== "object" || typeof link.target !== "object") return;
       
           const midX = (link.source.x + link.target.x) / 2;
           const midY = (link.source.y + link.target.y) / 2;
       
           const fontSize = 10 / scale;
           ctx.font = `${fontSize}px Sans-Serif`;
       
           ctx.fillStyle = "#e9d5ff";
           ctx.textAlign = "center";
           ctx.textBaseline = "middle";
       
           ctx.fillText(link.type, midX, midY);
         }}
       />
       
        )}

        {!loading && graphData.nodes.length === 0 && (
          <div className="h-full flex items-center justify-center text-neutral-400">
            Load a manuscript to visualize
          </div>
        )}
      </div>

      {selectedNode && (
        <div className="mt-4 bg-neutral-800 text-white p-4 rounded-xl">
          <h3 className="font-bold text-xl">{selectedNode.name}</h3>
          <p className="text-neutral-400">{selectedNode.type}</p>
        </div>
      )}
    </div>
  );
}
