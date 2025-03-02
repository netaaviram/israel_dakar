import streamlit as st
import pandas as pd

# Title
st.title("🚖 Salary Calculator Web App")

# Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Ensure file is uploaded
if uploaded_file:
    try:
        # Load Excel file (requires openpyxl)
        xls = pd.ExcelFile(uploaded_file, engine="openpyxl")

        # Get available sheet names
        sheet_names = xls.sheet_names

        # Display available sheets (for debugging)
        st.write("🔍 Available Employees:", sheet_names)

        # Driver selection (Only show if valid sheets exist)
        drivers = ["MOUSSA", "PATHE"]
        selected_driver = st.radio("Select Driver:", drivers)

        if selected_driver in sheet_names:
            # Load the correct sheet with the correct header row (row 3 in Excel, so header=2 in Pandas)
            df = pd.read_excel(xls, sheet_name=selected_driver, header=1)

            # **Force column headers to strings**
            df.columns = df.columns.astype(str)

            # Print column names for debugging
            st.write("🔍 Columns in Excel File:", df.columns.tolist())

            # **Fix Potential Column Naming Issue**
            for col in df.columns:
                if "HEURES" in col and "NOMBRE" in col:  # Flexible match
                    df.rename(columns={col: "Hours_Worked"}, inplace=True)

            # Salary input
            total_salary = st.number_input("Enter Salary (CFA)", min_value=0, value=5000, step=1000)

            # Check if "Hours_Worked" exists
            if "Hours_Worked" not in df.columns:
                st.error("❌ Could not find 'Hours_Worked' column. Check the Excel file.")
            else:
                # Convert to numeric
                df["Hours_Worked"] = pd.to_numeric(df["Hours_Worked"], errors="coerce")
                
                # Remove "TOTAL" Rows
                df = df[~df["JOUR"].astype(str).str.contains("TOTAL", na=False, case=False)]

                # Categorize Work Hours
                def classify_hours(row):
                    if isinstance(row["JOUR"], str) and (row["JOUR"] in ["SAMEDI", "DIMANCHE"] or pd.notna(row["REMARQUES"])):
                        return "Weekend/Holiday"
                    return "Mid-Week"

                df["Category"] = df.apply(classify_hours, axis=1)

                # Compute Work Hours
                total_hours = df["Hours_Worked"].sum()
                weekend_hours = df[df["Category"] == "Weekend/Holiday"]["Hours_Worked"].sum()
                midweek_hours = df[df["Category"] == "Mid-Week"]["Hours_Worked"].sum()

                # Extract Extra Hours Table (Columns K-P)
                df_extra = df.loc[:, ["HS", "0.15", "0.4", "0.6", "1"]].dropna(how="all")
                df_extra = df_extra.apply(pd.to_numeric, errors="coerce")
                total_extra_hours = df_extra["HS"].sum()

                # Compute Salary Distributions
                overtime_salary = (total_extra_hours / (total_hours + total_extra_hours)) * total_salary
                regular_salary = total_salary - overtime_salary

                # Overtime Tariff Distribution
                tariff_15_salary = overtime_salary * (df_extra["0.15"].sum() / total_extra_hours)
                tariff_40_salary = overtime_salary * (df_extra["0.4"].sum() / total_extra_hours)
                tariff_60_salary = overtime_salary * (df_extra["0.6"].sum() / total_extra_hours)
                tariff_100_salary = overtime_salary * (df_extra["1"].sum() / total_extra_hours)

                # Split Salaries into Minhala and Batmach
                midweek_final_salary = (midweek_hours / total_hours) * regular_salary + tariff_15_salary + tariff_40_salary
                weekend_final_salary = (weekend_hours / total_hours) * regular_salary + tariff_60_salary + tariff_100_salary

                # Display Results
                st.subheader("📊 Work Hours Breakdown")
                st.write(f"**Total Hours Worked:** {total_hours:.2f}")
                st.write(f"**Weekend/Holiday Hours:** {weekend_hours:.2f}")
                st.write(f"**Mid-Week Hours:** {midweek_hours:.2f}")

                st.subheader("💰 Salary Breakdown")
                st.write(f"**Total Salary:** {total_salary:.2f} CFA")
                st.write(f"**Minhala Salary (Weekend/Holiday + Relevant Extra Hours):** {weekend_final_salary:.2f} CFA")
                st.write(f"**Batmach Salary (Mid-Week + Relevant Extra Hours):** {midweek_final_salary:.2f} CFA")

        else:
            st.error(f"❌ Sheet '{selected_driver}' not found in the Excel file. Please check the file.")

    except Exception as e:
        st.error(f"🚨 Error reading the Excel file: {e}")
