# Streamlit Log Analyzer

A Streamlit application for analyzing Windows Event Viewer CSV exports

## Features

- Upload Event Viewer CSV files
- Select timeframe
- Filter levels
- Search keywords
- Display the event information
- Display AI summary and suggestions
- Pie chart of level distribution
- Bar charts of top sources and event IDs
- Metrics containing event level counts
- Ability to download the filtered events to CSV

## Requirements

- Python 3.12.3+
- streamlit
- matplotlib
- pandas

## Run

```bash
streamlit run AnalyzerApp.py
