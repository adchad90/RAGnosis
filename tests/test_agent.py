# tests/test_agent.py
import sys
import os
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from diagnostic_ai.data.patient_simulator import PatientDataSimulator
from diagnostic_ai.agent.graph import initialize_diagnostic_workflow
from diagnostic_ai.rag.retriever import MedicalKnowledgeRAG

def test_patient_generation():
    """Test synthetic patient generation"""
    patient = PatientDataSimulator.generate_patient_case("normal")
    assert patient.patient_id.startswith("PT")
    assert 40 <= patient.age <= 85

def test_high_risk_patient():
    """Test high-risk patient generation"""
    patient = PatientDataSimulator.generate_patient_case("high_risk_acs")
    assert patient.recent_labs["troponin"] > 0.04

def test_patient_context_generation():
    """Test patient context string generation"""
    patient = PatientDataSimulator.generate_patient_case()
    context = PatientDataSimulator.patient_to_context(patient)
    assert patient.patient_id in context
    assert str(patient.age) in context

def test_workflow_initialization():
    """Test agent state initialization"""
    patient = PatientDataSimulator.generate_patient_case()
    context = PatientDataSimulator.patient_to_context(patient)
    state = initialize_diagnostic_workflow(context)
    
    assert state["patient_context"] == context
    assert state["next_action"] == "analyze_vitals"
    assert len(state["messages"]) == 0

def test_rag_initialization():
    """Test RAG system"""
    rag = MedicalKnowledgeRAG()
    assert rag.embeddings is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])