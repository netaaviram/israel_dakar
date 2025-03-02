import streamlit as st
import pandas as pd

def process_salary(file, salary):
    df = pd.read_csv(file, header=3)  # Load CSV file

    # Fix Column Names
    df.rename(columns={"HEURES\nEN NOMBRE": "Hours_Worked"}, inplace=True)

    # Convert Hours to Numeric
    df["Hours_Worked"] = pd.to_numeric(df["Hours_Worked"], errors="coerce")

    # Remove "TOTAL" Rows
    df = df[~df["JOUR"].str.contains("TOTAL", na=False)]

    # Categorize Work Hours
    def classify_hours(row):
        if row["JOUR"] in ["SAMEDI", "DIMANCHE"] or pd.notna(row["REMARQUES"]):  
            return "Weekend/Holiday"
        return "Mid-Week"

    df["Category"] = df.apply(classify_hours, axis=1)

    # Compute Base Work Hours
    total_hours = df["Hours_Worked"].sum()
    weekend_hours = df[df["Category"] == "Weekend/Holiday"]["Hours_Worked"].sum()
    midweek_hours = df[df["Category"] == "Mid-Week"]["Hours_Worked"].sum()

    # Extract Extra Hours Table
    df_extra = df[["HS", "0.15", "0.4", "0.6", "1"]].dropna(how="all")
    df_extra = df_extra.apply(pd.to_numeric, errors="coerce")
    total_extra_hours = df_extra["HS"].sum()

    # Compute Salary Distributions
    total_salary = salary
    overtime_salary = (total_extra_hours / (total_hours + total_extra_hours)) * total_salary
    regular_salary = total_salary - overtime_salary

    # Overtime Tariff Distribution
    tariff_15_salary = overtime_salary * (df_extra["0.15"].sum() / total_extra_hours)
    tariff_40_salary = overtime_salary * (df_extra["0.4"].sum() / total_extra_hours)
    tariff_60_salary = overtime_salary * (df_extra["0.6"].sum() / total_extra_hours)
    tariff_100_salary = overtime_salary * (df_extra["1"].sum() / total_extra_hours)

    # Split Salaries into Minhala and Batmach
    minhala_salary = (midweek_hours / total_hours) * regular_salary + tariff_15_salary + tariff_40_salary
    batmach_salary = (weekend_hours / total_hours) * regular_salary + tariff_60_salary + tariff_100_salary

    return {
        "Total Hours Worked": round(total_hours, 2),
        "Weekend/Holiday Hours": round(weekend_hours, 2),
        "Mid-Week Hours": round(midweek_hours, 2),
        "Total Salary": round(total_salary, 2),
        "Batmach Salary": round(batmach_salary, 2),
        "Minhala Salary": round(minhala_salary, 2),
    }

# 🌐 Streamlit Web Interface
st.title("Salary Calculator Web App")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
salary_input = st.number_input("Enter Salary (CFA)", min_value=0, value=5000)

if st.button("Calculate Salary Breakdown") and uploaded_file:
    results = process_salary(uploaded_file, salary_input)
    st.write("### Work Hours Breakdown")
    st.write(f"**Total Hours Worked:** {results['Total Hours Worked']}")
    st.write(f"**Weekend/Holiday Hours:** {results['Weekend/Holiday Hours']}")
    st.write(f"**Mid-Week Hours:** {results['Mid-Week Hours']}")

    st.write("### Salary Breakdown")
    st.write(f"**Total Salary:** {results['Total Salary']} CFA")
    st.write(f"**Batmach Salary:** {results['Batmach Salary']} CFA")
    st.write(f"**Minhala Salary:** {results['Minhala Salary']} CFA")

