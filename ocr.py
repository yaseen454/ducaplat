import pandas as pd
from calc import run_prime_calculator
import re
import streamlit as st


# Function to determine the 'Type' based on 'Average Ducats'
def determine_type(average_ducats):
    tolerance = 1e-6
    if average_ducats == 15:
        return 'Bronze15'
    elif average_ducats == 45:
        return 'Silver45'
    elif average_ducats == 100:
        return 'Gold'
    elif 15 < average_ducats < 30:
        return 'Bronze25'
    elif 35 <= average_ducats <= 40:
        return 'Silver45'
    elif abs(average_ducats - 40.714286) < tolerance:
        return 'Bronze25'
    elif 45 < average_ducats < 100:
        return 'Silver65'
    else:
        return 'Unknown'  # Default case if none of the conditions match



# Load the DataFrame
df = pd.read_csv('data/Cleaned Prime Data.csv')
df_cleaned = df.groupby('Item Name').agg({'Ducats': 'mean'}).reset_index()
df_cleaned.columns = ['Item Name', 'Average Ducats']
df_cleaned['Type'] = df_cleaned['Average Ducats'].apply(determine_type)
def return_df():
    return df_cleaned.drop('Average Ducats',axis=1)
# Outlier handling
df_cleaned.loc[df_cleaned['Item Name'] == 'Fang Prime Handle', 'Type'] = 'Bronze25'
df_cleaned.loc[df_cleaned['Item Name'] == 'Volt Prime Blueprint', 'Type'] = 'Bronze25'
df_cleaned.loc[df_cleaned['Item Name'] == 'Latron Prime Blueprint', 'Type'] = 'Bronze15'
df_cleaned.loc[df_cleaned['Item Name'] == 'Cernos Prime String', 'Type'] = 'Bronze25'
df_cleaned.loc[df_cleaned['Item Name'] == 'Knell Prime Receiver', 'Type'] = 'Silver45'
df_cleaned.loc[df_cleaned['Item Name'] == 'Nikana Prime Blueprint', 'Type'] = 'Bronze25'

# Save the DataFrame to a CSV file
df_cleaned.to_csv('data/Cleaned Average Prime Data.csv', index=False)

def convert_text_to_list(input_text):
    lines = input_text.strip().splitlines()
    result = []

    for line in lines:
        if ' X ' in line:
            quantity, item = line.split(' X ', 1)
            quantity = int(quantity)
            result.extend([item] * quantity)
        else:
            result.append(line)

    return result

def count_types(item_list, dataframe=df_cleaned):
    # Initialize the dictionary to hold counts of each 'Type'
    type_counts = {}

    for item in item_list:
        # Find the corresponding row in the DataFrame
        row = dataframe[dataframe['Item Name'] == item]
        if row.empty:
            # Raise a warning and stop the program if the item isn't found
            st.warning(f'Warning: Item "{item}" was not found amongts prime blueprints.')
            # raise ValueError(f"Warning: Item '{item}' was not found amongst prime blueprints.")

        if not row.empty:
            item_type = row.iloc[0]['Type']  # Get the 'Type' of the item

            # Increment the count in the dictionary
            if item_type in type_counts:
                type_counts[item_type] += 1
            else:
                type_counts[item_type] = 1

    return type_counts

# Function to parse the input string
def extract_items(input_str, df=df_cleaned):
    parsed_items = []
    
    # Find all instances of "N X" followed by an item
    n_x_pattern = r'(\d+)\s*X\s*([A-Za-z\s]+)'
    matches = re.findall(n_x_pattern, input_str)
    
    # Handle "N X Item" matches
    for match in matches:
        count = int(match[0])
        item_str = match[1].strip()
        
        # Find if the item is in the dataframe
        for index, row in df['Item Name'].iteritems():
            item = row['Item Name']
            if item_str.startswith(item):  # Ensure matching item
                parsed_items.extend([item] * count)
                input_str = input_str.replace(f'{count} X {item}', '', 1)
                break

    # Handle remaining single items (without "N X" prefix)
    for index, row in df['Item Name'].iteritems():
        item = row['Item Name']
        if item in input_str:
            parsed_items.append(item)
            input_str = input_str.replace(item, '', 1)

    return parsed_items


# def expand_list(items):
#     expanded_list = []
#     for item in items:
#         match = re.match(r'(\d+)X (.+)', item)
#         if match:
#             count = int(match.group(1))
#             element = match.group(2)
#             expanded_list.extend([element] * count)
#         else:
#             expanded_list.append(item)
#     return expanded_list

def expand_list(items):
    expanded_list = []
    for item in items:
        match = re.match(r'(\d+)\s*[xX]\s*(.+)', item)
        if match:
            count = int(match.group(1))
            element = match.group(2).strip()
            expanded_list.extend([element] * count)
        else:
            expanded_list.append(item)
    return expanded_list



def dict_count(item_list,dataframe=df_cleaned):
    result = count_types(item_list=item_list,dataframe=dataframe)
    Bronze15 = result.get('Bronze15', 0)
    Bronze25 = result.get('Bronze25', 0)
    Silver45 = result.get('Silver45', 0)
    Silver65 = result.get('Silver65', 0)
    Gold = result.get('Gold', 0)
    d = [Bronze15,Bronze25,Silver45,Silver65,Gold]
    return d

def count(dictionary):
    Bronze15 = dictionary.get('Bronze15', 0)
    Bronze25 = dictionary.get('Bronze25', 0)
    Silver45 = dictionary.get('Silver45', 0)
    Silver65 = dictionary.get('Silver65', 0)
    Gold = dictionary.get('Gold', 0)
    d = [Bronze15, Bronze25, Silver45, Silver65, Gold]
    return d

def finalize_process(item_list,df=df_cleaned):
    items = ' '.join(item_list)
    parsed = extract_items(items,df)
    return dict_count(parsed,df)

def price_of_all_primes(calc_type = 1,plot=False,dataframe=df_cleaned):
    d = dict_count(df_cleaned['Item Name'],dataframe=dataframe)
    return run_prime_calculator(bronze15=d[0], bronze25=d[1], silver45=d[2], silver65=d[3],
                                gold=d[4], bypass=True, plot=plot, calc_type=calc_type)


# at calculator 1
min_price_of_all = 1529
max_price_of_all = 2352
avg_price_of_all = 1940.5

if __name__ == '__main__':
    price_of_all_primes()

