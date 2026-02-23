-- Development Seed Data
-- Purpose: Populate database with test data for local development
-- Note: This assumes a test user exists in users table with id '00000000-0000-0000-0000-000000000001'

-- Clean existing data (optional - uncomment if needed)
-- TRUNCATE TABLE analytics_events, scraping_jobs, platform_credentials, knowledge_base_documents, keywords, bids, bidding_strategies, projects, user_profiles CASCADE;

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
--- Seed: projects
---
INSERT INTO projects (id, user_id, title, description, budget, budget_type, technologies, source_platform, status) VALUES
  (
    '40000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'Build a SaaS dashboard with Next.js and PostgreSQL',
    'We need an experienced developer to build a modern SaaS dashboard using Next.js 15, React 19, and PostgreSQL. The dashboard should include user authentication, data visualization, and subscription management. Expected timeline: 4-6 weeks.',
    5000.00,
    'fixed',
    ARRAY['Next.js', 'React', 'TypeScript', 'PostgreSQL', 'TailwindCSS'],
    'upwork',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Python FastAPI backend for AI application',
    'Looking for a Python expert to build a FastAPI backend with OpenAI integration. Must have experience with RAG, vector databases, and asynchronous programming. Budget is flexible for the right candidate.',
    8000.00,
    'fixed',
    ARRAY['Python', 'FastAPI', 'OpenAI', 'ChromaDB', 'PostgreSQL'],
    'freelancer',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'E-commerce website redesign (Shopify + React)',
    'Redesign our Shopify storefront with custom React components. Need someone with strong UI/UX skills and Shopify development experience. 20-30 hours per week for 8 weeks.',
    15000.00,
    'fixed',
    ARRAY['React', 'Shopify', 'JavaScript', 'CSS'],
    'upwork',
    'reviewed'
  ),
  (
    '40000000-0000-0000-0000-000000000004',
    '00000000-0000-0000-0000-000000000001',
    'Mobile app backend with Node.js and MongoDB',
    'Build a scalable RESTful API for our mobile app. Real-time features, push notifications, and payment integration required. Looking for 3-4 months commitment.',
    12000.00,
    'fixed',
    ARRAY['Node.js', 'Express', 'MongoDB', 'Socket.io'],
    'freelancer',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000005',
    '00000000-0000-0000-0000-000000000001',
    'Data visualization dashboard with D3.js',
    'Create interactive data visualizations for our analytics platform. Must be proficient in D3.js, React, and have strong design sense. Hourly rate preferred.',
    75.00,
    'hourly',
    ARRAY['React', 'D3.js', 'TypeScript', 'Redux'],
    'upwork',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000006',
    '00000000-0000-0000-0000-000000000001',
    'Full-stack developer for MVP (React + Python)',
    'Seeking a full-stack developer to build our MVP. Frontend in React, backend in Python/Django. Must be able to work independently and deliver quickly. Equity + pay.',
    10000.00,
    'fixed',
    ARRAY['React', 'Python', 'Django', 'PostgreSQL', 'AWS'],
    'manual',
    'bidding'
  ),
  (
    '40000000-0000-0000-0000-000000000007',
    '00000000-0000-0000-0000-000000000001',
    'Chrome extension for productivity (React + TypeScript)',
    'Build a Chrome extension with React and TypeScript. Features include tab management, time tracking, and sync across devices. Clean code and documentation required.',
    3500.00,
    'fixed',
    ARRAY['React', 'TypeScript', 'Chrome APIs', 'IndexedDB'],
    'upwork',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000008',
    '00000000-0000-0000-0000-000000000001',
    'AI chatbot integration (LangChain + OpenAI)',
    'Integrate an AI chatbot into our website using LangChain and OpenAI. Must support RAG for custom knowledge base. Previous AI experience required.',
    6000.00,
    'fixed',
    ARRAY['Python', 'LangChain', 'OpenAI', 'FastAPI', 'React'],
    'freelancer',
    'new'
  ),
  (
    '40000000-0000-0000-0000-000000000009',
    '00000000-0000-0000-0000-000000000001',
    'WordPress to Next.js migration',
    'Migrate our WordPress blog to Next.js with improved performance. Content should be fetched from headless WordPress API. SEO optimization critical.',
    4000.00,
    'fixed',
    ARRAY['Next.js', 'React', 'WordPress', 'REST API', 'SEO'],
    'upwork',
    'reviewed'
  ),
  (
    '40000000-0000-0000-0000-000000000010',
    '00000000-0000-0000-0000-000000000001',
    'Automated testing setup (Playwright + Jest)',
    'Set up comprehensive test suite for our Next.js app. E2E tests with Playwright, unit tests with Jest. CI/CD integration required.',
    2500.00,
    'fixed',
    ARRAY['Playwright', 'Jest', 'TypeScript', 'GitHub Actions'],
    'freelancer',
    'new'
  );

---
--- Seed: bids (sample proposals)
---
INSERT INTO bids (id, project_id, user_id, strategy_id, proposal, status, ai_generated) VALUES
  (
    '50000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    'I am excited to submit my proposal for your Next.js SaaS dashboard project. With over 5 years of experience building production-grade applications with Next.js and PostgreSQL, I am confident I can deliver exactly what you need within your 4-6 week timeline...',
    'draft',
    true
  ),
  (
    '50000000-0000-0000-0000-000000000002',
    '40000000-0000-0000-0000-000000000006',
    '00000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    'Your MVP project aligns perfectly with my full-stack expertise. I have successfully delivered 10+ MVPs combining React frontends with Python backends...',
    'approved',
    true
  );

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
COMMENT ON TABLE projects IS 'Seeded with 10 sample job postings from various platforms';
COMMENT ON TABLE bids IS 'Seeded with 2 sample proposals';
COMMENT ON TABLE knowledge_base_documents IS 'Seeded with 3 sample document metadata entries';

SELECT 'Seed data inserted successfully!' AS result;
