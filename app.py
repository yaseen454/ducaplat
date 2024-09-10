import easyocr
import streamlit as st
from calc import run_prime_calculator
from ocr import expand_list, count_types, count, return_df, dict_count
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
if 'expanded_items' not in st.session_state:
    st.session_state.expanded_items = []
# Store the pasted images and extracted text
if 'images' not in st.session_state:
    st.session_state.images = []
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = []
if 'processed' not in st.session_state:
    st.session_state.processed = False 


st.sidebar.title("Settings")
st.sidebar.header("Input Method")
input_method = st.sidebar.radio(
    "Choose how you want to input prime parts:",
    ("Manual Input", "Image from clipboard")
)
# Sidebar settings for calculation type and options

calc_type = st.sidebar.selectbox("Select Calculation Type", ["narrow", "broad"])
st.session_state.calc_type = 2 if calc_type == 'broad' else 1
st.session_state.display_anova = st.sidebar.checkbox("Display ANOVA results", value=st.session_state.display_anova)
st.session_state.enable_plot = st.sidebar.checkbox("Enable Plotting", value=st.session_state.enable_plot)

# Cache the OCR model loading
@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(['en'])

reader = load_ocr_model()

# Cache the dataframe creation (if this is time-consuming)
@st.cache_data
def get_data():
    return return_df()


def image_exists(new_img_data):
    for img in st.session_state.images:
        if np.array_equal(new_img_data, img):
            return True
    return False
# Function to handle pasting images
# Function to handle pasting images
def handle_paste_images():
    paste_result = pbutton("📋 Paste an image")  # Use pbutton to paste the image

    # Check if there's valid pasted image data
    if paste_result.image_data is not None:
        # Convert to numpy array
        img_np = np.array(paste_result.image_data)

        # Check if the image has already been added
        if not image_exists(img_np):
            st.session_state.images.append(img_np)
            st.write('Pasted image:')
            st.image(paste_result.image_data)

            # Reset the processed flag since a new image has been added
            st.session_state.processed = False
        # else:
        #     st.warning("This image has already been added.")


# Function to process images with EasyOCR and extract text
def process_images():
    combined_text = []
    print(st.session_state.images)
    for img in st.session_state.images:
        st.write("Processing image with EasyOCR...")
        extracted_text = reader.readtext(img,detail=0)  # Extract text
        combined_text.extend(extracted_text)

    st.session_state.extracted_text = combined_text
    st.write("Extracted Text:")
    st.write(combined_text)


# Function to remove last n items from extracted text
def remove_last_n_items(n):
    if len(st.session_state.extracted_text) >= n:
        st.session_state.extracted_text = st.session_state.extracted_text[:-n]
    else:
        st.session_state.extracted_text = []
    st.write(f"Text after removing last {n} items:")
    st.write(st.session_state.extracted_text)

# Function to reset all images and start over
def reset_images():
    st.session_state.images = []
    st.session_state.extracted_text = []
    st.session_state.processed = False
    st.success("All images have been reset. You can start over.")


def clipboard_code():
    # App title
    st.write("**Important Notes:** _make sure the image you copy is not bad in quality, where text is clear and visible so the ocr can run properly_")
    st.write("**Pasting does not support mobile browsers & firefox**")

    # Paste images section
    handle_paste_images()

    # Button to process images once done pasting
    if st.button("Done Pasting"):
        if st.session_state.images:
            # Only process images if they haven't been processed yet (flag is False)
            if not st.session_state.processed:
                process_images()
                st.session_state.processed = True  # Set the flag to prevent reprocessing
            else:
                st.write("Images have already been processed.")
        else:
            st.error("No images found. Please paste at least one image.")

    # Display text and provide option to remove last n items or continue
    if st.session_state.extracted_text:
        st.write("Modify Extracted Text:")

        # Add option to choose between actions
        action = st.radio("Choose an action:", ("Remove Last N Items", "Calculate Profit", "Reset All"))

        if action == "Remove Last N Items":
            # If the user chooses to remove last n items, show number input and remove button
            n_to_remove = st.number_input("Enter number of items to remove from the end", min_value=1, value=1,
                                          step=1)

            if st.button("Remove Last N Items"):
                remove_last_n_items(int(n_to_remove))

        elif action == "Calculate Profit":
            if st.session_state.extracted_text:
                st.write(st.session_state.extracted_text)
                expanded_text = expand_list(st.session_state.extracted_text)
                st.session_state.expanded_items = expanded_text
                d = dict_count(st.session_state.expanded_items)
                st.write(f'Expanded items {expanded_text}')
                result = run_prime_calculator(d[0],
                                              d[1],
                                              d[2],
                                              d[3],
                                              d[4], bypass=True, calc_type=st.session_state.calc_type,
                                              plot=st.session_state.enable_plot,
                                              display_anova=st.session_state.display_anova)
        elif action == 'Reset All':
            st.write('Press confirm to reset')
            if st.button("Confirm"):
                reset_images()


    
