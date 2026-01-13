-- Migration 002: Row Level Security Policies
-- Created: 2026-01-12
-- Description: Enable RLS and create security policies for all user-facing tables

---
--- Enable RLS on all tables
---
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE bidding_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE bids ENABLE ROW LEVEL SECURITY;

---
--- RLS Policies: user_profiles
---
CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
  ON user_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

---
--- RLS Policies: projects
---
CREATE POLICY "Users can view own projects"
  ON projects FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own projects"
  ON projects FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects"
  ON projects FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects"
  ON projects FOR DELETE
  USING (auth.uid() = user_id);

---
--- RLS Policies: bidding_strategies
---
CREATE POLICY "Users can manage own strategies"
  ON bidding_strategies FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

---
--- RLS Policies: bids
---
CREATE POLICY "Users can view own bids"
  ON bids FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own bids"
  ON bids FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bids"
  ON bids FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own bids"
  ON bids FOR DELETE
  USING (auth.uid() = user_id);

-- Comments
COMMENT ON POLICY "Users can view own profile" ON user_profiles IS 'Allow users to view their own profile only';
COMMENT ON POLICY "Users can view own projects" ON projects IS 'Isolate projects by user_id';
COMMENT ON POLICY "Users can manage own strategies" ON bidding_strategies IS 'Full CRUD access to own strategies';
COMMENT ON POLICY "Users can view own bids" ON bids IS 'Isolate proposals by user_id';
