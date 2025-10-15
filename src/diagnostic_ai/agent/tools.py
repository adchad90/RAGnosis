# src/diagnostic_ai/agent/tools.py
from langchain.tools import tool
from diagnostic_ai.rag.retriever import MedicalKnowledgeRAG
from typing import Dict, List
import json

rag = MedicalKnowledgeRAG()

@tool
def retrieve_clinical_guidelines(query: str) -> str:
    """
    Retrieve relevant clinical guidelines and diagnostic criteria from medical knowledge base.
    Use this to check diagnostic criteria, treatment protocols, and risk stratification rules.
    """
    docs = rag.retrieve_relevant_docs(query, k=5)
    return "\n\n".join(docs)

@tool
def analyze_vital_signs(vitals: Dict[str, float]) -> str:
    """
    Analyze vital signs and flag abnormalities.
    Input: dict with keys: heart_rate, bp_systolic, bp_diastolic, temperature, oxygen_saturation, respiratory_rate
    Returns: severity assessment and specific concerns
    """
    concerns = []
    severity = "normal"
    
    if vitals.get("heart_rate", 72) > 100:
        concerns.append("Tachycardia detected")
        severity = "elevated"
    if vitals.get("temperature", 98.6) > 100.4:
        concerns.append("Fever detected - possible infection")
        severity = "elevated"
    if vitals.get("oxygen_saturation", 98) < 94:
        concerns.append("Hypoxia detected - respiratory compromise")
        severity = "high"
    if vitals.get("respiratory_rate", 16) > 20:
        concerns.append("Tachypnea detected")
    
    return json.dumps({
        "severity": severity,
        "concerns": concerns,
        "recommendation": "Monitor closely and consider escalation" if severity != "normal" else "Within normal limits"
    })

@tool
def analyze_lab_values(labs: Dict[str, float]) -> str:
    """
    Analyze lab values and identify abnormalities.
    Returns: abnormalities and clinical significance
    """
    findings = []
    
    if labs.get("troponin", 0) > 0.04:
        findings.append("Elevated troponin - possible myocardial injury (ACS risk)")
    if labs.get("creatinine", 0.9) > 1.2:
        findings.append("Elevated creatinine - possible renal dysfunction")
    if labs.get("glucose", 95) > 150:
        findings.append("Hyperglycemia detected")
    if labs.get("lactate", 2) > 4:
        findings.append("Elevated lactate - possible tissue hypoperfusion/sepsis")
    
    return json.dumps({
        "abnormalities": findings,
        "clinical_significance": "Multiple concerning findings" if len(findings) > 1 else "Monitor"
    })

@tool
def check_diagnostic_criteria(condition: str, patient_context: str) -> str:
    """
    Check if patient meets diagnostic criteria for specific condition.
    Returns: whether criteria are met and confidence level
    """
    # Simplified logic - in production, use LLM-based evaluation with retrieved guidelines
    return json.dumps({
        "condition": condition,
        "criteria_met": "Possible - further investigation needed",
        "confidence": "moderate",
        "next_steps": "Order confirmatory tests and consider specialist consultation"
    })

@tool
def generate_clinical_alert(risk_assessment: Dict) -> str:
    """
    Generate actionable clinical alert for clinician.
    Input: risk assessment with condition, severity, and recommended actions
    Returns: formatted alert message
    """
    alert = f"""
    ⚠️ CLINICAL ALERT
    Condition: {risk_assessment.get('condition', 'Unknown')}
    Risk Level: {risk_assessment.get('severity', 'Unknown')}
    Confidence: {risk_assessment.get('confidence', 'N/A')}
    
    Recommended Actions:
    {chr(10).join(['- ' + action for action in risk_assessment.get('recommended_actions', [])])}
    
    URGENT: Clinician review required immediately.
    """
    return alert

def get_tools():
    """Return all available tools for the agent"""
    return [
        retrieve_clinical_guidelines,
        analyze_vital_signs,
        analyze_lab_values,
        check_diagnostic_criteria,
        generate_clinical_alert
    ]