#!/bin/bash

# BidMaster Pro - Quick Start Merge Script
# This script helps you set up the merged project structure

set -e  # Exit on error

BIDDING_ROOT="/Users/william.jiang/my-experiments/bidding"
BIDMASTER_PRO="$BIDDING_ROOT/bidmaster-pro"

echo "🚀 BidMaster Pro - Merge Setup Script"
echo "======================================"
echo ""

# Step 1: Check if projects exist
echo "📋 Step 1: Checking existing projects..."
if [ ! -d "$BIDDING_ROOT/bidmaster" ]; then
    echo "❌ Error: BidMaster project not found at $BIDDING_ROOT/bidmaster"
    exit 1
fi

if [ ! -d "$BIDDING_ROOT/biddingHub" ]; then
    echo "❌ Error: BiddingHub project not found at $BIDDING_ROOT/biddingHub"
    exit 1
fi

echo "✅ Both projects found!"
echo ""

# Step 2: Create new unified project
echo "📦 Step 2: Creating unified project structure..."
if [ -d "$BIDMASTER_PRO" ]; then
    echo "⚠️  Warning: bidmaster-pro directory already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted by user"
        exit 1
    fi
    rm -rf "$BIDMASTER_PRO"
fi

mkdir -p "$BIDMASTER_PRO"
echo "✅ Created $BIDMASTER_PRO"
echo ""

# Step 3: Copy BidMaster as foundation
echo "📂 Step 3: Copying BidMaster as foundation..."
cp -r "$BIDDING_ROOT/bidmaster/"* "$BIDMASTER_PRO/"
cp -r "$BIDDING_ROOT/bidmaster/."[!.]* "$BIDMASTER_PRO/" 2>/dev/null || true
echo "✅ BidMaster copied"
echo ""

# Step 4: Create migration directories
echo "📁 Step 4: Creating migration directories..."
mkdir -p "$BIDMASTER_PRO/database/migrations"
mkdir -p "$BIDMASTER_PRO/temp/biddinghub-features"
mkdir -p "$BIDMASTER_PRO/docs/migration"
echo "✅ Migration directories created"
echo ""

# Step 5: Copy BiddingHub files to migration folder
echo "📋 Step 5: Copying BiddingHub features for migration..."
cp -r "$BIDDING_ROOT/biddingHub/server/integrations" "$BIDMASTER_PRO/temp/biddinghub-features/"
cp "$BIDDING_ROOT/biddingHub/server/_core/llm.ts" "$BIDMASTER_PRO/temp/biddinghub-features/"
cp "$BIDDING_ROOT/biddingHub/server/routers.ts" "$BIDMASTER_PRO/temp/biddinghub-features/"
cp -r "$BIDDING_ROOT/biddingHub/drizzle/schema.ts" "$BIDMASTER_PRO/temp/biddinghub-features/"
cp -r "$BIDDING_ROOT/biddingHub/client/src/pages" "$BIDMASTER_PRO/temp/biddinghub-features/pages-to-port"
echo "✅ BiddingHub features copied to temp folder"
echo ""

# Step 6: Create database migration file
echo "📝 Step 6: Creating database migration template..."
cat > "$BIDMASTER_PRO/database/migrations/003_merge_biddinghub_features.sql" << 'EOF'
-- BidMaster Pro: Merge BiddingHub Features
-- Migration Date: 2026-01-12
-- Description: Add keywords, bidding_strategies, platform_credentials tables
--              and enhance existing projects and bids tables

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- Table: keywords
-- Description: Search keywords for job discovery
-- ==========================================
CREATE TABLE IF NOT EXISTS keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_keywords_user_id ON keywords(user_id);
CREATE INDEX idx_keywords_is_active ON keywords(is_active);

-- ==========================================
-- Table: bidding_strategies
-- Description: AI bidding strategies and prompts
-- ==========================================
CREATE TABLE IF NOT EXISTS bidding_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    tone VARCHAR(100),
    focus_areas JSONB,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategies_user_id ON bidding_strategies(user_id);
CREATE INDEX idx_strategies_is_default ON bidding_strategies(is_default);

-- ==========================================
-- Table: platform_credentials
-- Description: Encrypted API credentials for platforms
-- ==========================================
CREATE TABLE IF NOT EXISTS platform_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    platform VARCHAR(100) NOT NULL,
    api_key TEXT, -- Should be encrypted
    access_token TEXT, -- Should be encrypted
    refresh_token TEXT, -- Should be encrypted
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_credentials_user_id ON platform_credentials(user_id);
CREATE INDEX idx_credentials_platform ON platform_credentials(platform);

