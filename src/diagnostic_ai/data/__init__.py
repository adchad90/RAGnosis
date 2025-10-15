# src/diagnostic_ai/data/__init__.py
"""
Data module - Patient simulation and data generation
"""

from diagnostic_ai.data.patient_simulator import (
    PatientDataSimulator,
    PatientRecord,
)

__all__ = [
    "PatientDataSimulator",
    "PatientRecord",
]