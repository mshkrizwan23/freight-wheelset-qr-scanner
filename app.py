import streamlit as st
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import datetime

# Load wheelset data
data_file = "wheelset_data.csv"
df = pd.read_csv(data_file)

def scan_qr_code(image):
    """Scans a QR code from an uploaded image."""
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None

# Streamlit UI
st.set_page_config(page_title="Freight Wagon Wheelset QR Scanner", layout="centered")
st.title("Freight Wagon Wheelset QR Scanner")

uploaded_file = st.file_uploader("Upload a QR Code Image", type=["png", "jpg", "jpeg"])
if uploaded_file:
    qr_result = scan_qr_code(uploaded_file)
    if qr_result:
        wheelset_id = qr_result.split(":")[1]
        st.success(f"Scanned Wheelset ID: {wheelset_id}")
        
        # Retrieve wheelset data
        wheelset_info = df[df["Wheelset_ID"] == wheelset_id]
        if not wheelset_info.empty:
            st.write("### Wheelset Details")
            st.write(wheelset_info)
            
            # Automated Alerts
            if wheelset_info.iloc[0]['Condition'] == "Needs Maintenance":
                st.error("⚠️ This wheelset requires maintenance!")
            
            # Update Maintenance Record
            if st.button("Mark as Maintained"):
                df.loc[df["Wheelset_ID"] == wheelset_id, "Last_Maintenance"] = datetime.date.today()
                df.loc[df["Wheelset_ID"] == wheelset_id, "Condition"] = "Good"
                df.to_csv(data_file, index=False)
                st.success("✅ Maintenance record updated!")
                st.experimental_rerun()
            
            # Export Data
            export_option = st.radio("Export Data As:", ["CSV", "PDF"], index=0)
            if export_option == "CSV":
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv_data, "wheelset_data.csv", "text/csv")
            elif export_option == "PDF":
                import io
                from reportlab.pdfgen import canvas
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer)
                c.drawString(100, 800, "Wheelset Data Report")
                c.drawString(100, 780, f"Wheelset ID: {wheelset_id}")
                c.drawString(100, 760, f"Mileage: {wheelset_info.iloc[0]['Mileage']}")
                c.drawString(100, 740, f"Last Maintenance: {wheelset_info.iloc[0]['Last_Maintenance']}")
                c.drawString(100, 720, f"Condition: {wheelset_info.iloc[0]['Condition']}")
                c.drawString(100, 700, f"Remaining Useful Life: {wheelset_info.iloc[0]['RUL_km']} km")
                c.save()
                pdf_buffer.seek(0)
                st.download_button("Download PDF", pdf_buffer, "wheelset_report.pdf", "application/pdf")
        else:
            st.error("Wheelset not found in the database.")
    else:
        st.error("No QR Code detected. Try another image.")
