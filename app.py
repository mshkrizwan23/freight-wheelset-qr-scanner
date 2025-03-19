import streamlit as st
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode

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
        else:
            st.error("Wheelset not found in the database.")
    else:
        st.error("No QR Code detected. Try another image.")
