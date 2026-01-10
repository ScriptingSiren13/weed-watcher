import sys
import os

# ✅ Add this: Set root path to allow 'app' imports
sys.path.append(os.path.abspath(".."))

from streamlit_lottie import st_lottie
import streamlit as st
from PIL import Image
import json
from app.inference import detect_weeds
from app.utils import load_training_metrics
import plotly.express as px
import pandas as pd





if 'image_count' not in st.session_state:
    st.session_state.image_count = 0
if 'total_weeds' not in st.session_state:
    st.session_state.total_weeds = 0



# Helper function: Load Lottie from file
def load_lottie_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)




# PAGE SETUP
st.set_page_config(page_title="Weed Detection Demo", layout="centered")




st.markdown("""
    <!-- Load Font Awesome for social icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
""", unsafe_allow_html=True)




# SIDEBAR
st.sidebar.markdown("---")
theme = st.sidebar.radio("Choose a theme:", ["Light", "Dark"])
st.sidebar.markdown("---")
st.sidebar.markdown("""
<style>
.social-icons {
  display: flex;
  gap: 10px;
  font-size: 1.8rem;
  margin-top: 10px;
}

.social-icons a {
  color: #1b5e20;
  text-decoration: none;
  transition: transform 0.3s ease, color 0.3s ease;
  position: relative;
}

.social-icons a:hover {
  color: #ff9800;
  transform: scale(1.2);
}

/* Tooltip Styling */
.social-icons a .tooltip {
  visibility: hidden;
  background-color: #1b5e20;
  color: #fff;
  text-align: center;
  border-radius: 5px;
  padding: 4px 8px;
  position: absolute;
  z-index: 1;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s ease;
  font-size: 0.7rem;
  white-space: nowrap;
}

.social-icons a:hover .tooltip {
  visibility: visible;
  opacity: 1;
}
</style>

<div style="margin-top: 2rem;">
    <p> Made by Zarnain</p>
    <div class="social-icons">
        <a href="https://github.com/ScriptingSiren13" target="_blank">
            <i class="fab fa-github"></i>
            <span class="tooltip">GitHub</span>
        </a>
        <a href="https://www.linkedin.com/in/zarnain-723a31325/" target="_blank">
            <i class="fab fa-linkedin"></i>
            <span class="tooltip">LinkedIn</span>
        </a>
        <a href="mailto:zedd.web13@gmail.com">
            <i class="fas fa-envelope"></i>
            <span class="tooltip">Email</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)





# THEME COLORS
if theme == "Light":
    bg_color = "#ffffff"
    text_color = "#000000"
else:
    bg_color = "#0f0f0f"
    text_color = "#ffffff"




# GLOBAL CUSTOM CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        max-width: 1600px;  
        padding: 2rem;
        margin: 0 auto;
    }}
    .hover-box {{
        background-color: #e6f4ea;
        padding: 20px;
        border-radius: 10px;
        color: #2e7d32;
        font-size: 16px;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        height: 100%;
    }}
    .hover-box:hover {{
        background-color: #c8e6c9;
        box-shadow: 4px 4px 12px rgba(0,0,0,0.2);
        cursor: pointer;
    }}
    .equal-box {{
        height: 100%;
        display: flex;
        align-items: stretch;
        justify-content: center;
        flex-direction: column;
        background-color: #e6f4ea;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True
)




# HEADER WITH LOGO AND TITLE
col1, col2 = st.columns([1, 8])
with col1:
    st.image(r"D:\weed-detection-app\streamlit_app\logo.png", width=100)
with col2:
    st.markdown(
        """
        <h1 style='padding-top: 10px;font-size: 35px;'>
            Weed Watcher - A Weed Detection App
        </h1>
        """, 
        unsafe_allow_html=True
    )




# TABS
tab1, tab2, tab3 = st.tabs(["ℹ️ About", "📁 Upload", "📊 Stats"])

# TAB 1: ABOUT
with tab1:
    st.subheader("About")
    col_about, col_lottie = st.columns(2)

    with col_about:
        st.markdown(
            """
            <div class="equal-box">
                <div class="hover-box">
                    🌿 This app uses YOLOv8 to detect weeds in agricultural field images.
                    <br>Hover to see this box animate!
                    This project applies the YOLOv8 object detection model to identify and localize weeds in garden images using bounding boxes. 
                    A custom dataset was created by capturing and annotating real weed images from my garden.
                    The trained model enables fast and accurate weed detection, supporting applications in precision gardening and automated weed management.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_lottie:
        st.markdown('<div class="equal-box">', unsafe_allow_html=True)
        lottie_plant = load_lottie_file(r"D:\weed-detection-app\streamlit_app\farmer.json")
        st_lottie(lottie_plant, speed=1, height=370, key="plant")  # You can adjust height if needed
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander(" How Weed Detection Works"):
        st.markdown("""
        1. Upload an image from the field  
        2. YOLOv8 model processes the image  
        3. Bounding boxes are drawn around detected weeds  
        4. Stats (detections/images) are updated  
        5. Optionally save or review results
        """)





# TAB 2: UPLOAD
with tab2:
    st.write("Upload an Image to simulate detection")

    # Confidence Threshold Slider
    conf_threshold = st.slider(
        "Select Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Only detections with confidence above this value will be shown."
    )

    uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image")

        with st.spinner("Detecting weeds..."):
            # ✅ Pass the selected threshold into detect_weeds
            result_image, result_data = detect_weeds(image, conf_threshold)

        # Count weeds from results
        num_detections = len(result_data.boxes)

        # Update session state
        st.session_state.image_count += 1
        st.session_state.total_weeds += num_detections

        st.image(result_image, caption="Detected Weeds")
        st.success(f"✅ {num_detections} weed(s) detected!")
        st.balloons()





# TAB 3: STATS
with tab3:
    st.subheader("📊 Model Training Summary")

    metrics = load_training_metrics(r"D:\weed-detection-app\streamlit_app\data\results.csv")

    if "error" in metrics:
        st.error(f"Error loading training metrics: {metrics['error']}")
        st.write("❗ Debug info:", metrics)
    else:
        # ✅ Safely extract DataFrame
        df = metrics.get("df")

        # ✅ Show metrics as cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Precision", f"{metrics['precision'] * 100:.1f}%")
        col2.metric("Recall", f"{metrics['recall'] * 100:.1f}%")
        col3.metric("mAP@0.5", f"{metrics['map50'] * 100:.1f}%")

        col4, col5, col6 = st.columns(3)
        col4.metric("mAP@0.5:0.95", f"{metrics['map5095'] * 100:.1f}%")
        col5.metric("Train Loss", round(metrics["train_loss"], 4))
        col6.metric("Val Loss", round(metrics["val_loss"], 4))

        st.info(f"Model trained for {metrics['epoch'] + 1} epochs.")

        # ✅ Check if DataFrame is valid before plotting
        if df is not None and not df.empty:
            st.markdown("### 📉 Training Loss Over Epochs")
            fig_loss = px.line(df, x="epoch", y=["train/box_loss", "val/box_loss"],
                               labels={"value": "Loss", "epoch": "Epoch"},
                               title="Box Loss During Training")
            st.plotly_chart(fig_loss, use_container_width=True)

            # ✅ Precision and Recall Graph
            st.markdown("### 🎯 Precision and Recall")
            fig_pr = px.line(df, x="epoch", y=["metrics/precision(B)", "metrics/recall(B)"],
                    labels={"value": "Score", "epoch": "Epoch"},
                    title="Precision & Recall Over Epochs")
            st.plotly_chart(fig_pr, use_container_width=True)

            # ✅ mAP Graphs
            st.markdown("### 🎯 mAP@0.5 and mAP@0.5:0.95")
            fig_map = px.line(df, x="epoch", y=["metrics/mAP50(B)", "metrics/mAP50-95(B)"],
                    labels={"value": "mAP", "epoch": "Epoch"},
                    title="mAP Scores Over Epochs")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("📉 No data found in results.csv to plot training graphs.")
