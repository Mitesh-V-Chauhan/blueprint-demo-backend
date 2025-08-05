import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
from datetime import datetime
import uuid

from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai

from utils.config import Settings

logger = logging.getLogger(__name__)

class PineconeVectorStore:
    """Pinecone-based vector store for project knowledge management"""
    
    _client: Optional[Pinecone] = None
    _index = None
    _settings: Settings = Settings()
    _index_name = "ai-blueprint-knowledge"
    _dimension = 768  # Gemini embedding dimension
    
    @classmethod
    async def initialize(cls):
        """Initialize Pinecone client and index"""
        try:
            # Initialize Pinecone
            cls._client = Pinecone(api_key=cls._settings.PINECONE_API_KEY)
            
            # Create index if it doesn't exist
            await cls._ensure_index_exists()
            
            # Get index reference
            cls._index = cls._client.Index(cls._index_name)
            
            # Initialize Gemini for embeddings
            genai.configure(api_key=cls._settings.GEMINI_API_KEY_1)
            
            logger.info("Pinecone vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone vector store: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """Close vector store connections"""
        # Pinecone doesn't require explicit closing
        logger.info("Pinecone vector store connections closed")
    
    @classmethod
    async def health_check(cls) -> str:
        """Check vector store health"""
        try:
            if cls._index:
                stats = cls._index.describe_index_stats()
                total_vectors = stats.total_vector_count
                return f"healthy - {total_vectors} vectors"
            return "unhealthy - no index connection"
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return f"unhealthy: {e}"
    
    @classmethod
    async def _ensure_index_exists(cls):
        """Ensure the Pinecone index exists"""
        try:
            # List existing indexes
            existing_indexes = [index.name for index in cls._client.list_indexes()]
            
            if cls._index_name not in existing_indexes:
                # Create new index
                cls._client.create_index(
                    name=cls._index_name,
                    dimension=cls._dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"  # Change to your preferred region
                    )
                )
                logger.info(f"Created Pinecone index '{cls._index_name}'")
            else:
                logger.info(f"Pinecone index '{cls._index_name}' already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
    
    @classmethod
    def _generate_embedding(cls, text: str) -> List[float]:
        """Generate embedding using Gemini"""
        try:
            # Use Gemini's text embedding model
            model = 'models/text-embedding-004'
            result = genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * cls._dimension
    
    @classmethod
    def _create_vector_id(cls, project_id: str, doc_type: str, identifier: str) -> str:
        """Create unique vector ID"""
        content = f"{project_id}:{doc_type}:{identifier}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @classmethod
    async def add_project_overview(cls, project_id: str, content: str, 
                                 tech_stack: Dict[str, Any], user_flow: str):
        """Add project overview to vector store"""
        try:
            # Combine all content for embedding
            combined_content = f"""
            Project Overview: {content}
            
            Tech Stack: {json.dumps(tech_stack, indent=2)}
            
            User Flow: {user_flow}
            """
            
            embedding = cls._generate_embedding(combined_content)
            
            vector_id = cls._create_vector_id(project_id, "overview", "main")
            
            # Prepare metadata
            metadata = {
                "project_id": project_id,
                "doc_type": "overview",
                "content": content[:1000],  # Pinecone metadata size limit
                "tech_stack": json.dumps(tech_stack)[:500],
                "user_flow": user_flow[:500],
                "timestamp": datetime.now().isoformat(),
                "searchable_content": combined_content[:1000]
            }
            
            # Upsert to Pinecone
            cls._index.upsert(
                vectors=[(vector_id, embedding, metadata)]
            )
            
            logger.info(f"Added project overview for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to add project overview: {e}")
            raise
    
    @classmethod
    async def add_code_file(cls, project_id: str, file_path: str, 
                          content: str, explanation: str = ""):
        """Add code file to vector store"""
        try:
            # Extract file extension to determine language
            file_ext = file_path.split('.')[-1] if '.' in file_path else ''
            
            # Combine content and explanation for better search
            combined_content = f"""
            File: {file_path}
            Language: {file_ext}
            
            Code:
            {content[:2000]}  # Limit content size
            
            Explanation:
            {explanation}
            """
            
            embedding = cls._generate_embedding(combined_content)
            
            vector_id = cls._create_vector_id(project_id, "code", file_path)
            
            # Prepare metadata (Pinecone has size limits)
            metadata = {
                "project_id": project_id,
                "doc_type": "code",
                "file_path": file_path,
                "content": content[:800],  # Truncate for metadata
                "explanation": explanation[:500],
                "language": file_ext,
                "timestamp": datetime.now().isoformat(),
                "searchable_content": combined_content[:1000]
            }
            
            # Upsert to Pinecone
            cls._index.upsert(
                vectors=[(vector_id, embedding, metadata)]
            )
            
            logger.info(f"Added code file {file_path} for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to add code file: {e}")
            raise
    
    @classmethod
    async def add_flowchart_data(cls, project_id: str, flowchart_json: Dict[str, Any], 
                               description: str = ""):
        """Add flowchart data to vector store"""
        try:
            # Extract meaningful information from flowchart
            nodes_info = []
            edges_info = []
            
            if 'nodes' in flowchart_json:
                for node in flowchart_json['nodes'][:10]:  # Limit to first 10 nodes
                    node_data = node.get('data', {})
                    node_info = f"Node {node['id']}: {node_data.get('label', 'Unknown')} ({node.get('type', 'default')})"
                    nodes_info.append(node_info)
            
            if 'edges' in flowchart_json:
                for edge in flowchart_json['edges'][:10]:  # Limit to first 10 edges
                    edge_info = f"Connection: {edge['source']} -> {edge['target']}"
                    if 'label' in edge:
                        edge_info += f" ({edge['label']})"
                    edges_info.append(edge_info)
            
            combined_content = f"""
            Architecture Description: {description}
            
            Components:
            {chr(10).join(nodes_info)}
            
            Connections:
            {chr(10).join(edges_info)}
            """
            
            embedding = cls._generate_embedding(combined_content)
            
            vector_id = cls._create_vector_id(project_id, "flowchart", "current")
            
            metadata = {
                "project_id": project_id,
                "doc_type": "flowchart",
                "description": description[:500],
                "nodes_count": len(flowchart_json.get('nodes', [])),
                "edges_count": len(flowchart_json.get('edges', [])),
                "timestamp": datetime.now().isoformat(),
                "searchable_content": combined_content[:1000]
            }
            
            cls._index.upsert(
                vectors=[(vector_id, embedding, metadata)]
            )
            
            logger.info(f"Added flowchart data for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to add flowchart data: {e}")
            raise
    
    @classmethod
    async def add_conversation_context(cls, project_id: str, conversation: List[Dict[str, str]]):
        """Add conversation context to vector store"""
        try:
            # Combine recent conversation for context
            conversation_text = []
            for msg in conversation[-10:]:  # Last 10 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                conversation_text.append(f"{role}: {content}")
            
            combined_content = f"""
            Recent Conversation Context:
            {chr(10).join(conversation_text)}
            """
            
            embedding = cls._generate_embedding(combined_content)
            
            vector_id = cls._create_vector_id(project_id, "conversation", "recent")
            
            metadata = {
                "project_id": project_id,
                "doc_type": "conversation",
                "message_count": len(conversation),
                "timestamp": datetime.now().isoformat(),
                "searchable_content": combined_content[:1000]
            }
            
            cls._index.upsert(
                vectors=[(vector_id, embedding, metadata)]
            )
            
            logger.info(f"Added conversation context for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to add conversation context: {e}")
            raise
    
    @classmethod
    async def search_project_knowledge(cls, project_id: str, query: str, 
                                     doc_types: List[str] = None, 
                                     limit: int = 5) -> List[Dict[str, Any]]:
        """Search project knowledge base"""
        try:
            query_embedding = cls._generate_embedding(query)
            
            # Build filter for project and document types
            filter_dict = {"project_id": {"$eq": project_id}}
            
            if doc_types:
                filter_dict["doc_type"] = {"$in": doc_types}
            
            # Search vectors
            search_results = cls._index.query(
                vector=query_embedding,
                filter=filter_dict,
                top_k=limit,
                include_metadata=True
            )
            
            results = []
            for match in search_results.matches:
                result = {
                    "score": match.score,
                    "doc_type": match.metadata.get("doc_type"),
                    "content": match.metadata.get("searchable_content", ""),
                    "metadata": {k: v for k, v in match.metadata.items() 
                               if k not in ["searchable_content"]}
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} relevant documents for query: {query[:100]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search project knowledge: {e}")
            return []
    
    @classmethod
    async def get_project_context(cls, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project context"""
        try:
            # Query all vectors for this project
            filter_dict = {"project_id": {"$eq": project_id}}
            
            # Get all vectors (using a dummy query vector)
            dummy_vector = [0.0] * cls._dimension
            
            results = cls._index.query(
                vector=dummy_vector,
                filter=filter_dict,
                top_k=100,  # Get up to 100 vectors
                include_metadata=True
            )
            
            context = {
                "overview": None,
                "code_files": [],
                "flowchart": None,
                "conversation": None,
                "total_documents": len(results.matches)
            }
            
            for match in results.matches:
                doc_type = match.metadata.get("doc_type")
                
                if doc_type == "overview":
                    context["overview"] = {
                        "content": match.metadata.get("content"),
                        "tech_stack": match.metadata.get("tech_stack"),
                        "user_flow": match.metadata.get("user_flow")
                    }
                elif doc_type == "code":
                    context["code_files"].append({
                        "file_path": match.metadata.get("file_path"),
                        "language": match.metadata.get("language"),
                        "explanation": match.metadata.get("explanation")
                    })
                elif doc_type == "flowchart":
                    context["flowchart"] = {
                        "description": match.metadata.get("description"),
                        "nodes_count": match.metadata.get("nodes_count"),
                        "edges_count": match.metadata.get("edges_count")
                    }
                elif doc_type == "conversation":
                    context["conversation"] = {
                        "message_count": match.metadata.get("message_count"),
                        "last_updated": match.metadata.get("timestamp")
                    }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get project context: {e}")
            return {"error": str(e)}
    
    @classmethod
    async def delete_project_data(cls, project_id: str):
        """Delete all vector data for a project"""
        try:
            # Pinecone doesn't have direct filter delete, so we need to:
            # 1. Query all vectors for this project
            # 2. Delete them by ID
            
            filter_dict = {"project_id": {"$eq": project_id}}
            dummy_vector = [0.0] * cls._dimension
            
            # Get all vector IDs for this project
            results = cls._index.query(
                vector=dummy_vector,
                filter=filter_dict,
                top_k=1000,  # Max vectors to delete at once
                include_metadata=False
            )
            
            if results.matches:
                vector_ids = [match.id for match in results.matches]
                
                # Delete vectors in batches
                batch_size = 100
                for i in range(0, len(vector_ids), batch_size):
                    batch = vector_ids[i:i + batch_size]
                    cls._index.delete(ids=batch)
                
                logger.info(f"Deleted {len(vector_ids)} vectors for project {project_id}")
            else:
                logger.info(f"No vectors found for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete project data: {e}")
            raise

# Create alias for backward compatibility
VectorStore = PineconeVectorStore