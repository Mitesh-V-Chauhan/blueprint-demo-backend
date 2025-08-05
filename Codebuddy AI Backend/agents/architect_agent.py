import json
import logging
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, HumanMessage

from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentContext

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """Agent specialized in designing technical architecture and recommending tech stacks"""
    
    def __init__(self, api_key_index: int = 3):
        super().__init__(AgentType.ARCHITECT, api_key_index)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define architect-specific tools"""
        return [
            {
                "name": "analyze_requirements",
                "description": "Analyze requirements to determine architectural needs",
                "parameters": {
                    "requirements": "dict",
                    "constraints": "dict"
                }
            },
            {
                "name": "recommend_tech_stack",
                "description": "Recommend optimal technology stack",
                "parameters": {
                    "project_type": "str",
                    "requirements": "dict",
                    "user_preferences": "dict"
                }
            },
            {
                "name": "design_architecture",
                "description": "Design system architecture patterns",
                "parameters": {
                    "tech_stack": "dict",
                    "requirements": "dict"
                }
            },
            {
                "name": "assess_scalability",
                "description": "Assess scalability requirements and solutions",
                "parameters": {
                    "architecture": "dict",
                    "expected_load": "str"
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """Get architect system prompt"""
        return """You are the Technical Architecture Agent for an AI Blueprint Generator system. Your role is to:

1. ANALYZE project requirements to determine architectural needs
2. RECOMMEND optimal technology stacks based on project goals
3. DESIGN scalable system architectures and patterns
4. CONSIDER performance, security, and maintainability factors
5. PROVIDE detailed justifications for architectural decisions

Your Expertise:
- Modern software architecture patterns (microservices, serverless, MVC, etc.)
- Frontend frameworks (React, Vue, Angular, Next.js, etc.)
- Backend technologies (Node.js, Python, Java, .NET, Go, etc.)
- Databases (SQL, NoSQL, vector databases, caching solutions)
- Cloud platforms (AWS, Azure, GCP, Vercel, Netlify)
- DevOps and deployment strategies
- Security best practices
- Performance optimization
- Scalability planning

Tech Stack Selection Criteria:
1. Project complexity and requirements
2. Team experience and preferences
3. Development speed vs. performance needs
4. Scalability and maintenance requirements
5. Budget and resource constraints
6. Community support and ecosystem
7. Future growth and evolution potential

Response Format:
Always respond with a JSON object containing:
{
    "tech_stack": {
        "frontend": {
            "framework": "React",
            "language": "TypeScript", 
            "styling": "Tailwind CSS",
            "state_management": "Zustand",
            "build_tool": "Vite"
        },
        "backend": {
            "framework": "FastAPI",
            "language": "Python",
            "database": "PostgreSQL",
            "cache": "Redis",
            "auth": "Auth0"
        },
        "deployment": {
            "frontend": "Vercel",
            "backend": "Railway",
            "database": "Neon",
            "cdn": "Cloudflare"
        },
        "additional_tools": ["Docker", "GitHub Actions", "Sentry"]
    },
    "architecture_pattern": "Full-stack web application with API-first design",
    "justification": "Detailed explanation of technology choices and architectural decisions",
    "alternatives": {
        "frontend": ["Vue.js + Nuxt.js", "Angular + TypeScript"],
        "backend": ["Node.js + Express", "Java + Spring Boot"],
        "database": ["MongoDB", "MySQL"]
    },
    "scalability_plan": {
        "immediate": ["Vertical scaling", "CDN implementation"],
        "future": ["Microservices migration", "Load balancing"]
    },
    "security_considerations": ["Authentication", "Data encryption", "API security"],
    "development_workflow": ["Git workflow", "CI/CD pipeline", "Testing strategy"],
    "estimated_complexity": "Medium",
    "development_timeline": "8-12 weeks"
}

