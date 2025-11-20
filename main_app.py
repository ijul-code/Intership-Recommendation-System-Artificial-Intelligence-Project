import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1) Import module
from fuzzy_model import get_fuzzy_score
from evaluation_metrics import calculate_baseline_score

# constraints
DATA_FILE = 'utp_internship_data.csv'
SKILLS = ["Python", "MATLAB", "Leadership", "Teamwork", "AutoCAD"]
SECTOR_TO_COMPANY = {
    'oil & gas': 'PETRONAS Energy Solutions',
    'tech & software': 'UTP Digital Labs',
    'finance & consulting': 'Perak Financial Group',
    'manufacturing': 'Malaysian AutoWorks',
    'construction': 'Bota Infra Group',
}


@st.cache_data
def load_data():
    """
    loads ana returns the structured data
    """
    try:
        df = pd.read_csv(DATA_FILE)
        # ensure text columns are lowercased for matching
        df['Pref_Sector'] = df['Pref_Sector'].str.lower()
        df['req_Sector'] = df['req_Sector'].str.lower()
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file {DATA_FILE} not found. Ensure Person 1 ran data_collection.py.")
        return pd.DataFrame()


# 2. Run Recommendation engine logic

def run_recommendation(student_profile, df_internships):
    """
    iterates through all internships and calculates score
    """
    recommendations = []

    for index, job in df_internships.iterrows():
        # calculate skill match score for fuzzy model (0-100)
        skill_scores = []

        for s in SKILLS:
            student_val = student_profile[f'Skill_{s}']
            req_val = job[f'Req_Skill_{s}_Level']

            # if job require skill, calculate how close student is
            if req_val > 0:
                ratio = (student_val / req_val) * 100
                skill_scores.append(min(100, ratio))
            else:
                # if job doesn't require it, student gets full points for this skill
                skill_scores.append(100)

        # final input is the average of all individual skill matches
        skill_match_score = np.mean(skill_scores) if skill_scores else 0

        # prepare input for both models
        sector_match_value = 1.0 if student_profile['Pref_Sector'] == job['req_Sector'] else 0.0

        # get score from models
        fuzzy_score = get_fuzzy_score(
            float(student_profile['CGPA']),
            skill_match_score,
            sector_match_value
        )

        student_skill_sum = sum(student_profile[f'Skill_{s}'] for s in SKILLS)
        req_skill_sum = sum(job[f'Req_Skill_{s}_Level'] for s in SKILLS)

        baseline_score = calculate_baseline_score(
            float(student_profile['CGPA']),
            job['Req_CGPA'],
            student_profile['Pref_Sector'], job['req_Sector'],
            student_skill_sum, req_skill_sum
        )

        company_name = SECTOR_TO_COMPANY.get(job['req_Sector'], 'Global Internship Co.')

        recommendations.append({
            'Company': company_name,
            'Sector': job['req_Sector'].title(),
            'Fuzzy Score': fuzzy_score,
            'Baseline Score': baseline_score,
            'Required_CGPA': job['Req_CGPA']
        })

    # rank by fuzzy score and return the top results
    results_df = pd.DataFrame(recommendations)
    results_df = results_df.sort_values(by='Fuzzy Score', ascending=False)

    # scale fuzzy score from 0-100 to 0.0-1.0 for consistency with baseline
    results_df['Fuzzy Score'] = results_df['Fuzzy Score'] / 100

    return results_df.head(10)  # show top 10 recommendation


# 3. User Interface

def main():
    st.set_page_config(layout="wide")
    st.title(" UTP INTERNSHIP RECOMMENDATION SYSTEM")
    st.markdown("### Powered by Fuzzy Logic")

    df_internships = load_data()
    if df_internships.empty:
        return

    st.header("1. Your Profile")

    # Organize CGPA and Sector in two columns
    col1, col2 = st.columns(2)

    with col1:
        # CGPA Input
        cgpa = st.slider("CGPA (Scale 2.0 - 4.0)", 2.0, 4.0, 3.5, 0.1)

    with col2:
        # Sector preference
        sectors = df_internships['req_Sector'].unique()
        pref_sector = st.selectbox('Preferred Industry Sector', sectors).lower()

    st.header("2. Your Skill Levels (0-100)")

    # Organize skills in two columns
    col_skills_1, col_skills_2, col_skills_3 = st.columns(3)  # Using three columns for better spread
    skill_levels = {}

    # Divide SKILLS into columns
    skill_groups = [SKILLS[:2], SKILLS[2:4], SKILLS[4:]]
    cols = [col_skills_1, col_skills_2, col_skills_3]

    # Place sliders into columns
    for group, col in zip(skill_groups, cols):
        with col:
            for skill in group:
                slider_value = st.slider(f"{skill} Proficiency", 0, 100, 70, 5)
                skill_levels[f'Skill_{skill}'] = float(slider_value)

    # Place the button below all the inputs
    if st.button("Generate Recommendations"):
        # Construct the current student profile
        student_profile = {'CGPA': float(cgpa), 'Pref_Sector': pref_sector, **skill_levels}

        # run the engine
        top_recommendations = run_recommendation(student_profile, df_internships)

        # display the result
        st.session_state['recommendations'] = top_recommendations
        st.session_state['run'] = True

    # main area for result display
    if st.session_state.get('run', False):
        st.header("Top 10 Internship Recommendations")

        # Display the ranked table (Using width='stretch')
        st.dataframe(
            st.session_state['recommendations'][
                ['Company', 'Sector', 'Fuzzy Score', 'Baseline Score', 'Required_CGPA']],
            width='stretch',
            column_config={
                'Fuzzy Score': st.column_config.ProgressColumn("Fuzzy Score", format="%.2f", min_value=0, max_value=1),
                'Baseline Score': st.column_config.ProgressColumn("Baseline Score", format="%.2f", min_value=0,
                                                                  max_value=1)
            }
        )

        st.subheader("Model Comparison Visualization")
        st.write("Fuzzy Score Mean:", st.session_state['recommendations']['Fuzzy Score'].mean())

        # Create data for visualization
        avg_scores = st.session_state['recommendations'][['Fuzzy Score', 'Baseline Score']].mean().reset_index()
        avg_scores.columns = ['Model', 'Average Score']

        # plot using plotly (Using width='stretch')
        fig = px.bar(
            avg_scores,
            x='Model',
            y='Average Score',
            color='Model',
            title="Average Recommendation Score for Top 10 Results",
            range_y=[0.0, 1.0]
        )
        st.plotly_chart(fig, width='stretch')


if __name__ == '__main__':
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = pd.DataFrame()
    if 'run' not in st.session_state:
        st.session_state['run'] = False
    main()
