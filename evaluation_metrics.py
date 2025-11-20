
def calculate_baseline_score(student_cgpa, req_cgpa, pref_sector, req_sector, student_skill_sum, req_skill_sum):
    """
    Calculates a simple recommendation score (0.0 to 1.0) based on CGPA and Sector/Skill comparison.
    this serves as the baseline for the Fuzzy Logic Model comparison
    """
    score = 0
    weights = {
        'gpa_match': 0.3,
        'sector_match': 0.3,
        'skill_match': 0.4
    }

    # 1. CGPA Match (30% weight)
    # Give full score if CGPA meets or exceeds the minimum requirement
    if student_cgpa >= req_cgpa:
        score += weights['gpa_match']

    # 2. Sector Match (30% weight)
    # Check if the student's preferred sector matches the job's sector
    if pref_sector == req_sector:
        score += weights['sector_match']

    # 3. Basic skill check (40% weight)
    # Check if the student's total skill level is greater than the required skill sum
    if student_skill_sum > req_skill_sum:
        score += weights['skill_match']

    # ensure score doesnt exceed 1.0
    return round(min(score, 1.0), 2)

def precision_at_k(actual_relevant_set, recommended_list, k=5):
    """
    calculate precision at k. measures how many of the top K recommendations were actually relevant
    """
    if not recommended_list:
        return 0.0

    # take only the top k recommendation
    top_k = set(recommended_list[:k])

    # calculate true positive
    true_positives = len(top_k.intersection(actual_relevant_set))

    # precision at k = true positive / k
    return true_positives / k
