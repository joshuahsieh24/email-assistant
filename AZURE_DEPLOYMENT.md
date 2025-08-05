# Azure App Service Deployment Guide

## Prerequisites
- Azure subscription
- Azure CLI installed
- GitHub repository access

## Step 1: Create Azure App Service

### Option A: Azure Portal (Easiest)
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "App Service" and select it
4. Click "Create"
5. Fill in the details:
   - **Resource Group**: Create new or use existing
   - **Name**: `openai-gateway`
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Choose closest to your users
   - **App Service Plan**: Basic B1 (or higher for production)
6. Click "Review + create" then "Create"

### Option B: Azure CLI
```bash
# Login to Azure
az login

# Create resource group
az group create --name openai-gateway-rg --location eastus

# Create App Service plan
az appservice plan create --name openai-gateway-plan --resource-group openai-gateway-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group openai-gateway-rg --plan openai-gateway-plan --name openai-gateway --runtime "PYTHON:3.11"
```

## Step 2: Configure Environment Variables

In Azure Portal:
1. Go to your App Service
2. Navigate to "Settings" → "Configuration"
3. Add these Application settings:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `JWT_SECRET_KEY` = your JWT secret key
   - `WEBSITES_PORT` = 8000

## Step 3: Deploy from GitHub

### Option A: GitHub Actions (Recommended)
1. In Azure Portal, go to "Deployment Center"
2. Choose "GitHub" as source
3. Connect your GitHub account
4. Select repository: `joshuahsieh24/email-assistant`
5. Select branch: `master`
6. Set build provider: "GitHub Actions"
7. Click "Save"

### Option B: Direct Deployment
```bash
# Get publish profile
az webapp deployment list-publishing-profiles --name openai-gateway --resource-group openai-gateway-rg

# Deploy using Azure CLI
az webapp deployment source config --name openai-gateway --resource-group openai-gateway-rg --repo-url https://github.com/joshuahsieh24/email-assistant --branch master --manual-integration
```

## Step 4: Update Salesforce Configuration

Once deployed, your Azure URL will be: `https://openai-gateway.azurewebsites.net`

Update your Salesforce Apex code to use this URL instead of localhost:

```apex
// In AIEmailService.cls, update the endpoint:
req.setEndpoint('https://openai-gateway.azurewebsites.net/v1/chat/completions');
```

## Step 5: Test the Deployment

1. Visit: `https://openai-gateway.azurewebsites.net/healthz`
2. Should return: `{"status": "healthy", "timestamp": "..."}`

## Monitoring and Logs

- **Application Logs**: Azure Portal → App Service → Logs → Application Logs
- **Metrics**: Azure Portal → App Service → Monitoring → Metrics
- **Health Checks**: Azure Portal → App Service → Monitoring → Health Check

## Security Best Practices

1. **Enable HTTPS**: Azure App Service provides free SSL certificates
2. **Network Security**: Configure IP restrictions if needed
3. **Authentication**: Consider adding Azure AD authentication
4. **Secrets Management**: Use Azure Key Vault for sensitive environment variables

## Scaling

- **Auto-scaling**: Configure in Azure Portal → App Service → Scale out
- **Manual scaling**: Change App Service Plan tier
- **Load balancing**: Multiple instances automatically load balanced 