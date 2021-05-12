#import libraries
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import plotly.express as px #maybe streamlit doesn't support plotly express ...

st.write("""
# The Effect of COVID-19 on Mental Health

Rates of anxiety and depression among adults were increasing before the outbreak of COVID. Causes of depression are often listed as some combination of isolation, poor habits, substance dependency, financial worry, and/or stressful life events. Thus, it makes sense that COVID and its after-effects acted as a sort of accelerant to what was already a national mental health crisis.

To begin the healing process, and offer the types of help and service that hard hit communities need, we first need to identify these hard hit demographics. With this as the motivation, we'll explore  and visualize the locations and demographics that were hardest hit with rising rates of anxiety and depression as a result of COVID-19.

""")

url = 'https://raw.githubusercontent.com/Magnus-PS/DATA-608/main/Indicators_of_Anxiety_or_Depression.csv'
df = pd.read_csv(url)

#-------------------------------------------------Initial Processing of Dataframe-----------------------------------------------#

#Drop impertinent columns
drop_cols = ['Phase','Time Period Start Date', 'Time Period End Date', 'Low CI', 'High CI', 'Confidence Interval', 'Quartile Range']
df = df.drop(columns=drop_cols)

#Filter Indicator feature for both Anxiety and Depressive disorder
df = df[df.Indicator == 'Symptoms of Anxiety Disorder or Depressive Disorder'] 

#Rename columns for easier access/ identification
df = df.rename(columns={'Time Period': 'Interval', 'Time Period Label': 'IntervalRange', 'Value': 'Rate'})

#Convert Interval column to type integer
df['Interval'] = pd.to_numeric(df['Interval'])

#Filter Interval feature for April thru December 2020
df = df[df.Interval <= 21]

#Drop repeat observations from Interval (where Value == NaN)
df = df.dropna()

#-------------------------------------------------Did not use BELOW-----------------------------------------------#

#Reorder so that Intervals are ascending and there are no repeat values:

##Create dictionary of NEW Interval:IntervalRange pairings
#uniqueInterval = print(list(df.IntervalRange.unique()))
#numInterval = list(range(len(df.IntervalRange.unique())))

#Use dictionary comprehension to convert lists to dictionary
#res = dict(zip(uniqueInterval, numInterval)) #uniqueInverval as key
#print(res)

#Renumber intervals based on IntervalRange
#df['Interval'] = [res[x] for x in df['IntervalRange']]

#-------------------------------------------------Did not use ABOVE-----------------------------------------------#

#-------------------------------------------------Processing Data for 1st Plot-----------------------------------------------#

#Prepare df2 for 1st plot (Group data)
drop_cols2 = ['Indicator', 'State']
df2 = df.drop(columns=drop_cols2)

#Simplify group labels (ie. 'By Race ...' = 'Race')
df2['Group'] = df2['Group'].replace(['By Race/Hispanic ethnicity'],'Race')
df2['Group'] = df2['Group'].replace(['By Age'],'Age')
df2['Group'] = df2['Group'].replace(['By Education'],'Education')
df2['Group'] = df2['Group'].replace(['By Sex'],'Sex')
#print(df2.Group.unique()) #verify

#Simplify Race subgroup labels (ie. 'Non-Hispanic white ...' --> 'White')
df2['Subgroup'] = df2['Subgroup'].replace(['Hispanic or Latino'],'Hispanic')
df2['Subgroup'] = df2['Subgroup'].replace(['Non-Hispanic white, single race'],'White')
df2['Subgroup'] = df2['Subgroup'].replace(['Non-Hispanic black, single race'],'Black')
df2['Subgroup'] = df2['Subgroup'].replace(['Non-Hispanic Asian, single race'],'Asian')
df2['Subgroup'] = df2['Subgroup'].replace(['Non-Hispanic, other races and multiple races'],'Other/Mixed')

#Simplify Education subgroup labels
df2['Subgroup'] = df2['Subgroup'].replace(['Less than a high school diploma'],'Less than High School')
df2['Subgroup'] = df2['Subgroup'].replace(['High school diploma or GED'],'High School')
df2['Subgroup'] = df2['Subgroup'].replace(["Some college/Associate's degree"],'Some College')
df2['Subgroup'] = df2['Subgroup'].replace(["Bachelor's degree or higher"],"Bachelor's or Higher")

#-------------------------------------------------1st Plot Input-----------------------------------------------#

