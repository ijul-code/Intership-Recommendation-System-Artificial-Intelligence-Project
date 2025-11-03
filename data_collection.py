import pandas as pd
import random

# Define project parameters
NUM_RECORDS = 2000
MAJORS = ["Computer Science", "Petroleum Engineering", "Chemical Engineering", "Electrical Engineering"]
SECTORS = ["Oil & Gas", "Tech & Software", "Finance & Consulting", "Manufacturing"]
SKILLS = ["Python", "MATLAB", "Leadership", "Teamwork", "AutoCAD"]

data = []
for i in range(1, NUM_RECORDS + 1):
    # simulate student profile
    major = random.choice(MAJORS)
    cgpa = round(random.uniform(2.5, 4.0), 2)
    pref_sector = random.choice(SECTORS)

    # simulate internship requirements (linked to sector/major logic)
    req_cgpa = round(random.uniform(2.8, 3.8), 2)
    req_sector = pref_sector if random.random() < 0.7 else random.choice(SECTORS) # 70% match

    record = {
        'StudentID' : f'S{i:04}',
        'Major_Course' : major,
        'CGPA' : cgpa,
        'Pref_Sector' : pref_sector,
        'req_Sector' : req_sector,
        'Req_CGPA' : req_cgpa,
    }

    #simulate skills (0-100 scale) for both student and requirement
    for skill in SKILLS:
        record[f'Skill_{skill}_Level'] = random.randint(30, 95)
        record[f'Req_Skill_{skill}_Level'] = random.randint(50, 90)

    data.append(record)

df = pd.DataFrame(data)

# Preprocessing: ensure consistency
df['Major_Course'] = df['Major_Course'].str.lower()
df['req_Sector'] = df['req_Sector'].str.lower()

df.to_csv('utp_internship_data.csv', index=False)
print("Data simulation complete. 'utp_internship_data.csv' created")
