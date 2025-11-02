# 🔧 Manual Build Instructions (if auto-deploy fails)

## Quick Fix - Manual Deploy

### Option 1: Render Dashboard (RECOMMENDED)

1. **Go to**: https://dashboard.render.com/
2. **Select**: your `ton-pool-unified` or `my-ton-pull` service
3. **Settings** tab → **Build & Deploy** section:
   - **Build Command**: Make sure it says `python build.py`
   - If not, change it and click **Save Changes**
4. **Manual Deploy** button (top right)
5. Select **Clear build cache & deploy**
6. Wait ~5 minutes

### Option 2: Check Build Logs

Look for this in build logs:
```
==> Выполнение команды сборки 'python build.py'...
🚀 TON Pool - Unified Build
```

If you see `pip install -r requirements.txt` instead, then Render didn't use build.py.

### Option 3: Force rebuild with commit

If Render ignores `build.py`, add this to `render.yaml`:

```yaml
buildCommand: "python3 build.py"  # Try python3 instead of python
```

Or even more explicit:

```yaml
buildCommand: "ls -la && python build.py && ls -la frontend/out"
```

---

## Current Status Check

Your logs show:
```
📂 Каталог существует: False
```

This means `frontend/out` directory doesn't exist = frontend wasn't built.

**Expected after successful build:**
```
🚀 TON Pool - Unified Build
====================================
🔧 Installing Python dependencies
✅ Success
====================================
🔧 Installing Node.js dependencies
✅ Success
====================================
🔧 Building Next.js frontend
✅ Success
====================================
📦 Frontend build output (X files):
   - index.html
   - _next/...
🎉 BUILD SUCCESSFUL!
```

Then on start:
```
📂 Каталог существует: True  ← Should be True!
```

---

## Immediate Action

**Do this NOW in Render Dashboard:**

1. Open service settings
2. Verify Build Command = `python build.py`
3. Click "Manual Deploy" → "Clear build cache & deploy"
4. Watch build logs for "🚀 TON Pool - Unified Build"

If `python build.py` doesn't run, there may be an issue with Render detecting the correct runtime or command.

---

## Alternative: Use shell script

If Python build.py still doesn't work, we can try:

```yaml
buildCommand: "sh -c 'pip install --upgrade pip && pip install -r backend/requirements.txt && cd frontend && npm install && npm run build'"
```

Let me know what you see in the build logs!
