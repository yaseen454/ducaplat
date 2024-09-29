import numpy as np
import streamlit as st
import pandas as pd
import seaborn as sns
from statistics import multimode
from matplotlib import pyplot as plt
from scipy.stats import ttest_1samp
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd

def generate_costs():
    tuples_list = []
    for b15 in [1]:
        for b25 in [1, 2]:
            for s45 in range(2, 4 + 1):
                for s65 in range(4, 7 + 1):
                    for g in range(7, 10 + 1):
                        tuples_list.append((b15, b25, s45, s65, g))
    return tuples_list
def generate_costs2():
    tuples_list = []
    for b15 in [1]:
        for b25 in [1, 2]:
            for s45 in range(2, 4 + 1):
                for s65 in range(2, 7 + 1):
                    for g in range(5, 10 + 1):
                        tuples_list.append((b15, b25, s45, s65, g))
    return tuples_list

def filter_costs(tuples_list, filter_values):
    filtered_list = [t for t in tuples_list if not any(x in t for x in filter_values)]
    return filtered_list

def generate_and_filter_costs(exclusion_sets):
    costs = generate_costs()
    cost_set = [filter_costs(costs, exclusion) for exclusion in exclusion_sets]
    return cost_set

def generate_and_filter_costs2(exclusion_sets):
    costs = generate_costs2()
    cost_set = [filter_costs(costs, exclusion) for exclusion in exclusion_sets]
    return cost_set

# Example usage:
exclusion_sets2 = [
    [],
    [5],
    [6],
    [7],         # No exclusions, original costs
    [9],         # Exclude 9s
    [10],        # Exclude 10s
    [8],
    [5,6],
    [5,7],
    [5,8],
    [5,9],
    [5,10],
    [6,7],
    [6,8],
    [6,9],
    [6,10],
    [7,8],
    [7,9],
    [7,10],
    [9, 10],
    [8, 9],
    [8, 10]
]

exclusion_sets = [
    [],          # No exclusions, original costs
    [9],         # Exclude 9s
    [10],        # Exclude 10s
    [8],         # Exclude 8s
    [9, 10],     # Exclude 9s and 10s
    [8, 9],      # Exclude 8s and 9s
    [8, 10]      # Exclude 8s and 10s
]

costs = generate_costs()
costs2 = generate_costs2()
cost_set = generate_and_filter_costs(exclusion_sets)
cost_set_2 = generate_and_filter_costs2(exclusion_sets2)

def set_info(set_type=1):
    info = ['All Costs', 'Costs Without 9s', 'Costs Without 10', 'Costs Without 8s',
            'Costs With 8s Only', 'Costs With 10s Only', 'Costs With 9s Only']
    info_2 = [
        'All Costs',
        'Costs Without 5s',
        'Costs Without 6s',
        'Costs Without 7s',
        'Costs Without 9s',
        'Costs Without 10s',
        'Costs Without 8s',
        'Costs Without 5s, 6s',
        'Costs Without 5s, 7s',
        'Costs Without 5s, 8s',
        'Costs Without 5s, 9s',
        'Costs Without 5s, 10s',
        'Costs Without 6s, 7s',
        'Costs Without 6s, 8s',
        'Costs Without 6s, 9s',
        'Costs Without 6s, 10s',
        'Costs Without 7s, 8s',
        'Costs Without 7s, 9s',
        'Costs Without 7s, 10s',
        'Costs Without 9s, 10s',
        'Costs Without 8s, 9s',
        'Costs Without 8s, 10s'
    ]
    if set_type == 1:
        return info
    elif set_type == 2:
        return info[1:]
    else:
        return info_2



def print_tukey_table(set_info, tukey_result):
    tukey_df = pd.DataFrame(data=tukey_result._results_table.data[1:], columns=tukey_result._results_table.data[0])
    set_info_dict = dict(enumerate(set_info, start=1))

    tukey_df['group1'] = tukey_df['group1'].map(set_info_dict)
    tukey_df['group2'] = tukey_df['group2'].map(set_info_dict)

    result_df = tukey_df[['group1', 'group2', 'p-adj', 'reject']].copy()
    result_df['reject'] = result_df['reject'].map({False: 'No significant difference', True: 'Significant difference'})
    result_df = result_df._rename(columns={'p-adj':'pvalue'})

    for row in result_df.itertuples(index=False):
        st.write(f"({row.group1}) vs. ({row.group2}): p = {row.pvalue} , {row.reject}")

