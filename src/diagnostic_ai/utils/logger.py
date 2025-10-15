# src/diagnostic_ai/utils/logger.py
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AuditLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.audit_trail = []
    
    def log_agent_action(self, action: str, input_data: dict, output_data: dict):
        """Log all agent actions for compliance"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "input": input_data,
            "output": output_data
        }
        self.audit_trail.append(entry)
        self.logger.info(f"Agent Action: {action}")
    
    def get_audit_trail(self):
        return self.audit_trail