from pipeline.state import TrueHireState
from models.jd import Tier
from config import SCORE_WEIGHTS

def hr_gate_node(state: TrueHireState) -> TrueHireState:
    jd = state.get("weighted_jd")
    if not jd or not jd.skills:
        return state
        
    print("\n--- HR Gate: Tier the extracted skills ---")
    
    final_skills = []
    
    for skill in jd.skills:
        # Check for vague terms
        vague_terms = ["rockstar", "ninja", "10x", "passion"]
        if any(v in skill.name.lower() for v in vague_terms):
            print(f"\n[WARNING] Flagged inflated/vague skill: '{skill.name}'")
            print("Suggest removing or replacing.")
        
        while True:
            print(f"\nSkill: {skill.name}")
            ans = input("Tier? [B]locker / [I]mportant / [N]ice to have / [R]ewrite / [S]kip: ").strip().lower()
            
            if ans == 'b':
                skill.tier = Tier.blocker
                skill.weight = SCORE_WEIGHTS["blocker"]
                final_skills.append(skill)
                break
            elif ans == 'i':
                skill.tier = Tier.important
                skill.weight = SCORE_WEIGHTS["important"]
                final_skills.append(skill)
                break
            elif ans == 'n':
                skill.tier = Tier.nice_to_have
                skill.weight = SCORE_WEIGHTS["nice_to_have"]
                final_skills.append(skill)
                break
            elif ans == 'r':
                new_name = input(f"Rewrite '{skill.name}' as: ").strip()
                if new_name:
                    skill.name = new_name
                    # prompt again for tier
            elif ans == 's':
                print("Skipping skill.")
                break
            else:
                print("Invalid input.")

    print("\n--- Summary of Skills ---")
    for s in final_skills:
        print(f"- {s.name}: {s.tier.value} (Weight: {s.weight})")
        
    confirm = input("Confirm? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Please rerun the pipeline to try again.")
        # Simple handler, real app might loop
        
    jd.skills = final_skills
    state["weighted_jd"] = jd
    
    return state
