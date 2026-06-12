from langgraph.graph import StateGraph, START, END
from pipeline.state import TrueHireState
from pipeline.nodes.jd_parser import jd_parser_node
from pipeline.nodes.hr_gate import hr_gate_node
from pipeline.nodes.profile_parser import profile_parser_node
from pipeline.nodes.link_verifier import link_verifier_node
from pipeline.nodes.github_analyzer import github_analyzer_node
from pipeline.nodes.social_analyzer import social_analyzer_node
from pipeline.nodes.ai_detector import ai_detector_node
from pipeline.nodes.skill_transfer import skill_transfer_node
from pipeline.nodes.llm_analyst import llm_analyst_node
from pipeline.nodes.llm_challenger import llm_challenger_node
from pipeline.nodes.synthesizer import synthesizer_node
from pipeline.nodes.ranker import ranker_node

def build_graph():
    workflow = StateGraph(TrueHireState)
    
    workflow.add_node("jd_parser", jd_parser_node)
    workflow.add_node("hr_gate", hr_gate_node)
    workflow.add_node("profile_parser", profile_parser_node)
    workflow.add_node("link_verifier", link_verifier_node)
    workflow.add_node("github_analyzer", github_analyzer_node)
    workflow.add_node("social_analyzer", social_analyzer_node)
    workflow.add_node("ai_detector", ai_detector_node)
    workflow.add_node("skill_transfer", skill_transfer_node)
    workflow.add_node("llm_analyst", llm_analyst_node)
    workflow.add_node("llm_challenger", llm_challenger_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("ranker", ranker_node)

    workflow.add_edge(START, "jd_parser")
    workflow.add_edge("jd_parser", "hr_gate")
    workflow.add_edge("hr_gate", "profile_parser")
    workflow.add_edge("profile_parser", "link_verifier")
    workflow.add_edge("link_verifier", "github_analyzer")
    workflow.add_edge("github_analyzer", "social_analyzer")
    workflow.add_edge("social_analyzer", "ai_detector")
    workflow.add_edge("ai_detector", "skill_transfer")
    workflow.add_edge("skill_transfer", "llm_analyst")
    workflow.add_edge("llm_analyst", "llm_challenger")
    workflow.add_edge("llm_challenger", "synthesizer")
    workflow.add_edge("synthesizer", "ranker")
    workflow.add_edge("ranker", END)
    
    return workflow.compile()
