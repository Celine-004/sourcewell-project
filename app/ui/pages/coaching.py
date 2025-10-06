"""
Coaching Page - Personalized Recommendations
"""
import streamlit as st
from typing import Dict, Any, List
import sys
from pathlib import Path

def render(interface):
    """Render the Coaching page"""
    st.title("🎯 Coaching - Personalized Action Plan")
    st.markdown("*Evidence-based recommendations for your health journey*")
    
    # Progress indicator
    st.progress(1.0)
    st.caption("Step 4 of 4: Action Planning")
    
    # Check prerequisites
    if not st.session_state.get('patient_data'):
        st.warning("⚠️ No patient data available. Please complete the Patient History section first.")
        return
    
    if not st.session_state.get('risk_results'):
        st.warning("⚠️ No risk assessment results. Please complete the Assessment section first.")
        return
    
    patient_data = st.session_state.patient_data
    risk_results = st.session_state.risk_results
    
    # Overview section
    st.subheader("📋 Your Health Profile Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**👤 Patient Information:**")
        st.write(patient_data.summary())
        st.write(patient_data.clinical_summary())
    
    with col2:
        st.markdown("**🎯 Risk Assessment Results:**")
        display_risk_summary_coaching(risk_results)
    
    # Priority Actions
    st.markdown("---")
    st.subheader("🚨 Priority Actions")
    
    priority_actions = extract_priority_actions(risk_results)
    if priority_actions:
        for action in priority_actions:
            if action['priority'] == 'critical':
                st.error(f"🔴 **CRITICAL:** {action['action']}")
            elif action['priority'] == 'high':
                st.warning(f"🟠 **HIGH PRIORITY:** {action['action']}")
    else:
        st.success("✅ No critical priority actions identified")
    
    # Personalized Recommendations
    st.markdown("---")
    st.subheader("💡 Personalized Recommendations")
    
    # Create tabs for different recommendation categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "🍎 Lifestyle", "🩺 Medical", "📊 Monitoring", "🎯 Goals"
    ])
    
    with tab1:
        display_lifestyle_recommendations(patient_data, risk_results)
    
    with tab2:
        display_medical_recommendations(patient_data, risk_results)
    
    with tab3:
        display_monitoring_recommendations(patient_data, risk_results)
    
    with tab4:
        display_goal_setting(patient_data, risk_results)
    
    # Next Steps Section
    st.markdown("---")
    st.subheader("📅 Recommended Next Steps")
    
    next_steps = generate_next_steps(patient_data, risk_results)
    
    for i, step in enumerate(next_steps, 1):
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"### {step['timeframe']}")
            
            with col2:
                st.markdown(f"**{step['action']}**")
                if step.get('details'):
                    st.caption(step['details'])
                
                if step.get('urgent'):
                    st.error("⚠️ Urgent - Schedule within 2 weeks")
    
    # Resources and Tools
    st.markdown("---")
    st.subheader("📚 Additional Resources")
    
    resources = get_relevant_resources(patient_data, risk_results)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔗 Educational Resources:**")
        for resource in resources['educational']:
            st.markdown(f"• [{resource['title']}]({resource['url']})")
    
    with col2:
        st.markdown("**🏥 Professional Guidelines:**")
        for guideline in resources['guidelines']:
            st.markdown(f"• {guideline['title']}")
    
    # Download Action Plan
    st.markdown("---")
    
    if st.button("📥 Download Complete Action Plan", type="primary", use_container_width=True):
        action_plan = generate_action_plan_document(patient_data, risk_results, priority_actions, next_steps)
        st.download_button(
            label="💾 Save Action Plan",
            data=action_plan,
            file_name="sourcewell_action_plan.txt",
            mime="text/plain"
        )