#Read in user specified group (for 1st plot)
group = st.sidebar.radio("Select demographic data for the first plot:",('Age', 'Education', 'Race', 'Sex'))
st.sidebar.write('You selected:', group) #default: By Age
df_group = df2[df2.Group == group]

#-------------------------------------------------1st Plot Output-----------------------------------------------#

st.write("## Rate of Anxiety and Depressive Disorder by ", group)
fig = px.line(df_group, x='IntervalRange', y='Rate', color='Subgroup')
st.plotly_chart(fig)

st.write("*Note: data is from 2020. July 22 - Aug 18 excluded due to missing values.*")

#-------------------------------------------------Processing Data for 2nd Plot-----------------------------------------------#

#Filter for Group = State, National Estimate
desired_groups = ['National Estimate', 'By State']
df3 = df[df.Group.isin(desired_groups)]

#Prepare df3 for 2nd plot (State data)
drop_cols3 = ['Indicator', 'Group', 'Subgroup', 'Interval']
df3 = df3.drop(columns=drop_cols3)

#Rename United States --> National Average
df3['State'] = df3['State'].replace(['United States'],'National Average')

#State name tuple
state_names = ("Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming")

#-------------------------------------------------2nd Plot Input/Output-----------------------------------------------#

#Single state selector sidebar - not useful?
#state = st.sidebar.radio("Select the region for which you'd like to view state data for the second plot:",state_names)

state = st.sidebar.text_input("If you'd like to explore individual state data, enter the state whose data you'd like to explore for the second plot:")
if state in state_names:
    st.sidebar.write('You entered:', state)
    comp_list = [state, 'National Average']
    #df_state = df3[df3.State == state | df3.State == 'United States']
    df_state = df3[df3.State.isin(comp_list)]
    
    st.write("## Rate of Anxiety and Depressive Disorder for ", state)
    fig2 = px.line(df_state, x='IntervalRange', y='Rate', color='State')
    st.plotly_chart(fig2)

else:
    st.sidebar.write('Improper entry, please try again (ie. New York).')

#-------------------------------------------------Processing Data for 3rd Plot-----------------------------------------------#

#Region name tuple
region_names = ("Midwest", "Northeast", "Southeast", "Southwest", "West")

#-------------------------------------------------3rd Plot Input/Output-----------------------------------------------#

#Region selector sidebar
region = st.sidebar.radio("Select the region for which you'd like to view state data for the second plot:",region_names)
st.sidebar.write('You selected:', region) #default: MidWest

#Select states based on region
if region == 'Northeast':
    state_list = ["Connecticut", "Delaware", "Maine", "Maryland", "Massachusetts", "New Hampshire", "New Jersey", "New York", "Pennsylvania", "Rhode Island", "Vermont"]
elif region == 'Southeast':
    state_list = ["Alabama", "Arkansas", "Florida", "Georgia", "Kentucky", "Louisiana", "Mississippi", "North Carolina", "South Carolina", "Tennessee", "Virginia", "West Virginia"]
elif region == 'Southwest':
    state_list = ["Arizona", "New Mexico", "Oklahoma", "Texas"]
elif region == 'West':
    state_list = ["Alaska", "California", "Colorado", "Hawaii", "Idaho", "Montana", "Nevada", "Oregon", "Utah", "Washington", "Wyoming"]
else:
    state_list = ["Illinois", "Indiana", "Iowa", "Kansas", "Michigan", "Minnesota", "Missouri", "Nebraska", "North Dakota", "Ohio", "South Dakota", "Wisconsin"] #default: MidWest

#Subset based on all states in region
df_region = df3[df3.State.isin(state_list)]

#Create dataframe of average rates per state
avg_df = pd.DataFrame()
avg_df['State'] = state_list
seq = []

#Subset df_region based on each state in avg_df, sum the Rates, divide by 21 (the # of entries per State), and round to 2 places
for x in avg_df['State']:
    x_df = df_region[df_region['State'] == x]
    seq.append(round(sum(x_df['Rate']/21),2))

avg_df['Avg Rate'] = seq

#print(avg_df) #verify

#plot bar chart of average rates per state
st.write("## Rate of Anxiety and Depressive Disorder in the ", region)
fig3 = px.bar(avg_df, x='State', y="Avg Rate") #color="IntervalRange"
st.plotly_chart(fig3)




##Finalize: headers, transtions, sidebars, plots