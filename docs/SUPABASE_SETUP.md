# Supabase Setup for Mini CRM

This guide explains how to configure Supabase so your CRM stores data in a shared database.

---

## 1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **New project**
3. Fill in name, password, region
4. Wait for the project to be ready

---

## 2. Create the `clients` table

1. In the left sidebar, click **Table Editor**
2. Click **New table**
3. Name: `clients`
4. Add columns:

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | int8 | No | — |
| name | text | No | — |
| phone | text | No | — |
| status | text | No | 'interested' |
| notes | jsonb | Yes | — |

5. Set `id` as **Primary Key**
6. **Important:** If Supabase adds "Identity" to the id column, you may need to disable it so the app can insert explicit IDs. In SQL Editor, run:
   ```sql
   ALTER TABLE clients ALTER COLUMN id DROP IDENTITY;
   ```
   (Only if you get an error when saving clients.)

7. Click **Save**

---

## 3. Enable Row Level Security (RLS)

1. Go to **Authentication** → **Policies** (or Table Editor → clients → RLS)
2. For the `clients` table, add a policy:
   - **Policy name:** Allow anon all
   - **Allowed operation:** ALL
   - **Target roles:** anon
   - **USING expression:** `true`
   - **WITH CHECK expression:** `true`

This allows the app to read and write using the anon key.

---

## 4. Get your credentials

1. Go to **Project Settings** (gear icon) → **API**
2. Copy **Project URL** (e.g. `https://xxxxx.supabase.co`)
3. Copy **anon public** key (starts with `eyJ...`)

---

## 5. Configure the app

### Local development

1. Copy `.env.example` to `.env`
2. Edit `.env`:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   ```

### Streamlit Cloud

1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click **Settings** → **Secrets**
3. Add:
   ```
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your_anon_key_here"
   ```
4. Save and redeploy

---

## 6. Fallback behavior

- **With Supabase configured:** Data is stored in the database. All users (local + deployed) see the same data.
- **Without Supabase:** The app falls back to `clients.json` (local file). On Streamlit Cloud, data is ephemeral and may reset.
