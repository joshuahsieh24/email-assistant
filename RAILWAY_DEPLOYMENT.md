# Railway Deployment Guide

## Prerequisites
- Railway account (free tier available)
- GitHub repository access

## Step 1: Deploy to Railway

### Option A: Railway Web Interface (Easiest)
1. Go to [Railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository: `joshuahsieh24/email-assistant`
6. Railway will automatically detect the configuration and deploy

### Option B: Railway CLI (Alternative)
```bash
# Install Railway CLI (if not already installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to your project directory
cd /path/to/email-assistant

# Initialize Railway project
railway init

# Deploy
railway up
```

## Step 2: Configure Environment Variables

Once deployed, go to your Railway project dashboard:

1. Click on your project
2. Go to **"Variables"** tab
3. Add these environment variables:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `JWT_SECRET_KEY` = your JWT secret key

## Step 3: Get Your Railway URL

After deployment, Railway will provide you with a URL like:
`https://your-app-name.railway.app`

## Step 4: Update Salesforce Configuration

Update your Salesforce Apex code to use the Railway URL:

```apex
// In AIEmailService.cls, update the endpoint:
req.setEndpoint('https://your-app-name.railway.app/v1/chat/completions');
```

## Step 5: Test the Deployment

1. Visit: `https://your-app-name.railway.app/healthz`
2. Should return: `{"status": "healthy", "timestamp": "..."}`

## Monitoring and Logs

- **Logs**: Railway Dashboard → Your Project → "Deployments" tab
- **Metrics**: Railway Dashboard → Your Project → "Metrics" tab
- **Variables**: Railway Dashboard → Your Project → "Variables" tab

## Railway Benefits

✅ **Free Tier**: 500 hours/month free
✅ **Automatic HTTPS**: SSL certificates included
✅ **Global CDN**: Fast worldwide access
✅ **Auto-deploy**: Deploys on every GitHub push
✅ **Easy scaling**: Upgrade plan as needed

## Troubleshooting

### Common Issues:
1. **Build fails**: Check that `requirements.txt` exists in `openai_gateway/`
2. **Port issues**: Railway automatically sets `$PORT` environment variable
3. **Environment variables**: Make sure to set them in Railway dashboard

### Railway CLI Commands:
```bash
# Check status
railway status

# View logs
railway logs

# Set variables
railway variables --set "KEY=value"

# Redeploy
railway up
```

## Next Steps

Once deployed successfully:
1. Test the health endpoint
2. Update Salesforce with the Railway URL
3. Test email generation in your Salesforce org
4. Monitor logs for any issues 