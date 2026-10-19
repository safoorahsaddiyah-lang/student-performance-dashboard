"""
Student Performance Dataset Generator
Generates realistic, balanced sample student academic data.
Uses standard Python library (random, csv, math) so it can run anywhere.
"""

import csv
import random

def generate_sample_dataset(filename="sample_students.csv", num_records=250, seed=42):
    random.seed(seed)

    first_names = [
        "Liam", "Olivia", "Noah", "Emma", "Oliver", "Charlotte", "Elijah", "Amelia",
        "James", "Sophia", "William", "Isabella", "Benjamin", "Mia", "Lucas", "Evelyn",
        "Henry", "Harper", "Alexander", "Camila", "Mason", "Gianna", "Michael", "Abigail",
        "Ethan", "Luna", "Daniel", "Ella", "Jacob", "Elizabeth", "Logan", "Sofia",
        "Jackson", "Emily", "Sebastian", "Avery", "Jack", "Mila", "Aiden", "Arya",
        "Owen", "Chloe", "Samuel", "Layla", "Matthew", "Penelope", "Joseph", "Riley",
        "Levi", "Zoey", "David", "Nora", "John", "Lily", "Wyatt", "Eleanor",
        "Carter", "Hannah", "Julian", "Lillian", "Luke", "Addison", "Grayson", "Aubrey",
        "Isaac", "Ellie", "Jayden", "Stella", "Theodore", "Natalie", "Gabriel", "Zoe",
        "Anthony", "Leah", "Dylan", "Hazel", "Leo", "Violet", "Lincoln", "Aurora",
        "Jaxon", "Savannah", "Asher", "Audrey", "Christopher", "Brooklyn", "Josiah", "Bella",
        "Andrew", "Claire", "Thomas", "Skylar", "Joshua", "Lucy", "Ezra", "Paisley"
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
        "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
        "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Mendoza", "Patel"
    ]

    genders = ["Female", "Male"]
    grade_levels = ["Grade 10", "Grade 11", "Grade 12"]
    sections = ["Section A", "Section B", "Section C"]
    extracurriculars = ["Sports", "Music", "Debate", "Robotics", "Arts", "None"]

    records = []

    for i in range(1, num_records + 1):
        student_id = f"STU{1000 + i}"
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        gender = random.choice(genders)
        grade_level = random.choice(grade_levels)
        section = random.choice(sections)

        # Realistic correlated variables:
        # Attendance: beta-like distribution centered around 82%, between 50% and 100%
        base_factor = random.gauss(0.80, 0.12)
        attendance_rate = round(max(50.0, min(100.0, base_factor * 100)), 1)

        # Weekly study hours correlated somewhat with attendance and conscientiousness
        study_hours = round(max(3.0, min(35.0, (attendance_rate / 100) * 18 + random.gauss(4, 3.5))), 1)

        # Subject marks correlated with attendance & study hours + subject affinity
        intel_factor = (attendance_rate * 0.45) + (study_hours * 1.2) + random.gauss(15, 8)
        
        math_score = int(round(max(35, min(100, intel_factor + random.gauss(-2, 7)))))
        science_score = int(round(max(38, min(100, intel_factor + random.gauss(1, 6)))))
        english_score = int(round(max(40, min(100, intel_factor + random.gauss(4, 5)))))
        history_score = int(round(max(40, min(100, intel_factor + random.gauss(3, 6)))))

        # Compute averages & grades
        avg_score = round((math_score + science_score + english_score + history_score) / 4.0, 1)

        if avg_score >= 90:
            grade = "A"
        elif avg_score >= 80:
            grade = "B"
        elif avg_score >= 70:
            grade = "C"
        elif avg_score >= 60:
            grade = "D"
        else:
            grade = "F"

        status = "Pass" if avg_score >= 60 else "Fail"
        activity = random.choice(extracurriculars)

        records.append({
            "Student_ID": student_id,
            "Name": full_name,
            "Gender": gender,
            "Grade_Level": grade_level,
            "Section": section,
            "Attendance_Rate": attendance_rate,
            "Study_Hours_Per_Week": study_hours,
            "Math_Score": math_score,
            "Science_Score": science_score,
            "English_Score": english_score,
            "History_Score": history_score,
            "Average_Score": avg_score,
            "Grade": grade,
            "Status": status,
            "Extracurricular": activity
        })

    fieldnames = [
        "Student_ID", "Name", "Gender", "Grade_Level", "Section",
        "Attendance_Rate", "Study_Hours_Per_Week",
        "Math_Score", "Science_Score", "English_Score", "History_Score",
        "Average_Score", "Grade", "Status", "Extracurricular"
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully generated {num_records} student records in '{filename}'.")

if __name__ == "__main__":
    generate_sample_dataset()
