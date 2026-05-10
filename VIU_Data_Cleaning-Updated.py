# Generated from: VIU_Data_Cleaning-Updated.ipynb
# Converted at: 2026-05-10T16:02:56.712Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import pandas as pd
import numpy as np

# Load data
file_path = 'C:/Users/6362785/VIU Assignment 1 Data.xlsx'  # Replace with your correct file path
installs = pd.read_excel(file_path, sheet_name='Installs Raw Data')
google_cost = pd.read_excel(file_path, sheet_name='Google Cost')
fb_cost = pd.read_excel(file_path, sheet_name='FB Cost')
other_cost = pd.read_excel(file_path, sheet_name='Other Partners Cost')

# Step 1: Preprocessing installs data
installs['aps_install_date'] = pd.to_datetime(installs['aps_install_date'])
installs = installs[(installs['aps_install_date'] >= '2021-03-01') & (installs['aps_install_date'] <= '2021-03-05')]
installs['VVmins'] = installs['VVmins'].replace('#VALUE!', 0)
installs['aps_campaign_group'] = installs['aps_campaign_group'].replace('null', 'Unknown')
installs['aps_creative'] = installs['aps_creative'].replace('null', 'Unknown')
fb_cost['aps_install_date'] = pd.to_datetime(fb_cost['Day'])
google_cost['aps_install_date'] = pd.to_datetime(google_cost['Day'])
installs['VVs'] = installs['VVs'].replace('#VALUE!', 0)
installs['VVMins_7'] = installs['VVMins_7'].replace('#VALUE!', 0)
installs['new_DUV_7'] = installs['new_DUV_7'].replace('#VALUE!', 0)
installs['VVs_7'] = installs['VVs_7'].replace('#VALUE!', 0)
print(installs)


# Remove duplicates
installs.drop_duplicates(inplace=True)
print(installs)

# Step 2: Preprocessing cost data
installs['Media Source'] = 'Other'  # Default value if needed
# Now update values based on contributor_source
installs.loc[installs['contributor_source'].str.contains('facebook', case=False, na=False), 'Media Source'] = 'Facebook'
installs.loc[installs['contributor_source'].str.contains('google', case=False, na=False), 'Media Source'] = 'Google'
installs = installs.drop(['contributor_source'], axis=1)

fb_cost = fb_cost.rename(columns={'Campaign Name': 'contributor_campaign', 'Ad Set Name': 'aps_campaign_group', 'Ad Name': 'aps_creative', 'Amount Spent': 'fb_Cost', 'Link Clicks': 'fb_Clicks', 'Impressions': 'fb_Impressions'})
fb_cost = fb_cost.groupby(['aps_install_date', 'contributor_campaign','aps_campaign_group', 'aps_creative'])[['fb_Cost', 'fb_Clicks', 'fb_Impressions']].sum().reset_index()

print(fb_cost)
google_cost = google_cost.rename(columns={'Campaign': 'contributor_campaign', 'Ad group ID': 'aps_campaign_group', 'Cost': 'google_Cost', 'Clicks': 'google_Clicks', 'Impressions': 'google_Impressions'})
google_cost = google_cost.groupby(['aps_install_date', 'contributor_campaign','aps_campaign_group'])[['google_Cost', 'google_Clicks', 'google_Impressions']].sum().reset_index()

# Merge installs with Facebook and Google costs
installs = installs.merge(fb_cost[['contributor_campaign', 'aps_install_date', 'aps_campaign_group', 'aps_creative', 'fb_Cost', 'fb_Clicks', 'fb_Impressions']], on=['aps_install_date','contributor_campaign','aps_campaign_group', 'aps_creative'], how='outer')
installs = installs.merge(google_cost[['contributor_campaign', 'aps_install_date', 'aps_campaign_group','google_Cost', 'google_Clicks', 'google_Impressions']], on=['aps_install_date','contributor_campaign','aps_campaign_group'], how='outer')

