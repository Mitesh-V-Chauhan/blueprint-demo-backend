import json
import logging
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, HumanMessage

from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentContext

logger = logging.getLogger(__name__)

class RequirementsAgent(BaseAgent):
    """Agent specialized in analyzing project requirements and generating clarifying questions"""
    
    def __init__(self, api_key_index: int = 2):
        super().__init__(AgentType.REQUIREMENTS, api_key_index)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define requirements-specific tools"""
        return [
            {
                "name": "generate_questions",
                "description": "Generate clarifying questions based on project description",
                "parameters": {
                    "project_description": "str",
                    "user_profile": "dict"
                }
            },
            {
                "name": "analyze_requirements",
                "description": "Analyze and categorize project requirements",
                "parameters": {
                    "requirements": "str",
                    "context": "dict"
                }
            },
            {
                "name": "validate_completeness",
                "description": "Validate if requirements are complete enough for development",
                "parameters": {
                    "requirements": "dict"
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """Get requirements agent system prompt"""
        return """You are the Requirements Analysis Agent for an AI Blueprint Generator system. Your role is to:

1. ANALYZE project descriptions and extract core requirements
2. GENERATE targeted clarifying questions to fill knowledge gaps
3. CATEGORIZE requirements by type (functional, non-functional, technical)
4. VALIDATE requirement completeness for development readiness
5. IDENTIFY potential challenges and constraints

Your Expertise:
- Software requirement analysis and elicitation
- User story creation and acceptance criteria
- Risk identification and mitigation planning
- Technology constraint analysis
- Scope definition and boundary setting

Question Generation Rules:
1. Generate exactly 3 concise, specific questions
2. Focus on critical unknowns that impact architecture
3. Prioritize: core functionality, target users, technical constraints
4. Avoid generic questions - make them project-specific
5. Each question should unlock different aspects of the project

Response Format:
Always respond with a JSON object containing:
{
    "clarifying_questions": ["question1", "question2", "question3"],
    "requirement_analysis": {
        "functional_requirements": ["req1", "req2"],
        "non_functional_requirements": ["req1", "req2"],
        "technical_constraints": ["constraint1", "constraint2"],
        "user_personas": ["persona1", "persona2"],
        "success_criteria": ["criteria1", "criteria2"]
    },
    "risk_assessment": {
        "high_risk": ["risk1"],
        "medium_risk": ["risk2"],
        "mitigation_strategies": ["strategy1"]
    },
    "completeness_score": 0.7,
    "next_steps": ["step1", "step2"]
}

