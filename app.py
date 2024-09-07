import easyocr
import io
import streamlit as st
from calc import run_prime_calculator
from ocr import expand_list,count_types,count,return_df
from PIL import Image, ImageGrab
from streamlit_paste_button import paste_image_button as pbutton
import pytesseract
import numpy as np

# Initialize session state variables globally if they don't exist
if 'extracted_texts' not in st.session_state:
    st.session_state.extracted_texts = []
if 'expanded_items' not in st.session_state:
    st.session_state.expanded_items = []
if 'continue_checking' not in st.session_state:
    st.session_state.continue_checking = True
if 'calculation_done' not in st.session_state:
    st.session_state.calculation_done = False
if 'calc_type' not in st.session_state:
    st.session_state.calc_type = 1  # Initialize to 'narrow' by default
if 'display_anova' not in st.session_state:
    st.session_state.display_anova = False
if 'enable_plot' not in st.session_state:
    st.session_state.enable_plot = False



# Include Google Font
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


def process_image(image):
    """Extract text from the uploaded image."""
    text = pytesseract.image_to_string(image)
    formatted_text = [line.strip() for line in text.splitlines() if line.strip()]
    return formatted_text


# Ribbon for page navigation
tabs = st.tabs(["Home", "Calculator","Help","About"])

# The sidebar is defined only within this block
st.sidebar.header("Input Method")
input_method = st.sidebar.radio(
    "Choose how you want to input prime parts:",
    ("Manual Input", "Image Upload", "Image from clipboard")
)

with tabs[0]:
    # Large title (website name) before the main title with dark gold color and custom font
    st.markdown("<h1 class='large-title'>DucaPlat</h1>", unsafe_allow_html=True)
    # Title
    st.title("Warframe Prime Item Trading Calculator")
    st.write("_Welcome to **DucaPlat**! the Warframe Prime Item Trading Calculator. "
             "This tool allows you to calculate the profit from trading prime parts in Warframe._")
    st.write("_You can choose to input your prime parts either manually or "
             "by uploading images for OCR processing. Once you have processed "
             "the images or entered the data, you can calculate the profit and see detailed results._")
    st.write('### Prime Items')
    # Define the URL and the link text
    url = "https://drops.warframestat.us/"
    link_text = "drops.warframestat.us"

    # Use st.write with Markdown syntax to display the link
    st.write(f'_Processed and sourced from_ ',f"_[{link_text}]({url})_")
    st.dataframe(return_df())

with tabs[1]:
    st.title("Prime Item Trading Calculator")
    # Add a dropdown for calc_type selection
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
                plot=st.session_state.enable_plot, calc_type=calc_type,display_anova=st.session_state.display_anova
            )
            st.write(calculator_results)
    elif input_method == 'Image Upload':
        # Function to process the image and extract text
        def main1():
            st.title("Multi-Image Text Extractor")
            # Initialize session state for storing extracted texts and expanded list
            if 'extracted_texts' not in st.session_state:
                st.session_state.extracted_texts = []
            if 'expanded_items' not in st.session_state:
                st.session_state.expanded_items = []

            # File uploader widget to allow uploading multiple images
            uploaded_files = st.file_uploader("Upload images (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"],
                                              accept_multiple_files=True)

            # Button to trigger processing of images
            if st.button("Process Images"):
                if uploaded_files:
                    extracted_texts = []
                    # Process each uploaded image
                    for uploaded_file in uploaded_files:
                        image = Image.open(uploaded_file)
                        text = process_image(image)
                        extracted_texts.append(text)

                        # Display the extracted text
                        st.write(f"Text extracted from: {uploaded_file.name}")
                        st.write("\n".join(text))

                        # Optionally show the image
                        st.image(image, caption=f'Uploaded Image: {uploaded_file.name}', use_column_width=True)

                    # Flatten and store the extracted texts in session state
                    flat_extracted_texts = [item for sublist in extracted_texts for item in sublist]
                    st.session_state.extracted_texts = flat_extracted_texts
                    st.success("Images processed successfully!")
                else:
                    st.warning("Please upload at least one image to process.")

            # If there are extracted texts in session state, proceed to expansion and profit calculation
            if st.session_state.extracted_texts:
                st.subheader("Expanded List")
                expanded_items = expand_list(st.session_state.extracted_texts)
                st.session_state.expanded_items = expanded_items
                st.write(expanded_items)

                # Show the "Calculate Profit" button
                if st.button("Calculate Profit"):
                    # Perform the profit calculation using expanded items
                    dictionary = count_types(expanded_items)
                    counts = count(dictionary)
                    result = run_prime_calculator(counts[0], counts[1], counts[2], counts[3], counts[4], bypass=True,
                                                  plot=st.session_state.enable_plot,calc_type=calc_type,display_anova=st.session_state.display_anova)
                    st.write(result)
                # Run the main function
        main1()
    elif input_method == 'Image from clipboard':
        def main2():
            st.header("Extract Prime Parts from Clipboard Image")

            paste_result = pbutton("📋 Paste an image")
            image_ = paste_result.image_data
            image_np = np.array(image_)
            # Initialize EasyOCR reader
            reader = easyocr.Reader(['en'])
            # Perform OCR
            result = reader.readtext(image_np)
            # Extract text from the result
            text = ' '.join([item[1] for item in result])
            extracted_text = text

            if paste_result.image_data is not None:
                st.write('Pasted image:')
                st.image(paste_result.image_data)
                st.session_state.extracted_texts.extend(extracted_text)

            # Display extracted texts from clipboard images
            if st.session_state.extracted_texts:
                st.subheader("Extracted Prime Parts")
                expanded_items = expand_list(st.session_state.extracted_texts)
                st.session_state.expanded_items = expanded_items
                st.write(st.session_state.expanded_items)

            # Clear extracted items button
            if st.button("Clear Extracted Items"):
                st.session_state.extracted_texts = []
                st.session_state.expanded_items = []
                st.success("Extracted items cleared successfully!")
                st.rerun()  # Force a rerun to update the extracted parts display

                # Clear last extracted text button


            # Show the "Calculate Profit" button if there's at least one extracted text
            if st.session_state.extracted_texts:
                if st.button("Calculate Profit"):

                    dictionary = count_types(st.session_state.expanded_items)
                    counts = count(dictionary)
                    result = run_prime_calculator(
                        counts[0], counts[1], counts[2], counts[3], counts[4],
                        bypass=True, plot=st.session_state.enable_plot,
                        calc_type=calc_type, display_anova=st.session_state.display_anova
                    )
                    st.write(result)
        main2()
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

    # Display the image
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

