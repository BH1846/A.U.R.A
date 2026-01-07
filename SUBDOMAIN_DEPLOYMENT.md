# AURA Subdomain Deployment Guide

## Deployment as aura.i-intern.com

AURA is deployed as a subdomain of I-Intern: **aura.i-intern.com**

### 1. Render.com Configuration

#### Custom Domain Setup:
1. Go to Render Dashboard → Your AURA service
2. Click "Settings" → "Custom Domains"
3. Add custom domain: `aura.i-intern.com`
4. Render will provide DNS records (CNAME or A record)

#### DNS Configuration (at your domain provider):
Add these records to `i-intern.com` DNS:

```
Type: CNAME
Name: aura
Value: <your-render-service>.onrender.com
TTL: 3600
```

Or if using A record:
```
Type: A
Name: aura
Value: <Render IP address>
TTL: 3600
```

### 2. Environment Variables

Set these in Render Dashboard → Environment:

```bash
# Database
DATABASE_URL=<your-neon-postgresql-url>

# LLM API
GROQ_API_KEY=<your-groq-api-key>

# Storage
STORAGE_PROVIDER=local
UPLOADCARE_PUBLIC_KEY=<your-key>
UPLOADCARE_SECRET_KEY=<your-secret>

# I-Intern Integration
JWT_SECRET=<same-as-i-intern-secret-key>
JWT_ALGORITHM=HS256

# CORS (automatically includes I-Intern domains)
# No manual setting needed - defaults in config.py handle it
```

### 3. I-Intern Integration URLs

Update I-Intern backend `.env`:
```bash
AURA_BASE_URL=https://aura.i-intern.com
AURA_JWT_SECRET=<same-as-secret-key>

# Add AURA to CORS
ALLOWED_ORIGINS=https://i-intern.com,https://www.i-intern.com,https://aura.i-intern.com
```

### 4. SSL Certificate

Render automatically provisions SSL certificates for custom domains.
- HTTPS will be enabled automatically
- Certificate auto-renewal is handled by Render

### 5. Verification

After DNS propagation (can take up to 48 hours, usually < 1 hour):

1. **Test Health Endpoint:**
   ```bash
   curl https://aura.i-intern.com/health
   ```

2. **Test Frontend:**
   Open in browser: https://aura.i-intern.com

3. **Test Integration:**
   From I-Intern, call:
   ```bash
   GET /api/v1/aura/student/aura/start/{application_id}
   ```
   Should return URL with `aura.i-intern.com`

### 6. Deployment Checklist

- [ ] Create Render service for AURA
- [ ] Add custom domain `aura.i-intern.com` in Render
- [ ] Configure DNS at domain provider
- [ ] Set environment variables in Render
- [ ] Update I-Intern backend with AURA_BASE_URL
- [ ] Update shared JWT_SECRET in both platforms
- [ ] Wait for DNS propagation
- [ ] Test HTTPS endpoint
- [ ] Test JWT token generation from I-Intern
- [ ] Test complete assessment flow

### 7. Architecture

```
i-intern.com (Main platform)
    ├── www.i-intern.com (Frontend)
    ├── api.i-intern.com or backend subdomain (Backend API)
    └── aura.i-intern.com (Skill Assessment Platform)
            ├── /student/dashboard (Student Portal)
            ├── /company/dashboard (Recruiter Portal)
            └── /api/* (AURA API Endpoints)
```

### 8. Cookie Domain Configuration

Since AURA is a subdomain, cookies can be shared:

**I-Intern Backend:**
```env
COOKIE_DOMAIN=.i-intern.com
```

**AURA Backend (future enhancement):**
```env
COOKIE_DOMAIN=.i-intern.com
```

This allows seamless authentication across:
- i-intern.com
- www.i-intern.com
- aura.i-intern.com

### 9. Monitoring

Check deployment status:
- **Render Dashboard:** https://dashboard.render.com
- **Domain Status:** https://dnschecker.org
- **SSL Certificate:** https://www.ssllabs.com/ssltest/

### 10. Troubleshooting

**DNS not resolving?**
- Check DNS propagation: `nslookup aura.i-intern.com`
- Wait longer (up to 48 hours)
- Verify DNS records are correct

**SSL errors?**
- Render provisions SSL automatically
- May take a few minutes after DNS resolves
- Check Render dashboard for SSL status

**CORS errors?**
- Verify CORS_ORIGINS includes I-Intern domains
- Check browser console for specific error
- Ensure credentials are included in requests

**JWT token invalid?**
- Verify JWT_SECRET matches between platforms
- Check token expiration
- Ensure JWT_ALGORITHM is HS256
