"""
Phase 2: Project Understanding & Code Parsing
Parse repository structure, extract AST, identify modules and components
"""
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import tree_sitter
from tree_sitter import Language, Parser
from pydantic import BaseModel
from loguru import logger


class FunctionInfo(BaseModel):
    """Function information"""
    name: str
    parameters: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    line_start: int
    line_end: int


class ClassInfo(BaseModel):
    """Class information"""
    name: str
    methods: List[str]
    base_classes: List[str]
    docstring: Optional[str] = None
    line_start: int
    line_end: int


class FileAnalysis(BaseModel):
    """File analysis result"""
    file_path: str
    language: str
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[str]
    exports: List[str]
    api_routes: List[Dict[str, Any]]
    loc: int  # Lines of code


class ModuleInfo(BaseModel):
    """Module/component information"""
    name: str
    type: str  # api, model, util, component, service, etc.
    files: List[str]
    description: str


class ProjectStructure(BaseModel):
    """Project structure analysis"""
    entry_points: List[str]
    modules: List[ModuleInfo]
    tech_stack: List[str]
    frameworks: List[str]
    total_files: int
    total_loc: int


class CodeParser:
    """Code parser using tree-sitter"""
    
    def __init__(self):
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """Initialize tree-sitter parsers for supported languages"""
        # Note: In production, you'd build language libraries
        # For now, we'll use regex-based parsing as fallback
        pass
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext)
    
    def parse_python_file(self, file_path: str, content: str) -> FileAnalysis:
        """Parse Python file using regex (fallback when tree-sitter not available)"""
        functions = []
        classes = []
        imports = []
        
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Extract imports
        import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+([\w,\s.]+)'
        for i, line in enumerate(lines):
            match = re.match(import_pattern, line.strip())
            if match:
                imports.append(line.strip())
        
        # Extract functions
        func_pattern = r'^def\s+(\w+)\s*\((.*?)\)'
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line.strip())
            if match:
                func_name = match.group(1)
                params = [p.strip().split(':')[0].strip() for p in match.group(2).split(',') if p.strip()]
                
                # Get docstring
                docstring = None
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        docstring = next_line.strip('"\'')
                
                functions.append(FunctionInfo(
                    name=func_name,
                    parameters=params,
                    docstring=docstring,
                    line_start=i + 1,
                    line_end=i + 10  # Approximate
                ))
        
        # Extract classes
        class_pattern = r'^class\s+(\w+)(?:\((.*?)\))?:'
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line.strip())
            if match:
                class_name = match.group(1)
                base_classes = [b.strip() for b in (match.group(2) or '').split(',') if b.strip()]
                
                # Get docstring
                docstring = None
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        docstring = next_line.strip('"\'')
                
                # Find methods
                methods = []
                for j in range(i + 1, min(i + 100, len(lines))):
                    method_match = re.match(r'^\s+def\s+(\w+)\s*\(', lines[j])
                    if method_match:
                        methods.append(method_match.group(1))
                    elif re.match(r'^class\s+\w+', lines[j]):
                        break
                
                classes.append(ClassInfo(
                    name=class_name,
                    methods=methods,
                    base_classes=base_classes,
                    docstring=docstring,
                    line_start=i + 1,
                    line_end=i + 50  # Approximate
                ))
        
        return FileAnalysis(
            file_path=file_path,
            language='python',
            functions=functions,
            classes=classes,
            imports=imports,
            exports=[],
            api_routes=[],
            loc=loc
        )
    
    def parse_javascript_file(self, file_path: str, content: str) -> FileAnalysis:
        """Parse JavaScript/TypeScript file"""
        functions = []
        classes = []
        imports = []
        exports = []
        
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        # Extract imports
        import_patterns = [
            r'^import\s+.*?from\s+[\'"](.+?)[\'"]',
            r'^const\s+.*?=\s+require\([\'"](.+?)[\'"]\)'
        ]
        for line in lines:
            for pattern in import_patterns:
                match = re.search(pattern, line.strip())
                if match:
                    imports.append(line.strip())
                    break
        
        # Extract functions
        func_patterns = [
            r'(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:async\s*)?\(([^)]*)\)',
            r'(\w+)\s*:\s*(?:async\s*)?\(([^)]*)\)\s*=>',
        ]
        for i, line in enumerate(lines):
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    params = [p.strip().split(':')[0].strip() for p in match.group(2).split(',') if p.strip()]
                    
                    functions.append(FunctionInfo(
                        name=func_name,
                        parameters=params,
                        line_start=i + 1,
                        line_end=i + 10
                    ))
                    break
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                base_class = match.group(2)
                
                classes.append(ClassInfo(
                    name=class_name,
                    methods=[],
                    base_classes=[base_class] if base_class else [],
                    line_start=i + 1,
                    line_end=i + 50
                ))
        
        # Extract exports
        export_pattern = r'^export\s+(?:default\s+)?(?:class|function|const|let|var)?\s*(\w+)'
        for line in lines:
            match = re.search(export_pattern, line.strip())
            if match:
                exports.append(match.group(1))
        
        return FileAnalysis(
            file_path=file_path,
            language='javascript',
            functions=functions,
            classes=classes,
            imports=imports,
            exports=exports,
            api_routes=[],
            loc=loc
        )
    
    def parse_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Parse a single file"""
        try:
            language = self.detect_language(file_path)
            if not language:
                return None
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if language == 'python':
                return self.parse_python_file(file_path, content)
            elif language in ['javascript', 'typescript']:
                return self.parse_javascript_file(file_path, content)
            else:
                # Generic parsing
                lines = content.split('\n')
                return FileAnalysis(
                    file_path=file_path,
                    language=language,
                    functions=[],
                    classes=[],
                    imports=[],
                    exports=[],
                    api_routes=[],
                    loc=len([l for l in lines if l.strip()])
                )
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None


class ProjectAnalyzer:
    """Analyze project structure and identify components"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.parser = CodeParser()
    
    def identify_entry_points(self) -> List[str]:
        """Identify main entry point files"""
        entry_point_names = [
            'main.py', 'app.py', '__main__.py', 'server.py',
            'index.js', 'main.js', 'app.js', 'server.js',
            'index.ts', 'main.ts', 'app.ts',
            'Main.java', 'Application.java'
        ]
        
        entry_points = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file in entry_point_names:
                    entry_points.append(os.path.join(root, file))
        
        return entry_points
    
    def identify_modules(self) -> List[ModuleInfo]:
        """Identify major modules/components"""
        modules = []
        
        # Common module directory patterns
        module_patterns = {
            'api': ['api', 'routes', 'endpoints', 'controllers'],
            'model': ['models', 'schemas', 'entities'],
            'service': ['services', 'business', 'logic'],
            'util': ['utils', 'helpers', 'common'],
            'component': ['components', 'views', 'pages'],
            'middleware': ['middleware', 'middlewares'],
            'config': ['config', 'configuration', 'settings'],
            'test': ['tests', 'test', '__tests__'],
        }
        
        for root, dirs, files in os.walk(self.repo_path):
            dir_name = os.path.basename(root).lower()
            
            for module_type, patterns in module_patterns.items():
                if dir_name in patterns:
                    # Get files in this module
                    module_files = []
                    for file in files:
                        if not file.startswith('.'):
                            module_files.append(os.path.join(root, file))
                    
                    if module_files:
                        modules.append(ModuleInfo(
                            name=dir_name,
                            type=module_type,
                            files=module_files,
                            description=f"{module_type.capitalize()} module"
                        ))
        
        return modules
    
    def detect_tech_stack(self) -> tuple[List[str], List[str]]:
        """Detect technologies and frameworks used"""
        tech_stack = []
        frameworks = []
        
        # Check for common config files
        indicators = {
            'package.json': ['Node.js', 'npm'],
            'requirements.txt': ['Python'],
            'Pipfile': ['Python', 'Pipenv'],
            'pom.xml': ['Java', 'Maven'],
            'build.gradle': ['Java', 'Gradle'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go'],
            'composer.json': ['PHP', 'Composer'],
        }
        
        for file_name, techs in indicators.items():
            if os.path.exists(os.path.join(self.repo_path, file_name)):
                tech_stack.extend(techs)
                
                # Read file for framework detection
                try:
                    with open(os.path.join(self.repo_path, file_name), 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                        # Framework patterns
                        framework_patterns = {
                            'react': ['React'],
                            'vue': ['Vue.js'],
                            'angular': ['Angular'],
                            'next': ['Next.js'],
                            'express': ['Express.js'],
                            'fastapi': ['FastAPI'],
                            'flask': ['Flask'],
                            'django': ['Django'],
                            'spring': ['Spring Boot'],
                            'tensorflow': ['TensorFlow'],
                            'pytorch': ['PyTorch'],
                            'sklearn': ['scikit-learn'],
                        }
                        
                        for pattern, fw in framework_patterns.items():
                            if pattern in content:
                                frameworks.extend(fw)
                except Exception as e:
                    logger.warning(f"Error reading {file_name}: {e}")
        
        return list(set(tech_stack)), list(set(frameworks))
    
    def analyze(self) -> ProjectStructure:
        """Perform complete project analysis"""
        logger.info(f"Analyzing project at {self.repo_path}")
        
        entry_points = self.identify_entry_points()
        modules = self.identify_modules()
        tech_stack, frameworks = self.detect_tech_stack()
        
        # Count files and LOC
        total_files = 0
        total_loc = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if self.parser.detect_language(file):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    analysis = self.parser.parse_file(file_path)
                    if analysis:
                        total_loc += analysis.loc
        
        logger.success(f"Project analysis complete: {total_files} files, {total_loc} LOC")
        
        return ProjectStructure(
            entry_points=entry_points,
            modules=modules,
            tech_stack=tech_stack,
            frameworks=frameworks,
            total_files=total_files,
            total_loc=total_loc
        )