-- ==========================================
-- Enhance: projects table
-- Description: Add fields from BiddingHub schema
-- ==========================================
ALTER TABLE projects ADD COLUMN IF NOT EXISTS external_id VARCHAR(255);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS search_keyword VARCHAR(255);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS client_rating VARCHAR(50);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

CREATE INDEX IF NOT EXISTS idx_projects_external_id ON projects(external_id);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- ==========================================
-- Enhance: bids table
-- Description: Add AI-generated content fields
-- ==========================================
ALTER TABLE bids ADD COLUMN IF NOT EXISTS external_project_id VARCHAR(255);
ALTER TABLE bids ADD COLUMN IF NOT EXISTS job_title VARCHAR(255);
ALTER TABLE bids ADD COLUMN IF NOT EXISTS cover_letter TEXT;
ALTER TABLE bids ADD COLUMN IF NOT EXISTS bidding_statement TEXT;
ALTER TABLE bids ADD COLUMN IF NOT EXISTS submission_method VARCHAR(50);

-- ==========================================
-- Triggers: Auto-update timestamps
-- ==========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON bidding_strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credentials_updated_at BEFORE UPDATE ON platform_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- Row Level Security (RLS)
-- Description: Ensure users can only access their own data
-- ==========================================

-- Enable RLS
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE bidding_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_credentials ENABLE ROW LEVEL SECURITY;

-- Keywords policies
CREATE POLICY "Users can view their own keywords"
    ON keywords FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own keywords"
    ON keywords FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own keywords"
    ON keywords FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own keywords"
    ON keywords FOR DELETE
    USING (auth.uid() = user_id);

-- Bidding strategies policies
CREATE POLICY "Users can view their own strategies"
    ON bidding_strategies FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own strategies"
    ON bidding_strategies FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own strategies"
    ON bidding_strategies FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own strategies"
    ON bidding_strategies FOR DELETE
    USING (auth.uid() = user_id);

-- Platform credentials policies
CREATE POLICY "Users can view their own credentials"
    ON platform_credentials FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own credentials"
    ON platform_credentials FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own credentials"
    ON platform_credentials FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own credentials"
    ON platform_credentials FOR DELETE
    USING (auth.uid() = user_id);

-- ==========================================
-- Sample Data (for testing)
-- ==========================================
-- Note: This will only work after authentication is set up
-- Uncomment when ready to test

-- INSERT INTO keywords (user_id, keyword, description) VALUES
-- ('YOUR_USER_ID_HERE', 'react developer', 'Frontend React projects'),
-- ('YOUR_USER_ID_HERE', 'python ai', 'AI and machine learning projects');

-- INSERT INTO bidding_strategies (user_id, name, description, system_prompt, tone) VALUES
-- ('YOUR_USER_ID_HERE', 'Professional', 'Standard professional approach', 
--  'You are a professional proposal writer. Write clear, concise proposals highlighting relevant experience.', 
--  'professional');

EOF

echo "✅ Migration file created"
echo ""

# Step 7: Create Python service structure
echo "🐍 Step 7: Creating Python AI service structure..."
mkdir -p "$BIDDING_ROOT/python-ai-service/app/routers"
mkdir -p "$BIDDING_ROOT/python-ai-service/app/services"
mkdir -p "$BIDDING_ROOT/python-ai-service/app/models"

cat > "$BIDDING_ROOT/python-ai-service/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
chromadb==0.4.18
langchain==0.1.0
openai==1.3.0
pypdf==3.17.1
python-docx==1.1.0
python-multipart==0.0.6
pydantic==2.5.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
EOF

cat > "$BIDDING_ROOT/python-ai-service/.env.example" << 'EOF'
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# PostgreSQL Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/auto_bidder_dev

# ChromaDB
CHROMA_PERSIST_DIRECTORY=/app/chroma_db

# Platform APIs (optional)
UPWORK_API_KEY=
FREELANCER_API_KEY=

# Next.js URL (for CORS)
NEXTJS_URL=http://localhost:3000
EOF

cat > "$BIDDING_ROOT/python-ai-service/app/__init__.py" << 'EOF'
# BidMaster Pro AI Service
EOF

