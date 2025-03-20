import streamlit as st
import sqlite3
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import datetime

# Connect to SQLite database
def init_db():
    conn = sqlite3.connect("wheelset_data.db")
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Wheelset_Master (
            Wheelset_ID TEXT PRIMARY KEY,
            Wagon_No TEXT,
            Manufacturing_Date DATE,
            Current_Condition TEXT,
            Last_Maintenance DATE,
            RUL_km INTEGER,
            Total_Mileage INTEGER,
            QR_Code TEXT
        );

        CREATE TABLE IF NOT EXISTS Wheelset_Condition_History (
            Entry_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Wheelset_ID TEXT,
            Date_Recorded DATE,
            Condition TEXT,
            Wear_Level_mm REAL,
            Defects_Logged TEXT,
            FOREIGN KEY (Wheelset_ID) REFERENCES Wheelset_Master(Wheelset_ID)
        );

        CREATE TABLE IF NOT EXISTS Maintenance_History (
            Maintenance_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Wheelset_ID TEXT,
            Date DATE,
            Intervention_Type TEXT,
            Performed_By TEXT,
            Notes TEXT,
            FOREIGN KEY (Wheelset_ID) REFERENCES Wheelset_Master(Wheelset_ID)
        );
    ''')
    conn.commit()
    conn.close()

# Scan QR code
def scan_qr_code(image):
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None

# Fetch wheelset details
def fetch_wheelset_data(wheelset_id):
    conn = sqlite3.connect("wheelset_data.db")
    df = pd.read_sql(f"SELECT * FROM Wheelset_Master WHERE Wheelset_ID = '{wheelset_id}'", conn)
    conn.close()
    return df

# Update maintenance record
def mark_as_maintained(wheelset_id):
    conn = sqlite3.connect("wheelset_data.db")
    cursor = conn.cursor()
    today = datetime.date.today()
    cursor.execute("UPDATE Wheelset_Master SET Last_Maintenance = ?, Current_Condition = 'Good' WHERE Wheelset_ID = ?", (today, wheelset_id))
    conn.commit()
    conn.close()

import sqlite3

def populate_database():
    conn = sqlite3.connect("wheelset_data.db")
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM Wheelset_Master")
    count = cursor.fetchone()[0]
    
    if count == 0:  # Only insert data if the table is empty
        sample_data = [
            ("C8R2T90Y", "WGN001", "2018-05-12", "Needs Maintenance", "2021-11-28", 19496, 100663, "QR_C8R2T90Y.png"),
            ("7ENW5DCS", "WGN002", "2019-07-19", "Good", "2023-06-10", 34560, 125432, "QR_7ENW5DCS.png"),
            ("DVIX13QL", "WGN003", "2020-01-30", "Moderate", "2023-09-15", 28974, 112789, "QR_DVIX13QL.png")
        ]
        
        cursor.executemany("""
            INSERT INTO Wheelset_Master (Wheelset_ID, Wagon_No, Manufacturing_Date, Current_Condition, Last_Maintenance, RUL_km, Total_Mileage, QR_Code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
    
    conn.close()

populate_database()

# Streamlit UI
st.set_page_config(page_title="Freight Wagon Wheelset QR Scanner", layout="centered")
st.title("Freight Wagon Wheelset QR Scanner")

# Initialize database
init_db()

uploaded_file = st.file_uploader("Upload a QR Code Image", type=["png", "jpg", "jpeg"])
if uploaded_file:
    qr_result = scan_qr_code(uploaded_file)
    if qr_result:
        wheelset_id = qr_result.split(":")[1]
        st.success(f"Scanned Wheelset ID: {wheelset_id}")
        
        # Retrieve wheelset data
        wheelset_info = fetch_wheelset_data(wheelset_id)
        if not wheelset_info.empty:
            st.write("### Wheelset Details")
            st.write(wheelset_info)
            
            # Automated Alerts
            if wheelset_info.iloc[0]['Current_Condition'] == "Needs Maintenance":
                st.error("⚠️ This wheelset requires maintenance!")
            
            # Update Maintenance Record
            if st.button("Mark as Maintained"):
                mark_as_maintained(wheelset_id)
                st.success("✅ Maintenance record updated!")
                st.experimental_rerun()
        else:
            st.error("Wheelset not found in the database.")
    else:
        st.error("No QR Code detected. Try another image.")