installs['missing_campaign_flag'] = np.where(
    (installs['Media Source'] == 'Facebook') & (installs['fb_Cost'].isna()), 'Missing',
    np.where((installs['Media Source'] == 'Google') & (installs['google_Cost'].isna()), 'Missing', 'Matched')
)
installs.loc[installs['Media Source'].isna() & installs['fb_Cost'].isna(), 'Media Source'] = 'Google'
installs.loc[installs['Media Source'].isna() & installs['google_Cost'].isna(), 'Media Source'] = 'Facebook'


print(installs)
#install.groupby(['aps_install_date','contributor_campaign']).['fb_Clicks', 'fb_Impressions', 'fb_Cost'].sum().reset_index


#installs = installs.drop(['aps_campaign_group', 'aps_creative'], axis=1)
# Fill missing values for cost, clicks, impressions with 0
installs[['installs', 'VVmins', 'aps_install_date','aps_campaign_group', 'aps_creative', 'new_DUV', 'VVs', 'VVMins_7', 'new_DUV_7', 'VVs_7', 'fb_Cost', 'fb_Clicks', 'fb_Impressions', 'google_Cost', 'google_Clicks', 'google_Impressions' ]] = installs[['installs', 'VVmins', 'aps_install_date','aps_campaign_group', 'aps_creative', 'new_DUV', 'VVs', 'VVMins_7', 'new_DUV_7', 'VVs_7', 'fb_Cost', 'fb_Clicks', 'fb_Impressions', 'google_Cost', 'google_Clicks', 'google_Impressions' ]].fillna(0)
# Step 3: Campaign Decoding
print(installs)
def extract_platform(campaign):
    platforms = {'_WAP_': 'Wap', '_DES_': 'Desktop', '_AND_': 'Android', '_iOS_': 'iOS', '_TAB_': 'Tablet'}
    for code, name in platforms.items():
        if code in campaign:
            return name
    return 'Unknown'

def extract_country(campaign):
    countries = {'ID_': 'ID', 'MY_': 'MY'}
    for code, name in countries.items():
        if campaign.startswith(code):
            return name
    return 'Unknown'

def extract_campaign_type(campaign):
    types = {'_ACQ_': 'Acquisition', '_RET_': 'Retargeting'}
    for code, name in types.items():
        if code in campaign:
            return name
    return 'Unknown'

def extract_campaign_attribute(campaign):
    attributes = {'_AVOD': 'AVOD', '_SVOD': 'SVOD', '_Branding_': 'Branding'}
    for code, name in attributes.items():
        if code in campaign:
            return name
    return 'Unknown'

installs['Platform'] = installs['contributor_campaign'].apply(extract_platform)
installs['Country'] = installs['contributor_campaign'].apply(extract_country)
installs['Campaign Type'] = installs['contributor_campaign'].apply(extract_campaign_type)
installs['Campaign Attribute'] = installs['contributor_campaign'].apply(extract_campaign_attribute)
installs = installs[installs['Country'].isin(['MY', 'ID'])]
print(installs)
# installs['Media Source'] = 'Other'  # Default value if needed

# # Now update values based on contributor_source
# installs.loc[installs['contributor_source'].str.contains('facebook', case=False, na=False), 'Media Source'] = 'Facebook'
# installs.loc[installs['contributor_source'].str.contains('google', case=False, na=False), 'Media Source'] = 'Google'
# installs = installs.drop(['contributor_source'], axis=1)

other_cost['Campaigns of'] = other_cost['Campaigns of'].str.strip().str.upper()
installs['Country'] = installs['Country'].str.strip().str.upper()

# Step 4: Assign Cost, Clicks, Impressions
def assign_cost(row):
    if row['Media Source'] == 'Facebook':
        return row['fb_Cost'], row['fb_Clicks'], row['fb_Impressions']
    elif row['Media Source'] == 'Google':
        return row['google_Cost'], row['google_Clicks'], row['google_Impressions']
    else:
        partner_row = other_cost[other_cost['Campaigns of'] == row['Country']]
        if not partner_row.empty:
            cpi = partner_row['Cost per install (CPI)'].values[0]
            if pd.notnull(cpi):
                return cpi * row['installs'], 0, 0
            else:
                print(f"CPI is NaN for {row['Country']}")
                return 0, 0, 0
        else:
            print(f"No match found for {row['Country']}")
            return 0, 0, 0
