"""
Automated Integration & Unit Tests for Student Performance Analytics Dashboard
Tests all data cleaning, validation, statistical calculations, and Plotly charts.
"""

import unittest
import pandas as pd
import numpy as np
import app

class TestStudentDashboard(unittest.TestCase):

    def setUp(self):
        # Load sample data
        self.sample_df = pd.read_csv("sample_students.csv")

    def test_sample_dataset_structure(self):
        """Verify the pre-generated sample dataset has expected columns and rows."""
        self.assertFalse(self.sample_df.empty)
        self.assertGreaterEqual(len(self.sample_df), 100)
        expected_cols = [
            "Student_ID", "Name", "Gender", "Grade_Level", "Section",
            "Attendance_Rate", "Study_Hours_Per_Week",
            "Math_Score", "Science_Score", "English_Score", "History_Score"
        ]
        for col in expected_cols:
            self.assertIn(col, self.sample_df.columns)

    def test_clean_data_success(self):
        """Verify cleaning and validation of valid sample data."""
        cleaned_df, errors, warnings = app.validate_and_clean_data(self.sample_df)
        self.assertIsNotNone(cleaned_df)
        self.assertEqual(len(errors), 0)
        self.assertIn("Average_Score", cleaned_df.columns)
        self.assertIn("Grade", cleaned_df.columns)
        self.assertIn("Status", cleaned_df.columns)

    def test_empty_dataframe_validation(self):
        """Verify proper error returned when uploading an empty DataFrame."""
        empty_df = pd.DataFrame()
        cleaned_df, errors, warnings = app.validate_and_clean_data(empty_df)
        self.assertIsNone(cleaned_df)
        self.assertGreater(len(errors), 0)
        self.assertIn("empty", errors[0].lower())

    def test_missing_required_column_validation(self):
        """Verify validation flags missing required numeric columns."""
        broken_df = pd.DataFrame({
            "Student_ID": ["S1", "S2"],
            "Name": ["Alice", "Bob"],
            # Missing Attendance_Rate and Math_Score
            "Science_Score": [80, 90],
            "English_Score": [85, 95],
            "History_Score": [75, 88]
        })
        cleaned_df, errors, warnings = app.validate_and_clean_data(broken_df)
        self.assertIsNone(cleaned_df)
        self.assertTrue(any("Attendance_Rate" in err for err in errors))
        self.assertTrue(any("Math_Score" in err for err in errors))

    def test_missing_values_imputation(self):
        """Verify NaN values in numeric columns are imputed using median with user warnings."""
        df_with_nan = self.sample_df.copy().head(20)
        df_with_nan.loc[0, "Math_Score"] = np.nan
        df_with_nan.loc[1, "Attendance_Rate"] = np.nan
        
        cleaned_df, errors, warnings = app.validate_and_clean_data(df_with_nan)
        self.assertIsNotNone(cleaned_df)
        self.assertEqual(len(errors), 0)
        self.assertGreater(len(warnings), 0)
        self.assertFalse(cleaned_df["Math_Score"].isnull().any())
        self.assertFalse(cleaned_df["Attendance_Rate"].isnull().any())

    def test_missing_optional_columns_fallback(self):
        """Verify auto-generation of Student_ID, Name, and Study_Hours_Per_Week if absent."""
        minimal_df = pd.DataFrame({
            "Attendance_Rate": [85.0, 92.0, 70.0],
            "Math_Score": [78, 88, 65],
            "Science_Score": [82, 91, 60],
            "English_Score": [80, 85, 72],
            "History_Score": [75, 89, 68]
        })
        cleaned_df, errors, warnings = app.validate_and_clean_data(minimal_df)
        self.assertIsNotNone(cleaned_df)
        self.assertIn("Student_ID", cleaned_df.columns)
        self.assertIn("Name", cleaned_df.columns)
        self.assertIn("Study_Hours_Per_Week", cleaned_df.columns)
        self.assertEqual(len(cleaned_df), 3)

    def test_dynamic_insights_generation(self):
        """Verify insights are dynamically computed and contain expected structure."""
        cleaned_df, _, _ = app.validate_and_clean_data(self.sample_df)
        insights = app.generate_dynamic_insights(cleaned_df)
        self.assertIsInstance(insights, list)
        self.assertGreaterEqual(len(insights), 3)
        for item in insights:
            self.assertIn("title", item)
            self.assertIn("msg", item)
            self.assertIn("type", item)

    def test_all_chart_generators(self):
        """Verify Plotly charts build without exceptions."""
        cleaned_df, _, _ = app.validate_and_clean_data(self.sample_df)
        
        fig1 = app.render_subject_marks_chart(cleaned_df)
        self.assertIsNotNone(fig1)

        fig2 = app.render_grade_distribution_chart(cleaned_df)
        self.assertIsNotNone(fig2)

        fig3 = app.render_attendance_vs_marks_chart(cleaned_df)
        self.assertIsNotNone(fig3)

        fig4 = app.render_study_hours_vs_marks_chart(cleaned_df)
        self.assertIsNotNone(fig4)

        fig5 = app.render_demographic_comparison_chart(cleaned_df, "Grade_Level")
        self.assertIsNotNone(fig5)

if __name__ == "__main__":
    unittest.main()
