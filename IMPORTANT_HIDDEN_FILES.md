# ⚠️ IMPORTANT: Hidden Files (.streamlit directory)

## 🔍 The `.streamlit` Directory is Hidden!

The `.streamlit` directory **exists** but is **hidden** because it starts with a dot (`.`).

### ✅ It's There!
The directory is located at:
```
deploy_hf/.streamlit/config.toml
```

---

## 👀 How to See Hidden Files

### In Finder (macOS):
1. Press `Cmd + Shift + .` (period) to toggle hidden files
2. Or use Terminal: `ls -la`

### In VS Code / Cursor:
1. Go to Settings
2. Search for "files.exclude"
3. Make sure `.streamlit` is NOT in the exclude list
4. Or use: `Cmd + Shift + P` → "Files: Toggle Excluded Files"

### In Terminal:
```bash
cd deploy_hf
ls -la          # Shows hidden files
ls -la .streamlit/  # Shows contents
```

---

## 📤 Uploading to Hugging Face

### Option 1: Upload via Web Interface
When uploading files to Hugging Face Spaces:
- **You MUST upload the `.streamlit` directory**
- It may not be visible in some file browsers
- Use "Show hidden files" option if available
- Or upload via Git/GitHub

### Option 2: Upload via Git (Recommended)
If you're using Git to push to Hugging Face:
```bash
cd deploy_hf
git add .streamlit/
git commit -m "Add Streamlit config"
git push
```

### Option 3: Manual Upload
1. Create `.streamlit` folder in Hugging Face Space
2. Upload `config.toml` inside it
3. Make sure the path is: `.streamlit/config.toml`

---

## ✅ Verification

To verify the file exists:
```bash
cd /Users/Vee/workspace/cybersecurity-multi-agent-system/deploy_hf
ls -la .streamlit/
cat .streamlit/config.toml
```

You should see:
```
config.toml
```

---

## 📋 File Contents

The `.streamlit/config.toml` file contains:
```toml
[theme]
primaryColor = "#6B8E9F"
backgroundColor = "#1A1D29"
secondaryBackgroundColor = "#252836"
textColor = "#E8EAED"
font = "sans serif"

[server]
headless = true
enableXsrfProtection = false
# Port is set in Dockerfile CMD, don't specify here
```

---

## 🚨 Critical for Deployment

**The `.streamlit` directory is REQUIRED for the app to work!**

Without it:
- ❌ Theme won't work
- ❌ Server settings won't apply
- ❌ App may not start correctly

**Make sure to upload it!** ✅
