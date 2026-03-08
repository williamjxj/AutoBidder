-- Development Seed Data
-- Purpose: Populate database with test data for local development
-- Note: This assumes a test user exists in users table with id '00000000-0000-0000-0000-000000000001'

-- Clean existing data (optional - uncomment if needed)
-- TRUNCATE TABLE analytics_events, scraping_jobs, platform_credentials, knowledge_base_documents, keywords, bidding_strategies, proposals, user_project_status, projects, user_profiles CASCADE;

---
--- Seed: user_profiles
---
INSERT INTO user_profiles (id, user_id, subscription_tier, subscription_status, onboarding_completed) VALUES
  ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'pro', 'active', true)
ON CONFLICT (user_id) DO NOTHING;

---
--- Seed: bidding_strategies
---
INSERT INTO bidding_strategies (id, user_id, name, description, system_prompt, tone, is_default) VALUES
  (
    '20000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'Professional & Concise',
    'Standard professional tone with emphasis on deliverables',
    'You are an experienced freelancer writing a proposal. Be professional, concise, and focus on demonstrating relevant experience. Always reference specific past projects when relevant.',
    'professional',
    true
  ),
  (
    '20000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Technical Expert',
    'Technical depth with detailed approach',
    'You are a senior technical consultant. Provide detailed technical approaches, architecture considerations, and demonstrate deep expertise. Use technical terminology appropriately.',
    'technical',
    false
  ),
  (
    '20000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'Enthusiastic & Personal',
    'Warm, enthusiastic tone for creative projects',
    'You are an enthusiastic freelancer who loves their work. Be warm, personal, and show genuine excitement about the project. Emphasize collaboration and communication.',
    'enthusiastic',
    false
  );

---
--- Seed: keywords
---
INSERT INTO keywords (id, user_id, keyword, description, is_active) VALUES
  ('30000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'React', 'React.js frontend development', true),
  ('30000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Next.js', 'Next.js full-stack applications', true),
  ('30000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'TypeScript', 'TypeScript development', true),
  ('30000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'Node.js', 'Node.js backend development', true),
  ('30000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'Python', 'Python development', true);

---
--- Seed: projects (ETL schema - optional sample data for dev)
--- Projects are typically populated via ETL (Discover). These are sample rows for local dev.
---
INSERT INTO projects (id, platform, external_id, fingerprint_hash, category, title, description, skills_required, budget_min, budget_max, employer_name, etl_source, status) VALUES
  (
    '40000000-0000-0000-0000-000000000001',
    'upwork',
    'ext-001',
    'fp-upwork-ext-001',
    'web_development',
    'Build a SaaS dashboard with Next.js and PostgreSQL',
    'We need an experienced developer to build a modern SaaS dashboard using Next.js 15, React 19, and PostgreSQL. The dashboard should include user authentication, data visualization, and subscription management. Expected timeline: 4-6 weeks.',
    ARRAY['Next.js', 'React', 'TypeScript', 'PostgreSQL', 'TailwindCSS'],
    5000.00,
    5000.00,
    'TechCorp Inc',
    'seed',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000002',
    'freelancer',
    'ext-002',
    'fp-freelancer-ext-002',
    'ai_ml',
    'Python FastAPI backend for AI application',
    'Looking for a Python expert to build a FastAPI backend with OpenAI integration. Must have experience with RAG, vector databases, and asynchronous programming. Budget is flexible for the right candidate.',
    ARRAY['Python', 'FastAPI', 'OpenAI', 'ChromaDB', 'PostgreSQL'],
    8000.00,
    8000.00,
    'AI Startup',
    'seed',
    'new'
  )
ON CONFLICT (fingerprint_hash) DO NOTHING;

---
--- Seed: knowledge_base_documents (sample metadata - no actual files)
---
INSERT INTO knowledge_base_documents (id, user_id, filename, file_type, file_size_bytes, collection, processing_status, chunk_count) VALUES
  (
    '60000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'portfolio_saas_dashboard.pdf',
    'pdf',
    2048576,
    'case_studies',
    'completed',
    25
  ),
  (
    '60000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'team_profile.docx',
    'docx',
    512000,
    'team_profiles',
    'completed',
    10
  ),
  (
    '60000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'ecommerce_case_study.pdf',
    'pdf',
    3145728,
    'portfolio',
    'completed',
    40
  );

-- Comments
COMMENT ON TABLE user_profiles IS 'Seeded with 1 pro-tier test user';
COMMENT ON TABLE bidding_strategies IS 'Seeded with 3 sample strategies (Professional, Technical, Enthusiastic)';
COMMENT ON TABLE keywords IS 'Seeded with 5 common tech keywords';
COMMENT ON TABLE projects IS 'Job listings from ETL - seed adds 2 sample rows for dev (use Discover for more)';
COMMENT ON TABLE knowledge_base_documents IS 'Seeded with 3 sample document metadata entries';

SELECT 'Seed data inserted successfully!' AS result;
