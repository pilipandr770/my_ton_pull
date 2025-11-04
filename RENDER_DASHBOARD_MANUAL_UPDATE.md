# 🚨 CRITICAL: Manual Render Dashboard Update Required

## Problem Summary

The Render deployment is failing because:
- ❌ Dashboard Start Command: `cd backend && gunicorn ... --workers 2 ...` (outdated, hardcoded)
- ✅ render.yaml Start Command: `gunicorn --chdir backend ... --workers 1 ...` (updated, but ignored)
- 📍 Result: Render uses Dashboard command → deployment fails with `bash: line 1: cd: backend: No such file or directory`

**Root Cause:** Render Dashboard settings **OVERRIDE** repository files for existing services. The service was created before `render.yaml` existed, so Dashboard config takes priority.

**Solution:** Update the Dashboard Start Command manually via browser.

---

## 🎯 Step-by-Step Instructions

### Step 1: Open Render Dashboard
1. Go to: **https://render.com/dashboard/services/my-ton-pull**
2. You should see your service named "ton-pool-unified"
3. Click on it to open the service details

### Step 2: Find the Settings Page
1. Look for **"Settings"** tab at the top (usually between "Logs" and "Events")
2. Click on "Settings"
3. Scroll down to the **"Build & Deploy"** section

### Step 3: Locate the Start Command Field
In the "Build & Deploy" section, find the field labeled:
- **"Start Command"** or **"Command"** (depending on Render UI version)

You should see it currently shows something like:
```
cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```

### Step 4: Replace the Entire Command

**DELETE everything in the Start Command field**

Then **COPY & PASTE** this exact command:

```
gunicorn --chdir backend --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --timeout 120 --access-logfile - --error-logfile - app:app
```

**Important:** 
- Use `--chdir backend` (NOT `cd backend &&`)
- Use `--workers 1` (NOT `--workers 2`)
- Include all flags exactly as shown

### Step 5: Save Changes
1. Look for the **"Save changes"** button (usually at bottom of the form)
2. Click it
3. Wait for confirmation message: "Changes saved" or similar

### Step 6: Trigger Redeploy
After saving, Render will show a **"Redeploy"** button
1. Click **"Redeploy"** (or "Deploy")
2. This triggers a new build with the updated Start Command

### Step 7: Monitor the Deployment
1. Go to the **"Logs"** tab
2. Watch the **"Live Tail"** for deployment progress
3. Wait 3-5 minutes for build and deployment to complete

---

## ✅ Expected Success Signs

### In Render Logs, you should see:

```
==> Deploying...
==> Running 'gunicorn --chdir backend --bind 0.0.0.0:$PORT --workers 1 --worker-class sync ...'
[62] [INFO] Starting gunicorn 23.0.0
[62] [INFO] Listening at: http://0.0.0.0:XXXXX (62)
[62] [INFO] Using worker: sync
[62] [INFO] Booting worker with pid: 62
✅ TON Staking Pool started successfully on port XXXXX
✅ Database connected
✅ Transaction monitor started...
✅ Scheduler initialized (verified one worker)
```

### What you should see:
- ✅ Build completed successfully
- ✅ Start command executed without errors
- ✅ Only 1 worker process (PID 62 or similar)
- ✅ Transaction monitor started
- ✅ Scheduler initialized message

### What you should NOT see:
- ❌ `bash: line 1: cd: backend: No such file or directory`
- ❌ Multiple worker PIDs (e.g., `[62]` AND `[63]`)
- ❌ `⚠️ WARNING: Gunicorn configured with 2 workers!`
- ❌ `RuntimeError: working outside of application context`

---

## 🔍 Verification Checklist

After deployment completes, verify all items:

- [ ] **Build Status**: ✅ Build successful
- [ ] **Start Command**: ✅ Executed without "cd: backend" error
- [ ] **Worker Count**: ✅ Only 1 worker PID in logs
- [ ] **Worker Info**: ✅ Single `[PID] [INFO] Booting worker with pid: [PID]` message
- [ ] **Transaction Monitor**: ✅ `✅ Transaction monitor started...` visible
- [ ] **Scheduler**: ✅ `✅ Scheduler initialized (verified one worker)` visible
- [ ] **No Errors**: ✅ No RuntimeError or context errors
- [ ] **Website**: ✅ https://my-ton-pull.onrender.com loads

