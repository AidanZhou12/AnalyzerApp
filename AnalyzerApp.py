import streamlit as st
from matplotlib import pyplot as plt
import csv
from io import StringIO
from datetime import datetime, timedelta
import pandas as pd
from openai import OpenAI
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide")
st.title("Tell Me Why")

st.markdown("""
An app that takes an Event Viewer CSV file and analyzes it!
* **Python libraries:** streamlit, matplotlib, csv, pandas, openai
* **Data source:** Your machine's Event Viewer logs exported as CSV
""")

col_table, col_chart = st.columns([1.5, 1])

st.sidebar.header("Data")
f = st.sidebar.file_uploader(label="Upload your log file", type="csv")

st.sidebar.subheader("Filters")
search = st.sidebar.text_input("Search for a specific event", "")

filters = ["Last hour", "Last 12 hours", "Last 24 hours", "Last 7 days", "Last 30 days", "All Time"]
selected_filter = st.sidebar.selectbox("Select A Time Range", filters, index=5)

levels = ["Error", "Warning", "Information"]
selected_levels = st.sidebar.multiselect("Select Log Levels", levels, default=levels)

now = datetime.now()

total = 0
counter = {level: 0 for level in selected_levels}
events = []
types = dict()
if f is not None:
    try:
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
                if (row[0] in selected_levels) and (search.lower() in row[2].lower() or search.lower() in row[4].lower() or search.lower() in row[5].lower()):
                    total += 1
                    counter[row[0]] += 1
                    events.append({
                        "Level": row[0],
                        "Date and Time": row[1],
                        "Source": row[2],
                        "Event ID": row[3],
                        "Task Category": row[4],
                        "Description": row[5]
                    })
                    thrup = (row[0], row[2], row[3])
                    if thrup in types:
                        types[thrup]["count"] += 1
                    else:
                        types[thrup] = {"count": 1, "description": row[5]}
                else:
                    continue
        df = pd.DataFrame(events)
        with col_table:
            metric_columns = st.columns(len(selected_levels))
            for metric_column, level in zip(metric_columns, selected_levels):
                with metric_column:
                    st.metric(label=f"{level} Events", value=counter[level])
            st.dataframe(df, hide_index=True)
            if st.button("Generate AI Summary"):
                with st.spinner("Generating summary..."):
                    time.sleep(12)
                promp = {"Error": "", "Warning": "", "Information": ""}
                for (level, source, id) in types:
                    promp[level] += f"{source}\nEvent ID: {id}\nOccurences: {types[(level, source, id)]['count']}\nDescription: {types[(level, source, id)]['description']}\n\n"
                response = client.responses.create(
                    model="gpt-5-mini",
                    input=f"""Summarize the following log stats taken from an Event Viewer CSV export:
                    Errors:
                    {promp["Error"]}
                    Warnings:
                    {promp["Warning"]}
                    Information:
                    {promp["Information"]}
                    """,
                    instructions="If there are errors, summarize what went wrong and how to fix them. If there are warnings, give suggestions to avoid them. If there are information events, summarize what happened"
                )
                st.text_area("AI Summary", value=response.output_text, height=300, disabled=True)
        with col_chart:
            if total == 0:
                st.warning("No events found for the selected time range.")
            else:
                pie_data = [(label, counter[label]) for label in selected_levels if counter[label] > 0]
                values = [value for _, value in pie_data]
                total = sum(values)
                pie_labels = [f"{label} ({(value / total * 100):.1f}%)" for label, value in pie_data]
                fig, ax = plt.subplots()
                ax.pie(values, labels=pie_labels, labeldistance=1.15, startangle=90)
                ax.axis("equal")
                st.pyplot(fig)

                source_totals = {}
                for level, source, event_id in types:
                    source_totals[source] = source_totals.get(source, 0) + types[(level, source, event_id)]["count"]

                top_sources = sorted(source_totals.items(), key=lambda item: item[1], reverse=True)[:5]
                source_labels = [label for label, _ in top_sources]
                source_values = [value for _, value in top_sources]
                source_fig, source_ax = plt.subplots()
                source_ax.barh(source_labels, source_values)
                source_ax.invert_yaxis()
                source_ax.set_xlabel("Count")
                source_ax.set_title("Top Sources")
                st.pyplot(source_fig)

                id_totals = {}
                for level, source, event_id in types:
                    id_totals[event_id] = id_totals.get(event_id, 0) + types[(level, source, event_id)]["count"]

                top_ids = sorted(id_totals.items(), key=lambda item: item[1], reverse=True)[:5]
                id_labels = [label for label, _ in top_ids]
                id_values = [value for _, value in top_ids]
                id_fig, id_ax = plt.subplots()
                id_ax.bar(id_labels, id_values)
                id_ax.set_ylabel("Count")
                id_ax.set_title("Top Event IDs")
                st.pyplot(id_fig)
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV file to analyze.")