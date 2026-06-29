"""
Report Page - AI Explanations and Analysis
"""
import streamlit as st
from typing import Dict, Any
import sys
from pathlib import Path
import traceback

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    # from llm.phi3_engine import Phi3MiniEngine
    from llm.qwen3_engine import Qwen3Engine
    from llm.citation_verifier import CitationVerifier
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    import_error = str(e)

def render(interface):
    """Render the Report page"""
    st.title("📊 Report - AI Analysis & Explanations")
    st.markdown("*Evidence-based explanations of your health assessment*")
    # Check if AI modules are available
    if not AI_AVAILABLE:
        st.error(f"❌ AI modules not available: {import_error}")
        st.info("Please ensure all dependencies are installed: `pip install -r requirements.txt`")
        return

    # Progress indicator
    st.progress(0.75)
    st.caption("Step 3 of 4: AI Analysis")
    
    # Check prerequisites
    if not st.session_state.get('patient_data'):
        st.warning("⚠️ No patient data available. Please complete the Patient History section first.")
        return
    
    if not st.session_state.get('risk_results'):
        st.warning("⚠️ No risk assessment results. Please complete the Assessment section first.")
        return
    
    patient_data = st.session_state.patient_data
    risk_results = st.session_state.risk_results
    
    # Initialize AI engine if not done
    if 'ai_engine' not in st.session_state or st.session_state.ai_engine is None:
        with st.spinner("🤖 Initializing AI engine..."):
            try:
                # from llm.phi3_engine import Phi3MiniEngine
                # ai_engine = Phi3MiniEngine()
                from llm.qwen3_engine import Qwen3Engine
                ai_engine = Qwen3Engine()
                st.session_state.ai_engine = ai_engine
                st.info("✅ AI engine created (will initialize on first use)")
            except Exception as e:
                st.error(f"❌ AI engine creation failed: {e}")
                import traceback
                st.error(traceback.format_exc())
                return
    
    ai_engine = st.session_state.ai_engine
    
    # Verify ai_engine is not None
    if ai_engine is None:
        st.error("❌ AI engine is not available. Please refresh the page.")
        if 'ai_engine' in st.session_state:
            del st.session_state.ai_engine
        return
    
    # Display patient and results summary
    st.subheader("📋 Assessment Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("👤 Patient Overview"):
            interface.patient_data_collector.display_patient_summary(patient_data)
    
    with col2:
        with st.expander("🎯 Risk Results Summary"):
            interface.risk_dashboard.display_risk_summary(risk_results)
    
    # AI Explanation Generation Section
    st.subheader("🤖 AI-Generated Explanations")
    
    # Explanation type selection
    explanation_types = {
        "general": "📊 General Overview",
        "diabetes": "🍯 Diabetes Risk Focus",
        "cardiovascular": "❤️ Cardiovascular Risk Focus",
        "colorectal": "🎗️ Colorectal Screening Focus"
    }
    
    selected_type = st.selectbox(
        "Choose explanation focus:",
        options=list(explanation_types.keys()),
        format_func=lambda x: explanation_types[x],
        index=0
    )
    
    # Generation options
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        include_citations = st.checkbox("📚 Include Citations", value=True)
    
    with col2:
        verify_claims = st.checkbox("🔍 Verify Claims", value=True)
    
    with col3:
        detailed_analysis = st.checkbox("📝 Detailed Analysis", value=False)
    
    # Generate explanation button
    if st.button("🚀 Generate AI Explanation", type="primary", use_container_width=True):
        generate_explanation_safe(
            ai_engine, patient_data, risk_results, selected_type,
            include_citations, verify_claims, detailed_analysis
        )
    
    # Display existing explanations
    if st.session_state.get('ai_explanations'):
        display_ai_explanations(st.session_state.ai_explanations, verify_claims)
    
    # Quick summary section
    st.markdown("---")
    st.subheader("⚡ Quick Summary")
    
    if st.button("Generate Quick Summary"):
        with st.spinner("Generating summary..."):
            try:
                if ai_engine is None:
                    st.error("AI engine not available")
                else:
                    summary = ai_engine.generate_quick_summary(risk_results)
                    st.info(f"📝 **Summary:** {summary}")
            except Exception as e:
                st.error(f"Failed to generate summary: {e}")
                import traceback
                st.error(traceback.format_exc())


def generate_explanation_safe(
    ai_engine,
    patient_data,
    risk_results,
    explanation_type,
    include_citations,
    verify_claims,
    detailed_analysis
):
    """Generate AI explanation with better error handling"""
    
    if ai_engine is None:
        st.error("❌ AI engine is not initialized")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Check if generate_explanation method exists
        if not hasattr(ai_engine, 'generate_explanation'):
            st.error("❌ AI engine doesn't have generate_explanation method")
            return
        
        # Step 2: Generate explanation
        status_text.text("🔍 Retrieving medical evidence...")
        progress_bar.progress(0.2)
        
        status_text.text("🤖 Generating AI explanation...")
        progress_bar.progress(0.5)
        
        # Convert patient_data to dict if it has the method
        if hasattr(patient_data, 'to_calculator_dict'):
            patient_dict = patient_data.to_calculator_dict()
        else:
            # Fallback to dict conversion
            patient_dict = vars(patient_data) if hasattr(patient_data, '__dict__') else {}
        
        explanation_result = ai_engine.generate_explanation(
            patient_data=patient_dict,
            risk_results=risk_results,
            explanation_type=explanation_type,
            include_citations=include_citations and verify_claims,
            detailed=detailed_analysis
        )
        
        progress_bar.progress(0.8)
        
        if not explanation_result.get('success'):
            st.error(f"❌ Explanation generation failed: {explanation_result.get('error', 'Unknown error')}")
            return
        
        # Verification already handled inside engine
        status_text.text("🔍 Verifying medical claims...")
        
        progress_bar.progress(1.0)
        status_text.text("✅ Analysis complete!")
        
        # Store in session state
        if 'ai_explanations' not in st.session_state:
            st.session_state['ai_explanations'] = {}
        elif st.session_state.ai_explanations is None:
            st.session_state['ai_explanations'] = {}

        # Now safely assign
        st.session_state.ai_explanations[explanation_type] = explanation_result
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"✅ {explanation_type.title()} explanation generated successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")
        import traceback
        st.error("Error details:")
        st.code(traceback.format_exc())
        progress_bar.empty()
        status_text.empty()

