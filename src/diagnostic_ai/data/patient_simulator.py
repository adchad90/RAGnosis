# src/diagnostic_ai/data/patient_simulator.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import random

@dataclass
class PatientRecord:
    patient_id: str
    name: str
    age: int
    vitals: dict  # heart_rate, bp, temp, oxygen_sat, respiratory_rate
    recent_labs: dict  # troponin, creatinine, glucose, hemoglobin, etc.
    symptoms: List[str]
    medical_history: List[str]
    current_medications: List[str]
    last_visit: datetime

class PatientDataSimulator:
    """Simulates real patient data for MVP testing"""
    
    @staticmethod
    def generate_patient_case(risk_level: str = "normal") -> PatientRecord:
        """Generate synthetic patient with varied risk profiles"""
        
        risk_profiles = {
            "normal": {
                "vitals": {"hr": 72, "bp": "120/80", "temp": 98.6, "o2": 98, "rr": 16},
                "labs": {"troponin": 0.01, "creatinine": 0.9, "glucose": 95},
                "symptoms": ["mild fatigue"],
            },
            "high_risk_acs": {
                "vitals": {"hr": 95, "bp": "140/90", "temp": 99.2, "o2": 94, "rr": 22},
                "labs": {"troponin": 0.15, "creatinine": 1.1, "glucose": 180},
                "symptoms": ["chest tightness", "dyspnea", "diaphoresis"],
            },
            "high_risk_sepsis": {
                "vitals": {"hr": 110, "bp": "95/60", "temp": 101.5, "o2": 92, "rr": 28},
                "labs": {"troponin": 0.02, "creatinine": 2.1, "glucose": 250},
                "symptoms": ["fever", "confusion", "weakness"],
            }
        }
        
        profile = risk_profiles.get(risk_level, risk_profiles["normal"])
        
        return PatientRecord(
            patient_id=f"PT{random.randint(10000, 99999)}",
            name=f"Patient {random.randint(1, 100)}",
            age=random.randint(40, 85),
            vitals=profile["vitals"],
            recent_labs=profile["labs"],
            symptoms=profile["symptoms"],
            medical_history=["hypertension", "diabetes", "hyperlipidemia"],
            current_medications=["lisinopril", "metformin", "atorvastatin"],
            last_visit=datetime.now() - timedelta(days=random.randint(7, 90))
        )
    
    @staticmethod
    def patient_to_context(patient: PatientRecord) -> str:
        """Convert patient record to text context for RAG"""
        return f"""
        Patient ID: {patient.patient_id}
        Age: {patient.age}
        Vitals: HR={patient.vitals['hr']}, BP={patient.vitals['bp']}, Temp={patient.vitals['temp']}°F, O2 Sat={patient.vitals['o2']}%
        Recent Labs: Troponin={patient.recent_labs['troponin']}, Creatinine={patient.recent_labs['creatinine']}
        Current Symptoms: {', '.join(patient.symptoms)}
        Medical History: {', '.join(patient.medical_history)}
        Medications: {', '.join(patient.current_medications)}
        Last Visit: {patient.last_visit.strftime('%Y-%m-%d')}
        """