Quality Standards:
- Questions must be answerable by the user
- Analysis must be specific to the project domain
- Risk assessment should be realistic and actionable
- Completeness score should reflect actual readiness (0.0-1.0)
"""
    
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        """Process requirements analysis request"""
        try:
            # Get project data
            project_data = context.project_data
            initial_idea = project_data.get("initial_idea", "")
            user_profile = project_data.get("user_profile", {})
            user_answers = project_data.get("user_answers", [])
            
            if not initial_idea:
                return {
                    "message": "No project description provided",
                    "action_taken": "error",
                    "error": "Missing initial idea"
                }
            
            # Build context prompt
            context_prompt = self._build_context_prompt(context)
            
            # Determine if we need to generate questions or analyze existing answers
            if not user_answers:
                # Generate clarifying questions
                result = await self._generate_clarifying_questions(initial_idea, user_profile, context_prompt)
            else:
                # Analyze complete requirements
                result = await self._analyze_complete_requirements(initial_idea, user_answers, user_profile, context_prompt)
            
            return {
                "message": result.get("message", "Requirements analysis completed"),
                "action_taken": result.get("action_taken", "requirements_analysis"),
                "clarifying_questions": result.get("clarifying_questions", []),
                "requirement_analysis": result.get("requirement_analysis", {}),
                "risk_assessment": result.get("risk_assessment", {}),
                "completeness_score": result.get("completeness_score", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error processing requirements request: {e}")
            return {
                "message": f"Error in requirements analysis: {str(e)}",
                "action_taken": "error",
                "error": str(e)
            }
    
    async def _generate_clarifying_questions(self, initial_idea: str, user_profile: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate clarifying questions for initial project idea"""
        try:
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"""
Project Description: "{initial_idea}"

User Profile:
{json.dumps(user_profile, indent=2)}

Context:
{context}

Generate exactly 3 specific clarifying questions that will help determine:
1. Core functionality and key features
2. Target audience and use cases  
3. Technical preferences and constraints

Make questions specific to this project, not generic. Focus on critical unknowns that will impact the technical architecture and development approach.
""")
            ]
            
            response = await self._invoke_llm(messages)
            analysis = self._extract_json_from_response(response)
            
            if not analysis or "clarifying_questions" not in analysis:
                # Fallback question generation
                analysis = self._generate_fallback_questions(initial_idea, user_profile)
            
            # Ensure we have exactly 3 questions
            questions = analysis.get("clarifying_questions", [])
            if len(questions) != 3:
                questions = self._ensure_three_questions(questions, initial_idea)
            
            return {
                "message": f"Generated {len(questions)} clarifying questions to better understand your project requirements.",
                "action_taken": "question_generation",
                "clarifying_questions": questions,
                "requirement_analysis": analysis.get("requirement_analysis", {}),
                "completeness_score": 0.3  # Initial idea only
            }
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._generate_fallback_questions(initial_idea, user_profile)
    
    async def _analyze_complete_requirements(self, initial_idea: str, user_answers: List[str], 
                                           user_profile: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Analyze complete requirements with user answers"""
        try:
            # Build Q&A context
            qa_pairs = []
            default_questions = [
                "What are the main features you want in your application?",
                "Who is your target audience for this project?", 
                "Do you have any specific technical requirements or constraints?"
            ]
            
            for i, answer in enumerate(user_answers):
                question = default_questions[i] if i < len(default_questions) else f"Question {i+1}"
                qa_pairs.append(f"Q: {question}\nA: {answer}")
            
            qa_text = "\n\n".join(qa_pairs)
            
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"""
Project Description: "{initial_idea}"

User Profile:
{json.dumps(user_profile, indent=2)}

User Answers to Clarifying Questions:
{qa_text}

Context:
{context}

Now perform a comprehensive requirements analysis. Categorize requirements, assess risks, and determine development readiness. Provide a completeness score from 0.0 to 1.0.
""")
            ]
            
            response = await self._invoke_llm(messages)
            analysis = self._extract_json_from_response(response)
            
            if not analysis:
                analysis = self._generate_fallback_analysis(initial_idea, user_answers)
            
            # Calculate completeness score
            completeness = self._calculate_completeness_score(analysis, user_answers)
            analysis["completeness_score"] = completeness
            
            return {
                "message": f"Completed comprehensive requirements analysis. Project readiness: {int(completeness * 100)}%",
                "action_taken": "complete_analysis",
                "requirement_analysis": analysis.get("requirement_analysis", {}),
                "risk_assessment": analysis.get("risk_assessment", {}),
                "completeness_score": completeness,
                "next_steps": analysis.get("next_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing complete requirements: {e}")
            return self._generate_fallback_analysis(initial_idea, user_answers)
    
    def _generate_fallback_questions(self, initial_idea: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback questions when LLM fails"""
        # Analyze project type based on keywords
        idea_lower = initial_idea.lower()
        
        if any(word in idea_lower for word in ['app', 'mobile', 'ios', 'android']):
            questions = [
                "What are the core features users should be able to perform in your app?",
                "Will this be a native mobile app, web app, or cross-platform solution?",
                "Do you need user authentication, data storage, or third-party integrations?"
            ]
        elif any(word in idea_lower for word in ['website', 'web', 'blog', 'ecommerce']):
            questions = [
                "What type of content or functionality will your website provide?",
                "Who is your target audience and what devices will they use?",
                "Do you need a content management system, user accounts, or payment processing?"
            ]
        elif any(word in idea_lower for word in ['api', 'backend', 'service', 'microservice']):
            questions = [
                "What data will your API manage and what operations should it support?",
                "What applications or services will consume this API?",
                "Do you have specific performance, security, or scalability requirements?"
            ]
        else:
            # Generic questions
            questions = [
                "What are the 3 most important features your solution must have?",
                "Who will be using this system and what are their technical skill levels?",
                "Are there any specific technologies, platforms, or constraints you prefer?"
            ]
        
        return {
            "message": "Generated clarifying questions to understand your project better.",
            "action_taken": "fallback_question_generation",
            "clarifying_questions": questions,
            "completeness_score": 0.3
        }
    
    def _ensure_three_questions(self, questions: List[str], initial_idea: str) -> List[str]:
        """Ensure exactly 3 questions are returned"""
        if len(questions) >= 3:
            return questions[:3]
        
        # Add generic questions to reach 3
        generic_questions = [
            "What are the main features you want to implement?",
            "Who is your target audience for this project?",
            "Do you have any technical preferences or constraints?",
            "What platforms should this solution support?",
            "Are there any specific integrations or third-party services needed?"
        ]
        
        while len(questions) < 3:
            for generic_q in generic_questions:
                if generic_q not in questions:
                    questions.append(generic_q)
                    break
            if len(questions) >= 3:
                break
        
        return questions[:3]
    
    def _generate_fallback_analysis(self, initial_idea: str, user_answers: List[str]) -> Dict[str, Any]:
        """Generate fallback analysis when LLM fails"""
        return {
            "requirement_analysis": {
                "functional_requirements": [
                    "Core functionality as described in project idea",
                    "User interface for primary interactions"
                ],
                "non_functional_requirements": [
                    "Reliable performance",
                    "User-friendly interface",
                    "Secure data handling"
                ],
                "technical_constraints": [],
                "user_personas": ["Primary user"],
                "success_criteria": [
                    "Implements core functionality",
                    "Meets user expectations"
                ]
            },
            "risk_assessment": {
                "high_risk": [],
                "medium_risk": ["Unclear requirements", "Technology selection"],
                "mitigation_strategies": [
                    "Iterative development approach",
                    "Regular user feedback"
                ]
            },
            "completeness_score": 0.6,
            "next_steps": [
                "Finalize technical architecture",
                "Create detailed project plan"
            ]
        }
    
    def _calculate_completeness_score(self, analysis: Dict[str, Any], user_answers: List[str]) -> float:
        """Calculate requirement completeness score"""
        score = 0.0
        
        # Base score for having answers
        if user_answers:
            score += 0.4
        
        # Additional points for detailed analysis
        req_analysis = analysis.get("requirement_analysis", {})
        
        if req_analysis.get("functional_requirements"):
            score += 0.2
        
        if req_analysis.get("technical_constraints"):
            score += 0.1
        
        if req_analysis.get("user_personas"):
            score += 0.1
        
        if req_analysis.get("success_criteria"):
            score += 0.1
        
        # Points for risk assessment
        risk_assessment = analysis.get("risk_assessment", {})
        if risk_assessment.get("mitigation_strategies"):
            score += 0.1
        
        return min(score, 1.0)