# Generating Images for GitHub

The README includes example plot images. Here's how to generate and commit them:

## Quick Start

```bash
# Generate all example images
uv run examples/attack_analysis_complete.py
uv run examples/attack_comparison.py
uv run examples/attack_heatmap.py
uv run examples/team_attacks.py
uv run examples/plot_example.py

# Check what images were created
dir *.png  # Windows
ls *.png   # Mac/Linux

# Add images to git (if not in .gitignore)
git add *.png
git commit -m "Add example plot images"
git push
```

## Images Currently in README

The README.md references these images:
- `x5_attack_trajectories.png` - From `attack_analysis_complete.py`
- `attack_comparison.png` - From `attack_comparison.py`

## Option 1: Commit Images to Repository

**Pros:**
- Images display immediately on GitHub
- No CI/CD setup needed
- Simple workflow

**Cons:**
- Binary files in git repo
- Need to regenerate manually when code changes

**To use this approach:**
1. Generate images as shown above
2. Remove `*.png` from `.gitignore` if present
3. Commit and push the images

## Option 2: Use GitHub Actions (Advanced)

Create `.github/workflows/generate-plots.yml`:

```yaml
name: Generate Example Plots

on:
  push:
    branches: [main]
    paths:
      - 'examples/*.py'
      - 'datavolley/**/*.py'

jobs:
  generate-plots:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv sync && uv add matplotlib numpy shapely
      
      - name: Generate plots
        run: |
          uv run examples/attack_analysis_complete.py
          uv run examples/attack_comparison.py
      
      - name: Commit images
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add *.png
          git commit -m "Update example plots [skip ci]" || echo "No changes"
          git push
```

**Pros:**
- Automatically updates images
- Images always match code

**Cons:**
- More complex setup
- Requires Actions permissions

## Option 3: Host Images Externally

Upload images to:
- GitHub Releases
- Imgur
- Your own server

Update README image URLs:
```markdown
![X5 Trajectories](https://your-url.com/x5_trajectories.png)
```

**Pros:**
- Keeps repo clean
- Fast clones

**Cons:**
- External dependency
- More maintenance

## Recommended Approach

For this project, **Option 1 (commit images)** is recommended:

1. Images are small (< 500KB total)
2. They don't change frequently
3. Simple workflow for contributors
4. Immediate visibility on GitHub

## Current Setup

The images are already in `.gitignore` by default. To commit them:

```bash
# Remove *.png from .gitignore or add exception
echo "!x5_attack_trajectories.png" >> .gitignore
echo "!attack_comparison.png" >> .gitignore

# Or remove *.png line entirely from .gitignore

# Then commit
git add *.png
git commit -m "Add example plot images to README"
git push
```
