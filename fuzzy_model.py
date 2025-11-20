import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# define variable
# input 1:CGPA (Range 2.0 to 4.0)
# we use 2.0 as the minimum realistic floor for this model
cgpa = ctrl.Antecedent(np.arange(2.0, 4.1, 0.1), 'cgpa')

# input 2 skill match score (range 0 to 100)
# this represents how well the student skill meet the job requirement
# 0 = no skills match, 100 = perfect skill match
skill_match = ctrl.Antecedent(np.arange(0, 101, 1), 'skill_match')

# input 3: sector match (range 0.0 to 1.0)
# 0.0 = different sector, 1.0 = same sector
sector_match = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'sector_match')

# output: recommendation score (range 0 to 100)
# the final score indicating how strongly we recommend this internship
recommendation = ctrl.Consequent(np.arange(0, 101, 1), 'recommendation')

#define membership functions

# cgpa membership
cgpa['low'] = fuzz.trimf(cgpa.universe, [2.0, 2.0, 3.2])
cgpa['medium'] = fuzz.trimf(cgpa.universe, [2.9, 3.4, 3.8])
cgpa['high'] = fuzz.trimf(cgpa.universe, [3.6, 4.0, 4.0])

# skills match membership
skill_match['poor'] = fuzz.trimf(skill_match.universe, [0, 0, 60])
skill_match['fair'] = fuzz.trimf(skill_match.universe, [45, 70, 90])
skill_match['excellent'] = fuzz.trimf(skill_match.universe, [80, 100, 100])

# sector match membership
# use simple triangular functions for binary like logic
sector_match['no'] = fuzz.trimf(sector_match.universe, [0, 0, 0.6])
sector_match['yes'] = fuzz.trimf(sector_match.universe, [0.4, 1, 1])

# recommendation score membership (output)
recommendation['weak'] = fuzz.trimf(recommendation.universe, [0, 10, 40])
recommendation['moderate'] = fuzz.trimf(recommendation.universe, [30, 60, 80])
recommendation['strong'] = fuzz.trimf(recommendation.universe, [70, 100, 100])

#define FUZZY RULES
# these rules determine the logic of the recommendation engine

# rule 1: the ideal candidate (high cgpa, great skill, correct sector)
rule1 = ctrl.Rule(cgpa['high'] & skill_match['excellent'] & sector_match['yes'], recommendation['strong'])

# Rule 2: Strong Candidate (Medium GPA but Great Skills & Sector)
rule2 = ctrl.Rule(cgpa['medium'] & skill_match['excellent'] & sector_match['yes'], recommendation['strong'])

# Rule 3: Compensating Factor (Low GPA but Excellent Skills & Sector)
# Skills can make up for lower grades
rule3 = ctrl.Rule(cgpa['low'] & skill_match['excellent'] & sector_match['yes'], recommendation['moderate'])

# Rule 4: Good Academics, Decent Skills
rule4 = ctrl.Rule(cgpa['high'] & skill_match['fair'] & sector_match['yes'], recommendation['moderate'])

# Rule 5: Sector Mismatch (Even with good stats, wrong sector reduces score)
rule5 = ctrl.Rule(cgpa['high'] & skill_match['excellent'] & sector_match['no'], recommendation['moderate'])

# Rule 6: Poor Match (Low GPA or Poor Skills are dealbreakers)
rule6 = ctrl.Rule(cgpa['low'] | skill_match['poor'], recommendation['weak'])

# Rule 7: Wrong Sector and Average/Low Skills
rule7 = ctrl.Rule(sector_match['no'] & skill_match['fair'], recommendation['weak'])

# rule 8
rule8 = ctrl.Rule(cgpa['medium'] & skill_match['fair'] & sector_match['no'], recommendation['weak'])

# rule 9
rule9= ctrl.Rule(cgpa['high'] & sector_match['yes'], recommendation['moderate'])
# create control system
recommendation_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
recommendation_sim = ctrl.ControlSystemSimulation(recommendation_ctrl)

# MAIN FUNCTION

def get_fuzzy_score(student_cgpa, skill_match_score, sector_match_value):
    """
    Calculate the fuzzy recommendation score.

    Args:
        student_cgpa (float): Student CGPA (exp : 3.5).
        skill_match_score (int): 0-100 score representing how well skills match.
        sector_match_value (float): 1.0 if sectors match, 0.0 if not.

    Returns:
        float: A score between 0 and 100.
    """
    try:
        # pass inputs to the simulation
        recommendation_sim.input['cgpa'] = float(student_cgpa)
        recommendation_sim.input['skill_match'] = float(skill_match_score)
        recommendation_sim.input['sector_match'] = float(sector_match_value)

        # crunch the numbers
        recommendation_sim.compute()

        if 'recommendation'in recommendation_sim.output:
            return round(recommendation_sim.output['recommendation'], 2)
        else:
            return 5.0

    except Exception as e:
        # fallback in case of edge cases
        print(f"Fuzzy Logic Error: {e}")
        return 0.0

# test block
if __name__ == "__main__":
    print("--- Running Fuzzy Model Test ---")

    #Test case 1: Perfect Candidate
    s1 = get_fuzzy_score(3.9, 95,1.0)
    print(f"Perfect Candidate (3.9 CGPA, 95 Skill, Sector Match): {s1} (Expected: High)")

    # Test Case 2: Average Candidate
    s2 = get_fuzzy_score(3.2, 60, 1.0)
    print(f"Average Candidate (3.2 GPA, 60 Skill, Sector Match): {s2} (Expected: Moderate)")

    # Test Case 3: Weak Candidate
    s3 = get_fuzzy_score(2.2, 30, 0.0)
    print(f"Weak Candidate (2.2 GPA, 30 Skill, No Match): {s3} (Expected: Low)")
