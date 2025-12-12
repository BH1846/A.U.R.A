"""
Phase 3: Knowledge Storage & RAG (Retrieval-Augmented Generation)
Chunk code, create embeddings, and store in vector database
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from pydantic import BaseModel
from loguru import logger
from config import settings as app_settings


class CodeChunk(BaseModel):
    """Code chunk model"""
    chunk_id: str
    content: str
    file_path: str
    chunk_type: str  # code, comment, docstring, readme
    language: Optional[str]
    metadata: Dict[str, Any]


class ChunkingStrategy:
    """Strategies for chunking code and documentation"""
    
    @staticmethod
    def chunk_by_function(file_analysis) -> List[CodeChunk]:
        """Chunk code by functions"""
        chunks = []
        
        try:
            with open(file_analysis.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Chunk each function
            for func in file_analysis.functions:
                content = ''.join(lines[func.line_start-1:func.line_end])
                
                chunks.append(CodeChunk(
                    chunk_id=f"{file_analysis.file_path}::func::{func.name}",
                    content=content.strip(),
                    file_path=file_analysis.file_path,
                    chunk_type='code',
                    language=file_analysis.language,
                    metadata={
                        'function_name': func.name,
                        'parameters': func.parameters,
                        'docstring': func.docstring,
                        'line_start': func.line_start,
                        'line_end': func.line_end
                    }
                ))
            
            # Chunk each class
            for cls in file_analysis.classes:
                content = ''.join(lines[cls.line_start-1:cls.line_end])
                
                chunks.append(CodeChunk(
                    chunk_id=f"{file_analysis.file_path}::class::{cls.name}",
                    content=content.strip(),
                    file_path=file_analysis.file_path,
                    chunk_type='code',
                    language=file_analysis.language,
                    metadata={
                        'class_name': cls.name,
                        'methods': cls.methods,
                        'base_classes': cls.base_classes,
                        'docstring': cls.docstring,
                        'line_start': cls.line_start,
                        'line_end': cls.line_end
                    }
                ))
        
        except Exception as e:
            logger.error(f"Error chunking file {file_analysis.file_path}: {e}")
        
        return chunks
    
    @staticmethod
    def chunk_readme(readme_path: str) -> List[CodeChunk]:
        """Chunk README file by sections"""
        chunks = []
        
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split by markdown headers
            sections = []
            current_section = []
            current_title = "Introduction"
            
            for line in content.split('\n'):
                if line.startswith('#'):
                    # Save previous section
                    if current_section:
                        sections.append((current_title, '\n'.join(current_section)))
                    
                    # Start new section
                    current_title = line.strip('#').strip()
                    current_section = []
                else:
                    current_section.append(line)
            
            # Save last section
            if current_section:
                sections.append((current_title, '\n'.join(current_section)))
            
            # Create chunks
            for i, (title, text) in enumerate(sections):
                if text.strip():
                    chunks.append(CodeChunk(
                        chunk_id=f"{readme_path}::section::{i}",
                        content=text.strip(),
                        file_path=readme_path,
                        chunk_type='readme',
                        language=None,
                        metadata={
                            'section_title': title,
                            'section_index': i
                        }
                    ))
        
        except Exception as e:
            logger.error(f"Error chunking README {readme_path}: {e}")
        
        return chunks
    
    @staticmethod
    def chunk_by_size(content: str, file_path: str, max_size: int = 500) -> List[CodeChunk]:
        """Chunk content by size (fallback strategy)"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for line in lines:
            if current_size + len(line) > max_size and current_chunk:
                # Save current chunk
                chunks.append(CodeChunk(
                    chunk_id=f"{file_path}::chunk::{chunk_index}",
                    content='\n'.join(current_chunk),
                    file_path=file_path,
                    chunk_type='code',
                    language=None,
                    metadata={'chunk_index': chunk_index}
                ))
                
                current_chunk = [line]
                current_size = len(line)
                chunk_index += 1
            else:
                current_chunk.append(line)
                current_size += len(line)
        
        # Save last chunk
        if current_chunk:
            chunks.append(CodeChunk(
                chunk_id=f"{file_path}::chunk::{chunk_index}",
                content='\n'.join(current_chunk),
                file_path=file_path,
                chunk_type='code',
                language=None,
                metadata={'chunk_index': chunk_index}
            ))
        
        return chunks


