"""
Prompt Templates for Medical AI Explanations
"""
from typing import Dict, Any, List


class PromptTemplates:
    """Prompt templates for generating medical explanations"""

    def build_system_prompt(self, explanation_type: str = "general") -> str:
        """Build system prompt based on explanation type"""

        base = (
            "You are a medical AI assistant that explains health risk assessment results. "
            "Write in a professional yet warm tone. Be clear and concise. "
            "Ground your explanations in the provided medical evidence. "
            "When referencing evidence, mention the source naturally in your text. "
            "End by encouraging the patient to discuss results with their healthcare provider."
        )

        if explanation_type == "diabetes":
            return (
                f"{base} "
                "You are explaining FINDRISC diabetes risk assessment results. "
                "Focus on what the score means, which factors matter most, and evidence-based prevention."
            )
        elif explanation_type == "cardiovascular":
            return (
                f"{base} "
                "You are explaining Framingham cardiovascular risk assessment results. "
                "Focus on what the 10-year risk percentage means, modifiable risk factors, and prevention strategies."
            )
        elif explanation_type == "colorectal":
            return (
                f"{base} "
                "You are explaining colorectal cancer screening recommendations. "
                "Focus on current screening guidelines, available methods, and timing recommendations."
            )
        else:
            return (
                f"{base} "
                "You are explaining a comprehensive health risk assessment covering multiple areas. "
                "Provide a clear overview of all results and what they mean together."
            )

    def build_report_prompt(
        self,
        patient_data: Dict[str, Any],
        risk_results: Dict[str, Any],
        context: Dict[str, Any],
        explanation_type: str = "general"
    ) -> str:
        """Build the report task prompt with patient data, results, and evidence"""

        patient_summary = self._extract_patient_summary(patient_data)
        risk_summary = self._extract_risk_summary(risk_results)
        evidence_context = self._extract_evidence_context(context)

        if explanation_type == "diabetes":
            task = (
                "The patient has already seen their FINDRISC score and risk percentage. "
                "Explain what these results mean for them personally, "
                "which of their factors contribute most, "
                "what evidence-based steps they can take, and when to follow up."
            )
        elif explanation_type == "cardiovascular":
            task = (
                "The patient has already seen their Framingham risk percentage. "
                "Explain what this means for them personally, "
                "which risk factors they can change, "
                "evidence-based prevention strategies, and when to consider further action."
            )
        elif explanation_type == "colorectal":
            task = (
                "The patient has already seen their colorectal screening recommendation. "
                "Explain what this means for them, "
                "what screening options are available, and recommended timing."
            )
        else:
            task = (
                "The patient has already seen their individual risk scores. "
                "Explain how these results relate to each other, "
                "what the overall picture means, and the most important next steps."
            )

        return f"""PATIENT: {patient_summary}

RISK RESULTS: {risk_summary}

MEDICAL EVIDENCE:
{evidence_context}

TASK: {task}

Write 2-4 paragraphs. Do not use bullet points or numbered lists."""

    def _extract_patient_summary(self, patient_data: Dict[str, Any]) -> str:
        """Extract relevant patient information"""
        age = patient_data.get('age')
        gender = patient_data.get('gender')
        bmi = patient_data.get('bmi')

        risk_factors = []
        if patient_data.get('current_smoker'):
            risk_factors.append("current smoker")
        if patient_data.get('diabetes_diagnosed'):
            risk_factors.append("diagnosed diabetes")
        if patient_data.get('hypertension_medication'):
            risk_factors.append("on blood pressure medication")
        if patient_data.get('family_diabetes_history', 'none') != 'none':
            risk_factors.append("family history of diabetes")

        summary = f"{age}-year-old {gender}, BMI {bmi}"
        if risk_factors:
            summary += f", risk factors: {', '.join(risk_factors)}"

        return summary

    def _extract_risk_summary(self, risk_results: Dict[str, Any]) -> str:
        """Extract risk calculation results"""
        summaries = []

        if isinstance(risk_results, dict):
            if 'results' in risk_results:
                calc_results = risk_results.get('results', {})
            else:
                calc_results = risk_results
        else:
            return "No risk calculations available"

        for calc_name, result in calc_results.items():
            if result is None or isinstance(result, bool):
                continue

            if isinstance(result, dict) and 'error' in result:
                continue

            if calc_name == 'diabetes':
                if hasattr(result, 'total_score'):
                    score = result.total_score
                    risk_pct = result.ten_year_risk_percentage
                    summaries.append(f"FINDRISC diabetes risk: {score}/26 points, {risk_pct:.1f}% 10-year risk")

            elif calc_name == 'cardiovascular':
                if hasattr(result, 'ten_year_risk_percentage'):
                    risk_pct = result.ten_year_risk_percentage
                    summaries.append(f"Framingham cardiovascular risk: {risk_pct:.1f}% 10-year risk")

            elif calc_name == 'colorectal_screening':
                if hasattr(result, 'risk_level'):
                    risk_level = result.risk_level
                    summaries.append(f"Colorectal cancer risk: {risk_level} risk level")

            elif calc_name == 'findrisc' and isinstance(result, dict):
                if result.get('success'):
                    data = result.get('result', {})
                    score = data.get('score', 0)
                    risk_pct = data.get('ten_year_risk_percentage', 0)
                    summaries.append(f"FINDRISC diabetes risk: {score}/26 points, {risk_pct:.1f}% 10-year risk")

            elif calc_name == 'framingham' and isinstance(result, dict):
                if result.get('success'):
                    data = result.get('result', {})
                    risk_pct = data.get('ten_year_risk_percentage', 0)
                    summaries.append(f"Framingham cardiovascular risk: {risk_pct:.1f}% 10-year risk")

            elif calc_name == 'colorectal' and isinstance(result, dict):
                if result.get('success'):
                    data = result.get('result', {})
                    risk_level = data.get('risk_level', 'average')
                    summaries.append(f"Colorectal cancer risk: {risk_level} risk level")

        return "; ".join(summaries) if summaries else "No risk calculations available"

    def _extract_evidence_context(self, context: Dict[str, Any]) -> str:
        """Extract evidence from knowledge base"""
        sources = context.get('sources', [])

        if not sources:
            return "No evidence sources available."

        evidence_parts = []
        for i, source in enumerate(sources[:3]):
            title = source.get('title', 'Unknown source')
            content = source.get('content', '')[:800]
            organization = source.get('organization', 'Unknown')

            evidence_parts.append(f"[{i+1}] {title} ({organization}):\n{content}")

        return "\n\n".join(evidence_parts)
