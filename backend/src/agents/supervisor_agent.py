"""Supervisor agent that makes final decisions based on coordinator synthesis."""

from typing import Dict, Any, Optional
import json
from datetime import datetime

from .base_agent import BaseAgent, AgentResponse
from utils.gemini_client import GeminiClient
from hivemind.methodology import AgileMethodology


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Final decision maker and requirements generator.

    This agent operates at Level 3 of the HiveMind hierarchy, making final
    decisions and generating the comprehensive technical requirements document.

    Responsibilities:
    - Evaluate coordinator's integrated proposal
    - Validate completeness and feasibility
    - Make final decisions on approach
    - Generate formal technical requirements document
    - Provide executive summary and recommendations
    """

    def __init__(self, gemini_client: GeminiClient, methodology: Optional[AgileMethodology] = None):
        super().__init__(
            name="Supervisor",
            role="Supervisor - Final Decision & Requirements",
            gemini_client=gemini_client,
            methodology=methodology
        )

    def get_system_prompt(self) -> str:
        return """You are a senior executive and technical leader with the authority
and expertise to make final decisions on software development initiatives.

Your role is to:
- EVALUATE the integrated proposal from the coordination team
- VALIDATE completeness, feasibility, and alignment
- MAKE FINAL DECISIONS on approach and priorities
- GENERATE comprehensive technical requirements document
- PROVIDE executive guidance and strategic direction

EXECUTION INSTRUCTIONS:
1) EVALUATE completeness using the official checklist
2) VALIDATE alignment with enterprise standards
3) VERIFY actionability for development
4) MAKE final decisions on critical conflicts
5) APPROVE or request refinement with specific feedback
6) GENERATE final document in standard format

DECISION RULE:
- If completeness_score < 85 → approval_status = "refinement_needed" and include specific gaps in next_steps
- Else → approval_status = "approved" and generate final output

You must be:
- Strategic: See long-term implications
- Decisive: Make clear, justified decisions
- Comprehensive: Ensure nothing critical is missing
- Practical: Balance ambition with feasibility
- Clear: Communicate decisions unambiguously