def display_risk_summary_coaching(risk_results: Dict[str, Any]):
    """Display risk summary for coaching context"""
    
    # Check if risk_results has the full structure from runner
    if 'results' in risk_results:
        # It's the full assessment result from MultiCalculatorRunner
        calc_results = risk_results.get('results', {})
    else:
        # It might be just the results dict
        calc_results = risk_results
    
    # Display each calculator's results
    for calc_name, result in calc_results.items():
        # Skip if result is an error dict
        if isinstance(result, dict) and 'error' in result:
            continue
        
        # Handle actual result objects from calculators
        if calc_name in ['diabetes', 'findrisc']:
            if hasattr(result, 'total_score'):
                score = result.total_score
                risk_level = result.risk_level.value if hasattr(result.risk_level, 'value') else str(result.risk_level)
                risk_pct = result.ten_year_risk_percentage
                st.metric("Diabetes Risk", f"{score}/26 ({risk_level})", f"{risk_pct:.1f}% 10-year")
        
        elif calc_name in ['cardiovascular', 'framingham']:
            if hasattr(result, 'ten_year_risk_percentage'):
                risk_pct = result.ten_year_risk_percentage
                risk_level = result.risk_level.value if hasattr(result.risk_level, 'value') else str(result.risk_level)
                st.metric("10-Year CVD Risk", f"{risk_pct:.1f}%", risk_level)
        
        elif calc_name in ['colorectal_screening', 'colorectal']:
            if hasattr(result, 'risk_level'):
                risk_level = result.risk_level
                rec = result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation)
                st.metric("Colorectal Risk", risk_level, rec.replace('_', ' ').title())

