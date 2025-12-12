# Cloud Storage Configuration for AURA

AURA supports multiple cloud storage providers for storing cloned GitHub repositories. This keeps your server disk usage low and makes the system more scalable.

## Supported Providers

### 1. **Local Filesystem** (Default)
- No additional configuration needed
- Repositories stored on server disk
- Good for: Development, small deployments

### 2. **AWS S3**
- Most popular cloud storage
- Pay-as-you-go pricing (~$0.023/GB/month)
- Good for: Production deployments

### 3. **Cloudflare R2**
- S3-compatible API
- **Zero egress fees** (free data transfer)
- ~$0.015/GB/month storage
- Good for: Cost-effective production

### 4. **DigitalOcean Spaces**
- S3-compatible API
- $5/month for 250GB + 1TB transfer
- Good for: Predictable costs

### 5. **Uploadcare**
- Simple file hosting
- Free tier: 3GB storage + 10GB traffic
- Good for: Small projects, easy setup

## Configuration

### Option 1: Cloudflare R2 (Recommended for Production)

**Why R2?** Zero egress fees + S3 compatibility

1. **Create R2 Bucket:**
   - Go to Cloudflare Dashboard > R2
   - Create bucket: `aura-repositories`

2. **Get API Credentials:**
   - R2 > Manage R2 API Tokens > Create API Token
   - Copy Access Key ID and Secret Access Key

3. **Update `.env`:**
   ```env
   STORAGE_PROVIDER=s3
   AWS_ACCESS_KEY_ID=your_r2_access_key
   AWS_SECRET_ACCESS_KEY=your_r2_secret_key
   S3_BUCKET_NAME=aura-repositories
   S3_ENDPOINT_URL=https://[account-id].r2.cloudflarestorage.com
   S3_CDN_URL=https://pub-xxxxx.r2.dev  # Optional: R2 public URL
   DELETE_LOCAL_AFTER_UPLOAD=true  # Save disk space
   ```

### Option 2: AWS S3

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://aura-repositories --region us-east-1
   ```

2. **Create IAM User with S3 permissions**

3. **Update `.env`:**
   ```env
   STORAGE_PROVIDER=s3
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=aura-repositories
   DELETE_LOCAL_AFTER_UPLOAD=true
   ```

### Option 3: DigitalOcean Spaces

1. **Create Space in DigitalOcean**

2. **Generate API Keys**

3. **Update `.env`:**
   ```env
   STORAGE_PROVIDER=s3
   AWS_ACCESS_KEY_ID=your_do_key
   AWS_SECRET_ACCESS_KEY=your_do_secret
   S3_BUCKET_NAME=aura-repositories
   S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
   DELETE_LOCAL_AFTER_UPLOAD=true
   ```

### Option 4: Uploadcare

1. **Sign up at uploadcare.com**

2. **Get API keys from dashboard**

3. **Update `.env`:**
   ```env
   STORAGE_PROVIDER=uploadcare
   UPLOADCARE_PUBLIC_KEY=your_public_key
   UPLOADCARE_SECRET_KEY=your_secret_key
   DELETE_LOCAL_AFTER_UPLOAD=true
   ```

## Cost Comparison

| Provider | Storage Cost | Transfer Cost | Free Tier |
|----------|--------------|---------------|-----------|
| **Cloudflare R2** | $0.015/GB/month | **FREE** | 10GB storage |
| **AWS S3** | $0.023/GB/month | $0.09/GB | 5GB (12 months) |
| **DigitalOcean** | $5/month | Included (1TB) | - |
| **Uploadcare** | $25/month | $0.10/GB | 3GB + 10GB traffic |

**💰 For 100GB repositories:**
- Cloudflare R2: **$1.50/month**
- AWS S3: **$2.30/month** + transfer fees
- DigitalOcean: **$5/month** (fixed)
- Uploadcare: **$25/month**

## Cleanup Strategy

Repositories are automatically cleaned up after 24 hours from local disk:

```env
REPO_CLEANUP_MAX_AGE_HOURS=24
```

To run manual cleanup:
```bash
python backend/scripts/cleanup_repos.py
```

**Cron job (every 6 hours):**
```cron
0 */6 * * * /usr/bin/python3 /var/www/aura/backend/scripts/cleanup_repos.py
```

## Testing Storage

Test your storage configuration:

```bash
python -c "
from core.storage.storage_service import StorageService
import tempfile, os

storage = StorageService()

# Create test directory
test_dir = tempfile.mkdtemp()
with open(os.path.join(test_dir, 'test.txt'), 'w') as f:
    f.write('Hello AURA')

# Upload
url = storage.upload_repository(test_dir, 999, 'test-repo')
print(f'Uploaded to: {url}')

# Download
download_dir = tempfile.mkdtemp()
storage.download_repository(url, download_dir)
print(f'Downloaded to: {download_dir}')

# Cleanup
storage.delete_repository('repos/candidate_999_test-repo')
print('Cleanup complete')
"
```

## Best Practices

1. **Use Cloudflare R2 for production** - zero egress fees
2. **Enable `DELETE_LOCAL_AFTER_UPLOAD=true`** - save disk space
3. **Set up bucket lifecycle rules** - auto-delete old repos after 30 days
4. **Use CDN URL** - faster repository access
5. **Monitor storage costs** - set up billing alerts

## Troubleshooting

**"Failed to upload to S3":**
- Check credentials are correct
- Verify bucket exists
- Check IAM permissions (PutObject, GetObject, DeleteObject)

**"Download timeout":**
- Large repositories may take time
- Increase timeout in `storage_service.py`
- Consider using CDN

**"Out of disk space":**
- Enable `DELETE_LOCAL_AFTER_UPLOAD=true`
- Run cleanup script more frequently
- Reduce `REPO_CLEANUP_MAX_AGE_HOURS`

## Integration with AURA

The storage service is automatically integrated with the GitHub service. When a repository is cloned:

1. Repository is cloned to local temporary directory
2. If cloud storage is configured, repository is uploaded
3. If `DELETE_LOCAL_AFTER_UPLOAD=true`, local copy is removed
4. Cleanup job removes old local repos based on `REPO_CLEANUP_MAX_AGE_HOURS`

No code changes required - just configure environment variables!