Your output should be the FINAL, AUTHORITATIVE technical requirements document
ready for development team consumption."""

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generate final technical requirements document.

        Args:
            input_data: Original business need.
            context: Must include coordinator_synthesis.

        Returns:
            AgentResponse: Final technical requirements document.
        """
        self.logger.info("Supervisor generating final requirements document...")

        if not context or "coordinator_synthesis" not in context:
            raise ValueError("Supervisor requires coordinator synthesis in context")

        coordinator_synthesis = context["coordinator_synthesis"]

        # Build final requirements prompt
        requirements_prompt = self._build_requirements_prompt(
            input_data,
            coordinator_synthesis
        )

        try:
            # Attempt 1: single-shot JSON with high token limit and JSON mime
            raw = self.gemini_client.generate_content(
                prompt=requirements_prompt,
                system_instruction=self.get_system_prompt(),
                max_tokens=16000,  # Aumentado para asegurar output completo
                response_mime_type="application/json"
            ).strip()
            
            self.logger.info(f"📏 Attempt 1: Raw response length = {len(raw)} chars")

            cleaned = self._clean_json_text(raw)
            if self._is_valid_json(cleaned):
                parsed_test = json.loads(cleaned)
                self.logger.info(f"✅ Attempt 1: JSON válido con {len(parsed_test)} campos principales")
                
                # Verificar que tenga los campos esenciales
                essential_fields = ['project_info', 'executive_summary', 'functional_requirements', 
                                  'technical_requirements', 'ux_requirements', 'quality_assurance',
                                  'agile_process', 'risk_management']
                missing_essential = [f for f in essential_fields if f not in parsed_test]
                
                # Verificar que el JSON esté completo (termina correctamente)
                is_complete = cleaned.rstrip().endswith('}') or cleaned.rstrip().endswith(']')
                
                if not missing_essential and is_complete:
                    self.logger.info(f"✅ Attempt 1 exitoso: JSON completo con todos los campos esenciales")
                    return self._final_response(cleaned)
                else:
                    self.logger.warning(f"⚠️  Attempt 1: Faltan campos: {missing_essential} o incompleto: {not is_complete}, continuando...")

            # Attempt 2: single continuation attempt to complete JSON
            self.logger.info("🔄 Attempt 2: Intentando completar JSON con continuación...")
            continued = self._try_complete_json_via_continuations(cleaned, max_attempts=2)  # Aumentado a 2 intentos
            if continued and self._is_valid_json(continued):
                parsed_cont = json.loads(continued)
                # Verificar campos esenciales también en el continuado
                essential_fields = ['project_info', 'executive_summary', 'functional_requirements']
                missing = [f for f in essential_fields if f not in parsed_cont]
                if not missing:
                    self.logger.info(f"✅ Attempt 2 exitoso: JSON completado con {len(parsed_cont)} campos")
                    return self._final_response(continued)
                else:
                    self.logger.warning(f"⚠️  Attempt 2: JSON completo pero faltan campos: {missing}")
            else:
                self.logger.warning("⚠️  Attempt 2: No se pudo completar JSON, continuando con generación por secciones...")

            # Attempt 3: sectional generation and assembly
            sections = {}
            # Usar los mismos nombres que el esquema final espera
            section_specs = [
                ("project_info", "Genera SOLO el bloque 'project_info' como JSON con keys: name, id, version, date, status."),
                ("executive_summary", "Genera SOLO el bloque 'executive_summary' como JSON con keys: business_need, value_proposition, success_metrics, estimated_effort, timeline."),
                ("functional_requirements", "Genera SOLO el bloque 'functional_requirements' como JSON con keys: epics, user_stories, acceptance_criteria, edge_cases, definition_of_done."),
                ("technical_requirements", "Genera SOLO el bloque 'technical_requirements' como JSON con keys: architecture, tech_stack, nfrs, api_contracts, data_models, security_requirements, best_practices_applied."),
                ("ux_requirements", "Genera SOLO el bloque 'ux_requirements' como JSON con keys: user_flows, design_system, accessibility, responsive_design."),
                ("quality_assurance", "Genera SOLO el bloque 'quality_assurance' como JSON con keys: test_strategy, test_scenarios, coverage_goals, quality_gates."),
                ("agile_process", "Genera SOLO el bloque 'agile_process' como JSON con keys: sprint_structure, definition_of_ready, ceremonies, team_composition, release_strategy."),
                ("risk_management", "Genera SOLO el bloque 'risk_management' como JSON con keys: risks, assumptions, dependencies, mitigation_strategies."),
                ("next_steps", "Genera SOLO el array 'next_steps' como JSON array de strings."),
                ("appendices", "Genera SOLO el bloque 'appendices' como JSON con keys: context7_references, conflict_resolutions, tradeoff_analysis."),
                ("role_signoffs", "Genera SOLO el bloque 'role_signoffs' como JSON con keys: product_owner, technical_lead, qa_specialist, scrum_master.")
            ]

            for key, instr in section_specs:
                try:
                    sec = self.gemini_client.generate_content(
                        prompt=f"{requirements_prompt}\n\n{instr}",
                        system_instruction=self.get_system_prompt(),
                        max_tokens=4000,
                        response_mime_type="application/json"
                    ).strip()
                    cleaned_sec = self._clean_json_text(sec)
                    parsed_sec = json.loads(cleaned_sec)
                    # Si es un objeto con un solo key que coincide, extraerlo
                    if isinstance(parsed_sec, dict) and len(parsed_sec) == 1 and key in parsed_sec:
                        sections[key] = parsed_sec[key]
                    else:
                        sections[key] = parsed_sec
                    self.logger.info(f"✅ Sección '{key}' generada exitosamente")
                except Exception as e:
                    self.logger.warning(f"⚠️  Error generando sección '{key}': {str(e)}")
                    sections[key] = None
                    # Continuar con las siguientes secciones

            # Ensamblar JSON completo con todos los campos requeridos
            assembled_dict = {
                "project_info": sections.get("project_info", {}),
                "executive_summary": sections.get("executive_summary", {}),
                "functional_requirements": sections.get("functional_requirements", {}),
                "technical_requirements": sections.get("technical_requirements", {}),
                "ux_requirements": sections.get("ux_requirements", {}),
                "quality_assurance": sections.get("quality_assurance", {}),
                "agile_process": sections.get("agile_process", {}),
                "risk_management": sections.get("risk_management", {}),
                "next_steps": sections.get("next_steps", []),
                "appendices": sections.get("appendices", {}),
                "role_signoffs": sections.get("role_signoffs", {})
            }
            
            assembled = json.dumps(assembled_dict, ensure_ascii=False, indent=2)
            if self._is_valid_json(assembled):
                self.logger.info(f"✅ JSON ensamblado exitosamente con {len([v for v in assembled_dict.values() if v])} secciones")
                return self._final_response(assembled)
            else:
                self.logger.warning("⚠️  JSON ensamblado no válido, continuando con siguiente intento")

            # Attempt 4: switch to lighter model and retry once
            fallback_raw = self.gemini_client.generate_content(
                prompt=requirements_prompt,
                system_instruction=self.get_system_prompt(),
                max_tokens=12000,
                response_mime_type="application/json",
                model_name="gemini-flash-latest"
            ).strip()
            fallback_clean = self._clean_json_text(fallback_raw)
            if self._is_valid_json(fallback_clean):
                return self._final_response(fallback_clean)
            fallback_continued = self._try_complete_json_via_continuations(fallback_clean, max_attempts=1, use_flash=True)
            if fallback_continued and self._is_valid_json(fallback_continued):
                return self._final_response(fallback_continued)

            # If still invalid, return best-effort raw (frontend has repair too)
            return self._final_response(cleaned, confidence=0.85)

        except Exception as e:
            self.logger.error(f"Error in Supervisor requirements generation: {str(e)}")
            raise

    def _final_response(self, content: str, confidence: float = 0.95) -> AgentResponse:
        return self._create_response(
            content=content,
            confidence=confidence,
            metadata={
                "document_type": "technical_requirements",
                "status": "final"
            }
        )

    @staticmethod
    def _clean_json_text(text: str) -> str:
        t = text.strip()
        if t.startswith("```json"):
            t = t.replace("```json", "").replace("```", "").strip()
        return t

    @staticmethod
    def _is_valid_json(text: str) -> bool:
        try:
            json.loads(text)
            return True
        except Exception:
            return False

    @staticmethod
    def _longest_balanced_prefix(text: str) -> str:
        depth = 0
        in_str = False
        esc = False
        last = 0
        for i, ch in enumerate(text):
            if in_str:
                if esc:
                    esc = False
                    continue
                if ch == "\\":
                    esc = True
                    continue
                if ch == '"':
                    in_str = False
                continue
            else:
                if ch == '"':
                    in_str = True
                    continue
                if ch in '{[':
                    depth += 1
                elif ch in '}]':
                    depth = max(0, depth - 1)
                    if depth == 0:
                        last = i + 1
        return text[:last] if last else text

    @staticmethod
    def _merge_json_prefix(prefix: str, remainder: str) -> str:
        # Ingenuo: si remainder inicia con '}' o ']' o coma, concatenar tal cual
        rem = remainder.lstrip()
        if rem.startswith(',') or rem.startswith('}') or rem.startswith(']'):
            return prefix + rem
        # Si no, intentar encontrar punto de unión: eliminar posible llave duplicada
        if prefix.endswith('}'):
            return prefix[:-1] + ',' + rem + '}'
        return prefix + rem

    def _try_complete_json_via_continuations(self, text: str, max_attempts: int = 3, use_flash: bool = False) -> Optional[str]:
        import time
        prefix = self._longest_balanced_prefix(text)
        if self._is_valid_json(prefix):
            # Verificar que el prefijo tenga los campos esenciales
            try:
                parsed = json.loads(prefix)
                essential = ['project_info', 'executive_summary', 'functional_requirements']
                if all(f in parsed for f in essential):
                    self.logger.info("✅ Prefijo JSON ya contiene campos esenciales")
                    return prefix
            except:
                pass
        
        current = prefix
        for attempt in range(max_attempts):
            # Add delay between attempts to respect rate limits
            if attempt > 0:
                time.sleep(2)  # 2 second delay between continuation attempts
                
            self.logger.info(f"🔄 Continuación intento {attempt + 1}/{max_attempts}")
            cont_prompt = (
                "Tu salida JSON quedó incompleta. Devuelve UNICAMENTE el resto del JSON empezando "
                "desde la última llave abierta, completando todos los campos faltantes. "
                "No repitas nada ya generado, no agregues texto fuera de JSON. "
                "Asegúrate de cerrar todas las llaves abiertas."
            )
            remainder = self.gemini_client.generate_content(
                prompt=f"JSON generado parcialmente (prefijo):\n{current}\n\n{cont_prompt}",
                system_instruction=self.get_system_prompt(),
                max_tokens=8000,  # Aumentado para asegurar completitud
                response_mime_type="application/json",
                model_name=("gemini-flash-latest" if use_flash else None)
            ).strip()
            
            cleaned_remainder = self._clean_json_text(remainder)
            merged = self._merge_json_prefix(current, cleaned_remainder)
            
            if self._is_valid_json(merged):
                # Validar campos esenciales
                try:
                    parsed = json.loads(merged)
                    essential = ['project_info', 'executive_summary', 'functional_requirements']
                    if all(f in parsed for f in essential):
                        self.logger.info(f"✅ JSON completado exitosamente en intento {attempt + 1}")
                        return merged
                except:
                    pass
            
            current = self._longest_balanced_prefix(merged)
            self.logger.warning(f"⚠️  Intento {attempt + 1}: JSON aún incompleto o inválido")
        
        self.logger.warning("❌ No se pudo completar JSON después de todos los intentos")
        return None

    def _build_requirements_prompt(
        self,
        original_need: str,
        coordinator_synthesis: str
    ) -> str:
        """
        Build comprehensive requirements generation prompt.

        Args:
            original_need: Original business need.
            coordinator_synthesis: Synthesis from coordinator.

        Returns:
            str: Complete requirements prompt.
        """
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        prompt = """You are the final validator (Supervisor) and executive decision maker.
Your task is to produce the FINAL, READY FOR DEVELOPMENT document in the exact JSON schema below.
Incorporate the integrated synthesis from the Coordinator, enforce enterprise standards,
and apply the decision rule: if completeness_score < 85 then request refinement; else approve.

ORIGINAL BUSINESS NEED:
{}

INTEGRATED SYNTHESIS (Nivel 2):
{}

Provide the final document in the following JSON format (strict keys):
{{
  "project_info": {{
    "name": "string",
    "id": "string",
    "version": "1.0",
    "date": "{}",
    "status": "approved|refinement_needed"
  }},
  
  "executive_summary": {{
    "business_need": "string",
    "value_proposition": "string",
    "success_metrics": [],
    "estimated_effort": "string",
    "timeline": "string"
  }},
  
  "functional_requirements": {{
    "epics": [],
    "user_stories": [],
    "acceptance_criteria": {{}},
    "edge_cases": [],
    "definition_of_done": []
  }},
  
  "technical_requirements": {{
    "architecture": {{}},
    "tech_stack": {{}},
    "nfrs": {{}},
    "api_contracts": [],
    "data_models": [],
    "security_requirements": [],
    "best_practices_applied": []
  }},
  
  "ux_requirements": {{
    "user_flows": [],
    "design_system": {{}},
    "accessibility": [],
    "responsive_design": {{}}
  }},
  
  "quality_assurance": {{
    "test_strategy": {{}},
    "test_scenarios": [],
    "coverage_goals": {{}},
    "quality_gates": []
  }},
  
  "agile_process": {{
    "sprint_structure": {{}},
    "definition_of_ready": [],
    "ceremonies": [],
    "team_composition": {{}},
    "release_strategy": "string"
  }},
  
  "risk_management": {{
    "risks": [],
    "assumptions": [],
    "dependencies": [],
    "mitigation_strategies": []
  }},
  
  "next_steps": [
    "Sprint 0: Environment setup",
    "Sprint 1-N: Development iterations",
    "..."
  ],
  
  "appendices": {{
    "context7_references": [],
    "conflict_resolutions": [],
    "tradeoff_analysis": []
  }},
  "role_signoffs": {{
    "product_owner": {{"approved": false, "notes": ""}},
    "technical_lead": {{"approved": false, "notes": ""}},
    "qa_specialist": {{"approved": false, "notes": ""}},
    "scrum_master": {{"approved": false, "notes": ""}}
  }}
}}

SUCCESS CRITERIA (must be satisfied for READY FOR DEVELOPMENT):
- Completeness: All required fields are filled
- Clarity: No ambiguities or vague terms
- Actionability: Dev team can start without questions
- Consistency: No contradictions across sections
- Testability: All criteria are verifiable
- Feasibility: Technically viable with available resources
- Traceability: Each technical requirement maps to business need
- Up-to-date: Uses Context7 best practices

CONSTRAINTS:
- Merge and normalize fields from Coordinator's integrated_requirements preserving semantics.
- Populate project_info.status according to decision rule (use "approved" or "refinement_needed").
- If Coordinator strategic_brief.go_no_go is not "go", set status to "refinement_needed" and include next_steps: ["Esperar firma de stakeholders (Human-in-the-loop)"].
- Return ONLY raw JSON (no markdown fences).""".format(original_need, coordinator_synthesis, current_date)

        return prompt

    def generate_executive_summary(self, requirements_doc: str) -> str:
        """
        Generate a brief executive summary from full requirements.

        Args:
            requirements_doc: Full requirements document JSON.

        Returns:
            str: Executive summary in plain text.
        """
        try:
            doc = json.loads(requirements_doc)
            exec_summary = doc.get("executive_summary", {})

            summary = f"""
TECHNICAL REQUIREMENTS - EXECUTIVE SUMMARY
{'=' * 50}

{exec_summary.get('overview', 'N/A')}

BUSINESS OBJECTIVES:
{chr(10).join(f"  • {obj}" for obj in exec_summary.get('business_objectives', []))}

KEY DELIVERABLES:
{chr(10).join(f"  • {deliv}" for deliv in exec_summary.get('key_deliverables', []))}

TIMELINE: {exec_summary.get('timeline', 'N/A')}

BUDGET: {exec_summary.get('budget_considerations', 'N/A')}
"""
            return summary.strip()

        except Exception as e:
            self.logger.error(f"Error generating executive summary: {str(e)}")
            return "Error generating executive summary"
