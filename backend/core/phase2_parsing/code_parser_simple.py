"""
Phase 2: Simplified Code Parser (no tree-sitter required)
Basic AST parsing for Python files
"""
import os
import ast
from typing import Dict, List, Any
from pathlib import Path
from loguru import logger


class CodeParser:
    """Lightweight code parser"""
    
    def __init__(self, language: str = "python"):
        self.language = language
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse file - Python AST for .py, basic text for others"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.endswith('.py'):
                return self._parse_python(content, file_path)
            else:
                return self._parse_text(content, file_path)
        except Exception as e:
            return {"error": str(e), "file": file_path}
    
    def _parse_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Parse Python with AST"""
        try:
            tree = ast.parse(content)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            
            return {
                "file": file_path,
                "language": "python",
                "functions": functions,
                "classes": classes,
                "imports": list(set(imports))
            }
        except:
            return {"file": file_path, "error": "Parse failed"}
    
    def _parse_text(self, content: str, file_path: str) -> Dict[str, Any]:
        """Basic text analysis"""
        return {
            "file": file_path,
            "language": "text",
            "lines": len(content.splitlines())
        }


class ProjectAnalyzer:
    """Simple project analyzer"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.parser = CodeParser()
    
    def analyze(self) -> Dict[str, Any]:
        """Scan and analyze project"""
        files_data = []
        language_counts = {}
        
        for ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c']:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                if 'node_modules' not in str(file_path) and 'venv' not in str(file_path):
                    parsed = self.parser.parse_file(str(file_path))
                    files_data.append(parsed)
                    
                    # Count languages
                    lang = parsed.get('language', 'unknown')
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            "repo_path": str(self.repo_path),
            "total_files": len(files_data),
            "files": files_data,
            "languages": language_counts  # Added for tech_stack compatibility
        }
