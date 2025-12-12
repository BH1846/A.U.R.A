"""
Cloud Storage Service for AURA
Supports multiple storage providers: Local, AWS S3, Cloudflare R2, DigitalOcean Spaces, Uploadcare
"""
import os
import shutil
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import time
from loguru import logger


class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    def upload_directory(self, local_path: str, remote_path: str) -> str:
        """Upload a directory and return the remote URL"""
        pass
    
    @abstractmethod
    def download_directory(self, remote_path: str, local_path: str) -> None:
        """Download a directory from remote storage"""
        pass
    
    @abstractmethod
    def delete_directory(self, remote_path: str) -> None:
        """Delete a directory from remote storage"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage (default/fallback)"""
    
    def upload_directory(self, local_path: str, remote_path: str) -> str:
        """Just return local path for local storage"""
        return local_path
    
    def download_directory(self, remote_path: str, local_path: str) -> None:
        """No-op for local storage"""
        pass
    
    def delete_directory(self, remote_path: str) -> None:
        """Delete local directory"""
        if os.path.exists(remote_path):
            shutil.rmtree(remote_path)


class S3StorageProvider(StorageProvider):
    """AWS S3 / Cloudflare R2 / DigitalOcean Spaces storage"""
    
    def __init__(self):
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT_URL'),  # For R2/Spaces compatibility
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket = os.getenv('S3_BUCKET_NAME')
        self.cdn_url = os.getenv('S3_CDN_URL', '')  # Optional CDN URL
    
    def upload_directory(self, local_path: str, remote_path: str) -> str:
        """Upload directory as zip to S3"""
        try:
            # Create zip file
            zip_path = f"{local_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(local_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, local_path)
                        zipf.write(file_path, arcname)
            
            # Upload to S3
            s3_key = f"{remote_path}.zip"
            self.s3_client.upload_file(zip_path, self.bucket, s3_key)
            
            # Clean up local zip
            os.remove(zip_path)
            
            # Return CDN URL or S3 URL
            if self.cdn_url:
                return f"{self.cdn_url}/{s3_key}"
            else:
                return f"https://{self.bucket}.s3.amazonaws.com/{s3_key}"
            
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise
    
    def download_directory(self, remote_path: str, local_path: str) -> None:
        """Download zip from S3 and extract"""
        try:
            s3_key = f"{remote_path}.zip"
            zip_path = f"{local_path}.zip"
            
            # Download from S3
            self.s3_client.download_file(self.bucket, s3_key, zip_path)
            
            # Extract
            os.makedirs(local_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(local_path)
            
            # Clean up zip
            os.remove(zip_path)
            
        except Exception as e:
            logger.error(f"Failed to download from S3: {e}")
            raise
    
    def delete_directory(self, remote_path: str) -> None:
        """Delete zip from S3"""
        try:
            s3_key = f"{remote_path}.zip"
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
        except Exception as e:
            logger.error(f"Failed to delete from S3: {e}")


class UploadcareStorageProvider(StorageProvider):
    """Uploadcare storage provider"""
    
    def __init__(self):
        self.public_key = os.getenv('UPLOADCARE_PUBLIC_KEY')
        self.secret_key = os.getenv('UPLOADCARE_SECRET_KEY')
        self.api_url = 'https://upload.uploadcare.com'
    
    def upload_directory(self, local_path: str, remote_path: str) -> str:
        """Upload directory as zip to Uploadcare"""
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required for Uploadcare storage. Install with: pip install requests")
        
        try:
            # Create zip file
            zip_path = f"{local_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(local_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, local_path)
                        zipf.write(file_path, arcname)
            
            # Upload to Uploadcare
            with open(zip_path, 'rb') as f:
                response = requests.post(
                    f"{self.api_url}/base/",
                    headers={'Authorization': f'Uploadcare.Simple {self.public_key}:{self.secret_key}'},
                    files={'file': (f"{remote_path}.zip", f)}
                )
            
            response.raise_for_status()
            file_id = response.json()['file']
            
            # Clean up local zip
            os.remove(zip_path)
            
            return f"https://ucarecdn.com/{file_id}/"
            
        except Exception as e:
            logger.error(f"Failed to upload to Uploadcare: {e}")
            raise
    
    def download_directory(self, remote_url: str, local_path: str) -> None:
        """Download zip from Uploadcare and extract"""
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required for Uploadcare storage. Install with: pip install requests")
        
        try:
            zip_path = f"{local_path}.zip"
            
            # Download from Uploadcare
            response = requests.get(remote_url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract
            os.makedirs(local_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(local_path)
            
            # Clean up zip
            os.remove(zip_path)
            
        except Exception as e:
            logger.error(f"Failed to download from Uploadcare: {e}")
            raise
    
    def delete_directory(self, remote_url: str) -> None:
        """Delete file from Uploadcare"""
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required for Uploadcare storage. Install with: pip install requests")
        
        try:
            # Extract file ID from URL
            file_id = remote_url.split('/')[-2]
            
            response = requests.delete(
                f"https://api.uploadcare.com/files/{file_id}/",
                headers={'Authorization': f'Uploadcare.Simple {self.public_key}:{self.secret_key}'}
            )
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Failed to delete from Uploadcare: {e}")


class StorageService:
    """Storage service that manages repository storage"""
    
    def __init__(self):
        storage_type = os.getenv('STORAGE_PROVIDER', 'local').lower()
        
        if storage_type == 's3':
            self.provider = S3StorageProvider()
            logger.info("Using S3-compatible storage (AWS S3/Cloudflare R2/DigitalOcean Spaces)")
        elif storage_type == 'uploadcare':
            self.provider = UploadcareStorageProvider()
            logger.info("Using Uploadcare storage")
        else:
            self.provider = LocalStorageProvider()
            logger.info("Using local filesystem storage")
    
    def upload_repository(self, local_path: str, candidate_id: int, repo_name: str) -> str:
        """Upload cloned repository to cloud storage"""
        remote_path = f"repos/candidate_{candidate_id}_{repo_name}"
        return self.provider.upload_directory(local_path, remote_path)
    
    def download_repository(self, remote_url: str, local_path: str) -> None:
        """Download repository from cloud storage"""
        self.provider.download_directory(remote_url, local_path)
    
    def delete_repository(self, remote_path: str) -> None:
        """Delete repository from cloud storage"""
        self.provider.delete_directory(remote_path)
    
    def cleanup_local_repos(self, max_age_hours: int = 24):
        """Clean up old local repository clones"""
        repos_dir = os.getenv('REPOS_DIR', '../data/repos')
        if not os.path.exists(repos_dir):
            return
        
        current_time = time.time()
        
        for item in os.listdir(repos_dir):
            item_path = os.path.join(repos_dir, item)
            if os.path.isdir(item_path):
                item_age_hours = (current_time - os.path.getmtime(item_path)) / 3600
                if item_age_hours > max_age_hours:
                    logger.info(f"Cleaning up old repository: {item}")
                    shutil.rmtree(item_path)


# Singleton instance
storage_service = StorageService()