# def clipboard_code():
#     paste_result = pbutton("📋 Paste an image", errors='No image found in clipboard')

#     # Only process if image data is found
#     if paste_result.image_data is not None:
#         # Ensure we don't accidentally append the same image multiple times
#         if paste_result.image_data not in st.session_state.images:
#             # Append image and its OCR text to session state lists
#             st.session_state.images.append(paste_result.image_data)
#             st.session_state.texts.append(process_image(paste_result.image_data))
#             st.image(paste_result.image_data)
#         else:
#             st.warning("This image has already been pasted.")
#     else:
#         st.error('No image found in clipboard')

#     if st.button('Done Pasting'):
#         st.session_state.done_pasting = True
    
#     if st.session_state.done_pasting and st.session_state.images:
#         # Display all images and corresponding texts
#         for idx, (image, text) in enumerate(zip(st.session_state.images, st.session_state.texts)):
#             st.image(image, caption=f"Image {idx+1}")
#             st.write(f"Extracted Text {idx+1}: {text}")
        
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if st.button('Remove Last Image', disabled=not st.session_state.images):
#                 if st.session_state.images:
#                     st.session_state.images.pop()
#                     st.session_state.texts.pop()
#                 st.session_state.done_pasting = False  # Allow further pasting if necessary
#                 st.rerun()  # Refresh the page after removing

#         with col2:
#             if st.button('Remove All Images', disabled=not st.session_state.images):
#                 st.session_state.images = []
#                 st.session_state.texts = []
#                 st.session_state.done_pasting = False
#                 st.rerun()  # Refresh the page after removing

#         with col3:
#             if st.button('Start Over'):
#                 st.session_state.images = []
#                 st.session_state.texts = []
#                 st.session_state.done_pasting = False
#                 st.rerun() 


# # Initialize EasyOCR reader
# reader = easyocr.Reader(['en'])

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

with tabs[0]:
    # Large title (website name) before the main title with dark gold color and custom font
    st.markdown("<h1 class='large-title'>DucaPlat</h1>", unsafe_allow_html=True)
    st.title("Warframe Prime Item Trading Calculator")
    st.success("🎉 **Image Clipboard is now available!** 🎉 _check Help for more info._")
    st.write("_Welcome to **DucaPlat**! the Warframe Prime Item Trading Calculator. "
             "This tool allows you to calculate the profit from trading prime parts in Warframe._")
    st.write("_You can choose to input your prime parts either manually or "
             "by uploading images for OCR processing. Once you have processed "
             "the images or entered the data, you can calculate the profit and see detailed results._")
    st.write('### Prime Items')
    url = "https://drops.warframestat.us/"
    link_text = "drops.warframestat.us"
    st.write(f'_Processed and sourced from_ ', f"_[{link_text}]({url})_")
    df = get_data()
    st.dataframe(df)

with tabs[1]:
    st.title("Prime Item Trading Calculator")
    if input_method == "Manual Input":
        # Input fields for prime part quantities
        bronze15 = st.number_input("Bronze15", min_value=0, value=0, step=1)
        bronze25 = st.number_input("Bronze25", min_value=0, value=0, step=1)
        silver45 = st.number_input("Silver45", min_value=0, value=0, step=1)
        silver65 = st.number_input("Silver65", min_value=0, value=0, step=1)
        gold = st.number_input("Gold", min_value=0, value=0, step=1)
        
        # Button to explicitly trigger calculation
        if st.button("Calculate Profit"):
            with st.spinner('Calculating...'):
                # Call the calculation function when user presses the button
                calculator_results = run_prime_calculator(
                    bronze15=bronze15, 
                    bronze25=bronze25, 
                    silver45=silver45, 
                    silver65=silver65, 
                    gold=gold,
                    bypass=True,
                    plot=st.session_state.enable_plot,
                    calc_type=st.session_state.calc_type,
                    display_anova=st.session_state.display_anova
                )
            # Show results
            st.write(calculator_results)
    elif input_method == 'Image from clipboard':
        clipboard_code()
        # st.markdown("<h2 style='color: red;'>🚧 WORK IN PROGRESS 🚧</h2>", unsafe_allow_html=True)
