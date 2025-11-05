# AWS Amplify Deployment Guide

This guide walks you through deploying this store to AWS Amplify.

## ✅ Pre-Deployment Checklist

- [x] Production build tested successfully
- [x] Amplify configuration file created (`amplify.yml`)
- [x] Vite build optimized for production
- [x] All dependencies installed correctly

## 🚀 Deployment Steps

### Step 1: Push Code to GitHub

First, ensure your code is committed and pushed to GitHub:

```bash
# Check current status
git status

# Stage all changes
git add .

# Commit changes
git commit -m "Prepare for AWS Amplify deployment"

# Push to GitHub
git push origin main
```

### Step 2: Create AWS Amplify App

1. **Log in to AWS Console**
   - Go to: https://console.aws.amazon.com/
   - Navigate to AWS Amplify service

2. **Create New App**
   - Click "New app" → "Host web app"
   - Choose "GitHub" as your source

3. **Authorize GitHub**
   - Click "Authorize" to connect your GitHub account
   - Grant permissions for Amplify to access your repositories

4. **Select Repository**
   - Choose your repository (Store)
   - Select branch: `main`
   - Click "Next"

5. **Build Settings** (Auto-detected via `amplify.yml`)
   - Amplify will automatically detect the configuration file
   - Verify the build settings:
     ```yaml
     Build settings:
     - Node version: 18.x (or latest)
     - Build command: npm run build
     - Output directory: dist
     ```

6. **Review and Deploy**
   - Click "Save and deploy"
   - Wait for first deployment (5-8 minutes)

### Step 3: Configure Environment Variables

Currently, no environment variables are required. If you add features that need them:

1. Go to Amplify Console → Your App → Environment variables
2. Add variables as needed:
   - Example: `VITE_API_URL=https://api.example.com`

### Step 4: Custom Domain (Optional)

To add a custom domain:

1. In Amplify Console → Domain management
2. Click "Add domain"
3. Enter your domain name
4. Follow DNS setup instructions
5. Wait for SSL certificate provisioning (~30 minutes)

## 📋 Deployment Configuration

### Build Configuration

The `amplify.yml` file contains:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

### Build Performance

- **Build time**: ~5-8 minutes
- **Build size**: ~550KB (gzipped: ~143KB)
- **Assets**: Optimized for production

## 🔍 Post-Deployment Checklist

- [ ] Test all routes work correctly
- [ ] Verify product images load
- [ ] Test search functionality
- [ ] Check mobile responsiveness
- [ ] Verify dark mode toggle
- [ ] Test affiliate links open correctly

## 🐛 Troubleshooting

### Build Fails

**Issue**: Build fails with dependency errors
- **Solution**: Check that all dependencies are in `package.json`

**Issue**: Build succeeds but app doesn't load
- **Solution**: Verify `baseDirectory` in `amplify.yml` is `dist`

**Issue**: 404 errors on refresh
- **Solution**: This is normal for SPA. Amplify handles it with redirects.

### Performance Issues

**Issue**: Slow load times
- **Solution**: Images are large. Consider enabling Amplify CDN or optimizing images

**Issue**: Build takes too long
- **Solution**: Caching is configured. First build is slower, subsequent builds are faster.

## 🔄 Continuous Deployment

Once deployed, any push to `main` branch will trigger automatic deployment:

1. Push code to GitHub
2. Amplify detects changes
3. Build starts automatically
4. Deploys to production (~5-8 minutes)

## 📊 Monitoring

### Build History

- View in Amplify Console → App → Build history
- See build logs, duration, and status
- Click any build to see detailed logs

### Access Logs

- Amplify Console → Your App → Monitoring
- View access patterns and errors

## 💰 Cost Estimate

**AWS Amplify Pricing** (as of 2025):
- **Free Tier**: 1,000 build minutes/month
- **Storage**: 5GB included
- **Bandwidth**: 15GB/month included
- **Custom domains**: Free SSL certificates

**Your Usage**:
- Builds: ~8 minutes per deployment
- Storage: ~10-50MB
- **Estimated Cost**: **$0/month** (within free tier)

## 🎯 Next Steps

1. **Analytics**: Add Google Analytics or Amplify Analytics
2. **Performance**: Enable CDN for faster image delivery
3. **Security**: Configure custom headers in Amplify
4. **Backup**: Set up automated backups if needed

## 📞 Support

- **AWS Amplify Docs**: https://docs.aws.amazon.com/amplify/
- **AWS Support**: https://console.aws.amazon.com/support/
- **GitHub Issues**: Check your repository for known issues

## 🔗 Important Links

- **Amplify Console**: https://console.aws.amazon.com/amplify/
- **Your App**: (Will be provided after deployment)
- **GitHub Repository**: (Your repository URL)

## ✅ Deployment Complete!

Once deployed, you'll receive:
- A production URL (e.g., `https://main.xxxxxx.amplifyapp.com`)
- SSL certificate (automatic)
- Custom domain support
- Auto-deploy on git push

**Congratulations! Your store is now live! 🎉**




