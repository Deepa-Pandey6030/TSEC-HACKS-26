"""
API routes for Knowledge Graph (Story Memory)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.services.knowledge_graph import graph_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/graph", tags=["Knowledge Graph"])


# Response Models
class NodeProperties(BaseModel):
    """Properties of a graph node."""
    name: str
    manuscript_id: str
    archetype: Optional[str] = None
    emotion: Optional[str] = None
    goal: Optional[str] = None
    atmosphere: Optional[str] = None
    type: Optional[str] = None


class GraphNode(BaseModel):
    """A node in the knowledge graph."""
    id: str
    name: str
    type: str  # Character, Location, Scene, Manuscript
    properties: Dict[str, Any] = Field(default_factory=dict)
    first_appearance: Optional[str] = None
    last_appearance: Optional[str] = None


class EdgeProperties(BaseModel):
    """Properties of a graph edge."""
    context: Optional[str] = None
    strength: Optional[str] = None
    last_seen_in: Optional[str] = None


class GraphEdge(BaseModel):
    """An edge (relationship) in the knowledge graph."""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphNodesResponse(BaseModel):
    """Response model for node queries."""
    nodes: List[GraphNode]
    total: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdgesResponse(BaseModel):
    """Response model for edge queries."""
    edges: List[GraphEdge]
    total: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FullGraphResponse(BaseModel):
    """Response model for full graph export."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any]


