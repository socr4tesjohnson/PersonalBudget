# GitHub Actions CI/CD Pipeline

This project includes automated testing and deployment using GitHub Actions!

## 🚀 What's Automated

### 1. Continuous Testing (test.yml)
Runs on every push and pull request:
- ✅ Checks Python imports
- ✅ Tests Flask application
- ✅ Tests Budget Planner core functionality
- ✅ Validates API endpoints

### 2. Continuous Deployment (deploy.yml)
Runs when you push to `main` or `master`:
- ✅ Runs all tests first
- ✅ Triggers Render deployment
- ✅ Checks deployed app health
- ✅ Posts deployment summary

## 📋 Setup Instructions

### Basic Setup (Auto-Deploy via Render)

**Good news:** Render automatically deploys when you connect your GitHub repo! No extra setup needed.

1. Connect your repo to Render (see DEPLOY.md)
2. Render watches for pushes to your default branch
3. Auto-deploys on every push
4. GitHub Actions tests run in parallel

### Advanced Setup (Manual Deploy Trigger)

For more control, add Render webhook to GitHub Secrets:

#### Step 1: Get Render Deploy Hook

1. Go to your Render dashboard
2. Click on your service
3. Go to "Settings" tab
4. Scroll to "Deploy Hook"
5. Copy the webhook URL

#### Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"

Add these secrets:

**Secret 1: RENDER_DEPLOY_HOOK_URL**
- Name: `RENDER_DEPLOY_HOOK_URL`
- Value: (paste your Render deploy hook URL)

**Secret 2: RENDER_APP_URL** (optional)
- Name: `RENDER_APP_URL`
- Value: `https://your-app-name.onrender.com`

#### Step 3: Push to Trigger

```bash
git push origin main
```

Watch the magic happen in the "Actions" tab!

## 📊 Viewing Workflow Runs

1. Go to your GitHub repository
2. Click the "Actions" tab
3. See all workflow runs with status indicators
4. Click any run to see detailed logs

## 🔧 Workflow Files

### `.github/workflows/test.yml`
- Runs on: All pushes and pull requests
- Purpose: Validate code before merging
- Duration: ~1-2 minutes

### `.github/workflows/deploy.yml`
- Runs on: Pushes to main/master
- Purpose: Deploy to production
- Duration: ~2-3 minutes (+ deployment time)

## 🎯 Workflow Triggers

### Automatic Triggers
- Push to any branch → Runs tests
- Push to main/master → Runs tests + deploy
- Pull request → Runs tests

### Manual Triggers
You can manually trigger deployment:
1. Go to "Actions" tab
2. Select "Deploy to Render"
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

## ✅ What Gets Tested

### Import Tests
```python
✓ Flask app imports
✓ Budget planner imports
✓ All dependencies available
```

### Flask Tests
```python
✓ App creation
✓ Home page loads
✓ Health endpoint works
✓ API endpoints respond
```

### Core Functionality Tests
```python
✓ Budget creation
✓ Adding budget items
✓ Transaction generation
✓ Balance forecasting
```

## 🚨 Troubleshooting

### Tests Failing?

**Check the logs:**
1. Go to Actions tab
2. Click the failed workflow
3. Click the failing job
4. Expand the failing step

**Common issues:**
- Import errors → Check requirements.txt
- Test failures → Check code changes
- Timeout → Increase wait time in workflow

### Deploy Not Triggering?

**Checklist:**
- ✓ Pushed to main/master branch?
- ✓ Secrets configured correctly?
- ✓ Deploy hook URL is valid?
- ✓ Render service is active?

**Debug steps:**
1. Check Actions tab for workflow run
2. Look for deploy job (only runs on main/master)
3. Check Render dashboard for deployment

### Manual Deploy

If auto-deploy fails, manually deploy:
```bash
# Trigger via webhook
curl -X POST "$RENDER_DEPLOY_HOOK_URL"

# Or push a change
git commit --allow-empty -m "Trigger deploy"
git push origin main
```

## 🎨 Customizing Workflows

### Change Deploy Branch

Edit `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches:
      - main        # Change this
      - production  # Add more branches
```

### Add More Tests

Edit `.github/workflows/test.yml`:
```yaml
- name: My Custom Test
  run: |
    python -m pytest tests/  # If you add pytest
```

### Change Python Version

Both workflows use Python 3.11. To change:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'  # Change version
```

## 📈 Status Badges

Add to your README.md:

```markdown
![Deploy](https://github.com/USERNAME/PersonalBudget/actions/workflows/deploy.yml/badge.svg)
![Tests](https://github.com/USERNAME/PersonalBudget/actions/workflows/test.yml/badge.svg)
```

Replace `USERNAME` with your GitHub username.

## 🔐 Security Notes

- Never commit secrets to code
- Use GitHub Secrets for sensitive data
- Deploy hooks are like passwords - keep them safe
- Regenerate hooks if accidentally exposed

## 💡 Benefits

### For You
- 🚀 Automatic deployments
- 🧪 Catch bugs before production
- 📊 Clear deployment history
- ⏱️ Save time

### For Collaborators
- ✅ PR tests before merge
- 🔍 See test results inline
- 🤝 Confidence in changes
- 📝 Deployment tracking

## 🎓 Next Steps

1. **Push code** → Watch tests run
2. **Merge PR** → Watch deployment happen
3. **Check Actions tab** → See workflow history
4. **Add status badges** → Show build status

---

**Your code is now fully automated! Every push is tested and deployed automatically.** 🎉
