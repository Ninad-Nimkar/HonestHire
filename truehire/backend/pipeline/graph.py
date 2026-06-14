"""
LangGraph pipeline definition — 12-node candidate analysis pipeline.

Follows langgraph skill: StateGraph, conditional edges, linear flow.
"""

from langgraph.graph import StateGraph, START, END

from pipeline.state import PipelineState
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


def build_pipeline() -> StateGraph:
    """Build and return the compiled TrueHire analysis pipeline."""

    graph = StateGraph(PipelineState)

    # Add all 12 nodes
    graph.add_node("jd_parser", jd_parser_node)
    graph.add_node("hr_gate", hr_gate_node)
    graph.add_node("profile_parser", profile_parser_node)
    graph.add_node("link_verifier", link_verifier_node)
    graph.add_node("github_analyzer", github_analyzer_node)
    graph.add_node("social_analyzer", social_analyzer_node)
    graph.add_node("ai_detector", ai_detector_node)
    graph.add_node("skill_transfer", skill_transfer_node)
    graph.add_node("llm_analyst", llm_analyst_node)
    graph.add_node("llm_challenger", llm_challenger_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("ranker", ranker_node)

    # Linear flow: START → jd_parser → hr_gate → ... → ranker → END
    graph.add_edge(START, "jd_parser")
    graph.add_edge("jd_parser", "hr_gate")
    graph.add_edge("hr_gate", "profile_parser")
    graph.add_edge("profile_parser", "link_verifier")
    graph.add_edge("link_verifier", "github_analyzer")
    graph.add_edge("github_analyzer", "social_analyzer")
    graph.add_edge("social_analyzer", "ai_detector")
    graph.add_edge("ai_detector", "skill_transfer")
    graph.add_edge("skill_transfer", "llm_analyst")
    graph.add_edge("llm_analyst", "llm_challenger")
    graph.add_edge("llm_challenger", "synthesizer")
    graph.add_edge("synthesizer", "ranker")
    graph.add_edge("ranker", END)

    return graph.compile()


# Compiled pipeline instance
pipeline = build_pipeline()
