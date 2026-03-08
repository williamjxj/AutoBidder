/**
 * Database Types - PostgreSQL Schema
 * These types match the database schema defined in migrations
 */

export interface Database {
  public: {
    Tables: {
      user_profiles: {
        Row: {
          id: string
          user_id: string
          subscription_tier: 'free' | 'pro' | 'agency'
          subscription_status: 'active' | 'cancelled' | 'expired'
          subscription_expires_at: string | null
          usage_quota: Record<string, any>
          preferences: Record<string, any>
          onboarding_completed: boolean
          last_activity_at: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          subscription_tier?: 'free' | 'pro' | 'agency'
          subscription_status?: 'active' | 'cancelled' | 'expired'
          subscription_expires_at?: string | null
          usage_quota?: Record<string, any>
          preferences?: Record<string, any>
          onboarding_completed?: boolean
          last_activity_at?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          subscription_tier?: 'free' | 'pro' | 'agency'
          subscription_status?: 'active' | 'cancelled' | 'expired'
          subscription_expires_at?: string | null
          usage_quota?: Record<string, any>
          preferences?: Record<string, any>
          onboarding_completed?: boolean
          last_activity_at?: string
          created_at?: string
          updated_at?: string
        }
      }
      projects: {
        Row: {
          id: string
          user_id: string
          title: string
          description: string
          budget: number | null
          budget_type: 'fixed' | 'hourly' | 'not_specified' | null
          technologies: string[]
          source_platform: 'upwork' | 'freelancer' | 'manual' | 'other'
          source_url: string | null
          external_id: string | null
          client_rating: string | null
          client_reviews_count: number | null
          client_location: string | null
          search_keyword: string | null
          posted_date: string | null
          deadline: string | null
          status: 'new' | 'reviewed' | 'bidding' | 'archived' | 'won' | 'lost'
          scraped_at: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          title: string
          description: string
          budget?: number | null
          budget_type?: 'fixed' | 'hourly' | 'not_specified' | null
          technologies?: string[]
          source_platform: 'upwork' | 'freelancer' | 'manual' | 'other'
          source_url?: string | null
          external_id?: string | null
          client_rating?: string | null
          client_reviews_count?: number | null
          client_location?: string | null
          search_keyword?: string | null
          posted_date?: string | null
          deadline?: string | null
          status?: 'new' | 'reviewed' | 'bidding' | 'archived' | 'won' | 'lost'
          scraped_at?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          title?: string
          description?: string
          budget?: number | null
          budget_type?: 'fixed' | 'hourly' | 'not_specified' | null
          technologies?: string[]
          source_platform?: 'upwork' | 'freelancer' | 'manual' | 'other'
          source_url?: string | null
          external_id?: string | null
          client_rating?: string | null
          client_reviews_count?: number | null
          client_location?: string | null
          search_keyword?: string | null
          posted_date?: string | null
          deadline?: string | null
          status?: 'new' | 'reviewed' | 'bidding' | 'archived' | 'won' | 'lost'
          scraped_at?: string
          created_at?: string
          updated_at?: string
        }
      }
      bidding_strategies: {
        Row: {
          id: string
          user_id: string
          name: string
          description: string | null
          system_prompt: string
          tone: 'professional' | 'enthusiastic' | 'technical' | 'friendly' | 'formal'
          focus_areas: Record<string, any>
          temperature: number
          max_tokens: number
          is_default: boolean
          use_count: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          name: string
          description?: string | null
          system_prompt: string
          tone?: 'professional' | 'enthusiastic' | 'technical' | 'friendly' | 'formal'
          focus_areas?: Record<string, any>
          temperature?: number
          max_tokens?: number
          is_default?: boolean
          use_count?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          name?: string
          description?: string | null
          system_prompt?: string
          tone?: 'professional' | 'enthusiastic' | 'technical' | 'friendly' | 'formal'
          focus_areas?: Record<string, any>
          temperature?: number
          max_tokens?: number
          is_default?: boolean
          use_count?: number
          created_at?: string
          updated_at?: string
        }
      }
      keywords: {
        Row: {
          id: string
          user_id: string
          keyword: string
          description: string | null
          is_active: boolean
          match_type: 'exact' | 'partial' | 'fuzzy'
          jobs_matched: number
          last_match_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          keyword: string
          description?: string | null
          is_active?: boolean
          match_type?: 'exact' | 'partial' | 'fuzzy'
          jobs_matched?: number
          last_match_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          keyword?: string
          description?: string | null
          is_active?: boolean
          match_type?: 'exact' | 'partial' | 'fuzzy'
          jobs_matched?: number
          last_match_at?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      knowledge_base_documents: {
        Row: {
          id: string
          user_id: string
          filename: string
          file_type: 'pdf' | 'docx' | 'txt'
          file_size_bytes: number
          file_url: string | null
          collection: 'case_studies' | 'team_profiles' | 'portfolio' | 'other'
          processing_status: 'pending' | 'processing' | 'completed' | 'failed'
          processing_error: string | null
          chunk_count: number
          token_count: number
          embedding_model: string | null
          chroma_collection_name: string | null
          retrieval_count: number
          last_retrieved_at: string | null
          uploaded_at: string
          processed_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          filename: string
          file_type: 'pdf' | 'docx' | 'txt'
          file_size_bytes: number
          file_url?: string | null
          collection: 'case_studies' | 'team_profiles' | 'portfolio' | 'other'
          processing_status?: 'pending' | 'processing' | 'completed' | 'failed'
          processing_error?: string | null
          chunk_count?: number
          token_count?: number
          embedding_model?: string | null
          chroma_collection_name?: string | null
          retrieval_count?: number
          last_retrieved_at?: string | null
          uploaded_at?: string
          processed_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          filename?: string
          file_type?: 'pdf' | 'docx' | 'txt'
          file_size_bytes?: number
          file_url?: string | null
          collection?: 'case_studies' | 'team_profiles' | 'portfolio' | 'other'
          processing_status?: 'pending' | 'processing' | 'completed' | 'failed'
          processing_error?: string | null
          chunk_count?: number
          token_count?: number
          embedding_model?: string | null
          chroma_collection_name?: string | null
          retrieval_count?: number
          last_retrieved_at?: string | null
          uploaded_at?: string
          processed_at?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      user_session_states: {
        Row: {
          id: string
          user_id: string
          active_feature: 'projects' | 'proposals' | 'keywords' | 'analytics' | 'knowledge-base' | 'settings' | 'strategies' | 'dashboard' | null
          entity_id: string | null
          context_data: Record<string, any>
          navigation_history: Record<string, any>[]
          last_activity_at: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          active_feature?: 'projects' | 'proposals' | 'keywords' | 'analytics' | 'knowledge-base' | 'settings' | 'strategies' | 'dashboard' | null
          entity_id?: string | null
          context_data?: Record<string, any>
          navigation_history?: Record<string, any>[]
          last_activity_at?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          active_feature?: 'projects' | 'proposals' | 'keywords' | 'analytics' | 'knowledge-base' | 'settings' | 'strategies' | 'dashboard' | null
          entity_id?: string | null
          context_data?: Record<string, any>
          navigation_history?: Record<string, any>[]
          last_activity_at?: string
          created_at?: string
          updated_at?: string
        }
      }
      draft_work: {
        Row: {
          id: string
          user_id: string
          entity_type: 'proposal' | 'project' | 'keyword' | 'knowledge_document' | 'strategy'
          entity_id: string | null
          draft_data: Record<string, any>
          draft_version: number
          auto_save_count: number
          last_auto_save_at: string | null
          is_recovered: boolean
          recovered_at: string | null
          expires_at: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          entity_type: 'proposal' | 'project' | 'keyword' | 'knowledge_document' | 'strategy'
          entity_id?: string | null
          draft_data: Record<string, any>
          draft_version?: number
          auto_save_count?: number
          last_auto_save_at?: string | null
          is_recovered?: boolean
          recovered_at?: string | null
          expires_at?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          entity_type?: 'proposal' | 'project' | 'keyword' | 'knowledge_document' | 'strategy'
          entity_id?: string | null
          draft_data?: Record<string, any>
          draft_version?: number
          auto_save_count?: number
          last_auto_save_at?: string | null
          is_recovered?: boolean
          recovered_at?: string | null
          expires_at?: string
          created_at?: string
          updated_at?: string
        }
      }
      workflow_analytics: {
        Row: {
          id: string
          user_id: string | null
          event_type: string
          event_category: 'performance' | 'user_action' | 'error' | 'recovery' | null
          duration_ms: number | null
          success: boolean | null
          error_message: string | null
          metadata: Record<string, any>
          user_agent: string | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id?: string | null
          event_type: string
          event_category?: 'performance' | 'user_action' | 'error' | 'recovery' | null
          duration_ms?: number | null
          success?: boolean | null
          error_message?: string | null
          metadata?: Record<string, any>
          user_agent?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string | null
          event_type?: string
          event_category?: 'performance' | 'user_action' | 'error' | 'recovery' | null
          duration_ms?: number | null
          success?: boolean | null
          error_message?: string | null
          metadata?: Record<string, any>
          user_agent?: string | null
          created_at?: string
        }
      }
    }
    Views: Record<string, never>
    Functions: Record<string, never>
    Enums: Record<string, never>
  }
}
