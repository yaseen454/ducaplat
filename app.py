import easyocr
import streamlit as st
from calc import run_prime_calculator
from ocr import expand_list, count_types, count, return_df
from PIL import Image
from streamlit_paste_button import paste_image_button as pbutton
import numpy as np
import io

# Initialize session state variables globally if they don't exist
if 'calc_type' not in st.session_state:
    st.session_state.calc_type = 1  # Initialize to 'narrow' by default
if 'display_anova' not in st.session_state:
    st.session_state.display_anova = False
if 'enable_plot' not in st.session_state:
    st.session_state.enable_plot = False
# Initialize session state for images and text
if 'texts' not in st.session_state:
    st.session_state['texts'] = []
if 'done_pasting' not in st.session_state:
    st.session_state['done_pasting'] = False

# Function to process images with EasyOCR
def process_image(image):
    # Convert PIL image to OpenCV format (numpy array)
    image_np = np.array(image)
    results = reader.readtext(image_np)
    return " ".join([result[1] for result in results])


def clipboard_code():
# Display or hide the paste button based on the 'done_pasting' state
    paste_result = pbutton("📋 Paste an image",errors='No image found in clipboard')

    if paste_result.image_data is not None:
        st.session_state.texts = process_image(paste_result.image)
        st.image(paste_result.image_data)
    
    # Button to indicate done pasting
    if st.button('Done Pasting'):
        st.session_state['done_pasting'] = True

    # Display images and extracted text only after done pasting
    if st.session_state.done_pasting:
        if st.session_state['texts']:
            for idx, text in enumerate(st.session_state['texts']):
            st.write(f"Extracted Text {idx + 1}: {text}")

        # Buttons for managing images/texts and resetting the state
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button('Remove Last Image', disabled=not st.session_state['images']):
                if st.session_state['images']:
                    st.session_state['images'].pop()
                    st.session_state['texts'].pop()
        with col2:
            if st.button('Remove All Images', disabled=not st.session_state['images']):
                st.session_state['images'] = []
                st.session_state['texts'] = []
        with col3:
            if st.button('Start Over'):
                st.session_state['done_pasting'] = False
                st.session_state['images'] = []
                st.session_state['texts'] = []

        # Display the current state of extracted texts
        if st.session_state['texts']:
            st.write("Current Extracted Texts:")
            for idx, text in enumerate(st.session_state['texts']):
                st.write(f"Text {idx + 1}: {text}")



# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');
        .large-title {
            font-family: 'Roboto', sans-serif;
            text-align: center;
            color: #DAA520;  /* Dark gold color */
            font-size: 4em;  /* Adjust font size as needed */
            margin: 0;
            padding: 0;
        }
    </style>
    """, unsafe_allow_html=True)

# Ribbon for page navigation
tabs = st.tabs(["Home", "Calculator", "Help", "About"])

st.sidebar.header("Input Method")
input_method = st.sidebar.radio(
    "Choose how you want to input prime parts:",
    ("Manual Input", "Image from clipboard")
)

with tabs[0]:
    # Large title (website name) before the main title with dark gold color and custom font
    st.markdown("<h1 class='large-title'>DucaPlat</h1>", unsafe_allow_html=True)
    st.title("Warframe Prime Item Trading Calculator")
    st.write("_Welcome to **DucaPlat**! the Warframe Prime Item Trading Calculator. "
             "This tool allows you to calculate the profit from trading prime parts in Warframe._")
    st.write("_You can choose to input your prime parts either manually or "
             "by uploading images for OCR processing. Once you have processed "
             "the images or entered the data, you can calculate the profit and see detailed results._")
    st.write('### Prime Items')
    url = "https://drops.warframestat.us/"
    link_text = "drops.warframestat.us"
    st.write(f'_Processed and sourced from_ ', f"_[{link_text}]({url})_")
    st.dataframe(return_df())

with tabs[1]:
    st.title("Prime Item Trading Calculator")
    calc_type = st.sidebar.selectbox("Select Calculation Type", ["broad", "narrow"])
    calc_type = 2 if calc_type == 'broad' else 1
    st.session_state.display_anova = st.sidebar.checkbox("Display ANOVA results",
                                                         value=st.session_state.display_anova)
    st.session_state.enable_plot = st.sidebar.checkbox("Enable Plotting", value=st.session_state.enable_plot)

    if input_method == "Manual Input":
        st.header("Input Prime Parts")
        bronze15 = st.number_input("Bronze15", min_value=0, value=0)
        bronze25 = st.number_input("Bronze25", min_value=0, value=0)
        silver45 = st.number_input("Silver45", min_value=0, value=0)
        silver65 = st.number_input("Silver65", min_value=0, value=0)
        gold = st.number_input("Gold", min_value=0, value=0)
        if st.button("Calculate Profit"):
            calculator_results = run_prime_calculator(
                bronze15=bronze15, bronze25=bronze25, silver45=silver45, silver65=silver65, gold=gold, bypass=True,
                plot=st.session_state.enable_plot, calc_type=calc_type, display_anova=st.session_state.display_anova
            )
            st.write(calculator_results)
    elif input_method == 'Image from clipboard':
        clipboard_code()
with tabs[2]:
    st.title('Tool Usage & Info')
    st.write("### Image Fetch Steps:")
    st.write('_You can use images instead of manually inputting and counting '
             'your prime parts yourself to save up some time_')
    st.write("- **Step [ 1 ] :** Launch warframe and hit up your inventory ")
    st.write(
        "- **Step [ 2 ] :** Go to the prime parts section and select whatever you want to analyize "
        "as if you want to sell those items for credits")
    st.write(
        "- **Step [ 3 ] :** When your done selecting, take screenshots of the selling lists")
    st.write("- **Step [ 4 ] :** Now you're done! upload or copy the images to your clipboard and watch your prime junk transform into plat.")

    image = Image.open('data/Prime_Parts.png')
    st.image(image, caption='This is a sample image', use_column_width=True)
    st.write('### How the calculator works:')
    st.write("...")  # The previous explanation content goes here.

with tabs[3]:
    st.write('**_Nothing here yet_**')
