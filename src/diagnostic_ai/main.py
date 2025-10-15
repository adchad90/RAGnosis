# src/diagnostic_ai/main.py
from diagnostic_ai.agent.graph import diagnostic_graph, initialize_diagnostic_workflow
from diagnostic_ai.data.patient_simulator import PatientDataSimulator
from diagnostic_ai.rag.retriever import MedicalKnowledgeRAG
from diagnostic_ai.utils.logger import AuditLogger
import json

audit_logger = AuditLogger("DiagnosticAIApp")

# Sample medical knowledge for RAG
SAMPLE_MEDICAL_DOCS = [
    """Acute Coronary Syndrome (ACS) Diagnostic Criteria:
    - Chest pain or discomfort lasting >20 minutes
    - Elevated cardiac biomarkers (troponin >0.04)
    - ST-segment elevation or depression on ECG
    - Risk factors: age, smoking, diabetes, hypertension
    - Tachycardia, tachypnea, hypoxia may be present
    - Immediate ECG and troponin measurement recommended""",
    
    """Sepsis Diagnostic Criteria (qSOFA):
    - Suspected infection + 2 of following:
    - Altered mental status (confusion)
    - Respiratory distress (RR >22)
    - Systolic BP <100 mmHg
    - Fever (>100.4°F) or hypothermia (<96.8°F)
    - Elevated lactate (>4 mmol/L)
    - Urgent antibiotics and supportive care required""",
    
    """Hypertensive Crisis:
    - Systolic BP >180 or diastolic BP >120
    - Signs of end-organ damage: chest pain, SOB, neuro changes
    - Urgent assessment and treatment indicated
    - Monitor for MI, stroke, pulmonary edema""",
]

def initialize_rag():
    """Initialize RAG system with medical knowledge"""
    rag = MedicalKnowledgeRAG()
    rag.build_knowledge_base(SAMPLE_MEDICAL_DOCS)
    return rag

def run_diagnostic_analysis(patient_risk_level: str = "normal"):
    """
    Run complete diagnostic analysis workflow on synthetic patient
    """
    print(f"\n{'='*60}")
    print(f"DIAGNOSTIC AI AGENT - MVP DEMONSTRATION")
    print(f"{'='*60}\n")
    
    # Generate synthetic patient
    patient = PatientDataSimulator.generate_patient_case(risk_level=patient_risk_level)
    patient_context = PatientDataSimulator.patient_to_context(patient)
    
    print(f"Patient Generated: {patient.patient_id}")
    print(f"Risk Profile: {patient_risk_level}")
    print(f"\nPatient Context:\n{patient_context}\n")
    
    # Initialize workflow
    initial_state = initialize_diagnostic_workflow(patient_context)
    
    # Run diagnostic agent
    print("Running diagnostic analysis...\n")
    final_state = diagnostic_graph.invoke(initial_state)
    
    # Output results
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Risk Assessment:\n{json.dumps(final_state['risk_assessment'], indent=2)}\n")
    
    if final_state["alerts"]:
        print(f"{'⚠️ '*20}")
        print("CLINICAL ALERTS GENERATED:")
        for alert in final_state["alerts"]:
            print(f"\n{alert}")
        print(f"{'⚠️ '*20}\n")
    
    # Audit trail
    print(f"\n{'='*60}")
    print("AUDIT TRAIL (Compliance Record)")
    print(f"{'='*60}\n")
    print(json.dumps(audit_logger.get_audit_trail(), indent=2))
    
    return final_state

if __name__ == "__main__":
    # Initialize RAG
    initialize_rag()
    
    # Test with different risk profiles
    print("\n🔵 TEST 1: Normal Patient")
    run_diagnostic_analysis("normal")
    
    print("\n\n🔴 TEST 2: High-Risk ACS Patient")
    run_diagnostic_analysis("high_risk_acs")
    
    print("\n\n🔴 TEST 3: High-Risk Sepsis Patient")
    run_diagnostic_analysis("high_risk_sepsis")