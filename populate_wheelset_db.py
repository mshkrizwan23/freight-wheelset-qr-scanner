import sqlite3
import datetime

# Connect to SQLite database
def populate_database():
    conn = sqlite3.connect("wheelset_data.db")
    cursor = conn.cursor()
    
    # Insert sample wheelset data
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
    conn.close()
    print("✅ Sample data inserted successfully!")

# Run the function to populate the database
if __name__ == "__main__":
    populate_database()
