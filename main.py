import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Define file path for storing task data
data_file = "task_data.csv"

def load_data():
    """Load task data from a CSV file or initialize if not exists."""
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["Task", "User Completion", "Officer Completion", "Marks"])

def save_data(df):
    """Save the task data to a CSV file."""
    df.to_csv(data_file, index=False)

def calculate_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

def generate_pdf(df):
    """Generate a PDF report of the task data."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Task Completion Report")

    pdf.drawString(100, 750, "Task Completion Report")
    pdf.drawString(100, 730, "-" * 40)

    y_position = 710
    for i, row in df.iterrows():
        pdf.drawString(100, y_position, f"{row['Task']}: {row['Officer Completion']}% completed, Marks: {row['Marks']:.2f}")
        y_position -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

# Load existing data
df = load_data()

# User authentication
st.sidebar.header("Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer"])

# Title
st.title("Task Completion Tracker")
st.write("This app tracks task completion reviewed by the Reporting Officer.")

if role == "Employee":
    st.header("Add New Tasks")
    
    # Add a new task
    new_task = st.text_input("Enter Task Name")
    if st.button("Add Task") and new_task:
        df = df.append({"Task": new_task, "User Completion": 0, "Officer Completion": 0, "Marks": 0}, ignore_index=True)
        save_data(df)
        st.success(f"Task '{new_task}' added successfully!")

    st.header("Enter Completion Percentages")
    for i in range(len(df)):
        df.at[i, "User Completion"] = st.slider(f'{df.at[i, "Task"]} Completion', 0, 100, int(df.at[i, "User Completion"]), 5)
    
    if st.button("Submit Completion"):
        save_data(df)
        st.success("Task completion updated successfully!")

elif role == "Reporting Officer":
    st.header("Reporting Officer Review & Adjustments")
    total_marks_obtained = 0
    for i in range(len(df)):
        st.write(f"{df.at[i, 'Task']}: {df.at[i, 'User Completion']}% completed")
        df.at[i, "Officer Completion"] = st.slider(f"Adjust completion for {df.at[i, 'Task']}:", 0, 100, int(df.at[i, "User Completion"]), 5)
        df.at[i, "Marks"] = calculate_marks(df.at[i, "Officer Completion"])
        total_marks_obtained += df.at[i, "Marks"]
        st.progress(df.at[i, "Officer Completion"] / 100)
        st.write(f"Adjusted Marks: {df.at[i, 'Marks']:.2f}")
    
    st.subheader(f"Total Marks Obtained: {total_marks_obtained:.2f}")

    if st.button("Finalize Review"):
        save_data(df)
        st.success("Reporting Officer's review has been saved!")

# Export Report with Download Buttons
st.sidebar.header("Export Report")

# CSV Download
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name="task_report.csv",
    mime="text/csv",
)

# PDF Download
pdf_buffer = generate_pdf(df)
st.sidebar.download_button(
    label="Download PDF",
    data=pdf_buffer,
    file_name="task_report.pdf",
    mime="application/pdf",
)