# # Apply the function and get three columns
installs[['Total Spend', 'Total Clicks', 'Total Impressions']] = installs.apply(assign_cost, axis=1, result_type='expand')

installs = installs.merge(other_cost[['Campaigns of', 'Cost per install (CPI)']],
                          left_on='Country', right_on='Campaigns of', how='left')
print(installs)
installs = installs.groupby(['aps_install_date','contributor_campaign', 'aps_campaign_group', 'aps_creative','missing_campaign_flag','fb_Cost', 'fb_Clicks', 'fb_Impressions', 'google_Cost', 'google_Clicks', 'google_Impressions', 'Platform', 'Country', 'Campaign Type', 'Campaign Attribute', 'Media Source','Cost per install (CPI)'])[['installs', 'VVmins', 'new_DUV', 'VVs', 'VVMins_7', 'new_DUV_7', 'VVs_7']].sum().reset_index()

# 2. Set Total Spend, Total Clicks, Total Impressions in one go
installs['Total Spend'] = np.where(
    installs['Media Source'] == 'Facebook', installs['fb_Cost'],
    np.where(
        installs['Media Source'] == 'Google', installs['google_Cost'],
        installs['Cost per install (CPI)'] * installs['installs']
    )
)

installs['Total Clicks'] = np.where(
    installs['Media Source'] == 'Facebook', installs['fb_Clicks'],
    np.where(
        installs['Media Source'] == 'Google', installs['google_Clicks'],
        0
    )
)

installs['Total Impressions'] = np.where(
    installs['Media Source'] == 'Facebook', installs['fb_Impressions'],
    np.where(
        installs['Media Source'] == 'Google', installs['google_Impressions'],
        0
    )
)

# Remove invalid installs and costs
 #installs = installs[installs['Total Spend'] >= 0]

# # Step 4: Derived KPIs
installs['CPI_Overall'] = np.where(installs['installs'] > 0, installs['Total Spend'] / installs['installs'], np.nan)

# # True CPI (only for matched campaigns)
installs['CPI_True'] = np.where(
    installs['missing_campaign_flag'] == 'Matched',
    np.where(installs['installs'] > 0, installs['Total Spend'] / installs['installs'], np.nan),
    np.nan
)
installs['CTR'] = installs.apply(lambda x: (x['Total Clicks'] / x['Total Impressions']) if x['Total Impressions'] > 0 else None, axis=1)
installs['Install Rate'] = installs.apply(lambda x: (x['installs'] / x['Total Clicks']) if x['Total Clicks'] > 0 else None, axis=1)

# # Engagement KPIs
installs['Install_Day_Engagement_Rate'] = installs['new_DUV'] / installs['installs']
installs['Install_Day_Views_per_User'] = installs['VVs'] / installs['new_DUV']
installs['Retention_7Day_Rate'] = installs['new_DUV_7'] / installs['installs']
installs['Views_per_Viewer_7Day'] = installs['VVs_7'] / installs['new_DUV_7']
installs['Avg_WatchMins_per_User_7Day'] = installs['VVMins_7'] / installs['installs']
installs['Avg_WatchMins_per_Viewer_7Day'] = installs['VVMins_7'] / installs['new_DUV_7']

# Final clean up: replace inf/nan
installs.replace([float('inf'), -float('inf')], 0, inplace=True)
installs.fillna(0, inplace=True)
#Export final cleaned data
installs.drop_duplicates(inplace=True)
print(installs)
cols_to_round = ['Total Spend', 'Total Clicks', 'Total Impressions', 'CPI_True', 'CPI_Overall', 'CTR', 'Install Rate', 'Install_Day_Engagement_Rate', 'Install_Day_Views_per_User', 'Retention_7Day_Rate', 'Views_per_Viewer_7Day', 'Avg_WatchMins_per_User_7Day', 'Avg_WatchMins_per_Viewer_7Day']
installs[cols_to_round] = installs[cols_to_round].round(2)
installs = installs[(installs['aps_install_date'] >= '2021-03-01') & (installs['aps_install_date'] <= '2021-03-05')]
installs.to_csv('C:/Users/6362785/FINAL_DATA.csv', index=False)



installs.to_csv('C:/Users/6362785/FINAL_DATA.csv', index=False)