#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 09:12:20 2023

@author: rouguiatouba
"""
# %% IMPORT 

import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import matplotlib.pyplot as plt
from tabulate import tabulate

# %% Convert the database (file `wells_data.db`) to an XLSX and send it to a local PostgreSQL database (you can also send it to a new SQLite database if you do not have a PostgreSQL database).

def convert_postgresql_to_xlsx(host, database, user, password, table='wells_data'):
    """
    This function converts data from a database to an XLSX file.

    Arguments:
    host (str): PostgreSQL host.
    database (str): PostgreSQL database name.
    user (str): PostgreSQL username.
    password (str): PostgreSQL password.
    postgresql_url (str): URL for the PostgreSQL database.
    table (str, optional): Name of the table in the PostgreSQL database. Default is 'wells_data'.

    Returns:
    str: Path to the generated XLSX file.
    """
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)

    # Use Pandas to read data from the database
    data = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)

    # Write the data to an XLSX file
    data.to_excel(f'{table}.xlsx', index=False)

    # Close the database connection
    conn.close()
    
    return f'{table}.xlsx'

def convert_xlsx_to_postgresql(postgresql_url, excel_file_path, table_name, sheet_name=None):
    """
    This function converts data from an XLSX file to a PostgreSQL database.

    Arguments:(rt êb)
    postgresql_url (str): URL for the PostgreSQL database.
    excel_file_path (str): Path to the XLSX file.
    table_name (str): Name of the table in the PostgreSQL database to store the data.
    sheet_name (str, optional): Name of the sheet in the XLSX file. Default is None.

    Returns:
    dataframe: A Pandas DataFrame containing the data from the specified table in the PostgreSQL database.
    """
    # Create an engine for the PostgreSQL database
    engine = create_engine(postgresql_url)

    if sheet_name is None:
        # Read data from the first sheet of the Excel file into a Pandas DataFrame
        excel_data = pd.read_excel(excel_file_path)
    else:
        # Read data from the specified sheet of the Excel file into a Pandas DataFrame
        excel_data = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    # Upload the Excel data to the PostgreSQL database
    excel_data.to_sql(table_name, con=engine, if_exists='replace', index=False)
    
    # Read the data from the specified table in the PostgreSQL database into a Pandas DataFrame
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', con=engine)
    
    return df

#%% Make a scatter Plot of the bottom hole temperature (vertical axis) according to the total depth (horizontal axis); try with and with out removing the 0° temperature value;

def temperature_scatter_plot(df, include_zero_temperature=True):
    """
    This function create a scatter plot of Temperature vs Total Depth with or without 0° Temperature.

    Arguments:
    df                  - DataFrame with the data.
    include_zero_temperature - Whether to include rows with 0° Temperature (default=True).
    """
    
    # Filter the DataFrame based on the include_zero_temperature parameter
    if include_zero_temperature:
        filtered_df = df
        title_suffix = "Including 0° Temperature"
    else:
        filtered_df = df[df['wlbBottomHoleTemperature'] != 0]
        title_suffix = "Excluding 0° Temperature"

    # Create a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(filtered_df['wlbTotalDepth'], filtered_df['wlbBottomHoleTemperature'], c='blue' if include_zero_temperature else 'red', label=f'With 0° Temperature' if include_zero_temperature else 'Without 0° Temperature')
    plt.xlabel('Total Depth')
    plt.ylabel('Bottom Hole Temperature (°C)')
    plt.title(f'Scatter Plot of Temperature vs Total Depth ({title_suffix})')
    plt.legend()
    plt.grid(True)
    plt.show()

#%% Make a scatter Plot of the drilling days (vertical axis) according to the total depth (horizontal axis); use query function to keep only 0 < wlbDrillingDays < 800

def drilling_days_scatter_plot(df, min_days=0, max_days=800):
    """
    This function create a scatter plot of Drilling Days vs Total Depth with filtering criteria.

    Arguments:
    df        - DataFrame with the data.
    min_days  - Minimum drilling days to include (default=0).
    max_days  - Maximum drilling days to include (default=800).
    """

    # Filter the DataFrame based on the minimum and maximum drilling days
    filtered_df = df[(df['wlbDrillingDays'] > min_days) & (df['wlbDrillingDays'] < max_days)]

    # Create a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(filtered_df['wlbTotalDepth'], filtered_df['wlbDrillingDays'], c='green')
    plt.xlabel('Total Depth')
    plt.ylabel('Drilling Days')
    plt.title(f'Scatter Plot of Drilling Days vs Total Depth ({min_days} < wlbDrillingDays < {max_days})')
    plt.grid(True)
    plt.show()
#%% Calculate the mean of the total depth according to the "Age At Td", show it as a table, sorted by mean total depth. 

def calculate_mean_depth_by_age(df):
    """
    This function calculate the mean total depth by "Age At Td" and return a sorted DataFrame.

    Arguments:
    df - DataFrame with the data.

    Returns:
    sorted_mean_depth - Sorted DataFrame with mean total depth by "Age At Td".
    """
    # Group by "Age At Td" and calculate the mean total depth
    mean_depth_by_age = df.groupby('wlbAgeAtTd')['wlbTotalDepth'].mean().reset_index()

    # Sort the DataFrame by mean total depth in descending order
    sorted_mean_depth = mean_depth_by_age.sort_values(by='wlbTotalDepth', ascending=False)

    # Use tabulate to format the DataFrame as a table
    table_str = tabulate(sorted_mean_depth, headers='keys', tablefmt='pretty')
    

    return table_str

#%% Make a plot with the monthly production data (Oil, Gas and Water) of the `7405` NPDCode Volve according to the time. You will need to add and `monthly` column, create by concatenating the `Year` and the `Month` columns; Plot: vertical axis: the 3 productions (Oil, Gas and Water) and horizontal axis: the month and the year (ex: 2020-01).

def plot_monthly_production_data(output_excel_file):
    """
    This function loads the production data from an input Excel file, creates a 'monthly' column by
    extracting the year and month from 'DATEPRD', filters data for '7405' NPDCode Volve,
    creates a plot of monthly production data with individual y-axes for Oil, Gas, and Water, and saves
    the filtered data to a new Excel file.

    Arguments:
    output_excel_file (str): The path to the output Excel file to save the filtered data.

    Returns:
    None
    """
    
    # Creation of the 'monthly' column
    monthly_production_df['monthly'] = monthly_production_df['Year'].astype(str) + '-' + monthly_production_df['Month'].astype(str).str.zfill(2)

    # Data of the '7405' NPDCode Volve
    volve_data = monthly_production_df[monthly_production_df['NPDCode'] == 7405]

    # CPlot of monthly production data for Oil, Gas, and Water with individual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    ax1.set_xlabel('Year-Month')
    ax1.set_ylabel('Oil (Sm3)', color='tab:blue')
    ax1.plot(volve_data['monthly'], volve_data['Oil (Sm3)'], color='tab:blue', label='Oil', marker='o')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Gas (Sm3)', color='tab:orange')
    ax2.plot(volve_data['monthly'], volve_data['Gas (Sm3)'], color='tab:orange', label='Gas', marker='o')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.set_ylabel('Water (Sm3)', color='tab:green')
    ax3.plot(volve_data['monthly'], volve_data['Water (Sm3)'], color='tab:green', label='Water', marker='o')
    ax3.tick_params(axis='y', labelcolor='tab:green')

    plt.title('Monthly Production Data for Volve (7405 NPDCode)')
    
    # Legends for each variable
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='upper left')

    
    plt.grid(True)
    
    # Save the DataFrame with the new 'monthly' column to a new Excel file
    volve_data.to_excel(output_excel_file, index=False)
    plt.show()
#%% Calculate the sum of the Oil production by Volve

def calculate_total_oil_production(dataframe):
    """
    This function calculate the total oil production by Volve 

    Arguments:
    dataframe (pd.DataFrame): The DataFrame containing the production data.

    Returns:
    float: Total oil production by Volve in Sm3.
    """

    # Computation of the sum of the 'Oil (Sm3)' column for each Volve
    total_oil_production = dataframe.groupby('NPDCode')['Oil (Sm3)'].sum().reset_index()
    table = tabulate(total_oil_production, headers='keys', tablefmt='pretty', showindex=False)

    return table
#%% `partial_wells_data` from `wells_data` by keeping only `wlbTotalDepthcolumns` and the common column and `partial_mpd` from `monthly_production_data` (`mpd`) by keeping only `Oil`, `Gas` `Water` and the common column and making a sum aggregation grouping by the common column

def create_partial_dataframes(dataframe1, dataframe2, columns_to_select_1,columns_to_select_2,common_column_1,common_column_2):
    """
    This function create partial dataframes from two input dataframes.

    Arguments:
    dataframe1 (pd.DataFrame): The first dataframe.
    dataframe2 (pd.DataFrame): The second dataframe.
    common_column_1 (str): The common column in dataframe1 to merge on.
    common_column_2 (str): The common column in dataframe2 to merge on.
    columns_to_select_1 (list): List of column names to select from dataframe1.
    columns_to_select_2 (list): List of column names to select from dataframe2.


    Returns:
    pd.DataFrame: Partial dataframe from dataframe1.
    pd.DataFrame: Partial dataframe from dataframe2 with aggregation.
    pd.DataFrame: Merged dataframe of the two partials one.
    """
    columns_1=common_column_1+columns_to_select_1
    columns_2=common_column_2+columns_to_select_2

    # Creation of the partial dataframe from dataframe1
    partial_df1 = dataframe1[columns_1]

    # Creation of the partial dataframe from dataframe2 with aggregation
    partial_df2 = dataframe2[columns_2].groupby(common_column_2).sum().reset_index()
    
    #Merging
    merged_data = pd.merge(partial_df1, partial_df2, left_on='wlbWellboreName', right_on='Wellbore name')
    
    #plots
    oil_production = merged_data['Oil (Sm3)']
    total_depth = merged_data['wlbTotalDepth']
    
    plt.figure(figsize=(8, 6))
    plt.scatter(total_depth, oil_production, marker='o', color='blue')
    plt.title('Scatter Plot of Oil Production vs. Total Depth')
    plt.xlabel('Total Depth')
    plt.ylabel('Oil Production (Sm3)')
    plt.grid(True)
    plt.show()
    
    return partial_df1, partial_df2, merged_data

#%%
if __name__ == "__main__":
    
    # Set up the PostgreSQL for the database
    host = 'localhost'             
    database = 'well_db'    
    user = 'postgres'             
    password = 'postgres' 
    postgresql_url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/well_db'
    
    #xlsx path
    xlsx_path=convert_postgresql_to_xlsx(host, database, user, password, table='wells_data')
    # Convert data from the 'wells_data.xlsx' Excel file to a PostgreSQL database
    well_df = convert_xlsx_to_postgresql(postgresql_url, xlsx_path, 'wells_data')
    
    # Convert data from 'Volve_production_data.xlsx' Excel file (specific sheet: 'Monthly Production Data') to PostgreSQL database
    monthly_production_df = convert_xlsx_to_postgresql(postgresql_url, 'Volve_production_data.xlsx', 'Monthly Production Data','Monthly Production Data')
    
    # Create scatter plots of temperature vs. total depth
    # Include rows with 0° temperature and exclude them, and display both plots.
    temperature_scatter_plot(well_df, include_zero_temperature=True)  # Including 0° Temperature
    temperature_scatter_plot(well_df, include_zero_temperature=False)  # Excluding 0° Temperature
    
    # Create a scatter plot of drilling days vs. total depth
    # Filter data to include rows with 0 < wlbDrillingDays < 800.
    drilling_days_scatter_plot(well_df, min_days=0, max_days=800)
    
    # Calculate the mean total depth by "Age At Td" and display it as a sorted table.
    sorted_mean_depth_table = calculate_mean_depth_by_age(well_df)
    print('Table of the mean total depth by age at total depth:\n', sorted_mean_depth_table)
    
    # Create and save a plot of monthly production data for Volve
    plot_monthly_production_data("Volve_production_data_with_monthly.xlsx")
    
    # Calculate the total oil production by Volve
    total_oil_production = calculate_total_oil_production(monthly_production_df)
    print('Total oil production by Volve:\n', total_oil_production)
    
    # Define columns to select for partial dataframes and common columns
    wells_column = ['wlbTotalDepth']
    wells_common_column = ['wlbNpdidWellbore', 'wlbWellboreName', 'wlbField', 'wlbProductionLicence', 'wlbDrillPermit', 'wlbWellType', 'wlbDrillingOperator', 'wlbEntryDate', 'wlbCompletionDate']
    mpd_column = ['Oil (Sm3)', 'Gas (Sm3)', 'Water (Sm3)']
    mpd_common_column = ['Wellbore name', 'NPDCode', 'Year', 'Month']
    
    # Create partial dataframes and merge them
    partial_wells_data, partial_mpd, merged_data = create_partial_dataframes(well_df, monthly_production_df, wells_column, mpd_column, wells_common_column, mpd_common_column)
    print('Partial Wells Data:\n', partial_wells_data)
    print('Partial Monthly Production Data:\n', partial_mpd)
    print('Merged Data:\n', merged_data)
    print("It is noticeable that the deeper we go, the less significant the oil production becomes. For instance, between 1500m and 3800m depth, we have more than 100000Sm3 oil production, whereas beyond 4500m depth, we have 50000Sm3 or less oil production. Additionally, it is worth noting that between 3800m depth and 4500m depth, there is almost no production.")