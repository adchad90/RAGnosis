# src/diagnostic_ai/agent/graph.py
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.schema import AIMessage, HumanMessage
from typing import TypedDict, List, Annotated
from diagnostic_ai.config import settings
from diagnostic_ai.agent.tools import get_tools
from diagnostic_ai.utils.logger import AuditLogger
import json

audit_logger = AuditLogger("DiagnosticAgent")

class AgentState(TypedDict):
    patient_context: str
    messages: List[dict]
    analysis_results: dict
    alerts: List[str]
    next_action: str
    risk_assessment: dict
    vitals_analysis: str
    labs_analysis: str
    guidelines: str

def initialize_diagnostic_workflow(patient_context: str) -> AgentState:
    """Initialize agent state with patient data"""
    return {
        "patient_context": patient_context,
        "messages": [],
        "analysis_results": {},
        "alerts": [],
        "next_action": "analyze_vitals",
        "risk_assessment": {},
        "vitals_analysis": "",
        "labs_analysis": "",
        "guidelines": ""
    }

def create_diagnostic_agent():
    """Create LangGraph workflow for diagnostic analysis"""
    
    # Use FREE Groq LLM
    llm = ChatGroq(
        model=settings.llm_model,
        temperature=settings.temperature,
        api_key=settings.groq_api_key,
        max_tokens=2048
    )
    
    tools = get_tools()
    # Create tool name to function mapping
    tool_map = {tool.name: tool for tool in tools}
    
    def analyze_vitals_node(state: AgentState):
        """Extract and analyze vital signs"""
        # Simple prompt without tool binding - direct analysis
        prompt = f"""
        You are a medical AI analyzing patient vital signs. 
        
        Patient data:
        {state['patient_context']}
        
        Analyze the vital signs and identify any abnormalities. Look for:
        - Heart rate (normal: 60-100 bpm)
        - Blood pressure (normal: <120/80)
        - Temperature (normal: 97-99°F)
        - Oxygen saturation (normal: >95%)
        - Respiratory rate (normal: 12-20/min)
        
        Provide a brief assessment of vital sign abnormalities.
        """
        
        response = llm.invoke(prompt)
        result = response.content if hasattr(response, 'content') else str(response)
        
        audit_logger.log_agent_action("analyze_vitals", 
                                     {"patient_context": state["patient_context"]},
                                     {"analysis": result})
        
        return {
            **state,
            "vitals_analysis": result,
            "next_action": "analyze_labs"
        }
    
    def analyze_labs_node(state: AgentState):
        """Extract and analyze lab values"""
        prompt = f"""
        You are a medical AI analyzing laboratory results.
        
        Patient data:
        {state['patient_context']}
        
        Analyze the lab values and identify any abnormalities. Key values:
        - Troponin (normal: <0.04) - cardiac injury marker
        - Creatinine (normal: 0.7-1.3) - kidney function
        - Glucose (normal: 70-100 fasting) - blood sugar
        - Lactate (normal: <2) - tissue perfusion
        
        Provide a brief assessment of concerning lab findings.
        """
        
        response = llm.invoke(prompt)
        result = response.content if hasattr(response, 'content') else str(response)
        
        audit_logger.log_agent_action("analyze_labs",
                                     {"patient_context": state["patient_context"]},
                                     {"analysis": result})
        
        return {
            **state,
            "labs_analysis": result,
            "next_action": "retrieve_guidelines"
        }
    
    def retrieve_guidelines_node(state: AgentState):
        """Retrieve relevant clinical guidelines"""
        # Use RAG to get guidelines
        from diagnostic_ai.agent.tools import retrieve_clinical_guidelines
        
        # Determine what to search for based on symptoms
        context_lower = state['patient_context'].lower()
        
        queries = []
        if 'chest' in context_lower or 'troponin' in context_lower:
            queries.append("acute coronary syndrome ACS criteria")
        if 'fever' in context_lower or 'confusion' in context_lower:
            queries.append("sepsis qSOFA criteria")
        if 'blood pressure' in context_lower or 'bp' in context_lower:
            queries.append("hypertensive crisis")
        
        # Default query if no specific symptoms
        if not queries:
            queries.append("diagnostic criteria general assessment")
        
        guidelines_text = ""
        for query in queries:
            guidelines_text += retrieve_clinical_guidelines.invoke({"query": query}) + "\n\n"
        
        audit_logger.log_agent_action("retrieve_guidelines",
                                     {"queries": queries},
                                     {"guidelines": guidelines_text})
        
        return {
            **state,
            "guidelines": guidelines_text,
            "next_action": "assess_risk"
        }
    
    def assess_risk_node(state: AgentState):
        """Comprehensive risk assessment"""
        prompt = f"""
        You are a medical AI performing a comprehensive diagnostic risk assessment.
        
        PATIENT DATA:
        {state['patient_context']}
        
        VITAL SIGNS ANALYSIS:
        {state['vitals_analysis']}
        
        LAB ANALYSIS:
        {state['labs_analysis']}
        
        CLINICAL GUIDELINES:
        {state['guidelines']}
        
        Based on ALL this information:
        1. Identify the top 2-3 most likely diagnoses
        2. Assess risk level for each (HIGH/MODERATE/LOW)
        3. Explain your reasoning using the clinical guidelines
        
        Format your response as:
        **Diagnosis 1:** [Name]
        **Risk Level:** [HIGH/MODERATE/LOW]
        **Reasoning:** [Brief explanation]
        
        **Diagnosis 2:** [Name]
        **Risk Level:** [HIGH/MODERATE/LOW]
        **Reasoning:** [Brief explanation]
        """
        
        response = llm.invoke(prompt)
        assessment = response.content if hasattr(response, 'content') else str(response)
        
        risk_data = {
            "assessment": assessment,
            "timestamp": "current"
        }
        
        audit_logger.log_agent_action("assess_risk",
                                     {"patient_context": state["patient_context"]},
                                     risk_data)
        
        return {
            **state,
            "risk_assessment": risk_data,
            "next_action": "generate_alert"
        }
    
    def generate_alert_node(state: AgentState):
        """Generate actionable clinical alert if high-risk condition detected"""
        assessment = state['risk_assessment'].get('assessment', '')
        
        # Check if HIGH risk is mentioned
        if 'HIGH' in assessment.upper():
            prompt = f"""
            Based on this risk assessment:
            {assessment}
            
            Generate a clinical alert for the healthcare provider. Include:
            1. Priority level (🔴 HIGH PRIORITY)
            2. Suspected condition
            3. Key findings that support this
            4. Recommended immediate actions (specific tests, consultations, treatments)
            
            Format as a clear, actionable alert.
            """
            
            response = llm.invoke(prompt)
            alert_text = response.content if hasattr(response, 'content') else str(response)
            
            alerts = [f"🔴 CLINICAL ALERT\n\n{alert_text}"]
        else:
            alerts = []
        
        audit_logger.log_agent_action("generate_alert",
                                     {"risk_assessment": state["risk_assessment"]},
                                     {"alerts": alerts})
        
        return {
            **state,
            "alerts": alerts,
            "next_action": "end"
        }
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze_vitals", analyze_vitals_node)
    workflow.add_node("analyze_labs", analyze_labs_node)
    workflow.add_node("retrieve_guidelines", retrieve_guidelines_node)
    workflow.add_node("assess_risk", assess_risk_node)
    workflow.add_node("generate_alert", generate_alert_node)
    
    # Add edges
    workflow.add_edge("analyze_vitals", "analyze_labs")
    workflow.add_edge("analyze_labs", "retrieve_guidelines")
    workflow.add_edge("retrieve_guidelines", "assess_risk")
    workflow.add_edge("assess_risk", "generate_alert")
    workflow.add_edge("generate_alert", END)
    
    workflow.set_entry_point("analyze_vitals")
    
    return workflow.compile()

# Initialize graph
diagnostic_graph = create_diagnostic_agent()