---

## 🎓 Why Manual Update is Required

**Why can't we fix this with code/git?**

1. **Render Dashboard ≠ Repository**
   - Dashboard settings stored on Render servers (not in git repo)
   - render.yaml is in repo but ignored for existing services

2. **Service Creation Timeline**
   - Service created: Before render.yaml existed
   - Dashboard default: Used at creation time (--workers 2)
   - Result: Dashboard config locked in, overrides later render.yaml

3. **Render Priority System (Existing Services)**
   - 🥇 **#1 Priority**: Render Dashboard UI settings
   - 🥈 #2: render.yaml (only for NEW services)
   - 🥉 #3: Repository files

4. **Why Code Won't Help**
   - ❌ Committing code changes → render.yaml updated, Dashboard unchanged
   - ❌ Deleting Procfile → Dashboard still overrides
   - ❌ Creating render.yaml → Dashboard still overrides
   - ✅ Only browser Dashboard update works

---

## 🆘 Troubleshooting

### "I can't find the Start Command field"

**Solution:**
1. Try scrolling down more on the Settings page
2. Look for "Build & Deploy" section header
3. Check if there's an "Advanced" or "More settings" expandable section
4. Render UI may vary by region/account - check Render docs

### "I see the field but changes don't seem to work"

**Solution:**
1. Make sure you clicked **"Save changes"** (not just editing the field)
2. Make sure you clicked **"Redeploy"** after saving
3. Wait full 5 minutes for deployment to complete
4. Check Render Logs Live Tail - it should show `Running 'gunicorn --chdir backend ...'`

### "Still seeing 'cd: backend: No such file or directory' error"

**Solution:**
1. Go back to Dashboard Settings
2. Copy the exact command again (no typos)
3. Try clicking "Save changes" again
4. Try manual redeploy from "Deployments" tab
5. If still failing, check Render Support docs

### "Deployment succeeds but app won't start"

**Solution:**
1. Check logs for specific error message
2. Verify `--chdir backend` is correct (exact spelling)
3. Verify gunicorn path is correct
4. Check if app.py exists in backend directory

---

## 📋 Command Reference

### What NOT to use (will fail):
```bash
# ❌ These will fail:
cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app
```

### What TO use (will work):
```bash
# ✅ Correct command:
gunicorn --chdir backend --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --timeout 120 --access-logfile - --error-logfile - app:app
```

**Key Differences:**
- `--chdir backend` instead of `cd backend &&`
- `--workers 1` instead of `--workers 2`
- `--worker-class sync` for reliability
- Access and error logging enabled

---

## 🎯 After This Fix is Complete

Once the deployment succeeds with single worker:

1. ✅ **Single Worker Mode Active**: Only 1 Gunicorn worker running
2. ✅ **APScheduler Fixed**: Transaction polling runs once (not twice)
3. ✅ **App Context Working**: No "RuntimeError: working outside of application context"
4. ✅ **All 5 Phase 4.7 Optimizations Active**:
   - Single worker mode
   - APScheduler app context wrapper
   - ProxyFix HTTPS handling
   - Flask-Limiter rate limiting
   - Stripe webhook idempotency

5. ✅ **System Production-Ready**: All 20 features + 5 optimizations deployed

---

## 📞 Need More Help?

- **Render Documentation**: https://render.com/docs/services
- **Render Support**: https://render.com/support
- **GitHub Issues**: Create issue with error logs if deployment still fails

---

## 📝 Summary

| Item | Current | Target | Status |
|------|---------|--------|--------|
| **Render.yaml** | ✅ Updated (`--chdir`, `--workers 1`) | ✅ Correct | Ready |
| **Code/Config** | ✅ All changes deployed | ✅ Complete | Done |
| **Dashboard Command** | ❌ Old (`cd backend`, `--workers 2`) | ✅ New command needed | ⏳ Blocking |
| **Deployment** | ❌ Fails (cd: backend error) | ✅ Success | Pending |

**🎯 Current Blocker**: Manual Render Dashboard Start Command update  
**🎯 ETA**: 2-5 minutes to complete  
**🎯 Impact**: Unblocks production deployment with all optimizations