# noinspection PyTypeChecker
def prime_calc(bronze15, bronze25, silver45, silver65, gold, costs,prints = True,return_df = False,save_path=None):
    c = 0
    profit_list = []
    count = bronze15 + bronze25 + silver45 + silver65 + gold
    ducats = 15 * bronze15 + 25 * bronze25 + 45 * silver45 + 65 * silver65 + 100 * gold
    trades = count / 6
    if isinstance(trades, float) and not trades.is_integer(): trades += 1
    cost_dictionary = {}

    for cost in costs:
        c += 1
        operation = cost[0] * bronze15 + cost[1] * bronze25 + cost[2] \
                    * silver45 + cost[3] * silver65 + cost[4] * gold
        profit_list.append(operation)


    avg = round(float(np.mean(profit_list)), 2)
    sd = round(float(np.std(profit_list)), 2)
    min_ = np.min(profit_list)
    max_ = np.max(profit_list)
    mid = round(float(np.median(profit_list)), 2)
    mid_range = (min(profit_list) + max(profit_list)) / 2
    range_ = max(profit_list) - min(profit_list)
    modes = list(multimode(profit_list))
    mode_avg = round(float(np.mean(modes)))
    trades = round(np.floor(trades))

    for i in range(len(costs)):
        key = f'Cost {i+1}'
        value = profit_list[i]
        cost_dictionary[key] = [value,costs[i]]
    sorted_cost_dict = dict(sorted(cost_dictionary.items(),key= lambda item: item[1],reverse=True))
    if return_df:
        df_data = []
        for key, item in sorted_cost_dict.items():
            value = item[0]
            price = item[1]
            category = ""
            if value == avg:
                category = "Average"
            elif value > avg:
                category = "Above Average"
            elif value < avg:
                category = "Below Average"
            df_data.append([key, value, price, category])
        df = pd.DataFrame(df_data, columns=['Cost', 'Profit', 'Prices', 'Category'])
        index_of_cost_18 = df[df['Cost'] == 'Cost 18'].index[0]
        df.loc[index_of_cost_18 + 1:, 'Category'] = 'Below Expectation'
        pd.set_option('display.max_rows', None)
        if prints: prime_prints(bronze15,bronze25,silver45,silver65,gold,count,trades,
                                ducats,sorted_cost_dict,avg,min_,max_,mid_range,range_,mid,modes,mode_avg,sd,df_printing=True,df=df)
        df.to_csv("C:\\Users\\yasee\\Documents\\My PC\\My Programming Files\\"
                    "My Python\\Personal Projects\\For Fun\\prime_excel.csv",index=False)
        return df
    if prints and not return_df: prime_prints(bronze15,bronze25,silver45,silver65,gold,count,trades
                                              ,ducats,sorted_cost_dict,avg,min_,max_,mid_range,range_,mid,modes,mode_avg,sd)

    return profit_list