# Endpoints
@router.get("/nodes", response_model=GraphNodesResponse)
async def get_nodes(
    manuscript_id: str = Query(..., description="Manuscript identifier"),
    node_type: Optional[str] = Query(None, description="Filter by node type (Character, Location)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of nodes to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Query nodes from the knowledge graph.
    
    Returns characters, locations, and other entities from the story.
    
    Args:
        manuscript_id: Story identifier
        node_type: Optional filter by type (Character, Location)
        limit: Maximum results (1-500)
        offset: Pagination offset
        
    Returns:
        List of graph nodes with metadata
    """
    try:
        logger.info(f"Querying nodes for manuscript: {manuscript_id}, type: {node_type}")
        
        with graph_db.driver.session() as session:
            # Build query
            if node_type:
                query = """
                    MATCH (n:NarrativeEntity {manuscript_id: $mid})
                    WHERE $type IN labels(n)
                    OPTIONAL MATCH (n)-[:APPEARS_IN]->(s:Scene)
                    WITH n, 
                         min(s.created_at) as first_appearance,
                         max(s.created_at) as last_appearance
                    RETURN n, first_appearance, last_appearance
                    ORDER BY n.name
                    SKIP $offset
                    LIMIT $limit
                """
                params = {"mid": manuscript_id, "type": node_type, "offset": offset, "limit": limit}
            else:
                query = """
                    MATCH (n:NarrativeEntity {manuscript_id: $mid})
                    OPTIONAL MATCH (n)-[:APPEARS_IN]->(s:Scene)
                    WITH n, 
                         min(s.created_at) as first_appearance,
                         max(s.created_at) as last_appearance
                    RETURN n, first_appearance, last_appearance
                    ORDER BY n.name
                    SKIP $offset
                    LIMIT $limit
                """
                params = {"mid": manuscript_id, "offset": offset, "limit": limit}
            
            result = session.run(query, **params)
            
            nodes = []
            for record in result:
                node = record["n"]
                node_labels = list(node.labels)
                
                # Determine primary type (Character or Location)
                primary_type = "NarrativeEntity"
                if "Character" in node_labels:
                    primary_type = "Character"
                elif "Location" in node_labels:
                    primary_type = "Location"
                
                nodes.append(GraphNode(
                    id=f"{primary_type.lower()}_{node['name'].lower().replace(' ', '_')}",
                    name=node["name"],
                    type=primary_type,
                    properties=dict(node),
                    first_appearance=record.get("first_appearance"),
                    last_appearance=record.get("last_appearance")
                ))
            
            # Get total count
            count_query = """
                MATCH (n:NarrativeEntity {manuscript_id: $mid})
                RETURN count(n) as total
            """
            if node_type:
                count_query = f"""
                    MATCH (n:NarrativeEntity {{manuscript_id: $mid}})
                    WHERE $type IN labels(n)
                    RETURN count(n) as total
                """
            
            count_result = session.run(count_query, mid=manuscript_id, type=node_type if node_type else None)
            total = count_result.single()["total"]
        
        logger.info(f"Found {len(nodes)} nodes (total: {total})")
        
        return GraphNodesResponse(
            nodes=nodes,
            total=total,
            metadata={
                "manuscript_id": manuscript_id,
                "node_type": node_type,
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Error querying nodes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to query nodes: {str(e)}")


@router.get("/edges", response_model=GraphEdgesResponse)
async def get_edges(
    manuscript_id: str = Query(..., description="Manuscript identifier"),
    source: Optional[str] = Query(None, description="Filter by source node name"),
    target: Optional[str] = Query(None, description="Filter by target node name"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of edges to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Query relationships (edges) from the knowledge graph.
    
    Returns relationships between characters, locations, and other entities.
    
    Args:
        manuscript_id: Story identifier
        source: Optional filter by source node name
        target: Optional filter by target node name
        relationship_type: Optional filter by relationship type
        limit: Maximum results (1-500)
        offset: Pagination offset
        
    Returns:
        List of graph edges with metadata
    """
    try:
        logger.info(f"Querying edges for manuscript: {manuscript_id}")
        
        with graph_db.driver.session() as session:
            # Build dynamic query based on filters
            where_clauses = ["a.manuscript_id = $mid", "b.manuscript_id = $mid"]
            params = {"mid": manuscript_id, "offset": offset, "limit": limit}
            
            if source:
                where_clauses.append("a.name = $source")
                params["source"] = source
            
            if target:
                where_clauses.append("b.name = $target")
                params["target"] = target
            
            where_clause = " AND ".join(where_clauses)
            
            # Note: We can't filter by relationship type in WHERE clause easily
            # So we'll filter in Python if needed
            query = f"""
                MATCH (a:NarrativeEntity)-[r]->(b:NarrativeEntity)
                WHERE {where_clause}
                RETURN a.name as source, b.name as target, type(r) as rel_type, properties(r) as props
                ORDER BY a.name, b.name
                SKIP $offset
                LIMIT $limit
            """
            
            result = session.run(query, **params)
            
            edges = []
            for record in result:
                rel_type = record["rel_type"]
                
                # Apply relationship type filter if specified
                if relationship_type and rel_type != relationship_type:
                    continue
                
                edges.append(GraphEdge(
                    source=record["source"],
                    target=record["target"],
                    type=rel_type,
                    properties=dict(record["props"]) if record["props"] else {}
                ))
            
            # Get total count
            count_query = f"""
                MATCH (a:NarrativeEntity)-[r]->(b:NarrativeEntity)
                WHERE {where_clause}
                RETURN count(r) as total
            """
            count_result = session.run(count_query, **{k: v for k, v in params.items() if k not in ['offset', 'limit']})
            total = count_result.single()["total"]
        
        logger.info(f"Found {len(edges)} edges (total: {total})")
        
        return GraphEdgesResponse(
            edges=edges,
            total=total,
            metadata={
                "manuscript_id": manuscript_id,
                "source": source,
                "target": target,
                "relationship_type": relationship_type,
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Error querying edges: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to query edges: {str(e)}")


@router.get("/node/{node_name}")
async def get_node_details(
    node_name: str,
    manuscript_id: str = Query(..., description="Manuscript identifier")
):
    """
    Get detailed information about a specific node.
    
    Returns node properties, relationships, and appearance history.
    
    Args:
        node_name: Name of the node to query
        manuscript_id: Story identifier
        
    Returns:
        Detailed node information
    """
    try:
        logger.info(f"Querying node details: {node_name} in manuscript: {manuscript_id}")
        
        with graph_db.driver.session() as session:
            # Get node with relationships
            query = """
                MATCH (n:NarrativeEntity {name: $name, manuscript_id: $mid})
                OPTIONAL MATCH (n)-[r]->(target:NarrativeEntity)
                OPTIONAL MATCH (n)-[:APPEARS_IN]->(s:Scene)
                RETURN n, 
                       collect(DISTINCT {type: type(r), target: target.name, context: r.context}) as relationships,
                       collect(DISTINCT {scene_id: s.id, timestamp: s.created_at}) as appearances
            """
            
            result = session.run(query, name=node_name, mid=manuscript_id)
            record = result.single()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
            
            node = record["n"]
            node_labels = list(node.labels)
            
            primary_type = "NarrativeEntity"
            if "Character" in node_labels:
                primary_type = "Character"
            elif "Location" in node_labels:
                primary_type = "Location"
            
            return {
                "node": {
                    "id": f"{primary_type.lower()}_{node['name'].lower().replace(' ', '_')}",
                    "name": node["name"],
                    "type": primary_type,
                    "properties": dict(node),
                    "relationships": [r for r in record["relationships"] if r["type"]],
                    "appearances": [a for a in record["appearances"] if a["scene_id"]]
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying node details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to query node: {str(e)}")


@router.get("", response_model=FullGraphResponse)
async def get_full_graph(
    manuscript_id: str = Query(..., description="Manuscript identifier")
):
    """
    Export the complete knowledge graph for a manuscript.
    
    Returns all nodes and edges. Use with caution for large graphs.
    
    Args:
        manuscript_id: Story identifier
        
    Returns:
        Complete graph with all nodes and edges
    """
    try:
        logger.info(f"Exporting full graph for manuscript: {manuscript_id}")
        
        # Get all nodes - pass actual values, not Query objects
        nodes_response = await get_nodes(
            manuscript_id=manuscript_id,
            node_type=None,
            limit=500,
            offset=0
        )
        
        # Get all edges - pass actual values, not Query objects
        edges_response = await get_edges(
            manuscript_id=manuscript_id,
            source=None,
            target=None,
            relationship_type=None,
            limit=500,
            offset=0
        )
        
        metadata = {
            "manuscript_id": manuscript_id,
            "node_count": nodes_response.total,
            "edge_count": edges_response.total,
            "character_count": len([n for n in nodes_response.nodes if n.type == "Character"]),
            "location_count": len([n for n in nodes_response.nodes if n.type == "Location"])
        }
        
        logger.info(f"Graph export complete: {metadata['node_count']} nodes, {metadata['edge_count']} edges")
        
        return FullGraphResponse(
            nodes=nodes_response.nodes,
            edges=edges_response.edges,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error exporting graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export graph: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for Knowledge Graph service."""
    try:
        # Test Neo4j connection
        with graph_db.driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        
        return {
            "status": "healthy",
            "service": "knowledge_graph",
            "database": "neo4j",
            "connection": "active"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "knowledge_graph",
            "database": "neo4j",
            "connection": "failed",
            "error": str(e)
        }