cat > "$BIDDING_ROOT/python-ai-service/README.md" << 'EOF'
# BidMaster Pro - Python AI Service

FastAPI service providing RAG-powered proposal generation.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## API Docs

Visit: http://localhost:8000/docs
EOF

echo "✅ Python service structure created"
echo ""

# Step 8: Update package.json
echo "📦 Step 8: Installing additional dependencies..."
cd "$BIDMASTER_PRO"

# Check if package.json exists
if [ -f "package.json" ]; then
    echo "Installing OpenAI SDK..."
    pnpm add openai@latest
    echo "✅ Dependencies installed"
else
    echo "⚠️  Warning: package.json not found. Skipping dependency installation."
fi
echo ""

# Step 9: Create documentation
echo "📄 Step 9: Creating migration documentation..."
cat > "$BIDMASTER_PRO/docs/migration/MIGRATION_NOTES.md" << 'EOF'
# Migration Notes: BiddingHub → BidMaster Pro

## Files Copied

### From BiddingHub
- `server/integrations/` → `temp/biddinghub-features/integrations/`
- `server/_core/llm.ts` → `temp/biddinghub-features/llm.ts`
- `server/routers.ts` → `temp/biddinghub-features/routers.ts`
- `client/src/pages/` → `temp/biddinghub-features/pages-to-port/`

## Next Steps

1. **Database Migration**:
   - Review `database/migrations/003_merge_biddinghub_features.sql`
   - Apply migration: Run SQL in PostgreSQL using psql or a DB client

2. **Backend API Port**:
   - Convert tRPC routers to Next.js API routes
   - Create `/api/keywords`, `/api/strategies`, `/api/proposals/generate`

3. **Frontend Port**:
   - Adapt React pages to Next.js app router
   - Create `/app/keywords/page.tsx`, `/app/strategies/page.tsx`

4. **Python Service**:
   - Implement FastAPI service in `../python-ai-service/`
   - Follow implementation plan in MERGE_AND_UPGRADE_PLAN.md

## Reference Files

- Main Plan: `/MERGE_AND_UPGRADE_PLAN.md`
- Checklist: `/IMPLEMENTATION_CHECKLIST.md`
- BiddingHub Features: `temp/biddinghub-features/`

## Database Schema Changes

See `database/migrations/003_merge_biddinghub_features.sql` for:
- New tables: `keywords`, `bidding_strategies`, `platform_credentials`
- Enhanced columns in `projects` and `bids` tables
- Row Level Security policies
EOF

echo "✅ Documentation created"
echo ""

# Step 10: Summary
echo "✅ =========================================="
echo "✅  MERGE SETUP COMPLETE!"
echo "✅ =========================================="
echo ""
echo "📁 Project Location: $BIDMASTER_PRO"
echo ""
echo "📋 Next Steps:"
echo "   1. Review the database migration:"
echo "      → $BIDMASTER_PRO/database/migrations/003_merge_biddinghub_features.sql"
echo ""
echo "   2. Apply the migration in PostgreSQL:"
echo "      → Option A: Run via docker: docker exec -i auto-bidder-postgres psql -U postgres -d auto_bidder_dev < database/migrations/003_merge_biddinghub_features.sql"
echo "      → Option B: Use psql directly: psql -h localhost -U postgres -d auto_bidder_dev -f database/migrations/003_merge_biddinghub_features.sql"
echo ""
echo "   3. Review BiddingHub features to port:"
echo "      → $BIDMASTER_PRO/temp/biddinghub-features/"
echo ""
echo "   4. Read the full plan:"
echo "      → $BIDDING_ROOT/MERGE_AND_UPGRADE_PLAN.md"
echo ""
echo "   5. Follow the checklist:"
echo "      → $BIDDING_ROOT/IMPLEMENTATION_CHECKLIST.md"
echo ""
echo "   6. Start development:"
echo "      → cd $BIDMASTER_PRO"
echo "      → pnpm install"
echo "      → pnpm dev"
echo ""
echo "🐍 Python AI Service:"
echo "   → Location: $BIDDING_ROOT/python-ai-service/"
echo "   → Setup: cd python-ai-service && python3 -m venv venv && source venv/bin/activate"
echo "   → Install: pip install -r requirements.txt"
echo ""
echo "🚀 Ready to start Phase 1 of the merge!"
echo ""
