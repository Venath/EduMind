# EduMind CI/CD Setup - Strategy 2

**Industry-Standard Hybrid Approach: GitHub Actions + Jenkins for Azure Deployment**

## 📋 Table of Contents

- [Overview](#overview)
- [Strategy 2 Architecture](#strategy-2-architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [GitHub Actions Setup](#github-actions-setup)
- [Jenkins Setup](#jenkins-setup)
- [Azure Configuration](#azure-configuration)
- [Deployment Flow](#deployment-flow)
- [Troubleshooting](#troubleshooting)
- [Cost Estimation](#cost-estimation)

---

## 🎯 Overview

This project uses **Strategy 2** - a hybrid CI/CD approach that combines GitHub Actions for fast PR validation with Jenkins for production-grade Azure deployments.

### Why Strategy 2?

- ✅ **Industry Standard**: Used by 70%+ Fortune 500 companies
- ⚡ **Fast Feedback**: 2-3 min PR validation vs 15-20 min full pipeline
- 💰 **Cost-Effective**: ~$30-50/month vs $200+/month for GitHub Actions enterprise
- 🔒 **Production Control**: Manual approval gates for production deployments
- 🐳 **Azure Optimized**: Native Azure CLI integration, ACR support

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Developer Workflow                        │
└─────────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Pull Request      │
                    │   (Feature Branch)  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │     GitHub Actions - PR Validation          │
        │  • Code quality (Black, isort, Flake8)     │
        │  • Security scan (Safety, Bandit)          │
        │  • Unit tests (pytest)                     │
        │  ⏱️  Duration: 2-3 minutes                  │
        └──────────────────────┬──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Merge to Branch   │
                    │   (main/develop)    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │     GitHub Actions - Trigger Jenkins        │
        │  • Detect changed services                  │
        │  • Call Jenkins webhook                     │
        │  ⏱️  Duration: <1 minute                     │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │         Jenkins - Build & Deploy            │
        │  • Build Docker images                      │
        │  • Security scan (Trivy)                   │
        │  • Push to Azure Container Registry        │
        │  • Deploy to staging                       │
        │  • Integration tests                       │
        │  • [Manual approval for prod]              │
        │  • Deploy to production                    │
        │  ⏱️  Duration: 10-15 minutes                │
        └─────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### Required Accounts & Services

1. **Azure Account**
   - Active subscription with contributor access
   - Resource group created (`edumind-rg`)
   - Service principal with deployment permissions

2. **Azure Container Registry (ACR)**
   - Created and accessible
   - Admin user enabled
   - ~$5/month for Basic tier

3. **Azure Container Apps**
   - Environment created for staging and production
   - Container App created for each service

4. **GitHub Repository**
   - Admin access to configure secrets and webhooks
   - Actions enabled

5. **Jenkins Server**
   - Self-hosted (Azure VM recommended) or local Docker setup
   - Min specs: 2 vCPU, 4 GB RAM
   - ~$30/month for Azure VM B2s

### Required Tools (Local Development)

```bash
# Docker & Docker Compose
docker --version  # 20.10+
docker-compose --version  # 1.29+

# Azure CLI
az --version  # 2.40+

# Git
git --version  # 2.30+
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/edumind.git
cd edumind
```

### 2. Configure Azure Resources

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Create resource group (if not exists)
az group create --name edumind-rg --location eastus

# Create Azure Container Registry
az acr create \
  --resource-group edumind-rg \
  --name edumindacr \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
az acr credential show --name edumindacr
```

### 3. Create Azure Service Principal

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "edumind-deploy" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/edumind-rg \
  --sdk-auth

# Save the output JSON - you'll need it for credentials
```

### 4. Setup Jenkins

#### Option A: Docker Compose (Recommended for Local/Testing)

```bash
cd jenkins

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start Jenkins
docker-compose up -d

# Check logs
docker-compose logs -f jenkins

# Access Jenkins at http://localhost:8080
```

#### Option B: Azure VM (Production)

```bash
# Create Azure VM for Jenkins
az vm create \
  --resource-group edumind-rg \
  --name jenkins-server \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard

# SSH into VM
ssh azureuser@<vm-public-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Copy jenkins folder to VM
scp -r jenkins/ azureuser@<vm-public-ip>:~/

# Start Jenkins
cd jenkins
docker-compose up -d
```

### 5. Configure GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

```
JENKINS_URL=http://your-jenkins-server:8080
JENKINS_USER=admin
JENKINS_TOKEN=your-jenkins-api-token
JENKINS_BUILD_TOKEN=your-secure-build-token

ACR_NAME=edumindacr
ACR_USERNAME=edumindacr
ACR_PASSWORD=<from step 2>

AZURE_SUBSCRIPTION_ID=<from service principal>
AZURE_TENANT_ID=<from service principal>
AZURE_CLIENT_ID=<from service principal>
AZURE_CLIENT_SECRET=<from service principal>
```

### 6. Test the Pipeline

```bash
# Create a test branch
git checkout -b test/ci-cd-setup

# Make a small change to a service
echo "# Test change" >> backend/services/user-service/README.md

# Commit and push
git add .
git commit -m "test: CI/CD pipeline setup"
git push origin test/ci-cd-setup

# Create a pull request on GitHub
# ✅ GitHub Actions should run validation (~2-3 minutes)

# Merge the PR
# ✅ Jenkins deployment should trigger automatically
```

---

## 🔄 GitHub Actions Setup

### Workflows Overview

1. **`.github/workflows/ci-app.yml`** - PR Validation
   - Runs on: Pull requests to `main` or `develop`
   - Duration: 2-3 minutes
   - Actions:
     - Detect changed services
     - Code quality checks (Black, isort, Flake8)
     - Security scanning (Safety, Bandit)
     - Unit tests (pytest)
     - Post results as PR comment

2. **`.github/workflows/trigger-jenkins.yml`** - Deployment Trigger
   - Runs on: Push to `main` or `develop`
   - Duration: <1 minute
   - Actions:
     - Detect changed services
     - Trigger Jenkins webhook with parameters
     - Post commit comment with Jenkins link

3. **`.github/workflows/ml-pipeline.yml`** - ML Model Training
   - Runs on: Changes to `ml/` directory
   - Duration: 5-20 minutes (depending on model)
   - Actions:
     - Train updated models
     - Validate model artifacts
     - Copy models to service directory
     - Trigger service deployment

### Manual Workflow Triggers

```bash
# Trigger deployment manually
gh workflow run trigger-jenkins.yml \
  -f services="user-service,course-service"

# Trigger ML training manually
gh workflow run ml-pipeline.yml \
  -f model_type="xai_predictor" \
  -f force_retrain=true
```

---

## 🏗️ Jenkins Setup

### Accessing Jenkins

1. Open browser: `http://your-jenkins-server:8080`
2. Login with credentials from `.env` file
3. Navigate to **EduMind Deploy** job

### Jenkins Configuration (Already Done via JCasC)

The `jenkins/jenkins.yaml` file automatically configures:

- ✅ Admin user and authentication
- ✅ Azure credentials
- ✅ ACR credentials
- ✅ GitHub token
- ✅ Job definitions
- ✅ Webhook triggers
- ✅ Required plugins

### Manual Jenkins Job Trigger

```bash
# Trigger Jenkins job manually
curl -X POST "http://your-jenkins-server:8080/job/edumind-deploy/buildWithParameters" \
  --user "admin:your-api-token" \
  --data-urlencode "BRANCH_NAME=develop" \
  --data-urlencode "GIT_COMMIT=$(git rev-parse HEAD)" \
  --data-urlencode "CHANGED_SERVICES=user-service,course-service" \
  --data-urlencode "TRIGGERED_BY=manual" \
  --data-urlencode "token=your-build-token"
```

### Getting Jenkins API Token

1. Login to Jenkins
2. Click your username (top right) → **Configure**
3. Scroll to **API Token** → **Add new Token**
4. Copy token and save to GitHub secrets as `JENKINS_TOKEN`

---

## ☁️ Azure Configuration

### Container Apps Environment

```bash
# Create Container Apps environment
az containerapp env create \
  --name edumind-env \
  --resource-group edumind-rg \
  --location eastus
```

### Create Container Apps (Per Service)

```bash
# Example: User Service
az containerapp create \
  --name edumind-user-service-staging \
  --resource-group edumind-rg \
  --environment edumind-env \
  --image edumindacr.azurecr.io/user-service:latest \
  --registry-server edumindacr.azurecr.io \
  --registry-username edumindacr \
  --registry-password "<acr-password>" \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars "ENVIRONMENT=staging"

# Production version
az containerapp create \
  --name edumind-user-service-prod \
  --resource-group edumind-rg \
  --environment edumind-env \
  --image edumindacr.azurecr.io/user-service:latest \
  --registry-server edumindacr.azurecr.io \
  --registry-username edumindacr \
  --registry-password "<acr-password>" \
  --target-port 8000 \
  --ingress external \
  --min-replicas 2 \
  --max-replicas 10 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars "ENVIRONMENT=production"
```

**Repeat for all services:**
- `course-service`
- `assessment-service`
- `service-xai-prediction`
- `service-learning-style`
- `service-engagement-tracker`

---

## 📊 Deployment Flow

### Detailed Step-by-Step Flow

#### 1. Developer Creates PR

```bash
git checkout -b feature/new-endpoint
# Make changes to backend/services/user-service/
git commit -m "feat: add new user endpoint"
git push origin feature/new-endpoint
# Create PR on GitHub
```

#### 2. GitHub Actions - PR Validation (ci-app.yml)

```
✅ Detect changed services: user-service
✅ Code quality checks: PASSED
✅ Security scan: PASSED
✅ Unit tests: 15/15 PASSED
✅ Comment on PR: "user-service validation success"
```

#### 3. PR Merged to Develop

```bash
# Reviewer approves and merges PR
```

#### 4. GitHub Actions - Trigger Jenkins (trigger-jenkins.yml)

```
✅ Detect changed services: user-service
✅ Call Jenkins webhook with parameters
✅ Comment on commit: "Jenkins deployment triggered"
```

#### 5. Jenkins Pipeline - Build & Deploy (backend/Jenkinsfile)

**Stage 1: Pipeline Info**
```
📋 Deployment Details:
├─ Branch: develop
├─ Commit: abc12345
├─ Services: user-service
└─ Target: STAGING
```

**Stage 2: Checkout**
```
🔄 Checking out branch: develop
✅ Code checked out
```

**Stage 3: Build Docker Images**
```
🐳 Building user-service...
✅ user-service image built
```

**Stage 4: Security Scan**
```
🔒 Scanning user-service...
✅ No critical vulnerabilities found
```

**Stage 5: Push to ACR**
```
📤 Pushing user-service to ACR...
✅ user-service:abc12345 pushed
✅ user-service:develop pushed
✅ user-service:latest pushed
```

**Stage 6: Deploy to Staging**
```
🚀 Deploying to STAGING...
🔄 Updating user-service in staging...
⏳ Waiting for stabilization...
✅ Health check passed (HTTP 200)
✅ Staging deployment complete!
```

**Stage 7: Integration Tests**
```
🧪 Running integration tests...
✅ Health endpoint: OK
✅ API endpoint: OK
✅ Integration tests passed
```

**Stage 8: Deploy to Production** (only for `main` branch)
```
🚨 MANUAL APPROVAL REQUIRED
[Wait for approval...]
🚀 Deploying to PRODUCTION...
✅ Production deployment complete!
```

---

## 🐛 Troubleshooting

### GitHub Actions Issues

#### "Jenkins webhook call failed"

**Symptoms:** trigger-jenkins.yml fails with HTTP error

**Solutions:**
1. Check Jenkins is accessible from GitHub (public URL required)
2. Verify `JENKINS_URL` secret is correct
3. Check `JENKINS_USER` and `JENKINS_TOKEN` are valid
4. Ensure `JENKINS_BUILD_TOKEN` matches Jenkins job configuration

```bash
# Test Jenkins accessibility
curl -I http://your-jenkins-server:8080/

# Test webhook manually
curl -X POST "http://your-jenkins-server:8080/job/edumind-deploy/buildWithParameters" \
  --user "admin:token" \
  --data-urlencode "BRANCH_NAME=develop"
```

#### "No services detected"

**Symptoms:** dorny/paths-filter doesn't detect changes

**Solutions:**
1. Verify file paths in `.github/workflows/ci-app.yml` match your structure
2. Check `fetch-depth: 0` is set in checkout step
3. Look at workflow logs for path filter output

```yaml
# Ensure paths are correct
filters: |
  user-service:
    - 'backend/services/user-service/**'  # Must match actual path
```

### Jenkins Issues

#### "Azure login failed"

**Symptoms:** Jenkins pipeline fails at Azure CLI commands

**Solutions:**
1. Verify Azure credentials in `jenkins/.env`
2. Check service principal has correct permissions
3. Test credentials manually:

```bash
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

#### "Docker build failed"

**Symptoms:** Image build fails in Jenkins

**Solutions:**
1. Check Dockerfile exists in service directory
2. Verify Docker socket is mounted: `/var/run/docker.sock`
3. Check Jenkins has Docker permissions:

```bash
# Inside Jenkins container
docker ps  # Should work without sudo
```

#### "ACR push failed"

**Symptoms:** Cannot push images to Azure Container Registry

**Solutions:**
1. Verify ACR credentials are correct
2. Check ACR admin user is enabled:

```bash
az acr update --name edumindacr --admin-enabled true
```

3. Test ACR login manually:

```bash
docker login edumindacr.azurecr.io \
  --username edumindacr \
  --password <password>
```

### Azure Container Apps Issues

#### "Container app not found"

**Symptoms:** Jenkins fails to update container app

**Solutions:**
1. Verify container app exists:

```bash
az containerapp list \
  --resource-group edumind-rg \
  --query "[].name" \
  -o tsv
```

2. Create if missing (see Azure Configuration section)

#### "Health check failed"

**Symptoms:** Deployment succeeds but health check returns non-200

**Solutions:**
1. Check service has `/health` endpoint implemented
2. Verify ingress configuration:

```bash
az containerapp show \
  --name edumind-user-service-staging \
  --resource-group edumind-rg \
  --query "properties.configuration.ingress"
```

3. Check container logs:

```bash
az containerapp logs show \
  --name edumind-user-service-staging \
  --resource-group edumind-rg \
  --tail 50
```

---

## 💰 Cost Estimation

### Monthly Costs (USD)

| Service | Tier | Monthly Cost | Notes |
|---------|------|--------------|-------|
| **Azure Container Registry** | Basic | ~$5 | 10 GB storage included |
| **Azure Container Apps** | Consumption | ~$10-20 | Pay-per-use, depends on traffic |
| **Jenkins VM** | Azure B2s | ~$30 | 2 vCPU, 4 GB RAM |
| **Total** | | **~$45-55** | Scales with usage |

### Cost Optimization Tips

1. **Use Azure Free Credits**
   - Students get $100/year with Azure for Students
   - Sign up: https://azure.microsoft.com/en-us/free/students/

2. **Container Apps Scaling**
   - Set `min-replicas: 0` for staging to scale to zero when idle
   - Saves ~$5-10/month

3. **Jenkins Alternatives**
   - Use GitHub Actions self-hosted runner (free)
   - Use Azure DevOps free tier (1800 min/month)

4. **ACR Optimization**
   - Clean up old images regularly
   - Use image retention policies

```bash
# Delete old images (keep last 5)
az acr repository show-tags \
  --name edumindacr \
  --repository user-service \
  --orderby time_desc \
  --output table

# Delete specific tag
az acr repository delete \
  --name edumindacr \
  --image user-service:old-tag
```

---

## 📚 Additional Resources

### Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/)

### Monitoring & Observability

- **Azure Monitor**: Track Container Apps performance
- **Azure Application Insights**: Detailed application telemetry
- **Jenkins Blue Ocean**: Better pipeline visualization

### Next Steps

1. ✅ Basic CI/CD pipeline working
2. ⏭️ Add comprehensive integration tests
3. ⏭️ Set up Azure Monitor and alerts
4. ⏭️ Configure automatic rollback on failed deployments
5. ⏭️ Add Slack/Teams notifications
6. ⏭️ Implement feature flags for safer deployments

---

## 🤝 Contributing

When modifying the CI/CD pipeline:

1. Test changes in a separate branch first
2. Use `workflow_dispatch` for manual testing
3. Update this documentation with any changes
4. Get approval before merging to `main`

---

## 📞 Support

Need help? Check:

1. **GitHub Actions logs**: Repository → Actions tab
2. **Jenkins logs**: Jenkins UI → Job → Console Output
3. **Azure logs**: Azure Portal → Container Apps → Logs
4. **Project issues**: GitHub Issues tab

---

**Last Updated:** 2024
**Maintained by:** EduMind Team
