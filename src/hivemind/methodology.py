"""Metodologías ágiles soportadas por HiveMind."""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


class AgileMethodology(Enum):
    """Metodologías ágiles soportadas."""
    SCRUM = "scrum"
    SAFE = "safe"
    KANBAN = "kanban"


@dataclass
class MethodologyContext:
    """Contexto específico de cada metodología ágil."""
    
    name: str
    description: str
    system_context: str
    roles_mapping: Dict[str, str]
    output_structure: Dict[str, Any]
    ceremonies: List[str]
    artifacts: List[str]
    metrics: List[str]


class MethodologyFactory:
    """Factory para crear contextos de metodologías ágiles."""
    
    @staticmethod
    def get_context(methodology: AgileMethodology) -> MethodologyContext:
        """Obtener contexto específico de la metodología."""
        
        if methodology == AgileMethodology.SCRUM:
            return MethodologyContext(
                name="Scrum",
                description="Metodología ágil centrada en sprints de desarrollo iterativo",
                system_context="""Sistema multi-agente especializado en metodología Scrum. 
                Transforma necesidades de negocio en Product Backlog refinado, User Stories 
                con criterios de aceptación, y documentación técnica lista para Sprint Planning. 
                Cada agente aporta su expertise específico siguiendo los roles y ceremonias de Scrum.""",
                roles_mapping={
                    "ProductManager": "Product Owner",
                    "ProductOwner": "Scrum Master + Product Owner",
                    "UXUI_Designer": "UX/UI Designer",
                    "ScrumMaster": "Scrum Master",
                    "TechnicalLead": "Technical Lead",
                    "QA_Specialist": "QA Specialist"
                },
                output_structure={
                    "product_backlog": "Product Backlog refinado con User Stories",
                    "sprint_planning": "Sprint Planning documentation",
                    "definition_of_done": "Definition of Done",
                    "ceremonies": "Ceremonias de Scrum",
                    "roles_responsibilities": "Roles y responsabilidades"
                },
                ceremonies=[
                    "Sprint Planning",
                    "Daily Scrum",
                    "Sprint Review",
                    "Sprint Retrospective"
                ],
                artifacts=[
                    "Product Backlog",
                    "Sprint Backlog",
                    "Increment",
                    "Burndown Chart"
                ],
                metrics=[
                    "Velocity",
                    "Burndown Rate",
                    "Sprint Goal Achievement",
                    "Team Satisfaction"
                ]
            )
            
        elif methodology == AgileMethodology.SAFE:
            return MethodologyContext(
                name="SAFe",
                description="Scaled Agile Framework para organizaciones grandes",
                system_context="""Sistema multi-agente especializado en metodología SAFe (Scaled Agile Framework). 
                Transforma necesidades de negocio en Features, Enablers, y documentación técnica 
                alineada con los niveles de Portfolio, Program y Team. Adaptado para organizaciones 
                que requieren escalabilidad y alineación estratégica.""",
                roles_mapping={
                    "ProductManager": "Product Manager (Portfolio)",
                    "ProductOwner": "Product Owner (Program)",
                    "UXUI_Designer": "UX/UI Designer",
                    "ScrumMaster": "Scrum Master (Team)",
                    "TechnicalLead": "Technical Lead",
                    "QA_Specialist": "QA Specialist"
                },
                output_structure={
                    "features": "Features y Enablers",
                    "epic_breakdown": "Epic breakdown",
                    "program_increment": "Program Increment planning",
                    "solution_intent": "Solution Intent",
                    "architectural_runway": "Architectural Runway"
                },
                ceremonies=[
                    "Portfolio Sync",
                    "Program Increment Planning",
                    "Scrum of Scrums",
                    "System Demo",
                    "Inspect & Adapt"
                ],
                artifacts=[
                    "Portfolio Backlog",
                    "Program Backlog",
                    "Team Backlog",
                    "Solution Intent",
                    "Architectural Runway"
                ],
                metrics=[
                    "Program Predictability",
                    "Feature Delivery Rate",
                    "Team Velocity",
                    "Solution Quality"
                ]
            )
            
        elif methodology == AgileMethodology.KANBAN:
            return MethodologyContext(
                name="Kanban",
                description="Metodología de flujo continuo con límites de trabajo en progreso",
                system_context="""Sistema multi-agente especializado en metodología Kanban. 
                Transforma necesidades de negocio en Work Items categorizados, WIP limits, 
                y documentación técnica optimizada para flujo continuo. Enfocado en 
                visualización del trabajo y mejora continua del flujo.""",
                roles_mapping={
                    "ProductManager": "Service Request Manager",
                    "ProductOwner": "Flow Manager",
                    "UXUI_Designer": "UX/UI Designer",
                    "ScrumMaster": "Flow Coordinator",
                    "TechnicalLead": "Technical Lead",
                    "QA_Specialist": "QA Specialist"
                },
                output_structure={
                    "work_items": "Work Items categorizados",
                    "wip_limits": "WIP limits por columna",
                    "flow_metrics": "Flow metrics y SLAs",
                    "service_levels": "Service Level Expectations",
                    "kanban_board": "Diseño de Kanban Board"
                },
                ceremonies=[
                    "Replenishment Meeting",
                    "Flow Review",
                    "Service Delivery Review",
                    "Risk Review"
                ],
                artifacts=[
                    "Kanban Board",
                    "Work Item Types",
                    "Service Level Agreements",
                    "Flow Metrics Dashboard"
                ],
                metrics=[
                    "Lead Time",
                    "Cycle Time",
                    "Throughput",
                    "Work In Progress",
                    "Flow Efficiency"
                ]
            )
        
        else:
            raise ValueError(f"Metodología no soportada: {methodology}")
    
    @staticmethod
    def get_available_methodologies() -> List[AgileMethodology]:
        """Obtener lista de metodologías disponibles."""
        return list(AgileMethodology)
    
    @staticmethod
    def validate_methodology(methodology_str: str) -> AgileMethodology:
        """Validar y convertir string a metodología."""
        try:
            return AgileMethodology(methodology_str.lower())
        except ValueError:
            available = [m.value for m in AgileMethodology]
            raise ValueError(f"Metodología '{methodology_str}' no válida. Opciones disponibles: {available}")