with tabs[2]:
    st.title('Tool Usage & Info')
    # st.markdown("<h2 style='color: red;'>🚧 Image from clipboard: WORK IN PROGRESS 🚧</h2>", unsafe_allow_html=True)
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
    st.write("""
    The core principle of this computation is based on the concept of combinations. In Warframe's free market, players have the flexibility to set their own prices for items. However, in the case of prime junk trading, a common pricing structure tends to follow the (1,1,3,4,8) distribution for different rarity tiers (bronze15, bronze25, silver45, silver65, gold).

Recognizing this, I sought to explore all possible price combinations to gain a comprehensive understanding of potential earnings from selling these items. To achieve this, I developed a Python-based solution that simulates different pricing scenarios, calculates expected returns, and provides insights using statistical measures. The tool incorporates aggregations, statistical analysis, and various decision-support metrics to offer a clear view of average potential profits from trading in prime junk.
    """)
    st.write('### What is ANOVA?')
    st.write("""
    The core process of this computation is based on analyzing the variance within and between groups. ANOVA (Analysis of Variance) helps determine if there are statistically significant differences between the means of multiple groups. In essence, we are comparing how much the data points within a group vary compared to how much the group means themselves differ from each other.

ANOVA works by calculating two types of variance:

Within-group variance: This measures the variability within each group.
Between-group variance: This measures the variability between the means of the groups.
The ratio of these variances gives us the F-statistic, which helps determine whether the differences between the group means are significant. If the between-group variance is large compared to the within-group variance, this suggests that the group means are not all the same.

I implemented this process using Python, breaking it down into key steps: calculating the mean for each group, the overall mean, and the sum of squares for both within and between groups. Finally, I used these values to compute the F-statistic and provide p-values to help interpret the results. This tool includes statistical summaries and measures to guide you in making data-driven decisions about group differences.
    """)

    st.write('### Explanation of Grouping in ANOVA')
    st.write("""
    In this ANOVA analysis, the data is grouped based on different combinations of rare prime part prices, with the primary aim of determining which combination yields the most profit. The price of the rare prime parts—referred to as 'gold' items—is particularly important because these parts tend to have the highest prices, such as 8, 9, or 10 platinum.

To better understand how different price groupings impact profit, we organize the data into various inclusion and exclusion sets based on the price of rare parts:

**All Costs:** This set includes all possible values of rare prime parts, considering every price combination from bronze to gold tiers. It serves as a baseline for comparison.

**Costs Without 9s:** This set excludes rare prime parts that are priced at 9 platinum, allowing us to evaluate profitability when parts valued at 9 are not involved in the sale.

**Costs Without 10s:** Similar to the previous group, this set excludes rare prime parts that are priced at 10 platinum. By doing so, we can assess how the absence of the most expensive parts influences profit margins.

**Costs Without 8s:** This group excludes rare prime parts priced at 8 platinum, which represents a typical mid-range price for gold-tier items. It helps identify the profitability impact when these moderately priced parts are not included.

**Costs With 8s Only:** In contrast to the previous group, this set includes only rare prime parts that are priced at 8 platinum. It isolates the effects of focusing on this price point alone.

**Costs With 10s Only:** This group includes only rare prime parts priced at 10 platinum, focusing on high-priced items to see how they drive profitability on their own.

**Costs With 9s Only:** This group includes only rare prime parts priced at 9 platinum, which typically falls between the moderate and higher ends of the pricing spectrum. We analyze how focusing on these parts impacts the overall profit potential.

The goal of these groupings is to compare how different combinations of rare item prices affect profitability. Since gold-tier items tend to make the most significant difference in overall profit due to their higher prices, even slight adjustments in which prices are included or excluded can lead to large changes in the outcome. By examining these combinations through ANOVA, we can determine which set of price strategies offers the best balance between cost and potential profit.""")
    st.write('-----------------')
    st.write('**Note**: _When changing methods of calculation type, narrow offers a more general-ish approach of profit groups while broad explores a wider range of prices that are usually lower than the narrow counterpart but can offer more realism._')
    st.write()
    st.write('_I also know that technically there are more combinations in both broad and narrow sets, but that calculation is really unnecessary for the sake of simplicity and usability._')

with tabs[3]:
    st.write('**_Nothing here yet_**')
