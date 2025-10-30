"""
Prompt Templates for Medical AI Explanations
"""
from typing import Dict, Any, List

class PromptTemplates:
    """Prompt templates for generating medical explanations"""
    
    def __init__(self):
        self.base_system_prompt = """You are a medical AI assistant providing evidence-based health explanations. 

CRITICAL GUIDELINES:
- Base all explanations on the provided medical evidence
- Use clear, patient-friendly language
- Always include appropriate medical disclaimers
- Cite specific evidence when making claims
- Never provide specific medical advice or diagnoses
- Encourage consultation with healthcare providers

Your role is educational only."""

    def build_explanation_prompt(
        self,
        patient_data: Dict[str, Any],
        risk_results: Dict[str, Any], 
        context: Dict[str, Any],
        explanation_type: str = "general"
    ) -> str:
        """Build comprehensive explanation prompt"""
        
        # Extract patient summary
        patient_summary = self._extract_patient_summary(patient_data)
        
        # Extract risk summary
        risk_summary = self._extract_risk_summary(risk_results)
        
        # Extract evidence context
        evidence_context = self._extract_evidence_context(context)
        
        # Build prompt based on type
        if explanation_type == "diabetes":
            return self._build_diabetes_prompt(patient_summary, risk_summary, evidence_context)
        elif explanation_type == "cardiovascular":
            return self._build_cardiovascular_prompt(patient_summary, risk_summary, evidence_context)
        elif explanation_type == "colorectal":
            return self._build_colorectal_prompt(patient_summary, risk_summary, evidence_context)
        else:
            return self._build_general_prompt(patient_summary, risk_summary, evidence_context)
    
    def _extract_patient_summary(self, patient_data: Dict[str, Any]) -> str:
        """Extract relevant patient information"""
        age = patient_data.get('age', 'unknown')
        gender = patient_data.get('gender', 'unknown')
        bmi = patient_data.get('bmi', 'unknown')
        
        risk_factors = []
        if patient_data.get('current_smoker'):
            risk_factors.append("current smoker")
        if patient_data.get('diabetes_diagnosed'):
            risk_factors.append("diagnosed diabetes")
        if patient_data.get('hypertension_medication'):
            risk_factors.append("on blood pressure medication")
        if patient_data.get('family_diabetes_history', 'none') != 'none':
            risk_factors.append("family history of diabetes")
        
        summary = f"Patient: {age}-year-old {gender}"
        if bmi != 'unknown':
            summary += f", BMI: {bmi}"
        if risk_factors:
            summary += f", Risk factors: {', '.join(risk_factors)}"
        
        return summary
    
    def _extract_risk_summary(self, risk_results: Dict[str, Any]) -> str:
        """Extract risk calculation results"""
        summaries = []
        
        # Handle different possible structures of risk_results
        if isinstance(risk_results, dict):
            # Check if it has a 'results' key (full assessment structure)
            if 'results' in risk_results:
                calc_results = risk_results.get('results', {})
            else:
                # Assume it's directly the calculator results
                calc_results = risk_results
        else:
            return "No risk calculations available"
        
        # Process each calculator result
        for calc_name, result in calc_results.items():
            # Skip if result is not a valid object or dict
            if result is None or isinstance(result, bool):
                continue
                
            # Check if it's an error result
            if isinstance(result, dict) and 'error' in result:
                continue
            
            # Process successful results
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
            
            # Legacy format support (if results are stored differently)
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
            return "Limited evidence context available."
        
        evidence_text = "MEDICAL EVIDENCE:\n"
        for i, source in enumerate(sources[:5]):  # Limit to top 5 sources
            title = source.get('title', 'Unknown source')
            content = source.get('content', '')[:500]  # Limit content length
            organization = source.get('organization', 'Unknown')
            
            evidence_text += f"\n{i+1}. {title} ({organization})\n{content}...\n"
        
        return evidence_text
    
    def _build_general_prompt(self, patient_summary: str, risk_summary: str, evidence_context: str) -> str:
        """Build general explanation prompt"""
        return f"""You are a medical AI assistant. Provide a clear explanation of health risk assessment results.

    PATIENT CONTEXT:
    {patient_summary}

    RISK ASSESSMENT RESULTS:
    {risk_summary}

    MEDICAL EVIDENCE:
    {evidence_context}

    Provide a compassionate, clear explanation that:
    1. Explains what the risk percentages mean in simple terms
    2. Identifies key factors contributing to the risks
    3. Suggests evidence-based next steps
    4. Encourages consultation with healthcare providers

    Keep the response conversational and reassuring. Do not use bullet points or lists.

    Explanation:"""
    
    def _build_diabetes_prompt(self, patient_summary: str, risk_summary: str, evidence_context: str) -> str:
        """Build diabetes-specific explanation prompt"""
        return f"""
{self.base_system_prompt}

PATIENT CONTEXT:
{patient_summary}

DIABETES RISK ASSESSMENT:
{risk_summary}

{evidence_context}

TASK:
Provide a focused explanation of the FINDRISC diabetes risk assessment. Address:

1. **FINDRISC Score Interpretation** - What the score range means
2. **Risk Factor Analysis** - Which factors contribute most to their risk
3. **Prevention Strategies** - Evidence-based lifestyle modifications
4. **Monitoring Recommendations** - When and what to monitor

Base your explanation on the provided medical evidence, particularly focusing on diabetes prevention guidelines and FINDRISC validation studies.

This is educational information only - encourage consultation with healthcare providers for personalized diabetes prevention strategies.
"""
    
    def _build_cardiovascular_prompt(self, patient_summary: str, risk_summary: str, evidence_context: str) -> str:
        """Build cardiovascular-specific explanation prompt"""
        return f"""
{self.base_system_prompt}

PATIENT CONTEXT:
{patient_summary}

CARDIOVASCULAR RISK ASSESSMENT:
{risk_summary}

{evidence_context}

TASK:
Provide a focused explanation of the Framingham cardiovascular risk assessment. Address:

1. **Risk Percentage Interpretation** - What the 10-year CVD risk means
2. **Modifiable Risk Factors** - Factors the patient can potentially change
3. **Prevention Guidelines** - Evidence-based cardiovascular prevention strategies
4. **Treatment Considerations** - When to consider risk reduction therapies

Base your explanation on cardiovascular prevention guidelines from major medical organizations (AHA, ACC, etc.) provided in the evidence context.

This is educational information only - emphasize the importance of discussing cardiovascular risk management with their healthcare provider.
"""
    
    def _build_colorectal_prompt(self, patient_summary: str, risk_summary: str, evidence_context: str) -> str:
        """Build colorectal-specific explanation prompt"""
        return f"""
{self.base_system_prompt}

PATIENT CONTEXT:
{patient_summary}

COLORECTAL SCREENING ASSESSMENT:
{risk_summary}

{evidence_context}

TASK:
Provide a focused explanation of colorectal cancer screening recommendations. Address:

1. **Screening Guidelines** - Current recommendations for their age and risk level
2. **Risk Factors** - Personal and family history considerations
3. **Screening Options** - Available screening methods and their benefits
4. **Timing Recommendations** - When to start and how often to screen

Base your explanation on current USPSTF and professional society guidelines provided in the evidence context.

This is educational information only - encourage discussion of personalized screening plans with their healthcare provider.
"""