class MethodologyAdapter:
    """Adaptador para personalizar agentes según metodología."""
    
    def __init__(self, methodology: AgileMethodology):
        self.methodology = methodology
        self.context = MethodologyFactory.get_context(methodology)
    
    def adapt_system_prompt(self, base_prompt: str, agent_name: str) -> str:
        """Adaptar prompt del sistema según metodología."""
        
        methodology_context = f"""
CONTEXTO DE METODOLOGÍA: {self.context.name}
{self.context.description}

ROL EN {self.context.name}: {self.context.roles_mapping.get(agent_name, agent_name)}

ARTEFACTOS ESPECÍFICOS: {', '.join(self.context.artifacts)}
CEREMONIAS: {', '.join(self.context.ceremonies)}
MÉTRICAS CLAVE: {', '.join(self.context.metrics)}
"""
        
        return f"{methodology_context}\n\n{base_prompt}"
    
    def adapt_output_format(self, agent_name: str) -> Dict[str, Any]:
        """Adaptar formato de salida según metodología."""
        return self.context.output_structure
    
    def get_methodology_specific_instructions(self) -> str:
        """Obtener instrucciones específicas de la metodología."""
        return f"""
INSTRUCCIONES ESPECÍFICAS DE {self.context.name.upper()}:

1. Sigue las mejores prácticas de {self.context.name}
2. Genera artefactos específicos: {', '.join(self.context.artifacts)}
3. Considera las ceremonias: {', '.join(self.context.ceremonies)}
4. Incluye métricas relevantes: {', '.join(self.context.metrics)}
5. Adapta el lenguaje y estructura a {self.context.name}
"""
