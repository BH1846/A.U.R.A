"""
Phase 1: GitHub Repository Integration
Handle candidate input, validate GitHub URLs, and clone repositories
"""
import os
import re
import shutil
from typing import Optional, Dict, Any
from git import Repo, GitCommandError
from github import Github, GithubException
from pydantic import BaseModel, validator, HttpUrl
from config import settings
from loguru import logger


class CandidateInput(BaseModel):
    """Candidate input schema"""
    name: str
    email: str
    github_url: str
    role_type: str
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v
    
    @validator('github_url')
    def validate_github_url(cls, v):
        """Validate GitHub URL"""
        pattern = r'^https?://github\.com/[\w-]+/[\w.-]+/?$'
        if not re.match(pattern, v.rstrip('/')):
            raise ValueError("Invalid GitHub repository URL")
        return v.rstrip('/')
    
    @validator('role_type')
    def validate_role_type(cls, v):
        """Validate role type"""
        valid_roles = ['Frontend', 'Backend', 'ML', 'DevOps', 'FullStack']
        if v not in valid_roles:
            raise ValueError(f"Invalid role type. Must be one of: {', '.join(valid_roles)}")
        return v


class RepositoryInfo(BaseModel):
    """Repository information"""
    repo_name: str
    repo_url: str
    owner: str
    description: Optional[str]
    languages: Dict[str, int]
    stars: int
    forks: int
    last_commit: Optional[str]
    default_branch: str
    is_private: bool
    size_kb: int


class GitHubService:
    """GitHub repository service"""
    
    def __init__(self):
        self.github_token = settings.GITHUB_TOKEN
        self.repos_dir = settings.REPOS_DIR
        self.github_client = None
        
        if self.github_token:
            try:
                self.github_client = Github(self.github_token)
                logger.info("GitHub client initialized with token")
            except Exception as e:
                logger.warning(f"Failed to initialize GitHub client: {e}")
    
    def parse_github_url(self, github_url: str) -> tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name
        Returns: (owner, repo_name)
        """
        # Remove trailing slash and .git
        url = github_url.rstrip('/').replace('.git', '')
        
        # Extract owner and repo
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError("Invalid GitHub URL format")
        
        owner = match.group(1)
        repo_name = match.group(2)
        
        return owner, repo_name
    
    def get_repository_info(self, github_url: str) -> RepositoryInfo:
        """
        Fetch repository metadata from GitHub API
        """
        try:
            owner, repo_name = self.parse_github_url(github_url)
            
            if self.github_client:
                # Use authenticated API
                repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                
                return RepositoryInfo(
                    repo_name=repo.name,
                    repo_url=repo.html_url,
                    owner=repo.owner.login,
                    description=repo.description,
                    languages=repo.get_languages(),
                    stars=repo.stargazers_count,
                    forks=repo.forks_count,
                    last_commit=repo.pushed_at.isoformat() if repo.pushed_at else None,
                    default_branch=repo.default_branch,
                    is_private=repo.private,
                    size_kb=repo.size
                )
            else:
                # Fallback: basic info without API
                return RepositoryInfo(
                    repo_name=repo_name,
                    repo_url=github_url,
                    owner=owner,
                    description=None,
                    languages={},
                    stars=0,
                    forks=0,
                    last_commit=None,
                    default_branch="main",
                    is_private=False,
                    size_kb=0
                )
                
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"Failed to fetch repository info: {e}")
        except Exception as e:
            logger.error(f"Error fetching repository info: {e}")
            raise
    
    def validate_repository(self, github_url: str) -> bool:
        """
        Validate that repository exists and is accessible
        """
        try:
            self.get_repository_info(github_url)
            return True
        except Exception as e:
            logger.error(f"Repository validation failed: {e}")
            return False
    
    def clone_repository(self, github_url: str, candidate_id: int) -> str:
        """
        Clone repository to local storage
        Returns: local path to cloned repo
        """
        try:
            owner, repo_name = self.parse_github_url(github_url)
            
            # Create unique directory for this candidate's repo
            local_path = os.path.join(
                self.repos_dir,
                f"candidate_{candidate_id}_{owner}_{repo_name}"
            )
            
            # Remove existing directory if it exists
            if os.path.exists(local_path):
                logger.warning(f"Removing existing repository at {local_path}")
                shutil.rmtree(local_path)
            
            # Clone repository
            logger.info(f"Cloning repository from {github_url} to {local_path}")
            
            if self.github_token:
                # Clone with authentication
                auth_url = github_url.replace(
                    'https://github.com',
                    f'https://{self.github_token}@github.com'
                )
                Repo.clone_from(auth_url, local_path, depth=1)
            else:
                # Clone without authentication (public repos only)
                Repo.clone_from(github_url, local_path, depth=1)
            
            logger.success(f"Repository cloned successfully to {local_path}")
            return local_path
            
        except GitCommandError as e:
            logger.error(f"Git clone error: {e}")
            raise ValueError(f"Failed to clone repository: {e}")
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            raise
    
    def enumerate_directory(self, local_path: str) -> Dict[str, Any]:
        """
        Enumerate directory structure
        Returns: directory tree
        """
        def build_tree(path: str, max_depth: int = 5, current_depth: int = 0) -> Dict:
            """Recursively build directory tree"""
            if current_depth >= max_depth:
                return {"truncated": True}
            
            tree = {"type": "directory", "children": {}}
            
            try:
                for item in os.listdir(path):
                    # Skip hidden files and common ignore patterns
                    if item.startswith('.') or item in ['node_modules', '__pycache__', 'venv', 'env']:
                        continue
                    
                    item_path = os.path.join(path, item)
                    
                    if os.path.isdir(item_path):
                        tree["children"][item] = build_tree(item_path, max_depth, current_depth + 1)
                    else:
                        # Get file extension
                        ext = os.path.splitext(item)[1]
                        tree["children"][item] = {
                            "type": "file",
                            "extension": ext,
                            "size": os.path.getsize(item_path)
                        }
            except PermissionError:
                tree["error"] = "Permission denied"
            
            return tree
        
        return build_tree(local_path)
    
    def get_file_list(self, local_path: str, extensions: Optional[list] = None) -> list[str]:
        """
        Get list of files with specific extensions
        """
        file_list = []
        
        for root, dirs, files in os.walk(local_path):
            # Skip hidden and ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if extensions:
                    if any(file.endswith(ext) for ext in extensions):
                        file_list.append(os.path.join(root, file))
                else:
                    file_list.append(os.path.join(root, file))
        
        return file_list
    
    def cleanup_repository(self, local_path: str):
        """Remove cloned repository"""
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                logger.info(f"Cleaned up repository at {local_path}")
        except Exception as e:
            logger.error(f"Error cleaning up repository: {e}")


# Service instance
github_service = GitHubService()
