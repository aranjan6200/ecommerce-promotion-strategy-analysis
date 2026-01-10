# GitHub Setup Guide

## Quick Setup Steps

### Step 1: Initialize Git Repository (if not already done)

```bash
cd /Users/vishwa/Desktop/commerceIQ
git init
```

### Step 2: Add Files to Git

```bash
# Add all files (except those in .gitignore)
git add .

# Or add specific files:
git add README.md
git add analysis_notebook.py
git add CommerceIQ_Analysis.ipynb
git add Supporting_Document.md
git add requirements.txt
git add .gitignore
git add outputs/
```

### Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: CommerceIQ E-commerce Price Elasticity Analysis

- Complete analysis notebook and Jupyter notebook
- Supporting document with findings
- Visualizations and output data
- Requirements and documentation"
```

### Step 4: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name it: `commerceIQ-price-elasticity-analysis` (or your preferred name)
5. Choose Public or Private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### Step 5: Connect Local Repository to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/commerceIQ-price-elasticity-analysis.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/commerceIQ-price-elasticity-analysis.git
```

### Step 6: Push to GitHub

```bash
# Push to main branch (or master, depending on your default)
git branch -M main
git push -u origin main
```

## What's Included in .gitignore

The `.gitignore` file will exclude:
- Python cache files (`__pycache__/`)
- Virtual environments (`venv/`, `env/`)
- IDE settings (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`)
- Temporary files

**Note:** The data file (`ecom-elasticity-data1.tsv`) and `outputs/` folder are **NOT** in .gitignore by default. If your repository gets too large, you can:

1. **Option A:** Keep them (good for sharing the complete project)
2. **Option B:** Add them to .gitignore (recommended if file is very large)

To exclude the data file and outputs, uncomment these lines in `.gitignore`:
```
# outputs/
# ecom-elasticity-data1.tsv
```

## Recommended Repository Structure for GitHub

```
commerceIQ-price-elasticity-analysis/
├── .gitignore
├── README.md                          ✅ Include
├── requirements.txt                   ✅ Include
├── analysis_notebook.py               ✅ Include
├── CommerceIQ_Analysis.ipynb          ✅ Include
├── Supporting_Document.md             ✅ Include
├── SUBMISSION_CHECKLIST.md            ✅ Include (optional)
├── ecom-elasticity-data1.tsv          ⚠️ Optional (large file)
├── outputs/                           ⚠️ Optional (can regenerate)
│   ├── *.png                          ⚠️ Optional (visualizations)
│   └── *.csv                          ⚠️ Optional (can regenerate)
└── GITHUB_SETUP.md                    ❌ Delete after setup (or keep for reference)
```

## If Your Repository is Too Large

GitHub has a 100MB file size limit. If `ecom-elasticity-data1.tsv` is too large:

1. Use Git LFS (Large File Storage):
```bash
# Install git-lfs
brew install git-lfs  # macOS
# or download from https://git-lfs.github.com/

# Initialize LFS
git lfs install

# Track the large file
git lfs track "*.tsv"
git lfs track "outputs/*.csv"

# Add .gitattributes
git add .gitattributes

# Continue with normal git workflow
git add .
git commit -m "Add files with LFS tracking"
git push
```

2. Or exclude the data file and add instructions in README:
```bash
# Add to .gitignore
echo "ecom-elasticity-data1.tsv" >> .gitignore
echo "outputs/" >> .gitignore

# Update README to mention that data needs to be added separately
```

## Adding a GitHub README Badge (Optional)

You can add badges to your README.md:

```markdown
# CommerceIQ E-commerce Price Elasticity Analysis

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)
```

## Troubleshooting

### Issue: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Issue: "Large files detected"
```bash
# Use Git LFS (see above) or exclude large files in .gitignore
```

### Issue: Authentication failed
```bash
# Use GitHub CLI or personal access token
# Or set up SSH keys: https://docs.github.com/en/authentication
```

## Next Steps After Pushing

1. Add a repository description on GitHub
2. Add topics/tags: `data-analysis`, `ecommerce`, `price-elasticity`, `python`, `pandas`
3. Add a license file (MIT, Apache, etc.) if you want to share
4. Consider adding GitHub Actions for automated analysis (optional)

## Quick Command Summary

```bash
# Complete workflow (run these commands)
cd /Users/vishwa/Desktop/commerceIQ
git init
git add .
git commit -m "Initial commit: CommerceIQ analysis project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

---

**Need help?** Check GitHub documentation: https://docs.github.com/en/get-started

