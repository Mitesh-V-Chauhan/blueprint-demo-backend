import json
import logging
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, HumanMessage

from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentContext

logger = logging.getLogger(__name__)

class DesignerAgent(BaseAgent):
    """Agent specialized in creating flowcharts and visual architecture diagrams"""
    
    def __init__(self, api_key_index: int = 4):
        super().__init__(AgentType.DESIGNER, api_key_index)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define designer-specific tools"""
        return [
            {
                "name": "create_flowchart",
                "description": "Create React Flow compatible flowchart",
                "parameters": {
                    "architecture": "dict",
                    "requirements": "dict"
                }
            },
            {
                "name": "design_user_flow", 
                "description": "Design user interaction flow",
                "parameters": {
                    "user_stories": "list",
                    "features": "list"
                }
            },
            {
                "name": "create_component_diagram",
                "description": "Create system component diagram",
                "parameters": {
                    "tech_stack": "dict",
                    "architecture_pattern": "str"
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """Get designer system prompt"""
        return """You are the Visual Design Agent for an AI Blueprint Generator system. Your role is to:

1. CREATE comprehensive React Flow compatible flowcharts
2. DESIGN user interaction flows and journeys
3. VISUALIZE system architecture and component relationships
4. ENSURE diagrams are both beautiful and functional
5. OPTIMIZE layouts for readability and understanding

Your Expertise:
- React Flow node and edge design
- System architecture visualization
- User experience flow mapping
- Component relationship modeling
- Modern design principles and aesthetics
- Information hierarchy and visual clarity

React Flow Requirements:
- All nodes must have unique IDs
- Positions must be well-spaced (minimum 150px apart)
- Use appropriate node types: input, output, default, custom
- Apply modern styling with gradients and shadows
- Include meaningful labels and descriptions
- Create logical connection flows
- Use proper edge types: default, smoothstep, step
- Add animations where appropriate

Node Styling Standards:
- Use gradient backgrounds for visual appeal
- Apply consistent color schemes by component type
- Include rounded corners (borderRadius: 12px)
- Add subtle shadows for depth
- Use proper typography hierarchy
- Include icons or emojis for visual identification

Response Format:
Always respond with a JSON object containing:
{
    "flowchart": {
        "nodes": [
            {
                "id": "unique-id",
                "type": "input|output|default",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Component Name",
                    "description": "Component description",
                    "features": ["feature1", "feature2"]
                },
                "style": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color": "white",
                    "border": "none",
                    "borderRadius": 12,
                    "padding": "10px 15px",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "boxShadow": "0 4px 15px rgba(102, 126, 234, 0.3)",
                    "minWidth": "140px",
                    "textAlign": "center"
                }
            }
        ],
        "edges": [
            {
                "id": "edge-id",
                "source": "source-node-id",
                "target": "target-node-id",
                "type": "smoothstep",
                "animated": true,
                "style": {
                    "stroke": "#667eea",
                    "strokeWidth": 3
                },
                "label": "Connection Type",
                "labelStyle": {
                    "fontSize": "12px",
                    "fontWeight": "500",
                    "color": "#4a5568"
                }
            }
        ]
    },
    "design_rationale": "Explanation of design decisions and layout choices",
    "user_flow_summary": "Summary of user interaction patterns",
    "component_relationships": "Explanation of how components interact"
}