class VectorDBService:
    """Vector database service using ChromaDB"""
    
    def __init__(self):
        self.db_path = app_settings.CHROMA_DB_PATH
        self.client = chromadb.PersistentClient(path=self.db_path)
        logger.info(f"ChromaDB initialized at {self.db_path}")
    
    def create_collection(self, candidate_id: int) -> chromadb.Collection:
        """Create or get collection for a candidate"""
        collection_name = f"candidate_{candidate_id}"
        
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(name=collection_name)
        except:
            pass
        
        # Create new collection
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"candidate_id": candidate_id}
        )
        
        logger.info(f"Created collection: {collection_name}")
        return collection
    
    def get_collection(self, candidate_id: int) -> chromadb.Collection:
        """Get existing collection"""
        collection_name = f"candidate_{candidate_id}"
        return self.client.get_collection(name=collection_name)
    
    def add_chunks(self, candidate_id: int, chunks: List[CodeChunk]):
        """Add chunks to vector database"""
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        collection = self.create_collection(candidate_id)
        
        # Prepare data
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                'file_path': chunk.file_path,
                'chunk_type': chunk.chunk_type,
                'language': chunk.language or '',
                **chunk.metadata
            }
            for chunk in chunks
        ]
        
        # Add to collection (ChromaDB handles embeddings automatically)
        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.success(f"Added {len(chunks)} chunks to vector database")
        except Exception as e:
            logger.error(f"Error adding chunks to database: {e}")
            raise
    
    def query(self, candidate_id: int, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Query vector database"""
        try:
            collection = self.get_collection(candidate_id)
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return {'documents': [], 'metadatas': [], 'distances': []}
    
    def delete_collection(self, candidate_id: int):
        """Delete candidate's collection"""
        try:
            collection_name = f"candidate_{candidate_id}"
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")


class RAGService:
    """RAG (Retrieval-Augmented Generation) Service"""
    
    def __init__(self):
        self.vector_db = VectorDBService()
        self.chunking = ChunkingStrategy()
    
    def process_repository(self, candidate_id: int, repo_path: str, file_analyses: List) -> int:
        """
        Process repository and create vector embeddings
        Returns: number of chunks created
        """
        logger.info(f"Processing repository for candidate {candidate_id}")
        
        all_chunks = []
        
        # Process code files
        for analysis in file_analyses:
            chunks = self.chunking.chunk_by_function(analysis)
            all_chunks.extend(chunks)
        
        # Process README
        readme_paths = [
            os.path.join(repo_path, 'README.md'),
            os.path.join(repo_path, 'readme.md'),
            os.path.join(repo_path, 'README.MD'),
        ]
        
        for readme_path in readme_paths:
            if os.path.exists(readme_path):
                chunks = self.chunking.chunk_readme(readme_path)
                all_chunks.extend(chunks)
                break
        
        # Add chunks to vector database
        if all_chunks:
            self.vector_db.add_chunks(candidate_id, all_chunks)
            logger.success(f"Created {len(all_chunks)} chunks for candidate {candidate_id}")
        else:
            logger.warning(f"No chunks created for candidate {candidate_id}")
        
        return len(all_chunks)
    
    def retrieve_context(self, candidate_id: int, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query
        Returns: list of relevant chunks with metadata
        """
        results = self.vector_db.query(candidate_id, query, n_results)
        
        context_items = []
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        )):
            context_items.append({
                'content': doc,
                'metadata': meta,
                'relevance_score': 1 - dist,  # Convert distance to similarity
                'rank': i + 1
            })
        
        return context_items
    
    def get_project_overview_context(self, candidate_id: int) -> str:
        """Get overview context from README and main files"""
        # Query for README content
        readme_results = self.vector_db.query(candidate_id, "project overview purpose description", n_results=3)
        
        overview = "# Project Context\n\n"
        
        if readme_results['documents']:
            overview += "## Documentation:\n"
            for doc in readme_results['documents']:
                overview += f"\n{doc}\n"
        
        return overview


# Service instance
rag_service = RAGService()
