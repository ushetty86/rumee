# DEPLOYMENT GUIDE

## Deployment Overview

Rumee can be deployed to various platforms. Here's how to deploy both backend and frontend.

## Backend Deployment

### Option 1: Heroku (Recommended for beginners)

1. **Create Heroku Account**
   - Sign up at https://www.heroku.com
   - Install Heroku CLI

2. **Prepare Backend**
   ```bash
   cd backend
   
   # Create .env.production
   cp .env.example .env.production
   # Update with production values
   ```

3. **Deploy**
   ```bash
   # Initialize Heroku app
   heroku login
   heroku create rumee-api
   
   # Add MongoDB Atlas URI
   heroku config:set MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/rumee
   heroku config:set OPENAI_API_KEY=your_key_here
   heroku config:set JWT_SECRET=your_secret_here
   
   # Deploy
   git push heroku main
   
   # View logs
   heroku logs --tail
   ```

### Option 2: AWS EC2

1. **Create EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Configure security groups (ports 80, 443, 5000)

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Node.js
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install nodejs -y
   
   # Install Git
   sudo apt install git -y
   ```

3. **Deploy Application**
   ```bash
   git clone your-repo-url
   cd rumee/backend
   npm install
   
   # Create .env with production values
   nano .env
   
   # Build
   npm run build
   
   # Run with PM2
   npm install -g pm2
   pm2 start dist/index.js --name rumee-api
   pm2 startup
   pm2 save
   ```

### Option 3: DigitalOcean App Platform

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Create App on DigitalOcean**
   - Connect GitHub repo
   - Select backend directory as root
   - Set environment variables
   - Deploy

## Frontend Deployment

### Option 1: Vercel (Recommended)

1. **Connect GitHub**
   ```bash
   # Push code to GitHub first
   git push origin main
   ```

2. **Deploy on Vercel**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Configure project:
     - Framework: Next.js (or React)
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `build`

3. **Set Environment Variables**
   - Add `REACT_APP_API_URL` → your backend URL
   - Redeploy

### Option 2: Netlify

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**
   - Go to https://netlify.com
   - Drag and drop `build` folder
   - Or connect GitHub for auto-deployment

3. **Set Environment Variables**
   - In Netlify dashboard: Site Settings > Build & Deploy
   - Add `REACT_APP_API_URL`

### Option 3: AWS S3 + CloudFront

1. **Build**
   ```bash
   cd frontend
   npm run build
   ```

2. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://rumee-app
   ```

3. **Upload Build**
   ```bash
   aws s3 sync build/ s3://rumee-app
   ```

4. **Setup CloudFront**
   - Create distribution pointing to S3
   - Set custom domain if desired

## Database Deployment

### MongoDB Atlas (Recommended)

1. **Create Account**
   - Go to https://cloud.mongodb.com
   - Sign up free

2. **Create Cluster**
   - Choose cloud provider and region
   - Create cluster

3. **Get Connection String**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/rumee
   ```

4. **Update Environment**
   - Set MONGODB_URI in production environment

## Domain & SSL

### Custom Domain

1. **Purchase Domain**
   - Use GoDaddy, Namecheap, etc.

2. **Point to Deployment**
   - Update DNS records to point to your hosting
   - Most platforms handle SSL automatically

### Certbot for Self-Hosted

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --standalone -d yourdomain.com
```

## Environment Configuration

### Production Environment Variables

**Backend (.env.production)**
```
NODE_ENV=production
PORT=5000
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/rumee
JWT_SECRET=your_strong_secret_here
OPENAI_API_KEY=sk-...
CORS_ORIGIN=https://yourdomain.com
LOG_LEVEL=info
```

**Frontend (.env.production)**
```
REACT_APP_API_URL=https://api.yourdomain.com
```

## Post-Deployment Checklist

- [ ] Test all API endpoints
- [ ] Verify database connectivity
- [ ] Check SSL certificate is valid
- [ ] Test user authentication
- [ ] Verify file uploads if applicable
- [ ] Monitor error logs
- [ ] Setup error tracking (Sentry)
- [ ] Setup performance monitoring (New Relic)
- [ ] Configure backup strategy
- [ ] Setup CI/CD pipeline

## Continuous Integration/Deployment (CI/CD)

### GitHub Actions Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: npm install
      
      - name: Build backend
        run: npm run build --workspace=backend
      
      - name: Build frontend
        run: npm run build --workspace=frontend
      
      - name: Deploy to Heroku
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
        run: |
          git push https://heroku:$HEROKU_API_KEY@git.heroku.com/rumee-api.git main
```

## Monitoring & Maintenance

### Error Tracking

**Setup Sentry**:
```bash
npm install @sentry/node

# Add to backend/src/index.ts
import * as Sentry from "@sentry/node";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

### Performance Monitoring

**Setup New Relic**:
```bash
npm install newrelic

# Create newrelic.js with configuration
```

### Logging

**View Logs**:
```bash
# Heroku
heroku logs --tail

# AWS
tail -f /var/log/pm2.log

# Check application logs
pm2 logs rumee-api
```

## Scaling Strategies

### When Your App Grows

1. **Database Optimization**
   - Add indexes
   - Archive old data
   - Consider sharding

2. **Caching**
   - Add Redis for session/cache
   - Cache frequently accessed data

3. **Load Balancing**
   - Use multiple app instances
   - Add reverse proxy (nginx)

4. **Content Delivery**
   - Use CDN for frontend
   - Optimize images

## Backup Strategy

### Database Backups

**MongoDB Atlas**:
- Automatic backups included
- Manual backup via MongoDB Compass

**Manual Backup**:
```bash
mongodump --uri "mongodb+srv://..." --out ./backup
```

### Regular Backups
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * mongodump --uri "..." --out /backups/$(date +\%Y-\%m-\%d)
```

## Disaster Recovery

### Restore from Backup
```bash
mongorestore --uri "mongodb+srv://..." ./backup
```

## Version Management

Use semantic versioning for releases:
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

## Performance Tips

1. **Enable Gzip Compression**
   ```typescript
   import compression from 'compression';
   app.use(compression());
   ```

2. **Add Request Caching**
   - Cache API responses
   - Use Redis for session data

3. **Optimize Database Queries**
   - Use proper indexes
   - Avoid N+1 queries
   - Paginate large results

4. **Monitor Resource Usage**
   - Track CPU usage
   - Monitor memory
   - Watch database connections

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using Mongoose)
- [ ] XSS protection
- [ ] Rate limiting enabled
- [ ] Secrets not in version control
- [ ] Regular dependency updates
- [ ] Firewall rules configured

## Support & Documentation

For additional help:
- Check provider documentation
- Review error logs
- Test locally first before deploying
- Gradual rollout for large changes
