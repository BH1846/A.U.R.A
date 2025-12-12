"""
Test script to check cloud storage configuration and status
Run this to verify if cloud storage is being used
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

from colorama import init, Fore, Style
init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'='*60}\n")

def print_status(key, value, is_good=None):
    if is_good is True:
        icon = f"{Fore.GREEN}✓"
    elif is_good is False:
        icon = f"{Fore.RED}✗"
    else:
        icon = f"{Fore.YELLOW}•"
    
    print(f"{icon} {Fore.WHITE}{key:30} {Fore.CYAN}{value}")

def main():
    print_header("AURA Cloud Storage Status Check")
    
    # Check environment variables
    storage_provider = os.getenv('STORAGE_PROVIDER', 'local')
    delete_after_upload = os.getenv('DELETE_LOCAL_AFTER_UPLOAD', 'false')
    cleanup_hours = os.getenv('REPO_CLEANUP_MAX_AGE_HOURS', '24')
    
    print_status("Storage Provider:", storage_provider, storage_provider != 'local')
    print_status("Delete After Upload:", delete_after_upload, delete_after_upload.lower() == 'true')
    print_status("Cleanup Max Age (hours):", cleanup_hours)
    
    print(f"\n{Fore.YELLOW}{'─'*60}\n")
    
    # Check provider-specific configuration
    if storage_provider == 'uploadcare':
        print_header("Uploadcare Configuration")
        public_key = os.getenv('UPLOADCARE_PUBLIC_KEY', '')
        secret_key = os.getenv('UPLOADCARE_SECRET_KEY', '')
        
        if public_key and secret_key:
            print_status("Public Key:", f"{public_key[:10]}...", True)
            print_status("Secret Key:", f"{secret_key[:10]}...", True)
            print(f"\n{Fore.GREEN}✅ Uploadcare is CONFIGURED and will be used!")
        else:
            print_status("Public Key:", "Not set", False)
            print_status("Secret Key:", "Not set", False)
            print(f"\n{Fore.RED}❌ Uploadcare credentials missing!")
    
    elif storage_provider == 's3':
        print_header("S3/R2 Configuration")
        bucket = os.getenv('S3_BUCKET_NAME', '')
        endpoint = os.getenv('S3_ENDPOINT_URL', 'AWS Default')
        access_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        
        print_status("Bucket Name:", bucket or "Not set", bool(bucket))
        print_status("Endpoint:", endpoint)
        
        if access_key and secret_key:
            print_status("Access Key:", f"{access_key[:10]}...", True)
            print_status("Secret Key:", f"{secret_key[:10]}...", True)
            print(f"\n{Fore.GREEN}✅ S3/R2 is CONFIGURED and will be used!")
        else:
            print_status("Access Key:", "Not set", False)
            print_status("Secret Key:", "Not set", False)
            print(f"\n{Fore.RED}❌ S3/R2 credentials missing!")
    
    else:
        print(f"{Fore.YELLOW}ℹ️  Using LOCAL filesystem storage (default)")
        print(f"{Fore.YELLOW}   To enable cloud storage, set STORAGE_PROVIDER in .env")
    
    # Test import
    print(f"\n{Fore.YELLOW}{'─'*60}\n")
    print_header("Testing Storage Service Import")
    
    try:
        from core.storage.storage_service import storage_service
        print(f"{Fore.GREEN}✓ Storage service imported successfully")
        
        # Get provider type
        provider_type = type(storage_service.provider).__name__
        print_status("Provider Class:", provider_type, 'Local' not in provider_type)
        
    except ImportError as e:
        print(f"{Fore.RED}✗ Failed to import storage service: {e}")
        print(f"{Fore.YELLOW}  Make sure you're running from the correct directory")
    
    # Summary
    print(f"\n{Fore.YELLOW}{'─'*60}\n")
    print_header("Summary")
    
    if storage_provider != 'local':
        print(f"{Fore.GREEN}Cloud storage is ENABLED!")
        print(f"{Fore.CYAN}When you clone a repository:")
        print(f"{Fore.WHITE}  1. Repo clones to local directory")
        print(f"{Fore.WHITE}  2. Uploads to {storage_provider} automatically")
        if delete_after_upload.lower() == 'true':
            print(f"{Fore.WHITE}  3. Local copy deleted to save disk space")
        else:
            print(f"{Fore.YELLOW}  3. Local copy kept (set DELETE_LOCAL_AFTER_UPLOAD=true to save space)")
    else:
        print(f"{Fore.YELLOW}Cloud storage is DISABLED - using local storage")
        print(f"{Fore.CYAN}\nTo enable cloud storage:")
        print(f"{Fore.WHITE}  1. Choose a provider (uploadcare, s3)")
        print(f"{Fore.WHITE}  2. Set STORAGE_PROVIDER in .env")
        print(f"{Fore.WHITE}  3. Add provider credentials")
        print(f"{Fore.WHITE}  4. Restart the backend server")
    
    print(f"\n{Fore.CYAN}{'='*60}\n")
    
    # API endpoint info
    print(f"{Fore.YELLOW}💡 Tip: Check live status via API endpoint:")
    print(f"{Fore.CYAN}   curl http://localhost:8000/api/storage-status")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
        sys.exit(1)