def display_ai_explanations(explanations: Dict[str, Any], show_verification: bool = True):
    """Display generated AI explanations"""

    st.subheader("📄 Generated Explanations")

    for explanation_type, result in explanations.items():
        with st.expander(f"📊 {explanation_type.title()} Explanation", expanded=True):

            if not result.get('success'):
                st.error(f"Failed to generate {explanation_type} explanation")
                continue

            # Main explanation text
            explanation_text = result['explanation']

            st.markdown("### 📝 Explanation")
            st.markdown(explanation_text)

            # Metadata
            col1, col2, col3 = st.columns(3)

            with col1:
                confidence = result.get('confidence', 0)
                st.metric("Confidence", f"{confidence:.1%}")

            with col2:
                sources_count = result.get('context_sources', 0)
                st.metric("Evidence Sources", sources_count)

            with col3:
                if show_verification:
                    verification_score = result.get('verification_score', 0)
                    st.metric("Verification Score", f"{verification_score:.1%}")

            # Citations
            citations = result.get('citations', [])
            if citations:
                st.markdown("### 📚 Citations & Evidence")

                for citation in citations:
                    with st.container():
                        title = citation.get('title', 'Unknown source')
                        organization = citation.get('organization', '')
                        evidence_grade = citation.get('evidence_grade', '')
                        url = citation.get('url', '')

                        citation_text = f"**{title}**"
                        if organization:
                            citation_text += f" - *{organization}*"
                        if evidence_grade:
                            citation_text += f" (Evidence Grade: {evidence_grade})"

                        st.markdown(citation_text)

                        if url:
                            st.markdown(f"[View Source]({url})")

                        st.markdown("---")

            # Verification details
            if show_verification and result.get('verification_details', {}).get('success'):
                details = result['verification_details']

                with st.expander("🔍 Claim Verification Details"):
                    total_claims = details.get('total_claims', 0)
                    supported_claims = details.get('supported_claims', 0)
                    flagged_sentences = result.get('flagged_sentences', [])

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Total Medical Claims", total_claims)
                        st.metric("Supported Claims", supported_claims)

                    with col2:
                        if flagged_sentences:
                            st.warning(f"⚠️ {len(flagged_sentences)} claims need verification")
                            for sentence in flagged_sentences[:3]:
                                st.caption(f"• {sentence}")
                        else:
                            st.success("✅ All claims verified")

            # Download option
            if st.button(f"📥 Download {explanation_type.title()} Report", key=f"download_{explanation_type}"):
                report_content = generate_downloadable_report(explanation_type, result)
                st.download_button(
                    label="💾 Save Report",
                    data=report_content,
                    file_name=f"sourcewell_{explanation_type}_report.txt",
                    mime="text/plain"
                )

def generate_downloadable_report(explanation_type: str, result: Dict[str, Any]) -> str:
    """Generate downloadable report content"""
    
    report_lines = [
        "=" * 60,
        f"SourceWell Healthcare Platform - {explanation_type.title()} Report",
        "=" * 60,
        "",
        "🏥 MEDICAL DISCLAIMER:",
        "This report is for educational purposes only and should not replace",
        "professional medical advice. Please consult healthcare providers for",
        "personalized medical guidance.",
        "",
        "📊 AI EXPLANATION:",
        "-" * 40,
        result.get('explanation', 'No explanation available'),
        "",
    ]
    
    # Add citations
    citations = result.get('citations', [])
    if citations:
        report_lines.extend([
            "📚 EVIDENCE SOURCES:",
            "-" * 40,
        ])
        
        for i, citation in enumerate(citations, 1):
            title = citation.get('title', 'Unknown source')
            organization = citation.get('organization', '')
            
            report_lines.append(f"{i}. {title}")
            if organization:
                report_lines.append(f"   Organization: {organization}")
            report_lines.append("")
    
    # Add metadata
    report_lines.extend([
        "📈 ANALYSIS METADATA:",
        "-" * 40,
        f"Confidence Score: {result.get('confidence', 0):.1%}",
        f"Evidence Sources: {result.get('context_sources', 0)}",
        f"Generation Type: {explanation_type}",
        "",
        "Generated by SourceWell Healthcare AI Platform",
        "Local processing - No data transmitted externally",
        "=" * 60
    ])
    
    return "\n".join(report_lines)