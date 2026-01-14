from typing import Optional, Dict, List
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from app.services.vector_store import vector_store_service
import re


class ProposalService:
    """Service for generating proposals using LangChain and RAG."""
    
    def __init__(self):
        """Initialize the proposal service."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def analyze_job_requirements(self, description: str) -> Dict:
        """Analyze job requirements using AI."""
        
        system_prompt = """You are an expert job requirement analyzer. 
        Analyze the job description and extract:
        1. Key requirements
        2. Technologies mentioned
        3. Required skills
        4. Estimated complexity (Low/Medium/High)
        
        Format your response as JSON."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze this job description:\n\n{description}")
        ]
        
        try:
            response = self.llm(messages)
            
            # Parse response
            key_requirements = self._extract_requirements(description)
            technologies = self._extract_technologies(description)
            skills = self._extract_skills(description)
            complexity = self._estimate_complexity(description)
            
            return {
                "key_requirements": key_requirements,
                "technologies": technologies,
                "skills": skills,
                "estimated_complexity": complexity,
                "match_score": 0.8
            }
        except Exception as e:
            # Fallback to basic extraction if LLM fails
            return {
                "key_requirements": self._extract_requirements(description),
                "technologies": self._extract_technologies(description),
                "skills": self._extract_skills(description),
                "estimated_complexity": "Medium",
                "match_score": None
            }
    
    def generate_proposal(
        self, 
        job_title: str,
        job_description: str,
        requirements: List[str],
        user_profile: Optional[Dict] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict:
        """Generate a proposal using RAG."""
        
        # Retrieve relevant context from vector store
        query = f"{job_title} {job_description}"
        relevant_docs = vector_store_service.similarity_search(query, k=3)
        
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Build prompt
        system_prompt = """You are an expert proposal writer. 
        Create a compelling, professional proposal for the job posting.
        
        Guidelines:
        - Be specific and demonstrate understanding of requirements
        - Highlight relevant experience
        - Be concise but thorough
        - Use professional tone
        - Include a clear call to action
        """
        
        user_info = ""
        if user_profile:
            user_info = f"\n\nUser Profile:\n{self._format_profile(user_profile)}"
        
        custom_info = ""
        if custom_instructions:
            custom_info = f"\n\nCustom Instructions:\n{custom_instructions}"
        
        relevant_context = ""
        if context:
            relevant_context = f"\n\nRelevant Experience/Knowledge:\n{context}"
        
        human_prompt = f"""Job Title: {job_title}

Job Description:
{job_description}

Requirements:
{chr(10).join(['- ' + req for req in requirements])}
{user_info}{custom_info}{relevant_context}

Generate a professional proposal for this job."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.llm(messages)
            proposal_text = response.content
            
            return {
                "proposal": proposal_text,
                "confidence_score": 0.85,
                "suggestions": [
                    "Consider adding specific examples of similar projects",
                    "Mention your availability and timeline",
                    "Include links to portfolio or previous work"
                ],
                "sources": [doc.metadata.get("source", "knowledge_base") for doc in relevant_docs]
            }
        except Exception as e:
            # Fallback proposal
            return {
                "proposal": self._generate_fallback_proposal(job_title, job_description, requirements),
                "confidence_score": 0.5,
                "suggestions": [
                    "AI service unavailable - this is a template proposal",
                    "Please customize based on your experience"
                ],
                "sources": []
            }
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract key requirements from text."""
        requirements = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or 'require' in line.lower():
                requirements.append(line.lstrip('-•* '))
        
        return requirements[:5] if requirements else ["General development skills"]
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technologies mentioned in text."""
        common_tech = [
            'python', 'javascript', 'typescript', 'react', 'nextjs', 'vue',
            'angular', 'node', 'fastapi', 'django', 'flask', 'aws', 'azure',
            'docker', 'kubernetes', 'postgresql', 'mongodb', 'redis', 'langchain',
            'llama-index', 'openai', 'tensorflow', 'pytorch'
        ]
        
        text_lower = text.lower()
        technologies = []
        
        for tech in common_tech:
            if tech in text_lower:
                technologies.append(tech.capitalize())
        
        return technologies[:10]
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        common_skills = [
            'api development', 'frontend', 'backend', 'full-stack',
            'machine learning', 'ai', 'database design', 'testing',
            'deployment', 'agile', 'scrum', 'communication'
        ]
        
        text_lower = text.lower()
        skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        return skills[:8] if skills else ["Software Development"]
    
    def _estimate_complexity(self, text: str) -> str:
        """Estimate project complexity."""
        complexity_indicators = {
            'high': ['complex', 'enterprise', 'scalable', 'microservices', 'distributed'],
            'low': ['simple', 'basic', 'small', 'quick', 'straightforward']
        }
        
        text_lower = text.lower()
        
        for indicator in complexity_indicators['high']:
            if indicator in text_lower:
                return "High"
        
        for indicator in complexity_indicators['low']:
            if indicator in text_lower:
                return "Low"
        
        return "Medium"
    
    def _format_profile(self, profile: Dict) -> str:
        """Format user profile for prompt."""
        return "\n".join([f"{k}: {v}" for k, v in profile.items()])
    
    def _generate_fallback_proposal(self, title: str, description: str, requirements: List[str]) -> str:
        """Generate a basic fallback proposal."""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {title} position. With my extensive experience in software development and a proven track record of delivering high-quality solutions, I am confident in my ability to exceed your expectations.

I have carefully reviewed your requirements:
{chr(10).join(['• ' + req for req in requirements[:5]])}

I am well-equipped to handle these requirements and deliver exceptional results. My approach includes:
- Thorough analysis and planning
- Regular communication and updates
- Quality-focused development
- Timely delivery

I would welcome the opportunity to discuss how my skills and experience align with your needs. I am available to start immediately and committed to delivering outstanding results.

Best regards"""


# Singleton instance
proposal_service = ProposalService()
