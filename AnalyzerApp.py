import streamlit as st
from matplotlib import pyplot as plt
import csv
from io import StringIO
from datetime import datetime, timedelta
import pandas as pd

st.title("Log Analyzer App")

st.markdown("""
This app takes an Event Viewer CSV file and analyzes it!
* **Python libraries:** streamlit, matplotlib, csv
* **Data source:** Your machine's Event Viewer logs exported as CSV
""")

st.sidebar.header("Filters")

filters = ["Last hour", "Last 12 hours", "Last 24 hours", "Last 7 days", "Last 30 days", "All Time"]
selected_filter = st.sidebar.selectbox("Select A Time Range", filters, index=5)

levels = ["Error", "Warning", "Information"]
selected_levels = st.sidebar.multiselect("Select Log Levels", levels, default=levels)

now = datetime.now()

f = st.file_uploader(label="Upload your log file", type="csv")
total = 0
counter = {level: 0 for level in selected_levels}
events = []

if f is not None:
    text = StringIO(f.getvalue().decode("utf-8"))
    data = csv.reader(text)
    next(data)
    for row in data:
        timestamp = datetime.strptime(row[1], "%m/%d/%Y %I:%M:%S %p")
        if selected_filter == "Last hour" and timestamp < now - timedelta(hours=1):
            continue
        elif selected_filter == "Last 12 hours" and timestamp < now - timedelta(hours=12):
            continue
        elif selected_filter == "Last 24 hours" and timestamp < now - timedelta(hours=24):
            continue
        elif selected_filter == "Last 7 days" and timestamp < now - timedelta(days=7):
            continue
        elif selected_filter == "Last 30 days" and timestamp < now - timedelta(days=30):
            continue
        else:
            if row[0] in selected_levels:
                total += 1
                counter[row[0]] += 1
                events.append({
                    "Level": row[0],
                    "Date and Time": row[1],
                    "Source": row[2],
                    "Event ID": row[3],
                    "Task Category": row[4]
                })
            else:
                continue
    for level in selected_levels:
        st.write(f"{level} Events: {counter[level]}")
    if total == 0:
        st.warning("No events found for the selected time range.")
    else:
        values = [counter[label] for label in selected_levels]
        total = sum(values)
        pie_labels = [f"{label} ({(value / total * 100):.1f}%)" if total else f"{label} (0.0%)" for label, value in zip(selected_levels, values)]
        fig, ax = plt.subplots()
        ax.pie(values, labels=pie_labels, labeldistance=1.15, startangle=90)
        ax.axis("equal")
        st.pyplot(fig)