def extract_priority_actions(risk_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract priority actions from risk assessment results"""
    
    priority_actions = []
    
    # Check if risk_results has the full structure
    if 'results' in risk_results:
        calc_results = risk_results.get('results', {})
    else:
        calc_results = risk_results
    
    for calc_name, result in calc_results.items():
        # Skip error results
        if isinstance(result, dict) and 'error' in result:
            continue
        
        # Handle actual result objects
        if hasattr(result, 'recommendations'):
            recommendations = result.recommendations
            
            # Process recommendations
            for rec in recommendations:
                if isinstance(rec, str):
                    # Simple string recommendation - check for priority keywords
                    if 'URGENT' in rec.upper() or 'CRITICAL' in rec.upper():
                        priority_actions.append({
                            'priority': 'critical' if 'CRITICAL' in rec.upper() else 'high',
                            'action': rec,
                            'calculator': calc_name
                        })
                    elif 'HIGH' in rec.upper() or 'IMPORTANT' in rec.upper():
                        priority_actions.append({
                            'priority': 'high',
                            'action': rec,
                            'calculator': calc_name
                        })
                elif isinstance(rec, dict):
                    # Structured recommendation
                    priority = rec.get('priority', 'medium')
                    if priority in ['critical', 'high']:
                        priority_actions.append({
                            'priority': priority,
                            'action': rec.get('action', ''),
                            'calculator': calc_name
                        })
    
    return priority_actions

def display_lifestyle_recommendations(patient_data, risk_results: Dict[str, Any]):
    """Display lifestyle recommendations"""
    
    st.markdown("### 🏃‍♂️ Physical Activity")
    
    if not patient_data.physical_activity:
        st.warning("⚠️ **Increase Physical Activity**")
        st.markdown("""
        **Recommendations:**
        - Start with 150 minutes of moderate activity per week
        - Include both aerobic and strength training
        - Begin gradually if currently sedentary
        - Consider walking, swimming, or cycling
        """)
    else:
        st.success("✅ Currently active - maintain current level")
    
    st.markdown("### 🥗 Nutrition")
    
    if not patient_data.vegetable_fruit_daily:
        st.warning("⚠️ **Improve Diet Quality**")
        st.markdown("""
        **Recommendations:**
        - Aim for 5+ servings of fruits and vegetables daily
        - Choose whole grains over refined grains
        - Limit processed foods and added sugars
        - Consider Mediterranean-style eating pattern
        """)
    else:
        st.success("✅ Good fruit and vegetable intake")
    
    # Weight management (if applicable)
    if patient_data.bmi and patient_data.bmi >= 25:
        st.warning("⚠️ **Weight Management**")
        target_weight = calculate_target_weight(patient_data)
        st.markdown(f"""
        **Recommendations:**
        - Current BMI: {patient_data.bmi:.1f} ({patient_data.bmi_category})
        - Target weight range: {target_weight['min']:.1f} - {target_weight['max']:.1f} kg
        - Aim for 1-2 pounds weight loss per week
        - Focus on sustainable lifestyle changes
        """)
    
    # Smoking cessation (if applicable)
    if patient_data.current_smoker:
        st.error("🚨 **CRITICAL: Smoking Cessation**")
        st.markdown("""
        **Immediate Actions:**
        - Consult healthcare provider about cessation programs
        - Consider nicotine replacement therapy
        - Use smoking cessation apps and support groups
        - Set a quit date within the next 2 weeks
        """)

def display_medical_recommendations(patient_data, risk_results: Dict[str, Any]):
    """Display medical follow-up recommendations"""
    
    st.markdown("### 🩺 Healthcare Provider Consultations")
    
    consultations_needed = []
    
    # Get the actual results
    if 'results' in risk_results:
        calc_results = risk_results.get('results', {})
    else:
        calc_results = risk_results
    
    # Check risk levels and recommend consultations
    for calc_name, result in calc_results.items():
        # Skip error results
        if isinstance(result, dict) and 'error' in result:
            continue
        
        if calc_name in ['diabetes', 'findrisc']:
            if hasattr(result, 'total_score'):
                score = result.total_score
                if score >= 15:
                    consultations_needed.append({
                        'type': 'Primary Care / Endocrinology',
                        'reason': 'High diabetes risk - discuss prevention strategies',
                        'urgency': 'Within 1 month'
                    })
        
        elif calc_name in ['cardiovascular', 'framingham']:
            if hasattr(result, 'ten_year_risk_percentage'):
                risk_pct = result.ten_year_risk_percentage
                if risk_pct >= 7.5:
                    consultations_needed.append({
                        'type': 'Primary Care / Cardiology',
                        'reason': 'Elevated cardiovascular risk - discuss prevention',
                        'urgency': 'Within 2-4 weeks'
                    })
        
        elif calc_name in ['colorectal_screening', 'colorectal']:
            if hasattr(result, 'recommendation'):
                rec_value = result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation)
                if 'start_now' in rec_value.lower() or 'recommended' in rec_value.lower():
                    consultations_needed.append({
                        'type': 'Primary Care / Gastroenterology',
                        'reason': 'Discuss colorectal cancer screening options',
                        'urgency': 'Within 2-3 months'
                    })
    
    if consultations_needed:
        for consultation in consultations_needed:
            st.warning(f"⚠️ **{consultation['type']}**")
            st.markdown(f"- **Reason:** {consultation['reason']}")
            st.markdown(f"- **Timeline:** {consultation['urgency']}")
    else:
        st.success("✅ No urgent medical consultations needed based on current assessment")
    
    st.markdown("### 💊 Medication Considerations")
    
    # Blood pressure medication
    if patient_data.systolic_bp and patient_data.systolic_bp >= 140:
        if not patient_data.hypertension_medication:
            st.warning("⚠️ **Blood Pressure Management**")
            st.markdown("- Discuss antihypertensive medication with provider")
    
    # Statin consideration for high CVD risk
    framingham_result = risk_results.get('framingham', {})
    if framingham_result.get('success'):
        cvd_risk = framingham_result.get('result', {}).get('ten_year_risk_percentage', 0)
        if cvd_risk >= 7.5:
            st.info("ℹ️ **Statin Therapy Discussion**")
            st.markdown("- Consider discussing statin therapy with provider")

def display_monitoring_recommendations(patient_data, risk_results: Dict[str, Any]):
    """Display monitoring and screening recommendations"""
    
    st.markdown("### 📊 Regular Health Monitoring")
    
    monitoring_schedule = []
    
    # Blood pressure monitoring
    if patient_data.systolic_bp and patient_data.systolic_bp >= 130:
        monitoring_schedule.append({
            'test': 'Blood Pressure',
            'frequency': 'Monthly',
            'reason': 'Elevated blood pressure readings'
        })
    else:
        monitoring_schedule.append({
            'test': 'Blood Pressure',
            'frequency': 'Annually',
            'reason': 'Routine monitoring'
        })
    
    # Diabetes screening based on FINDRISC
    findrisc_result = risk_results.get('findrisc', {})
    if findrisc_result.get('success'):
        score = findrisc_result.get('result', {}).get('score', 0)
        if score >= 12:
            monitoring_schedule.append({
                'test': 'HbA1c / Fasting Glucose',
                'frequency': 'Every 6 months',
                'reason': 'Elevated diabetes risk'
            })
        else:
            monitoring_schedule.append({
                'test': 'HbA1c / Fasting Glucose',
                'frequency': 'Every 3 years',
                'reason': 'Routine diabetes screening'
            })
    
    # Lipid monitoring
    monitoring_schedule.append({
        'test': 'Lipid Panel',
        'frequency': 'Annually' if patient_data.total_cholesterol and patient_data.total_cholesterol > 200 else 'Every 5 years',
        'reason': 'Cardiovascular risk assessment'
    })
    
    # Display monitoring schedule
    for item in monitoring_schedule:
        st.info(f"📅 **{item['test']}** - {item['frequency']}")
        st.caption(f"Reason: {item['reason']}")

def display_goal_setting(patient_data, risk_results: Dict[str, Any]):
    """Display personalized health goals"""
    
    st.markdown("### 🎯 Personalized Health Goals")
    
    goals = generate_smart_goals(patient_data, risk_results)
    
    for goal in goals:
        with st.container():
            st.markdown(f"**🎯 {goal['category']}: {goal['goal']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Target:** {goal['target']}")
                st.markdown(f"**Timeline:** {goal['timeline']}")
            
            with col2:
                st.markdown(f"**How to measure:** {goal['measurement']}")
                st.markdown(f"**Action steps:** {goal['action_steps']}")
            
            # Progress tracker
            if st.checkbox(f"Track progress for {goal['category']}", key=f"track_{goal['category']}"):
                st.slider(
                    f"Progress towards {goal['category']} goal",
                    min_value=0,
                    max_value=100,
                    value=0,
                    help="Update your progress regularly"
                )
            
            st.markdown("---")

def generate_smart_goals(patient_data, risk_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SMART goals based on patient data and risk results"""
    
    goals = []
    
    # Weight loss goal (if applicable)
    if patient_data.bmi and patient_data.bmi >= 25:
        current_weight = patient_data.weight_kg
        target_loss = min(current_weight * 0.1, 10)  # 10% or 10kg max
        
        goals.append({
            'category': 'Weight Management',
            'goal': f'Achieve healthy weight',
            'target': f'Lose {target_loss:.1f} kg',
            'timeline': '6 months',
            'measurement': 'Weekly weigh-ins',
            'action_steps': 'Diet modification + 150min exercise/week'
        })
    
    # Physical activity goal
    if not patient_data.physical_activity:
        goals.append({
            'category': 'Physical Activity',
            'goal': 'Establish regular exercise routine',
            'target': '150 minutes moderate activity per week',
            'timeline': '8 weeks to build habit',
            'measurement': 'Weekly activity minutes',
            'action_steps': 'Start with 20min walks, gradually increase'
        })
    
    # Blood pressure goal (if elevated)
    if patient_data.systolic_bp and patient_data.systolic_bp >= 130:
        goals.append({
            'category': 'Blood Pressure',
            'goal': 'Lower blood pressure to healthy range',
            'target': 'BP < 130/80 mmHg',
            'timeline': '3-6 months',
            'measurement': 'Weekly BP checks',
            'action_steps': 'Medication adherence + lifestyle changes'
        })
    
    # Diabetes prevention (if at risk)
    findrisc_result = risk_results.get('findrisc', {})
    if findrisc_result.get('success'):
        score = findrisc_result.get('result', {}).get('score', 0)
        if score >= 12:
            goals.append({
                'category': 'Diabetes Prevention',
                'goal': 'Reduce diabetes risk factors',
                'target': 'Lower FINDRISC score by 3+ points',
                'timeline': '6-12 months',
                'measurement': 'Quarterly FINDRISC assessment',
                'action_steps': 'Weight loss + increased activity + diet improvement'
            })
    
    return goals

def generate_next_steps(patient_data, risk_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate prioritized next steps"""
    
    steps = []
    
    # Immediate steps (1-2 weeks)
    if patient_data.current_smoker:
        steps.append({
            'timeframe': 'Immediate',
            'action': 'Schedule smoking cessation consultation',
            'details': 'Contact primary care provider or smoking cessation program',
            'urgent': True
        })
    
    # Short-term steps (1 month)
    high_risk_conditions = []
    
    findrisc_result = risk_results.get('findrisc', {})
    if findrisc_result.get('success'):
        score = findrisc_result.get('result', {}).get('score', 0)
        if score >= 15:
            high_risk_conditions.append('diabetes')
    
    framingham_result = risk_results.get('framingham', {})
    if framingham_result.get('success'):
        risk_pct = framingham_result.get('result', {}).get('ten_year_risk_percentage', 0)
        if risk_pct >= 20:
            high_risk_conditions.append('cardiovascular disease')
    
    if high_risk_conditions:
        steps.append({
            'timeframe': '1 Month',
            'action': 'Schedule comprehensive health evaluation',
            'details': f'High risk for: {", ".join(high_risk_conditions)}',
            'urgent': True
        })
    
    # Medium-term steps (3 months)
    if patient_data.bmi and patient_data.bmi >= 30:
        steps.append({
            'timeframe': '3 Months',
            'action': 'Establish weight management program',
            'details': 'Consider structured program or nutritionist consultation'
        })
    
    # Long-term steps (6-12 months)
    steps.append({
        'timeframe': '6 Months',
        'action': 'Repeat risk assessments',
        'details': 'Re-evaluate progress and adjust recommendations'
    })
    
    steps.append({
        'timeframe': '1 Year',
        'action': 'Annual health screening',
        'details': 'Complete physical exam with updated lab work'
    })
    
    return steps

def calculate_target_weight(patient_data) -> Dict[str, float]:
    """Calculate healthy weight range"""
    height_m = patient_data.height_cm / 100
    
    # BMI 18.5-24.9 range
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    
    return {'min': min_weight, 'max': max_weight}

def get_relevant_resources(patient_data, risk_results: Dict[str, Any]) -> Dict[str, List]:
    """Get relevant educational resources"""
    
    resources = {
        'educational': [],
        'guidelines': []
    }
    
    # Diabetes resources
    if 'findrisc' in risk_results:
        resources['educational'].extend([
            {'title': 'Diabetes Prevention Program', 'url': 'https://www.cdc.gov/diabetes/prevention/'},
            {'title': 'ADA Risk Test', 'url': 'https://www.diabetes.org/risk-test'}
        ])
        resources['guidelines'].append({'title': 'ADA Standards of Medical Care in Diabetes'})
    
    # Cardiovascular resources
    if 'framingham' in risk_results:
        resources['educational'].extend([
            {'title': 'Heart Disease Prevention', 'url': 'https://www.heart.org/'},
            {'title': 'Million Hearts Initiative', 'url': 'https://millionhearts.hhs.gov/'}
        ])
        resources['guidelines'].append({'title': 'AHA/ACC Cardiovascular Risk Guidelines'})
    
    # Colorectal screening resources
    if 'colorectal' in risk_results:
        resources['educational'].extend([
            {'title': 'Colorectal Cancer Screening', 'url': 'https://www.cancer.org/'},
            {'title': 'Screen for Life Campaign', 'url': 'https://www.cdc.gov/cancer/colorectal/'}
        ])
        resources['guidelines'].append({'title': 'USPSTF Colorectal Cancer Screening Guidelines'})
    
    return resources

def generate_action_plan_document(patient_data, risk_results, priority_actions, next_steps) -> str:
    """Generate complete action plan document"""
    
    lines = [
        "=" * 60,
        "SourceWell Healthcare Platform - Personalized Action Plan",
        "=" * 60,
        "",
        "🏥 MEDICAL DISCLAIMER:",
        "This action plan is for educational purposes only and should not replace",
        "professional medical advice. Please consult healthcare providers for",
        "personalized medical guidance.",
        "",
        "👤 PATIENT SUMMARY:",
        "-" * 40,
        patient_data.summary(),
        patient_data.clinical_summary(),
        "",
        "🎯 RISK ASSESSMENT SUMMARY:",
        "-" * 40,
    ]
    
    # Add risk summaries
    for calc_name, result in risk_results.items():
        if result.get('success'):
            data = result.get('result', {})
            if calc_name == 'findrisc':
                score = data.get('score', 0)
                risk_pct = data.get('ten_year_risk_percentage', 0)
                lines.append(f"Diabetes Risk (FINDRISC): {score}/26 points ({risk_pct:.1f}% 10-year risk)")
            elif calc_name == 'framingham':
                risk_pct = data.get('ten_year_risk_percentage', 0)
                lines.append(f"Cardiovascular Risk: {risk_pct:.1f}% 10-year risk")
            elif calc_name == 'colorectal':
                risk_level = data.get('risk_level', 'average')
                lines.append(f"Colorectal Risk Level: {risk_level}")
    
    # Add priority actions
    if priority_actions:
        lines.extend([
            "",
            "🚨 PRIORITY ACTIONS:",
            "-" * 40,
        ])
        for action in priority_actions:
            lines.append(f"• {action['priority'].upper()}: {action['action']}")
    
    # Add next steps
    lines.extend([
        "",
        "📅 RECOMMENDED NEXT STEPS:",
        "-" * 40,
    ])
    
    for step in next_steps:
        lines.append(f"{step['timeframe']}: {step['action']}")
        if step.get('details'):
            lines.append(f"   Details: {step['details']}")
        if step.get('urgent'):
            lines.append("   ⚠️ URGENT - Schedule within 2 weeks")
        lines.append("")
    
    lines.extend([
        "=" * 60,
        "Generated by SourceWell Healthcare AI Platform",
        "Local processing - No data transmitted externally",
        "For questions, consult with your healthcare provider",
        "=" * 60
    ])
    
    return "\n".join(lines)