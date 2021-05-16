#import libraries
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px #maybe streamlit doesn't support plotly express ...
plotly.__version.__

#Introduction (main section)
st.write("""
# The Effect of COVID-19 on Mental Health

## Introduction

Rates of anxiety and depression among adults were increasing before the outbreak of COVID. Causes of depression are often listed as some combination of isolation, poor habits, substance dependency, financial worry, and/or stressful life events. Thus, it makes sense that COVID and its after-effects acted as a sort of accelerant to what was already a national mental health crisis.

To begin the healing process, and offer the types of help and service that hard hit communities need, we first need to identify where and with whom help is most needed. 

With this as the motivation, we'll explore the effect of COVID 19 on mental health at a regional, state, and demographic level using CDC data from April 23 - December 21 of 2020 (excluding July 22 - Aug 18 due to missing values).
""")

#Instructions (sidebar)
st.sidebar.write("""
### Instructions

Adjust the inputs below to see the effect of COVID on mental health at a regional, state, and demographic level.

""")

#Image (sidebar)
st.sidebar.image('https://images.unsplash.com/photo-1569437061241-a848be43cc82?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80')

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

#-------------------------------------------------Processing Data for 1st and 2nd Plot-----------------------------------------------#

#Filter for Group = State, National Estimate
desired_groups = ['National Estimate', 'By State']
df1 = df[df.Group.isin(desired_groups)]

#Prepare df3 for 2nd plot (State data)
drop_cols1 = ['Indicator', 'Group', 'Subgroup', 'Interval']
df1 = df1.drop(columns=drop_cols1)

#Rename United States --> National Average
df1['State'] = df1['State'].replace(['United States'],'National Average')

#State name tuple
state_names = ("Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming")

#Region name tuple
region_names = ("Midwest", "Northeast", "Southeast", "Southwest", "West")

#-------------------------------------------------1st Plot Input/Output-----------------------------------------------#

#Region selector sidebar
region = st.sidebar.radio("Select the region for which you'd like to view the average rate of anxiety and depressive disorder in the 1st plot:",region_names)
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
df_region = df1[df1.State.isin(state_list)]

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

#Bar chart of average rates per state in region
st.write("## Average Rate of Anxiety and Depressive Disorder in the ", region)
fig1 = px.bar(avg_df, x='State', y="Avg Rate") #color="IntervalRange"
st.plotly_chart(fig1)

#-------------------------------------------------2nd Plot Input/Output-----------------------------------------------#

#Single state selector sidebar - not useful?
state = st.sidebar.text_input("The 2nd plot will only appear if a state is entered in grammatically correct form. If you'd like to explore individual state data, enter the state whose data you'd like to explore:")
if state in state_names:
    st.sidebar.write('You entered:', state)
    comp_list = [state, 'National Average']
    #df_state = df3[df3.State == state | df3.State == 'United States']
    df_state = df1[df1.State.isin(comp_list)]
    
    st.write("## Rate of Anxiety and Depressive Disorder for ", state)
    fig2 = px.line(df_state, x='IntervalRange', y='Rate', color='State')
    st.plotly_chart(fig2)

else:
    st.sidebar.write('Improper entry, please try again (ie. New York).')

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

#-------------------------------------------------Processing Data for 3rd Plot-----------------------------------------------#

#Prepare df2 (Group data)
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

#-------------------------------------------------3rd Plot Input-----------------------------------------------#

#Read in user specified group (for 1st plot)
group = st.sidebar.radio("For the 3rd plot, select the demographic data you'd like to explore:",('Age', 'Education', 'Race', 'Sex'))
st.sidebar.write('You selected:', group) #default: By Age
df_group = df2[df2.Group == group]

#-------------------------------------------------3rd Plot Output-----------------------------------------------#

st.write("## Rate of Anxiety and Depressive Disorder by ", group)
fig3 = px.line(df_group, x='IntervalRange', y='Rate', color='Subgroup')
st.plotly_chart(fig3)

#-------------------------------------------------Citations-----------------------------------------------#

#Cite myself as author
st.sidebar.markdown(' ')
st.sidebar.markdown('......................................................')
st.sidebar.markdown("*This app was built by Magnus Skonberg using Python and Streamlit.*")

#Cite data and academic motivational sources
st.markdown(' ')
st.markdown('.............................................................................................')
st.write("""
## References

This app was built with reference to:

* Centers for Disease Control and Prevention. (2021). **Indicators of Anxiety or Depression Based on Reported Frequency of Symptoms During Last 7 Days** [data]. Retrieved from: https://data.cdc.gov/NCHS/Indicators-of-Anxiety-or-Depression-Based-on-Repor/8pt5-q6wp
* Mental Health America. (2020). **The State of Mental Health in America** [report]. Retrieved from: https://www.mhanational.org/issues/state-mental-health-america

"""
)