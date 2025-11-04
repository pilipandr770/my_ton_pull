# 🚨 URGENT: Render Dashboard Configuration Required

## Problem Identified

**Render is ignoring render.yaml startCommand** and using hardcoded settings from the **Render Dashboard** instead.

Current behavior:
```
==> Running 'gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app'
[62] Loading worker with pid: 62
[63] Loading worker with pid: 63
```

This shows 2 workers are starting, despite:
- ✅ Procfile deleted from repo
- ✅ render.yaml with --workers 1 in startCommand
- ✅ APScheduler context wrapper deployed

**Root cause:** Render service was created BEFORE render.yaml existed. Dashboard settings take precedence.

---

## ✅ MANUAL FIX REQUIRED (5 minutes)

### Step 1: Go to Render Dashboard
**URL:** https://render.com/dashboard/services/my-ton-pull

### Step 2: Find "Start Command" Setting
In the service settings, locate the field labeled:
- **"Start Command"** or
- **"Command"** or
- **"Run Command"**

### Step 3: Replace with Correct Command
**Current (WRONG):**
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```

**Replace with (CORRECT):**
```
cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --timeout 120 --access-logfile - --error-logfile - app:app
```

### Step 4: Save & Redeploy
1. Click "Save changes"
2. Click "Redeploy" or "Deploy latest"
3. Watch Live Tail for confirmation

---

## ✅ Expected Result After Dashboard Fix

**Live Tail should show:**
```
[14:XX:XX] gunicorn 23.0.0
[14:XX:XX] Listening at: http://0.0.0.0:10000
[14:XX:XX] Using worker: sync
[14:XX:XX] [XXXXX] Loading worker with pid: XXXXX  ← ONLY ONE
✅ Database schema 'ton_pool' ready
⚠️ ВНИМАНИЕ: Gunicorn настроен с 2 рабочими!  ← THIS WARNING WILL NOT APPEAR
✅ Запущен монитор транзакций (polling every 30s)
✅ Transaction monitor scheduler initialized (verified one worker)
```

**NOT this:**
```
[62] Loading worker with pid: 62
[63] Loading worker with pid: 63  ← TWO workers = STILL WRONG
```

---

## 📋 Complete Configuration For Reference

### If Dashboard has fields:
| Field | Value |
|-------|-------|
| **Service Type** | Web Service |
| **Language** | Python |
| **Build Command** | `(leave as is - render.yaml handles it)` |
| **Start Command** | `cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --timeout 120 --access-logfile - --error-logfile - app:app` |
| **Python Version** | 3.13 (or leave default) |

---

## 🔄 If Manual Fix Doesn't Work

**Option 1: Delete and Recreate Service**
1. Go to Render Dashboard → Service Settings
2. Scroll to bottom → "Delete Service"
3. Confirm deletion
4. Reconnect repo: Deploy again

This forces Render to read render.yaml from scratch.

**Option 2: Contact Render Support**
- Ask about render.yaml startCommand priority
- Dashboard settings might be cached/locked

---

## ✅ What's Been Deployed (Code Side)

| File | Change | Status |
|------|--------|--------|
| **backend/transaction_monitor.py** | App context wrapper for APScheduler | ✅ Pushed (3e404c2) |
| **backend/Procfile** | Deleted | ✅ Pushed (4759313) |
| **render.yaml** | Updated startCommand | ✅ Updated, ready to push |

### Commits Ready to Push:
```bash
git log --oneline -4
# Should show:
# 4759313 🗑️ Remove Procfile
# 3e404c2 🔧 Fix APScheduler app context
# d40d5b9 ⚡ Force Render redeploy
# 788e141 🔍 Add worker detection
```

---

## 🎯 Timeline

| Step | Action | Status |
|------|--------|--------|
| Code fixes | APScheduler + Procfile deletion | ✅ DONE |
| render.yaml | Updated startCommand | ✅ READY |
| **Render Dashboard** | **MANUAL UPDATE NEEDED** | ⏳ **BLOCKING** |
| Redeploy | Push + Dashboard changes | ⏳ NEXT |
| Verify | Check for single worker | ⏳ FINAL |

---

## 🚀 Next Steps

1. **RIGHT NOW:** Go to Render Dashboard and update "Start Command" field
2. **WHILE WAITING:** I'll push the render.yaml changes to repo
3. **AFTER DASHBOARD FIX:** Render will redeploy with correct single-worker config
4. **VERIFY:** Check Live Tail for "Loading worker with pid: [XXXXX]" (only ONCE)

**Critical:** Without the Dashboard fix, code changes alone won't work!
