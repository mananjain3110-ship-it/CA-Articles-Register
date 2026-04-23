import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import holidays

st.title("🧾 CA Articles Attendance & Work Diary System")

FILE = "attendance.csv"

# -------------------------------
# Create / Load Data
# -------------------------------
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Name","Date","Punch In","Punch Out","Work"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# -------------------------------
# Holiday Logic (Real Calendar)
# -------------------------------
india_holidays = holidays.country_holidays("IN")

def get_holidays(year):
    holiday_list = []

    for day, name in india_holidays.items():
        if day.year == year:
            holiday_list.append(day)

    # Holi (2 days)
    for day, name in india_holidays.items():
        if "Holi" in name:
            holiday_list.append(day)
            holiday_list.append(day + timedelta(days=1))

    # Diwali (3 days)
    for day, name in india_holidays.items():
        if "Diwali" in name or "Deepavali" in name:
            holiday_list.append(day - timedelta(days=1))
            holiday_list.append(day)
            holiday_list.append(day + timedelta(days=1))

    return list(set(holiday_list))

today = date.today()
holiday_list = get_holidays(today.year)

def is_holiday(d):
    return d.weekday() == 6 or d in holiday_list

# -------------------------------
# Employee Input
# -------------------------------
st.subheader("👤 Employee Details")
name = st.text_input("Enter Employee Name")

# -------------------------------
# Punch In
# -------------------------------
if st.button("🟢 Punch In"):
    new_row = {
        "Name": name,
        "Date": str(today),
        "Punch In": datetime.now().strftime("%H:%M:%S"),
        "Punch Out": "",
        "Work": ""
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("Punch In Recorded")

# -------------------------------
# Punch Out
# -------------------------------
if st.button("🔴 Punch Out"):
    for i in range(len(df)-1, -1, -1):
        if df.loc[i,"Name"] == name and df.loc[i,"Punch Out"] == "":
            df.loc[i,"Punch Out"] = datetime.now().strftime("%H:%M:%S")
            break
    df.to_csv(FILE, index=False)
    st.success("Punch Out Recorded")

# -------------------------------
# Work Diary
# -------------------------------
st.subheader("📘 Work Diary")

work = st.text_area("Enter Work Done Today")

if st.button("💾 Save Work"):
    for i in range(len(df)-1, -1, -1):
        if df.loc[i,"Name"] == name and df.loc[i,"Work"] == "":
            df.loc[i,"Work"] = work
            break
    df.to_csv(FILE, index=False)
    st.success("Work Saved")

# -------------------------------
# Attendance Register
# -------------------------------
st.subheader("📊 Attendance Register")
st.dataframe(df)

# -------------------------------
# Leave & Comp Off Calculation
# -------------------------------
st.subheader("📅 Leave Summary")

df["Date"] = pd.to_datetime(df["Date"])

present = 0
leave = 0
comp_off = 0

for i in range(len(df)):
    d = df.loc[i,"Date"].date()

    if is_holiday(d):
        if df.loc[i,"Punch In"] != "":
            comp_off += 1
    else:
        if df.loc[i,"Punch In"] != "":
            present += 1
        else:
            leave += 1

st.write(f"✅ Present Days: {present}")
st.write(f"❌ Leaves: {leave}")
st.write(f"🎁 Compensatory Leaves Earned: {comp_off}")

# -------------------------------
# Holiday Display
# -------------------------------
st.subheader("🎉 Holiday Calendar")

holiday_df = pd.DataFrame({
    "Holiday Date": sorted(holiday_list)
})

st.dataframe(holiday_df)