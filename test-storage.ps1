# Quick test script to check cloud storage status
Write-Host "`n=== AURA Cloud Storage Status ===" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/storage-status" -Method Get
    
    Write-Host "`n✓ API Response:" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    Write-Host "`nStorage Provider: " -NoNewline -ForegroundColor Yellow
    Write-Host $response.storage_provider -ForegroundColor White
    
    Write-Host "Cloud Storage: " -NoNewline -ForegroundColor Yellow
    $cloudStatus = if ($response.cloud_storage_enabled) { "ENABLED ✓" } else { "DISABLED (using local)" }
    $cloudColor = if ($response.cloud_storage_enabled) { "Green" } else { "Gray" }
    Write-Host $cloudStatus -ForegroundColor $cloudColor
    
    Write-Host "Delete After Upload: " -NoNewline -ForegroundColor Yellow
    Write-Host $response.delete_after_upload -ForegroundColor White
    
    Write-Host "Cleanup Max Age: " -NoNewline -ForegroundColor Yellow
    Write-Host "$($response.cleanup_max_age_hours) hours" -ForegroundColor White
    
    Write-Host "`n$($response.message)" -ForegroundColor Cyan
    
    # Show provider-specific info
    if ($response.PSObject.Properties.Name -contains 'uploadcare_configured' -and $response.uploadcare_configured) {
        Write-Host "`n✓ Uploadcare Credentials: CONFIGURED" -ForegroundColor Green
        Write-Host "  Public Key: $($response.uploadcare_public_key)" -ForegroundColor Gray
    }
    
    if ($response.PSObject.Properties.Name -contains 's3_configured' -and $response.s3_configured) {
        Write-Host "`n✓ S3/R2 Credentials: CONFIGURED" -ForegroundColor Green
        Write-Host "  Bucket: $($response.s3_bucket)" -ForegroundColor Gray
        Write-Host "  Endpoint: $($response.s3_endpoint)" -ForegroundColor Gray
    }
    
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "`n✅ Cloud storage is working!" -ForegroundColor Green
}
catch {
    Write-Host "`n✗ Failed to connect to backend" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nMake sure the backend is running on http://localhost:8000" -ForegroundColor Yellow
    Write-Host "Run: .\start.ps1" -ForegroundColor Cyan
}

Write-Host ""
