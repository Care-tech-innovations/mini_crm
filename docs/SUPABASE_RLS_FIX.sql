-- Run this in Supabase SQL Editor if migration fails with "row-level security" error
-- This allows the app (using anon key) to read and write the clients table

-- Option 1: Add policy to allow anon all operations
CREATE POLICY "Allow anon all" ON "Ramayana's Clients"
  FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);

-- Option 2 (if Option 1 fails): Disable RLS temporarily (less secure)
-- ALTER TABLE "Ramayana's Clients" DISABLE ROW LEVEL SECURITY;