# def prime_prints(bronze15=None, bronze25=None, silver45=None, silver65=None, gold=None, count=None, trades=None, ducats=None,
#                  sorted_cost_dict=None, avg=None,min_=None ,max_=None,mid_range=None, range_=None, mid=None, modes=None, mode_avg=None,sd=None,df_printing=False,df=None):
#     st.write('~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ')
#     st.write(f'Pricing for:\n{bronze15}'
#           f'x Bronze15, {bronze25}x Bronze25, '
#           f'{silver45}x Silver45, {silver65}x Silver65, '
#           f'{gold}x Gold')
#     st.write(f'Total items: {count}')
#     st.write(f'Total Trades: {trades}')
#     st.write(f'Total Ducats: {ducats}')
#     st.write('----------------------------')
#     st.write('Top Profits: ')
#     st.write(f'                      {bronze15}x {bronze25}x {silver45}x {silver65}x {gold}x')
#     below_avg_flag = False
#     avg_flag = False
#     c = 0
#     if not df_printing:
#         st.write(' ')
#         st.write('=========== ABOVE AVERAGE VALUES ===========')
#         for key, item, in sorted_cost_dict.items():
#             c+=1
#             if item[0] == avg and not avg_flag:
#                 st.write('=========== AVERAGE VALUES ===========')
#                 avg_flag = True
#             if item[0] < avg and not below_avg_flag:
#                 st.write('=========== BELOW AVERAGE VALUES ===========')
#                 below_avg_flag = True
#             if key == 'Cost 18':
#                 st.write(f'[{c}] {key} = {item[0]}, for prices {item[1]} => [MOST COMMON APPROACH]')
#             else:
#                 st.write(f'[{c}] {key} = {item[0]}, for prices {item[1]}')
#             if key == 'Cost 18':
#                 st.write('=========== BELOW EXPECTATION VALUES ===========')
#     else:
#         st.write(df)
#
#     st.write('----------------------------')
#     st.write(f'Average Plat Gained: {avg}')
#     st.write(f'Averaged 1 Plat Per Ducat: {round(ducats / avg,2)}')
#     st.write(f'10 Ducat/1 Plat Pricing: {ducats / 10}')
#     st.write(f'6 items /12 Plat Pricing: {count * 2}')
#     st.write(f'Midrange: {mid_range}')
#     st.write(f'Range: {range_}')
#     st.write(f'Median: {mid}')
#     st.write(f'Mode : {modes}')
#     st.write(f'Min: {min_}')
#     st.write(f'Max: {max_}')
#     st.write(f'Mode Average: {mode_avg}')
#     st.write(f'Standard Deviation: {sd}')
#     st.write('~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ')
#     st.write(' ')


def prime_prints(bronze15=None, bronze25=None, silver45=None, silver65=None, gold=None, count=None, trades=None,
                 ducats=None,
                 sorted_cost_dict=None, avg=None, min_=None, max_=None, mid_range=None, range_=None, mid=None,
                 modes=None, mode_avg=None, sd=None, df_printing=False, df=None):
    st.markdown('---')  # Adds a horizontal divider
    st.markdown('### Pricing Breakdown')  # Adds a bold header
    st.write(f'**{bronze15}x** Bronze15')
    st.write(f'**{bronze25}x** Bronze25')
    st.write(f'**{silver45}x** Silver45')
    st.write(f'**{silver65}x** Silver65')
    st.write(f'**{gold}x** Gold')
    # st.write(f'**Bronze15:** {bronze15} item(s)',
    #          f'   **Bronze25:** {bronze25} item(s)',
    #          f'   **Silver45:** {silver45} item(s)',
    #          f'   **Silver65:** {silver65} item(s)',
    #          f'  **Gold:** {gold} item(s)')

    col1, col2, col3, col4, col5 = st.columns(5)

    # Place metrics in columns
    with col1:
        st.metric(label="Total Items", value=count)
    with col2:
        st.metric(label="Total Trades", value=trades)
    with col3:
        st.metric(label="Total Ducats", value=ducats)
    with col4:
        st.metric(label="Avg 1 Plat Per Ducat",value = round(ducats / avg,2))
    with col5:
        st.metric(label="6/12 Plat Pricing",value = count * 2)

    st.markdown('---')
    st.write('### Top Profits')
    st.write(f'**Profit breakdown for each combination:**')
    st.write('_Prices = cost of each (Bronze15,Bronze25,Silver45,Silver65,Gold) possible combinations, '
             'setting calculation type = **broad** uses more combinations_')
    if df_printing:
        st.dataframe(df)
    else:
        avg_flag = below_avg_flag = False
        st.write(' ')  # Empty space

        c = 0
        st.markdown('#### Above Average Values:')
        for key, item, in sorted_cost_dict.items():
            c += 1
            if item[0] == avg and not avg_flag:
                st.markdown('#### Average Values:')
                avg_flag = True
            if item[0] < avg and not below_avg_flag:
                st.markdown('#### Below Average Values:')
                below_avg_flag = True
            st.write(f'[{c}] {key} = {item[0]}, for prices {item[1]}')
            if key == 'Cost 18':
                st.markdown('#### Below Expectation Values:')

    # Show final metrics
    st.markdown('---')
    col11, col12, col13 = st.columns(3)
    with col11:
        st.metric(label='Average Profit', value=avg)
    with col12:
        st.metric(label="Median", value=mid)
    with col13:
        st.metric(label='Mode Average',value=mode_avg)
    st.markdown('---')
