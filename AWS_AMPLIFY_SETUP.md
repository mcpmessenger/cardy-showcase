# AWS Amplify Console Setup - Quick Guide

Follow these steps to deploy your store via AWS Amplify Console.

## 🎯 Quick Start (5 minutes)

### Option A: Deploy from GitHub (Recommended)

1. **Go to AWS Amplify Console**
   ```
   https://console.aws.amazon.com/amplify/home
   ```

2. **Click "New app" → "Host web app"**

3. **Connect GitHub**
   - Select "GitHub" as repository service
   - Click "Connect branch"
   - Authorize AWS to access your GitHub account
   - Select your repository: `Store`
   - Select branch: `main`
   - Click "Next"

4. **Build Settings** (Auto-detected)
   - Amplify will auto-detect `amplify.yml`
   - Verify settings:
     - App name: `Store` (or your choice)
     - Environment: `Production`
   - Click "Save and deploy"

5. **Wait for Deployment**
   - First deployment: ~5-8 minutes
   - You'll see build progress in real-time
   - Green checkmark = Success! ✅

6. **Access Your Live Site**
   - Click the generated URL (e.g., `https://main.xxxxxx.amplifyapp.com`)
   - **Done!** 🎉

### Option B: Deploy from Code

If you prefer to upload code directly (not recommended for ongoing updates):

1. Zip your code:
   ```bash
   # Exclude unnecessary files
   git archive -o store-deploy.zip HEAD
   ```

2. In Amplify Console:
   - Choose "Deploy without Git provider"
   - Upload the zip file
   - Click "Deploy"

## 📝 Build Settings Reference

Your app uses these settings (auto-detected):

| Setting | Value |
|---------|-------|
| **Build image** | Amazon Linux 2023 |
| **Node version** | 18.x |
| **Build command** | `npm run build` |
| **Output directory** | `dist` |
| **Cache** | `node_modules/**/*` |

## ⚙️ Environment Variables

**Currently**: No environment variables needed.

If you add features later:

1. Go to **App settings → Environment variables**
2. Click "Manage variables"
3. Add key-value pairs:
   ```
   VITE_API_URL=https://api.example.com
   VITE_APP_NAME=My Store
   ```

## 🔗 Custom Domain (Optional)

### Option 1: Amplify Domain (Free)

1. Go to **Domain management**
2. Click "Add domain"
3. Choose a subdomain (e.g., `store-123.amplifyapp.com`)
4. It's free and includes SSL!

### Option 2: Your Own Domain

1. Purchase domain from:
   - Route 53 (AWS)
   - GoDaddy
   - Namecheap
   - Any registrar

2. Add domain to Amplify:
   - Go to **Domain management**
   - Click "Add domain"
   - Enter your domain (e.g., `mystore.com`)

3. Configure DNS:
   - Amplify will provide DNS records
   - Add them to your domain registrar
   - Wait 15-60 minutes for propagation

4. SSL Certificate:
   - **Automatic** - Amplify provisions SSL for free
   - Wait ~30 minutes for certificate to activate

## 🔍 Verify Deployment

After deployment, test these:

- [ ] Homepage loads correctly
- [ ] Products page shows all 108 products
- [ ] Search works
- [ ] Images load properly
- [ ] Category filters work
- [ ] Dark mode toggle works
- [ ] Mobile responsive
- [ ] Affiliate links open correctly

## 🚀 Automatic Deployments

**Once set up**, every push to `main` triggers auto-deploy:

1. Push code to GitHub
2. Amplify detects changes
3. Build starts automatically
4. Deploys in ~5 minutes

**No action needed from you!**

## 📊 Monitoring Your App

### View Logs

1. Go to your app in Amplify Console
2. Click **"Build history"** or **"Access logs"**
3. See real-time build progress
4. Check for errors

### Performance Metrics

1. Go to **Monitoring** tab
2. View:
   - Build duration
   - Deployment frequency
   - Success/failure rates

## 💰 Cost Breakdown

### Free Tier Includes:
- ✅ 1,000 build minutes/month
- ✅ 5 GB storage
- ✅ 15 GB bandwidth/month
- ✅ SSL certificates
- ✅ Custom domains
- ✅ Global CDN

### Your Usage (Estimated):
- **Builds**: ~8 min/deployment × 20 builds/month = 160 min ✓
- **Storage**: 10-50 MB ✓
- **Bandwidth**: < 15 GB ✓

**Cost: $0/month** (within free tier) 🎉

## 🐛 Common Issues

### "Build Failed"

**Check**:
1. Build logs in Amplify Console
2. Node version compatibility
3. Missing dependencies

**Fix**:
```bash
# Make sure package.json is complete
npm install
npm run build
```

### "404 on Refresh"

**Normal**: Single Page App behavior
**Fix**: Amplify auto-redirects already configured

### "Images Not Loading"

**Check**:
1. Image paths in `public/` folder
2. CDN caching

### "SSL Error"

**Wait**: SSL takes 15-60 minutes to provision
**Check**: Domain DNS records configured correctly

## 📞 Need Help?

### Resources:
- **AWS Amplify Docs**: https://docs.aws.amazon.com/amplify/
- **Amplify Console**: https://console.aws.amazon.com/amplify/
- **AWS Support**: https://console.aws.amazon.com/support/

### Community:
- AWS Amplify Forum
- Stack Overflow (tag: aws-amplify)
- GitHub Issues

## ✅ Success Checklist

- [ ] App deployed successfully
- [ ] URL works in browser
- [ ] SSL certificate active
- [ ] All features functional
- [ ] Auto-deploy enabled
- [ ] Monitoring set up

## 🎉 You're Live!

Your store is now deployed and accessible to the world!

**Next steps**:
1. Share your URL
2. Drive traffic
3. Monitor analytics
4. Iterate and improve

**Congratulations!** 🚀