Quality Standards:
- Recommendations must be practical and well-justified
- Consider both current needs and future scalability
- Balance complexity with development speed
- Provide clear alternatives and trade-offs
- Include security and performance considerations
"""
    
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        """Process architecture design request"""
        try:
            # Get project data
            project_data = context.project_data
            full_context = project_data.get("full_context", "")
            user_profile = project_data.get("user_profile", {})
            requirement_analysis = project_data.get("requirement_analysis", {})
            
            if not full_context:
                return {
                    "message": "Insufficient project context for architecture design",
                    "action_taken": "error",
                    "error": "Missing project context"
                }
            
            # Build context for architecture design
            context_prompt = self._build_context_prompt(context)
            
            # Design architecture and recommend tech stack
            result = await self._design_architecture(full_context, user_profile, requirement_analysis, context_prompt)
            
            return {
                "message": result.get("message", "Architecture design completed"),
                "action_taken": "architecture_design",
                "tech_stack": result.get("tech_stack", {}),
                "architecture_pattern": result.get("architecture_pattern", ""),
                "justification": result.get("justification", ""),
                "alternatives": result.get("alternatives", {}),
                "scalability_plan": result.get("scalability_plan", {}),
                "estimated_complexity": result.get("estimated_complexity", "Medium")
            }
            
        except Exception as e:
            logger.error(f"Error processing architecture request: {e}")
            return {
                "message": f"Error in architecture design: {str(e)}",
                "action_taken": "error",
                "error": str(e)
            }
    
    async def _design_architecture(self, full_context: str, user_profile: Dict[str, Any], 
                                 requirement_analysis: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Design system architecture and recommend tech stack"""
        try:
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"""
Project Context:
{full_context}

User Profile:
- Experience Level: {user_profile.get('experience_level', 'Intermediate')}
- Preferred Technologies: {user_profile.get('favorite_tech_stack', [])}
- Team Size: {user_profile.get('team_size', 'Unknown')}
- Company Size: {user_profile.get('company_size', 'Unknown')}

Requirements Analysis:
{json.dumps(requirement_analysis, indent=2)}

Additional Context:
{context}

Design a comprehensive technical architecture for this project. Consider:

1. PROJECT TYPE: Analyze if this is a web app, mobile app, API, desktop app, etc.
2. COMPLEXITY: Assess the technical complexity and scope
3. SCALABILITY: Determine current and future scaling needs
4. USER EXPERIENCE: Frontend requirements and user interaction patterns
5. DATA REQUIREMENTS: Database and data management needs
6. INTEGRATION NEEDS: Third-party services and APIs
7. DEPLOYMENT: Hosting and deployment strategy
8. TEAM CAPABILITIES: Match recommendations to team experience

Provide a detailed, practical architecture recommendation with clear justifications for each technology choice.
""")
            ]
            
            response = await self._invoke_llm(messages)
            architecture = self._extract_json_from_response(response)
            
            if not architecture or "tech_stack" not in architecture:
                # Generate fallback architecture
                architecture = self._generate_fallback_architecture(full_context, user_profile)
            
            # Enhance with additional analysis
            architecture = self._enhance_architecture_analysis(architecture, full_context, user_profile)
            
            return {
                "message": f"Designed {architecture.get('architecture_pattern', 'modern')} architecture with {architecture.get('estimated_complexity', 'medium')} complexity",
                "tech_stack": architecture.get("tech_stack", {}),
                "architecture_pattern": architecture.get("architecture_pattern", ""),
                "justification": architecture.get("justification", ""),
                "alternatives": architecture.get("alternatives", {}),
                "scalability_plan": architecture.get("scalability_plan", {}),
                "security_considerations": architecture.get("security_considerations", []),
                "development_workflow": architecture.get("development_workflow", []),
                "estimated_complexity": architecture.get("estimated_complexity", "Medium"),
                "development_timeline": architecture.get("development_timeline", "8-12 weeks")
            }
            
        except Exception as e:
            logger.error(f"Error designing architecture: {e}")
            return self._generate_fallback_architecture(full_context, user_profile)
    
    def _generate_fallback_architecture(self, full_context: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback architecture when LLM fails"""
        # Analyze project type from context
        context_lower = full_context.lower()
        
        # Determine project type and complexity
        if any(word in context_lower for word in ['mobile', 'app', 'ios', 'android']):
            return self._get_mobile_architecture()
        elif any(word in context_lower for word in ['api', 'backend', 'service', 'microservice']):
            return self._get_api_architecture()
        elif any(word in context_lower for word in ['dashboard', 'admin', 'analytics']):
            return self._get_dashboard_architecture()
        elif any(word in context_lower for word in ['ecommerce', 'shop', 'store', 'payment']):
            return self._get_ecommerce_architecture()
        else:
            return self._get_web_app_architecture()
    
    def _get_web_app_architecture(self) -> Dict[str, Any]:
        """Default web application architecture"""
        return {
            "tech_stack": {
                "frontend": {
                    "framework": "React",
                    "language": "TypeScript",
                    "styling": "Tailwind CSS",
                    "state_management": "Zustand",
                    "build_tool": "Vite"
                },
                "backend": {
                    "framework": "FastAPI",
                    "language": "Python",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "auth": "Auth0"
                },
                "deployment": {
                    "frontend": "Vercel",
                    "backend": "Railway",
                    "database": "Neon",
                    "cdn": "Cloudflare"
                },
                "additional_tools": ["Docker", "GitHub Actions", "Sentry"]
            },
            "architecture_pattern": "Full-stack web application with API-first design",
            "justification": "Modern stack optimized for development speed and scalability. React provides excellent UI capabilities, FastAPI offers high-performance backend with great documentation, PostgreSQL ensures data reliability.",
            "alternatives": {
                "frontend": ["Vue.js + Nuxt.js", "Angular + TypeScript"],
                "backend": ["Node.js + Express", "Django + REST"],
                "database": ["MongoDB", "MySQL"]
            },
            "estimated_complexity": "Medium",
            "development_timeline": "8-12 weeks"
        }
    
    def _get_mobile_architecture(self) -> Dict[str, Any]:
        """Mobile application architecture"""
        return {
            "tech_stack": {
                "frontend": {
                    "framework": "React Native",
                    "language": "TypeScript",
                    "navigation": "React Navigation",
                    "state_management": "Redux Toolkit",
                    "ui_library": "NativeBase"
                },
                "backend": {
                    "framework": "FastAPI",
                    "language": "Python",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "auth": "Firebase Auth"
                },
                "deployment": {
                    "app_store": "App Store & Google Play",
                    "backend": "Railway",
                    "database": "Neon",
                    "push_notifications": "Firebase"
                },
                "additional_tools": ["Expo", "CodePush", "Crashlytics"]
            },
            "architecture_pattern": "Cross-platform mobile app with REST API backend",
            "justification": "React Native allows code sharing between iOS and Android, reducing development time. FastAPI backend provides excellent performance for mobile API needs.",
            "estimated_complexity": "High",
            "development_timeline": "12-16 weeks"
        }
    
    def _get_api_architecture(self) -> Dict[str, Any]:
        """API-focused architecture"""
        return {
            "tech_stack": {
                "backend": {
                    "framework": "FastAPI",
                    "language": "Python",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "auth": "JWT",
                    "documentation": "OpenAPI/Swagger"
                },
                "deployment": {
                    "api": "Railway",
                    "database": "Neon",
                    "cache": "Redis Cloud",
                    "monitoring": "DataDog"
                },
                "additional_tools": ["Docker", "GitHub Actions", "Postman"]
            },
            "architecture_pattern": "RESTful API with microservices potential",
            "justification": "FastAPI provides excellent performance, automatic documentation, and async support. PostgreSQL offers reliability for data storage, Redis enables efficient caching.",
            "estimated_complexity": "Medium",
            "development_timeline": "6-10 weeks"
        }
    
    def _get_dashboard_architecture(self) -> Dict[str, Any]:
        """Dashboard/analytics architecture"""
        return {
            "tech_stack": {
                "frontend": {
                    "framework": "React",
                    "language": "TypeScript",
                    "ui_library": "Ant Design",
                    "charts": "Recharts",
                    "state_management": "React Query"
                },
                "backend": {
                    "framework": "FastAPI",
                    "language": "Python",
                    "database": "PostgreSQL",
                    "analytics": "ClickHouse",
                    "cache": "Redis"
                },
                "deployment": {
                    "frontend": "Vercel",
                    "backend": "Railway",
                    "database": "Neon",
                    "analytics": "ClickHouse Cloud"
                }
            },
            "architecture_pattern": "Analytics dashboard with real-time data processing",
            "justification": "Optimized for data visualization and analytics. ClickHouse provides excellent performance for analytical queries, Recharts offers rich visualization capabilities.",
            "estimated_complexity": "High",
            "development_timeline": "10-14 weeks"
        }
    
    def _get_ecommerce_architecture(self) -> Dict[str, Any]:
        """E-commerce architecture"""
        return {
            "tech_stack": {
                "frontend": {
                    "framework": "Next.js",
                    "language": "TypeScript",
                    "styling": "Tailwind CSS",
                    "state_management": "Zustand",
                    "payments": "Stripe Elements"
                },
                "backend": {
                    "framework": "FastAPI",
                    "language": "Python",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "payments": "Stripe",
                    "search": "Elasticsearch"
                },
                "deployment": {
                    "frontend": "Vercel",
                    "backend": "Railway",
                    "database": "Neon",
                    "cdn": "Cloudflare",
                    "images": "Cloudinary"
                },
                "additional_tools": ["Docker", "GitHub Actions", "Sentry", "Algolia"]
            },
            "architecture_pattern": "E-commerce platform with payment processing and inventory management",
            "justification": "Next.js provides excellent SEO and performance for e-commerce. Stripe handles secure payments, Elasticsearch enables fast product search, Redis caches frequently accessed data.",
            "estimated_complexity": "High",
            "development_timeline": "14-20 weeks"
        }
    
    def _enhance_architecture_analysis(self, architecture: Dict[str, Any], 
                                     full_context: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance architecture with additional analysis"""
        
        # Add security considerations if missing
        if "security_considerations" not in architecture:
            architecture["security_considerations"] = [
                "Authentication and authorization",
                "Data encryption in transit and at rest",
                "Input validation and sanitization",
                "API rate limiting",
                "Security headers implementation"
            ]
        
        # Add development workflow if missing
        if "development_workflow" not in architecture:
            architecture["development_workflow"] = [
                "Git-based version control",
                "Feature branch workflow",
                "Automated testing pipeline",
                "Code review process",
                "Continuous integration/deployment"
            ]
        
        # Add scalability plan if missing
        if "scalability_plan" not in architecture:
            architecture["scalability_plan"] = {
                "immediate": [
                    "Horizontal database scaling",
                    "CDN implementation",
                    "Caching strategy"
                ],
                "future": [
                    "Microservices architecture",
                    "Load balancing",
                    "Database sharding"
                ]
            }
        
        # Adjust complexity based on context
        context_lower = full_context.lower()
        if any(word in context_lower for word in ['simple', 'basic', 'minimal']):
            architecture["estimated_complexity"] = "Low"
            architecture["development_timeline"] = "4-8 weeks"
        elif any(word in context_lower for word in ['complex', 'enterprise', 'advanced', 'sophisticated']):
            architecture["estimated_complexity"] = "High"
            architecture["development_timeline"] = "12-20 weeks"
        
        # Consider user experience level
        experience = user_profile.get('experience_level', '').lower()
        if experience == 'beginner':
            # Suggest simpler alternatives
            if "alternatives" in architecture:
                architecture["alternatives"]["simplified"] = [
                    "WordPress + Custom Theme",
                    "Webflow + Custom Code",
                    "Firebase + React"
                ]
        
        return architecture
    
    def _determine_project_type(self, context: str) -> str:
        """Determine project type from context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['mobile', 'app', 'ios', 'android']):
            return "mobile_app"
        elif any(word in context_lower for word in ['api', 'backend', 'service']):
            return "api_service"
        elif any(word in context_lower for word in ['dashboard', 'admin', 'analytics']):
            return "dashboard"
        elif any(word in context_lower for word in ['ecommerce', 'shop', 'store']):
            return "ecommerce"
        elif any(word in context_lower for word in ['blog', 'cms', 'content']):
            return "content_site"
        elif any(word in context_lower for word in ['game', 'gaming']):
            return "game"
        else:
            return "web_app"
    
    def _calculate_complexity_score(self, requirements: Dict[str, Any], context: str) -> str:
        """Calculate project complexity"""
        complexity_points = 0
        
        # Check functional requirements
        functional_reqs = requirements.get("functional_requirements", [])
        complexity_points += len(functional_reqs) * 0.5
        
        # Check for complex features
        context_lower = context.lower()
        complex_features = [
            'authentication', 'payment', 'real-time', 'machine learning',
            'ai', 'analytics', 'search', 'notification', 'integration'
        ]
        
        for feature in complex_features:
            if feature in context_lower:
                complexity_points += 1
        
        # Check for scalability requirements
        if any(word in context_lower for word in ['scale', 'million', 'thousands']):
            complexity_points += 2
        
        # Determine complexity level
        if complexity_points <= 3:
            return "Low"
        elif complexity_points <= 6:
            return "Medium"
        else:
            return "High"