def prime_prompt(bronze15=0,bronze25=0,silver45=0,silver65=0,gold=0,bypass=False):
    if bypass:
        return [bronze15,bronze25,silver45,silver65,gold]
    while True:
        try:
            bronze15 = int(input('Enter the amount of Bronze15s: '))
            bronze25 = int(input('Enter the amount of Bronze25s: '))
            silver45 = int(input('Enter the amount of Silver45s: '))
            silver65 = int(input('Enter the amount of Silver65s: '))
            gold = int(input('Enter the amount of Golds: '))
            break

        except ValueError as e:
            st.write(f"Error: {e}. Please enter a valid integer. Try again.")
    prime = [bronze15,bronze25,silver45,silver65,gold]
    return prime

def perform_ttest(bronze15, bronze25, silver45, silver65, gold, costs,alpha = 0.05,prints = False):
    profit_list = prime_calc(bronze15,bronze25,silver45,silver65,gold,costs,prints)
    # Assuming the null hypothesis is that the mean profit is equal to some expected value (e.g., 0)
    expected_mean = 0

    # Perform t-test
    t_statistic, p_value = ttest_1samp(profit_list, expected_mean)

    # Print the results
    st.write("T-statistic:", t_statistic)
    st.write("P-value:", p_value)
    # Visualize the data using a boxplot

    # Interpret the results
    if p_value < alpha:
        st.write("Reject the null hypothesis. There is a significant difference.")
    else:
        st.write("Fail to reject the null hypothesis. There is no significant difference.")

    plt.boxplot(profit_list, vert=False)
    plt.title('Boxplot of Profit Data')
    plt.show()

