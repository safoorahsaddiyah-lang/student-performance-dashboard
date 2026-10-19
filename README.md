# 🎓 Student Performance Analytics Dashboard

An interactive, production-ready data analytics web application built with **Python**, **Streamlit**, **Pandas**, and **Plotly**. Designed for school administrators, teachers, and academic advisors to explore student performance, track key metrics, discover academic trends, and identify students requiring academic intervention.

---

## 🌟 Key Features

1. **Executive KPI Cards**: Real-time summary cards displaying Total Students, Average Marks, Average Attendance Rate, and Overall Pass Percentage.
2. **Interactive Visualizations**:
   - **Subject-Wise Analysis**: Mean vs. Median comparison across Mathematics, Science, English, and History.
   - **Grade Distribution**: Donut chart displaying proportions of grades (A, B, C, D, F).
   - **Attendance vs. Performance**: Scatter plot with Ordinary Least Squares (OLS) trendline.
   - **Study Habit Analysis**: Weekly study hours plotted against marks with attendance bubble weighting.
   - **Subject Correlation Matrix**: Pairwise correlation heatmap across all subjects.
   - **Demographic Comparisons**: Grouped performance comparisons across Grade Levels and Sections.
3. **Robust Data Validation**:
   - Gracefully handles missing files, empty data, non-numeric values, or missing headers.
   - Automatically computes missing averages, letter grades, and pass/fail statuses.
   - Provides non-destructive median imputation for missing values with user-facing alerts.
4. **Interactive Filters**:
   - Grade level, section, and gender multi-select filters.
   - Dual-handle range sliders for attendance rate and marks.
   - Pass/fail radio button filter.
5. **Data-Driven Automated Insights**:
   - Dynamically calculates the top-performing and lowest-performing subjects.
   - Measures mathematical correlation between attendance and marks.
   - Flags students requiring academic intervention (marks < 60 or attendance < 70%).
   - Generates an instant Honor Roll list (students with Grade A).
6. **Data Explorer & Export**:
   - Searchable, sortable student record table with progress bars.
   - One-click CSV export of cleaned and filtered datasets.
   - Downloadable CSV template for testing custom datasets.

---

## 📁 Project Structure

```text
student-performance-dashboard/
│
├── app.py                 # Main Streamlit application and dashboard UI
├── generate_data.py       # Standalone script to generate balanced sample student data
├── sample_students.csv    # Ready-to-use sample dataset (250 student records)
├── requirements.txt       # Python dependencies (streamlit, pandas, plotly, numpy)
├── .gitignore             # Standard git exclusions for Python & Streamlit
└── README.md              # Documentation, setup guide, and portfolio walkthrough
```

---

## 📊 Dataset Schema

The application accepts any CSV matching or containing the following columns:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Student_ID` | String | Unique identifier (e.g., `STU1001`) *(Auto-generated if absent)* |
| `Name` | String | Full name of the student *(Auto-generated if absent)* |
| `Gender` | String | `Female`, `Male`, or `Other` |
| `Grade_Level` | String | E.g., `Grade 10`, `Grade 11`, `Grade 12` |
| `Section` | String | Class section (e.g., `Section A`, `Section B`) |
| `Attendance_Rate` | Float | Percentage from `0.0` to `100.0` (**Required**) |
| `Study_Hours_Per_Week` | Float | Average weekly study hours outside class |
| `Math_Score` | Float/Int | Marks out of 100 (**Required**) |
| `Science_Score` | Float/Int | Marks out of 100 (**Required**) |
| `English_Score` | Float/Int | Marks out of 100 (**Required**) |
| `History_Score` | Float/Int | Marks out of 100 (**Required**) |
| `Average_Score` | Float | Automatically calculated mean of subjects |
| `Grade` | String | Letter grade: `A` (≥90), `B` (≥80), `C` (≥70), `D` (≥60), `F` (<60) |
| `Status` | String | `Pass` (≥60) or `Fail` (<60) |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have Python 3.10 or newer installed. Check your version with:
```bash
python --version
```

### 2. Clone or Open the Repository
```bash
cd student-performance-dashboard
```

### 3. (Optional but Recommended) Create a Virtual Environment
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
streamlit run app.py
```

The application will start immediately and automatically open in your default browser at:
👉 **`http://localhost:8501`**

---

## 🎨 How to Customize the Design

1. **Change the Color Palette**:
   - Open `app.py` and inspect `CHART_COLORWAY` around line 130:
     ```python
     CHART_COLORWAY = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]
     ```
   - Customize banner gradient or card colors inside the `CUSTOM_CSS` block.
2. **Add More Subjects**:
   - Add new column names to `CORE_SUBJECT_COLS` in `app.py` (e.g., `"Art_Score"`, `"Computer_Score"`).
   - The application will automatically factor them into average calculations, chart bars, and correlation matrices.
3. **Change Grade Thresholds**:
   - Modify the `calculate_grade()` function in `app.py` to match your local grading scale (e.g., standard UK, US, or Indian marks system).

---

## 📤 How to Upload to GitHub

Follow these simple steps in your terminal to publish this project to your GitHub profile:

1. **Initialize Git in the project directory**:
   ```bash
   git init
   ```
2. **Stage all files and make your first commit**:
   ```bash
   git add .
   git commit -m "feat: complete student performance analytics dashboard"
   ```
3. **Create a new repository on GitHub**:
   - Go to [github.com/new](https://github.com/new).
   - Enter Repository Name: `student-performance-dashboard`.
   - Leave it public and do not initialize with README (you already have one).
4. **Link your local repository and push**:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<YOUR-USERNAME>/student-performance-dashboard.git
   git push -u origin main
   ```

---

## 🌐 Free Cloud Deployment (Streamlit Community Cloud)

You can deploy this dashboard online for free so anyone can try it from a public link:

1. Push your code to GitHub following the steps above.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"**, select your repository `student-performance-dashboard`, branch `main`, and main file `app.py`.
4. Click **"Deploy"**! Your app will be live with a shareable URL in under 2 minutes.

---

## 📜 License
This project is open-source under the MIT License. Feel free to customize and showcase it in your data analytics portfolio!
