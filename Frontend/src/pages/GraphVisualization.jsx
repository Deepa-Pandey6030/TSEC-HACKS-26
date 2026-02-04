import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Network, AlertCircle, Users, MapPin, GitBranch, Loader2, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import ForceGraph2D from 'react-force-graph-2d';

const API_BASE_URL = 'http://localhost:8000';

export default function GraphVisualization() {
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [manuscriptId, setManuscriptId] = useState('');
    const [stats, setStats] = useState(null);
    const graphRef = useRef();

    const fetchGraphData = async (mid) => {
        if (!mid) return;

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/graph?manuscript_id=${mid}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch graph: ${response.statusText}`);
            }

            const data = await response.json();

            // Log the raw data to verify all attributes are received
            console.log('📊 Graph Data Received:', {
                nodeCount: data.nodes.length,
                edgeCount: data.edges.length,
                sampleNode: data.nodes[0]
            });

            // Transform API data to force-graph format
            const nodes = data.nodes.map(node => {
                // Log each node's properties to verify all attributes
                console.log(`Node "${node.name}" properties:`, Object.keys(node.properties || {}));

                return {
                    id: node.id,
                    name: node.name,
                    type: node.type,
                    properties: node.properties || {},
                    first_appearance: node.first_appearance,
                    last_appearance: node.last_appearance,
                    color: getNodeColor(node.type),
                    size: node.type === 'Character' ? 8 : 6
                };
            });

            const links = data.edges.map(edge => ({
                source: nodes.find(n => n.name === edge.source)?.id || edge.source,
                target: nodes.find(n => n.name === edge.target)?.id || edge.target,
                type: edge.type,
                properties: edge.properties || {},
                label: edge.type
            }));

            console.log('✅ Graph transformed:', {
                nodes: nodes.length,
                links: links.length,
                allProperties: [...new Set(nodes.flatMap(n => Object.keys(n.properties)))]
            });

            setGraphData({ nodes, links });
            setStats(data.metadata);
            setLoading(false);
        } catch (err) {
            console.error('Error fetching graph:', err);
            setError(err.message);
            setLoading(false);
        }
    };

    const getNodeColor = (type) => {
        switch (type) {
            case 'Character':
                return '#3b82f6'; // Blue
            case 'Location':
                return '#10b981'; // Green
            case 'Scene':
                return '#f59e0b'; // Amber
            default:
                return '#6b7280'; // Gray
        }
    };

    const handleNodeClick = (node) => {
        setSelectedNode(node);
    };

    const handleZoomIn = () => {
        if (graphRef.current) {
            graphRef.current.zoom(graphRef.current.zoom() * 1.2, 400);
        }
    };

    const handleZoomOut = () => {
        if (graphRef.current) {
            graphRef.current.zoom(graphRef.current.zoom() / 1.2, 400);
        }
    };

    const handleFitView = () => {
        if (graphRef.current) {
            graphRef.current.zoomToFit(400);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-white to-neutral-100 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900">
            <div className="container mx-auto px-6 py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <div className="flex items-center space-x-3 mb-2">
                        <Network className="w-8 h-8 text-primary-500" />
                        <h1 className="text-4xl font-bold text-neutral-900 dark:text-neutral-100">
                            Knowledge Graph Visualization
                        </h1>
                    </div>
                    <p className="text-neutral-600 dark:text-neutral-400">
                        Explore your story's characters, locations, and relationships
                    </p>
                </motion.div>

                {/* Input Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white dark:bg-neutral-800 rounded-2xl shadow-lg p-6 mb-6"
                >
                    <div className="flex items-center space-x-4">
                        <input
                            type="text"
                            placeholder="Enter manuscript ID (e.g., story_the_last_echo)"
                            value={manuscriptId}
                            onChange={(e) => setManuscriptId(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && fetchGraphData(manuscriptId)}
                            className="flex-1 px-4 py-3 bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-neutral-900 dark:text-neutral-100"
                        />
                        <Button
                            onClick={() => fetchGraphData(manuscriptId)}
                            disabled={!manuscriptId || loading}
                            className="px-6 py-3"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Loading...
                                </>
                            ) : (
                                'Load Graph'
                            )}
                        </Button>
                    </div>
                </motion.div>

                {/* Stats */}
                {stats && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"
                    >
                        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow p-4">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                                    <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                </div>
                                <div>
                                    <p className="text-sm text-neutral-600 dark:text-neutral-400">Characters</p>
                                    <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{stats.character_count}</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow p-4">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                                    <MapPin className="w-5 h-5 text-green-600 dark:text-green-400" />
                                </div>
                                <div>
                                    <p className="text-sm text-neutral-600 dark:text-neutral-400">Locations</p>
                                    <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{stats.location_count}</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow p-4">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                                    <GitBranch className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                                </div>
                                <div>
                                    <p className="text-sm text-neutral-600 dark:text-neutral-400">Relationships</p>
                                    <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{stats.edge_count}</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow p-4">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
                                    <Network className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                                </div>
                                <div>
                                    <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Nodes</p>
                                    <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{stats.node_count}</p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Error State */}
                {error && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 mb-6"
                    >
                        <div className="flex items-start space-x-3">
                            <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                            <div>
                                <h3 className="font-semibold text-red-900 dark:text-red-100 mb-1">Error Loading Graph</h3>
                                <p className="text-red-700 dark:text-red-300">{error}</p>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Graph Visualization */}
                {!loading && !error && graphData.nodes.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="bg-white dark:bg-neutral-800 rounded-2xl shadow-lg overflow-hidden relative"
                    >
                        {/* Controls */}
                        <div className="absolute top-4 right-4 z-10 flex flex-col space-y-2">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleZoomIn}
                                className="bg-white/90 dark:bg-neutral-700/90 backdrop-blur"
                            >
                                <ZoomIn className="w-4 h-4" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleZoomOut}
                                className="bg-white/90 dark:bg-neutral-700/90 backdrop-blur"
                            >
                                <ZoomOut className="w-4 h-4" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleFitView}
                                className="bg-white/90 dark:bg-neutral-700/90 backdrop-blur"
                            >
                                <Maximize2 className="w-4 h-4" />
                            </Button>
                        </div>

                        {/* Graph */}
                        <div className="w-full h-[600px]">
                            <ForceGraph2D
                                ref={graphRef}
                                graphData={graphData}
                                nodeLabel="name"
                                nodeColor="color"
                                nodeVal="size"
                                nodeCanvasObject={(node, ctx, globalScale) => {
                                    const label = node.name;
                                    const fontSize = 12 / globalScale;
                                    ctx.font = `${fontSize}px Sans-Serif`;
                                    const textWidth = ctx.measureText(label).width;
                                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

                                    // Draw node circle
                                    ctx.fillStyle = node.color;
                                    ctx.beginPath();
                                    ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI, false);
                                    ctx.fill();

                                    // Draw label background
                                    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                                    ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - node.size - bckgDimensions[1], ...bckgDimensions);

                                    // Draw label text
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'middle';
                                    ctx.fillStyle = '#000';
                                    ctx.fillText(label, node.x, node.y - node.size - fontSize / 2);
                                }}
                                linkLabel={link => link.label || link.type || ''}
                                linkDirectionalArrowLength={4}
                                linkDirectionalArrowRelPos={1}
                                linkCurvature={0.1}
                                linkDirectionalParticles={1}
                                linkDirectionalParticleWidth={2}
                                linkDirectionalParticleSpeed={0.005}
                                onNodeClick={handleNodeClick}
                                onLinkClick={(link) => {
                                    const source = typeof link.source === 'object' ? link.source.name : link.source;
                                    const target = typeof link.target === 'object' ? link.target.name : link.target;
                                    alert(`Relationship: ${link.type}\n\nFrom: ${source}\nTo: ${target}`);
                                }}
                                backgroundColor="#f9fafb"
                                linkColor={() => '#6b7280'}
                                linkWidth={1.5}
                            />
                        </div>
                    </motion.div>
                )}

                {/* Selected Node Details */}
                {selectedNode && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-6 bg-white dark:bg-neutral-800 rounded-2xl shadow-lg p-6"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                                {selectedNode.name}
                            </h3>
                            <span className="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full text-sm font-semibold">
                                {selectedNode.type}
                            </span>
                        </div>

                        {/* Dynamic Properties Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {selectedNode.properties && Object.entries(selectedNode.properties)
                                .filter(([key]) => !['name', 'manuscript_id'].includes(key)) // Filter out internal fields
                                .map(([key, value]) => (
                                    <div key={key} className="bg-neutral-50 dark:bg-neutral-700/50 rounded-lg p-4">
                                        <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-1 uppercase tracking-wide">
                                            {key.replace(/_/g, ' ')}
                                        </p>
                                        <p className="text-base font-semibold text-neutral-900 dark:text-neutral-100 break-words">
                                            {value !== null && value !== undefined && value !== ''
                                                ? String(value)
                                                : <span className="text-neutral-400 italic">Not set</span>
                                            }
                                        </p>
                                    </div>
                                ))
                            }

                            {/* Show message if no additional properties */}
                            {selectedNode.properties &&
                                Object.keys(selectedNode.properties).filter(k => !['name', 'manuscript_id'].includes(k)).length === 0 && (
                                    <div className="col-span-full text-center py-8 text-neutral-500 dark:text-neutral-400">
                                        <Network className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                        <p>No additional properties available</p>
                                    </div>
                                )}
                        </div>

                        {/* Appearance Info */}
                        {(selectedNode.first_appearance || selectedNode.last_appearance) && (
                            <div className="mt-6 pt-6 border-t border-neutral-200 dark:border-neutral-700">
                                <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                                    Appearance Timeline
                                </h4>
                                <div className="grid grid-cols-2 gap-4">
                                    {selectedNode.first_appearance && (
                                        <div className="bg-neutral-50 dark:bg-neutral-700/50 rounded-lg p-3">
                                            <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-1">First Seen</p>
                                            <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                                                {new Date(selectedNode.first_appearance).toLocaleString()}
                                            </p>
                                        </div>
                                    )}
                                    {selectedNode.last_appearance && (
                                        <div className="bg-neutral-50 dark:bg-neutral-700/50 rounded-lg p-3">
                                            <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-1">Last Seen</p>
                                            <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                                                {new Date(selectedNode.last_appearance).toLocaleString()}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </motion.div>
                )}

                {/* Empty State */}
                {!loading && !error && graphData.nodes.length === 0 && manuscriptId && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-neutral-100 dark:bg-neutral-800 rounded-2xl p-12 text-center"
                    >
                        <Network className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
                            No graph data found
                        </h3>
                        <p className="text-neutral-600 dark:text-neutral-400">
                            Try a different manuscript ID or create some content first
                        </p>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
