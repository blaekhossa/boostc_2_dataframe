# boostc_2_dataframe
Convert your Boostcamp workout history JSON into clean CSV or Excel (XLSX) tables for analysis, logging, or importing into other tools.

# 🏋️‍♂️ Boostcamp Workout Exporter

Convert your Boostcamp workout history JSON into clean **CSV** or **Excel (XLSX)** tables for analysis, logging, or importing into other tools.

---

## 📖 Description

Boostcamp stores your workout history in structured JSON. This project provides a script (`flatten_workouts.py`) that:

- Flattens nested session → exercise → set data into **one row per set**.  
- Propagates session-level and exercise-level fields down to each row.  
- Preserves set-specific details (reps, weight, skipped, etc.).  
- Infers and documents the schema of the JSON for transparency.  
- Outputs to both **CSV** and **XLSX**.

---

## 📥 How to Get the Data

As the overview page loads all the historical data, and filters the data that is shown on the front-end, we can use the response that is sent to be parsed and put into an csv or xlsx.

1. Open [Boostcamp](https://boostcamp.app/history) in **Chrome**.  
2. Go to the **History** tab where your workouts are listed.  
3. Press **F12** (or right-click → Inspect) to open **Developer Tools**.  
4. Switch to the **Network** tab.  
5. Filter for **XHR** requests. Look for a request like `history?...`  or just look for the `{:}history?_=SOME_ID` where id will be a bunch of numbers.
6. Click it, then go to the **Preview** or **Response** tab. In my case the **Preview** tab. 
7. You’ll see your workout data in JSON format.  
8. **Copy all of it** by just right clicking on the **data**, **copy value** paste into a plain text file, e.g. `example_data_payload.txt`.  

---

## ▶️ How to Run
Make sure you have python and pandas installed.
1. Clone, copy the code, or download this repo.  
2. Save your Boostcamp JSON into `example_data_payload.txt` in the project root.
3. Check the paths, and the PREFERRED_COLUMNS, that will select the columns from the flattened pandas dataframe. 
4. Run the script, via the following CLI command in the correct folder or via your IDE:

```bash
python flatten_workouts.py