Design Principles:
1. Start with user-facing components at the top
2. Flow logically from user input to data processing
3. Group related components visually
4. Use consistent color coding by layer/type
5. Ensure clear visual hierarchy
6. Make complex flows understandable at a glance
7. Include all major system components
8. Show both data flow and control flow where relevant
"""
    
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        """Process flowchart design request"""
        try:
            # Get project data
            project_data = context.project_data
            tech_stack = project_data.get("tech_stack", {})
            architecture_pattern = project_data.get("architecture_pattern", "")
            full_context = project_data.get("full_context", "")
            requirement_analysis = project_data.get("requirement_analysis", {})
            
            if not tech_stack and not full_context:
                return {
                    "message": "Insufficient data for flowchart design",
                    "action_taken": "error",
                    "error": "Missing tech stack or context"
                }
            
            # Build context for design
            context_prompt = self._build_context_prompt(context)
            
            # Create flowchart
            result = await self._create_architecture_flowchart(
                tech_stack, architecture_pattern, full_context, 
                requirement_analysis, context_prompt
            )
            
            return {
                "message": result.get("message", "Flowchart design completed"),
                "action_taken": "flowchart_creation",
                "flowchart": result.get("flowchart", {}),
                "design_rationale": result.get("design_rationale", ""),
                "user_flow_summary": result.get("user_flow_summary", ""),
                "component_relationships": result.get("component_relationships", "")
            }
            
        except Exception as e:
            logger.error(f"Error processing design request: {e}")
            return {
                "message": f"Error in flowchart design: {str(e)}",
                "action_taken": "error",
                "error": str(e)
            }
    
    async def _create_architecture_flowchart(self, tech_stack: Dict[str, Any], 
                                           architecture_pattern: str, full_context: str,
                                           requirement_analysis: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Create comprehensive architecture flowchart"""
        try:
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"""
Project Context:
{full_context}

Tech Stack:
{json.dumps(tech_stack, indent=2)}

Architecture Pattern: {architecture_pattern}

Requirements Analysis:
{json.dumps(requirement_analysis, indent=2)}

Additional Context:
{context}

Create a comprehensive, visually stunning React Flow compatible flowchart that shows:

1. USER INTERFACE LAYER: User entry points and interactions
2. BUSINESS LOGIC LAYER: Core application logic and processing
3. DATA LAYER: Databases, caching, and storage
4. EXTERNAL SERVICES: APIs, third-party integrations
5. INFRASTRUCTURE: Deployment and hosting components

Design Requirements:
- Use modern gradient styling with beautiful colors
- Position nodes with proper spacing (150px+ between nodes)
- Create logical flow from user interaction to data storage
- Include all major components from the tech stack
- Use appropriate node types and edge connections
- Add meaningful labels and descriptions
- Ensure the diagram tells the complete system story

Make this diagram both technically accurate and visually impressive!
""")
            ]
            
            response = await self._invoke_llm(messages)
            design = self._extract_json_from_response(response)
            
            if not design or "flowchart" not in design:
                # Generate fallback flowchart
                design = self._generate_fallback_flowchart(tech_stack, full_context)
            
            # Validate and enhance flowchart
            flowchart = self._validate_and_enhance_flowchart(design.get("flowchart", {}))
            
            return {
                "message": f"Created comprehensive architecture flowchart with {len(flowchart.get('nodes', []))} components and {len(flowchart.get('edges', []))} connections",
                "flowchart": flowchart,
                "design_rationale": design.get("design_rationale", "Modern layered architecture visualization"),
                "user_flow_summary": design.get("user_flow_summary", "User interactions flow through UI to business logic to data layer"),
                "component_relationships": design.get("component_relationships", "Components are organized by architectural layers")
            }
            
        except Exception as e:
            logger.error(f"Error creating flowchart: {e}")
            return self._generate_fallback_flowchart(tech_stack, full_context)
    
    def _generate_fallback_flowchart(self, tech_stack: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate fallback flowchart when LLM fails"""
        
        # Extract tech stack components
        frontend = tech_stack.get("frontend", {})
        backend = tech_stack.get("backend", {})
        deployment = tech_stack.get("deployment", {})
        
        nodes = []
        edges = []
        node_id = 1
        
        # User Interface Layer
        if frontend:
            ui_node = {
                "id": f"ui-{node_id}",
                "type": "input",
                "position": {"x": 100, "y": 50},
                "data": {
                    "label": f"🖥️ {frontend.get('framework', 'Frontend')}",
                    "description": "User Interface Layer",
                    "features": [frontend.get('language', 'JavaScript'), frontend.get('styling', 'CSS')]
                },
                "style": self._get_node_style("ui")
            }
            nodes.append(ui_node)
            node_id += 1
        
        # Business Logic Layer
        if backend:
            logic_node = {
                "id": f"logic-{node_id}",
                "type": "default",
                "position": {"x": 100, "y": 250},
                "data": {
                    "label": f"⚡ {backend.get('framework', 'Backend')}",
                    "description": "Business Logic Layer",
                    "features": [backend.get('language', 'Python'), "API Processing"]
                },
                "style": self._get_node_style("logic")
            }
            nodes.append(logic_node)
            
            # Connect UI to Logic
            if nodes:
                edges.append({
                    "id": f"ui-to-logic",
                    "source": nodes[0]["id"],
                    "target": logic_node["id"],
                    "type": "smoothstep",
                    "animated": True,
                    "style": {"stroke": "#667eea", "strokeWidth": 3},
                    "label": "User Requests"
                })
            node_id += 1
        
        # Database Layer
        if backend.get("database"):
            db_node = {
                "id": f"db-{node_id}",
                "type": "default",
                "position": {"x": 100, "y": 450},
                "data": {
                    "label": f"🗄️ {backend.get('database')}",
                    "description": "Data Storage Layer",
                    "features": ["Data Persistence", "Queries"]
                },
                "style": self._get_node_style("data")
            }
            nodes.append(db_node)
            
            # Connect Logic to Database
            if len(nodes) >= 2:
                edges.append({
                    "id": f"logic-to-db",
                    "source": nodes[1]["id"],
                    "target": db_node["id"],
                    "type": "smoothstep",
                    "animated": True,
                    "style": {"stroke": "#10b981", "strokeWidth": 3},
                    "label": "Data Operations"
                })
            node_id += 1
        
        # Deployment Layer
        if deployment:
            deploy_node = {
                "id": f"deploy-{node_id}",
                "type": "output",
                "position": {"x": 400, "y": 250},
                "data": {
                    "label": f"🚀 {deployment.get('frontend', 'Deployment')}",
                    "description": "Hosting & Deployment",
                    "features": ["Scalability", "Monitoring"]
                },
                "style": self._get_node_style("deployment")
            }
            nodes.append(deploy_node)
        
        return {
            "message": "Generated fallback architecture flowchart",
            "flowchart": {
                "nodes": nodes,
                "edges": edges
            },
            "design_rationale": "Simple layered architecture showing main system components",
            "user_flow_summary": "Users interact with frontend, which communicates with backend, which stores data"
        }
    
    def _get_node_style(self, node_type: str) -> Dict[str, Any]:
        """Get styling for different node types"""
        styles = {
            "ui": {
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "color": "white",
                "border": "none",
                "borderRadius": 12,
                "padding": "10px 15px",
                "fontSize": "14px",
                "fontWeight": "600",
                "boxShadow": "0 4px 15px rgba(102, 126, 234, 0.3)",
                "minWidth": "140px",
                "textAlign": "center"
            },
            "logic": {
                "background": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                "color": "white",
                "border": "none",
                "borderRadius": 12,
                "padding": "10px 15px",
                "fontSize": "14px",
                "fontWeight": "600",
                "boxShadow": "0 4px 15px rgba(240, 147, 251, 0.3)",
                "minWidth": "140px",
                "textAlign": "center"
            },
            "data": {
                "background": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                "color": "white",
                "border": "none",
                "borderRadius": 12,
                "padding": "10px 15px",
                "fontSize": "14px",
                "fontWeight": "600",
                "boxShadow": "0 4px 15px rgba(79, 172, 254, 0.3)",
                "minWidth": "140px",
                "textAlign": "center"
            },
            "deployment": {
                "background": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
                "color": "#2d3748",
                "border": "none",
                "borderRadius": 12,
                "padding": "10px 15px",
                "fontSize": "14px",
                "fontWeight": "600",
                "boxShadow": "0 4px 15px rgba(168, 237, 234, 0.3)",
                "minWidth": "140px",
                "textAlign": "center"
            }
        }
        
        return styles.get(node_type, styles["logic"])
    
    def _validate_and_enhance_flowchart(self, flowchart: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance flowchart structure"""
        nodes = flowchart.get("nodes", [])
        edges = flowchart.get("edges", [])
        
        # Ensure all nodes have required fields
        for node in nodes:
            if "id" not in node:
                node["id"] = f"node-{len(nodes)}"
            if "position" not in node:
                node["position"] = {"x": 100, "y": 100}
            if "data" not in node:
                node["data"] = {"label": "Component"}
            if "style" not in node:
                node["style"] = self._get_node_style("logic")
        
        # Ensure all edges have required fields
        for edge in edges:
            if "id" not in edge:
                edge["id"] = f"edge-{len(edges)}"
            if "source" not in edge or "target" not in edge:
                continue  # Skip invalid edges
            if "type" not in edge:
                edge["type"] = "smoothstep"
            if "style" not in edge:
                edge["style"] = {"stroke": "#667eea", "strokeWidth": 2}
        
        # Improve node positioning to avoid overlap
        nodes = self._improve_node_positioning(nodes)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _improve_node_positioning(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Improve node positioning to avoid overlaps"""
        if not nodes:
            return nodes
        
        # Simple grid layout algorithm
        cols = 3
        spacing_x = 300
        spacing_y = 200
        start_x = 100
        start_y = 100
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            
            node["position"] = {
                "x": start_x + (col * spacing_x),
                "y": start_y + (row * spacing_y)
            }
        
        return nodes