def perform_anova(bronze15, bronze25, silver45, silver65, gold, cost_set, alpha = 0.05, prints = False, set_type = 1, plot=False,
                  display_anova=True):
    profit_lists = []
    data_info = set_info(set_type=set_type)
    for costs in cost_set:
        profit_lists.append(prime_calc(bronze15,bronze25,silver45,silver65,gold,costs,prints=prints))
    st.write("**Profit Data Summary:**")
    max_list = []
    med_list = []
    avg_list = []
    min_list = []
    for i in range(len(profit_lists)):
        avg = round(np.mean(profit_lists[i]),2)
        avg_list.append(avg)
        med = np.median(profit_lists[i])
        med_list.append(med)
        max_ = np.max(profit_lists[i])
        max_list.append(max_)
        min_ = np.min(profit_lists[i])
        min_list.append(min_)
    data = {
        'Profits': data_info,
        'Min': min_list,
        'Median':med_list,
        'Average':avg_list,
        'Max':max_list
    }

    data = pd.DataFrame(data)
    st.table(data)
    st.write('**Note:** _Profit lists that exclude or include values like 8, 9 or 10 etc.. '
             'show how  rare (gold) items affect/compare between the different groups._')
    st.write()
    st.write(f'- > Average Median of Profits: {round(np.mean(med_list),2)}')
    st.write(f'- > Average Mean of Profits: {round(np.mean(avg_list),2)}')
    st.write(f'- > Average Max of Profits: {round(np.mean(max_list),2)}')
    st.write()
    f_statistic, p_value = f_oneway(*profit_lists)
    if display_anova:
        st.markdown("### ANOVA and Tukey's HSD Post-Hoc Test Results")
        st.write("----------------------------------------------\n")
        st.write(f"**- F-statistic:** {f_statistic}")
        st.write(f"**- p-value:** {p_value} alpha= ({alpha}))\n")

    if plot:
        overall_average = np.mean(np.concatenate(profit_lists))
        overall_median = np.median(np.concatenate(profit_lists))
        medians = [np.median(profit_list) for profit_list in profit_lists]
        sorted_indices = np.argsort(medians)

        # Set plot size for better visualization
        fig, ax = plt.subplots(figsize=(12, 8))  # Adjust figure size as needed

        # Use a color palette for better visual appeal
        palette = sns.color_palette("Set2", len(profit_lists))

        # Create the boxplot with sorted data and a nice color palette
        sns.boxplot(data=[profit_lists[i] for i in sorted_indices], notch=False, ax=ax, palette=palette,
                    width=0.6, linewidth=1.2, showfliers=False)  # `showfliers=False` removes outliers from box plot

        # Overlay actual data points (with jitter) to give a sense of data distribution
        for i, idx in enumerate(sorted_indices):
            sns.stripplot(data=profit_lists[idx], color='black', jitter=True, ax=ax, size=5, alpha=0.6)

        # Sort x-labels and rotate them for better readability
        sorted_x_labels = [data_info[i] for i in sorted_indices]
        ax.set_xticks(ticks=range(len(sorted_x_labels)))
        ax.set_xticklabels(sorted_x_labels, fontsize=10, rotation=45, ha='right')

        # Add horizontal lines for overall mean and median
        ax.axhline(overall_average, color='red', linestyle='dashed', linewidth=2, label='Overall Mean')
        ax.axhline(overall_median, color='blue', linestyle='dashed', linewidth=2, label='Overall Median')

        # Set titles and labels with improved font sizes
        ax.set_title('Boxplot of Profit Data', fontsize=16)
        ax.set_ylabel('Platinum', fontsize=12)
        ax.set_xlabel('Pricing Method', fontsize=12)

        # Add a legend and increase its size for better visibility
        ax.legend(fontsize=10)

        # Improve layout for better fit
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(fig)

    if display_anova:
        if p_value <= alpha:
            # Perform Tukey's HSD post-hoc test
            data = np.concatenate(profit_lists)
            groups = np.concatenate([[i+1] * len(profit_lists[i]) for i in range(len(profit_lists))])
            tukey_results = pairwise_tukeyhsd(data, groups)

            st.write("ANOVA Result: The means of at least two groups are significantly different.")
            st.write(' ')
            # print_tukey_table(data_info,tukey_results)
            st.write("\nTukey's HSD Post-Hoc Test:")
            st.write("---------------------------")
            st.write("The Tukey HSD test compares the means of all pairs of groups.\n")
            st.write(tukey_results)

            return tukey_results
        else:
            st.write("ANOVA Result: There is no significant difference in the means of the groups.")
            return


    # Boxplot using Seaborn




def run_calculator(bronze15=0,bronze25=0,silver45=0,silver65=0,gold=0,bypass=False,plot=False,display_anova=True):
    data = prime_prompt(bronze15=bronze15,bronze25=bronze25,silver45=silver45,silver65=silver65,gold=gold,bypass=bypass)
    calculator = prime_calc(data[0],data[1],data[2],data[3],data[4],costs=costs,return_df=True)
    perform_anova(data[0], data[1], data[2], data[3], data[4], cost_set=cost_set,plot=plot,set_type=1,display_anova=display_anova)
    return calculator

def run_calculator2(bronze15=0,bronze25=0,silver45=0,silver65=0,gold=0,bypass=False,plot=False,display_anova=True):
    data = prime_prompt(bronze15=bronze15,bronze25=bronze25,silver45=silver45,silver65=silver65,gold=gold,bypass=bypass)
    calculator = prime_calc(data[0],data[1],data[2],data[3],data[4],costs=costs2,return_df=True)
    perform_anova(data[0], data[1], data[2], data[3], data[4], cost_set=cost_set_2,plot=plot,set_type=3,display_anova=display_anova)
    return calculator

def run_prime_calculator(bronze15=0,bronze25=0,silver45=0,silver65=0,gold=0,bypass=False,plot=False,calc_type=1,display_anova=True):
    if calc_type == 1:
        run_calculator(bronze15=bronze15,bronze25=bronze25,silver45=silver45,silver65=silver65,gold=gold,bypass=bypass,plot=plot,display_anova=display_anova)
    else:
        run_calculator2(bronze15=bronze15,bronze25=bronze25,silver45=silver45,silver65=silver65,gold=gold,bypass=bypass,plot=plot,display_anova=display_anova)

if __name__ == '__main__':
    run_prime_calculator(calc_type=1)

print()
