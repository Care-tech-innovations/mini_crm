# Deploy Mini CRM — Share via Browser

This guide explains how to make your Mini CRM accessible to others through a link in the browser.

---

## Option 1: Streamlit Community Cloud (Recommended)

**Free, permanent URL, no server to manage.**

### Prerequisites

- GitHub account
- Your project pushed to a GitHub repository

### Steps

1. **Push your project to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/mini_crm.git
   git push -u origin feature/share-via-browser
   ```
   (Or push `main` after merging.)

2. **Go to Streamlit Community Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Deploy**
   - Click **"New app"**
   - **Repository:** select your `mini_crm` repo
   - **Branch:** `feature/share-via-browser` or `main`
   - **Main file path:** `src/app.py`
   - Click **"Deploy!"**

4. **Get your link**
   - After a few minutes, you'll get a URL like:
   - `https://your-app-name-xxxxx.streamlit.app`

### Supabase (persistent data)

To keep client data across restarts and share it between all users:

1. **Create a Supabase project** at [supabase.com](https://supabase.com)
2. **Create table `clients`** with columns: `id` (int8), `name` (text), `phone` (text), `status` (text), `notes` (jsonb)
3. **Enable RLS policies** to allow anon read/write (or use service role for simplicity)
4. **Add secrets** in Streamlit Cloud: Settings → Secrets:
   ```
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your_anon_public_key"
   ```
5. **Redeploy** the app

When Supabase credentials are set, the app uses the database. Otherwise it falls back to local JSON (ephemeral on Streamlit Cloud).

### Other notes

- **Logo:** Add `assets/logo_ramayana.png` to your repo for the logo to appear. The app works without it.

---

## Option 2: ngrok (Quick local sharing)

**Temporary link for testing. Your computer must stay on.**

### Prerequisites

- [ngrok](https://ngrok.com) account (free tier works)

### Steps

1. **Start your app**
   ```powershell
   streamlit run src/app.py
   ```
   (App runs on `http://localhost:8501`)

2. **In a new terminal, run ngrok**
   ```powershell
   ngrok http 8501
   ```

3. **Share the link**
   - ngrok shows a URL like `https://xxxx-xx-xx-xx.ngrok-free.app`
   - Share this link; anyone can access your app while it's running

4. **Stop when done**
   - Press `Ctrl+C` in both terminals to stop

---

## Option 3: Run on a VPS or server

If you have a server (DigitalOcean, AWS, etc.):

1. Clone the repo on the server
2. Install Python and dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run src/app.py --server.port 8501`
4. Use a reverse proxy (nginx) or firewall rules to expose port 8501

---

## Summary

| Method | Cost | Persistence | Best for |
|--------|------|-------------|----------|
| Streamlit Cloud + Supabase | Free | Persistent | Shared data, production |
| Streamlit Cloud (no DB) | Free | Ephemeral | Quick share, demos |
| ngrok | Free tier | While running | Testing with others |
| VPS | Paid | Full control | Production |
