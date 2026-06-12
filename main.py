import argparse
import os
from pipeline.graph import build_graph

def main():
    parser = argparse.ArgumentParser(description="TrueHire Candidate Ranking System")
    parser.add_argument("--jd", required=True, help="Path to Job Description file")
    parser.add_argument("--cvs", required=True, help="Directory containing CV files")
    args = parser.parse_args()
    
    with open(args.jd, "r") as f:
        raw_jd = f.read()
        
    raw_cvs = []
    for fn in os.listdir(args.cvs):
        if os.path.isfile(os.path.join(args.cvs, fn)):
            with open(os.path.join(args.cvs, fn), "r") as f:
                raw_cvs.append(f.read())
                
    graph = build_graph()
    
    # Run pipeline
    initial_state = {
        "raw_jd": raw_jd,
        "weighted_jd": None,
        "raw_cvs": raw_cvs,
        "candidates": [],
        "llm_a_scorecards": {},
        "llm_b_flags": {},
        "final_scorecards": []
    }
    
    print("Starting TrueHire pipeline...")
    final_state = graph.invoke(initial_state)
    print("\nPipeline finished! Check the truehire/output/ directory.")

if __name__ == "__main__":
    main()
