# Deployment Guide - PVC Cut Calculator

## Local Development

### Start the app:
```bash
python -m streamlit run streamlit_app.py
```

The app opens at: `http://localhost:8501`

---

## Streamlit Cloud (Recommended - Free)

The easiest way to share with others:

### Steps:

1. **Push to GitHub** (if not already done):
```bash
git add .
git commit -m "Initial Streamlit MVP deployment"
git push origin main
```

2. **Sign up at**: https://streamlit.io/cloud

3. **Deploy**:
   - Click "New App"
   - Select your GitHub repository: `byywork1/PVC-Cut-Calculator`
   - Select branch: `main`
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

4. **Access your app**: 
   - Streamlit generates a public URL automatically
   - Share the URL with your team

### Updating after changes:
```bash
git push origin main
# Changes deploy automatically within 1 minute
```

---

## Self-Hosted Options

### Option 1: Run on Your Computer (Always On)

**Pros**: Free, easy
**Cons**: Computer must stay on

Install systemd/scheduler service to auto-start:

```bash
# Windows: Create scheduled task
# Or just pin `streamlit run streamlit_app.py` to startup
```

---

### Option 2: Heroku (Easy Cloud)

**Pros**: Free tier available (limited), auto-scaling
**Cons**: Sleeps after 30 min inactivity on free tier

**Setup**:
1. Install Heroku CLI
2. Create `Procfile`:
```
web: python -m streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

3. Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

### Option 3: PythonAnywhere (Easy)

**Pros**: Free tier, always on
**Cons**: Limited resources

1. Sign up at https://www.pythonanywhere.com
2. Upload files via web console
3. Create web app from Flask template (or configure WSGI)
4. Point to `streamlit_app.py`

---

### Option 4: Docker (For Teams)

**Create `Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and run**:
```bash
docker build -t pvc-calc .
docker run -p 8501:8501 pvc-calc
```

---

## Environment Variables (For Security)

If you need to hide database paths or add credentials:

1. Create `.streamlit/secrets.toml`:
```toml
database_path = "/path/to/PVC Cut Database.xlsx"
```

2. In code:
```python
db_path = st.secrets.get("database_path", "data/PVC Cut Database .xlsx")
```

---

## Monitoring & Logs

### Streamlit Cloud:
- Logs visible in the web dashboard
- Automatic error notifications

### Self-hosted:
```bash
# View logs in real-time
python -m streamlit run streamlit_app.py --logger.level=debug
```

---

## Performance Tips

1. **Cache the loader** (already done with session state)
2. **Lazy load Excel** - only loads when app starts
3. **Optimize database** - ensure connectors are indexed

---

## Troubleshooting

### App won't start
```bash
# Clear cache
rm -rf .streamlit/cache/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database file not found
- Ensure `data/PVC Cut Database .xlsx` exists
- Check file path in `src/config.py`

### Port already in use
```bash
python -m streamlit run streamlit_app.py --server.port=8502
```

---

## Recommended: Streamlit Cloud

For a team or client, I recommend **Streamlit Cloud** because:
- ✅ Free hosting with custom domain option
- ✅ Automatic deploys from GitHub
- ✅ 1-click sharing with shareable URL
- ✅ Zero infrastructure management
- ✅ Built-in analytics and logs

**Get started**: https://streamlit.io/cloud
