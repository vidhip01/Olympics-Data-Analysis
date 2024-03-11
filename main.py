#importing libraries
import streamlit as st
import pandas as pd

import preprocessor , helper
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import plotly.figure_factory as ff
import scipy



# Load data from CSV files
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

# Preprocess data using a custom preprocessor
df = preprocessor.preprocess(df, region_df)

# Set up Streamlit sidebar and options
st.sidebar.title("Olympics Analysis")
st.sidebar.image("olympic_logo.png")

# Use a radio button to allow the user to select an analysis option
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# Check if the user selected 'Medal Tally' in the sidebar
if user_menu == 'Medal Tally':
    # Display relevant headers and options in the sidebar
    st.sidebar.header("Medal Tally")

    # Retrieve the list of years and countries for the user to choose from
    years, country = helper.country_year_list(df)

    # Allow the user to select a specific year and country from the sidebar
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    # Fetch the medal tally based on the user's selection
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Display the appropriate title based on the user's selection
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title("Overall Medal Tally of " + selected_country)
    elif selected_year != 'Overall' and selected_country != 'Overall':
        st.title("Medal Tally of " + selected_country + " in " + str(selected_year) + " Olympics")

    # Display the fetched medal tally in a table
    st.table(medal_tally)

#if the user selected 'Overall Analysis' in the sidebar
elif user_menu == 'Overall Analysis':
    # Calculate various statistics based on the entire dataset
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    # Display a title for this analysis
    st.title("Top Statistics")

    # Use st.columns to arrange the statistics in three columns
    col1, col2, col3 = st.columns(3)

    # Display statistics in the first column
    with col1:
        st.header("Editions")
        st.title(editions)

    # Display statistics in the second column
    with col2:
        st.header("Hosts")
        st.title(cities)

    # Display statistics in the third column
    with col3:
        st.header("Sports")
        st.title(sports)

    # Create another set of three columns for additional statistics
    col1, col2, col3 = st.columns(3)

    # Display additional statistics in the first column
    with col1:
        st.header("Events")
        st.title(events)

    # Display additional statistics in the second column
    with col2:
        st.header("Nations")
        st.title(nations)

    # Display additional statistics in the third column
    with col3:
        st.header("Athletes")
        st.title(athletes)

    # Visualize participating nations over the years
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x="Edition", y="region")
    st.title("Participating Nations over the years")
    st.plotly_chart(fig)

    # Visualize events over the years
    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x="Edition", y="Event")
    st.title("Events over the years")
    st.plotly_chart(fig)

    # Visualize athletes over the years
    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x="Edition", y="Name")
    st.title("Athletes over the years")
    st.plotly_chart(fig)

    # Visualize the number of events over time for every sport using a heatmap
    st.title("No. of events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
        annot=True
    )
    st.pyplot(fig)

    #Suuccessful athletes analysis
    st.title("Most Successful Athletes")
    sport_list= df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')

    selected_sport= st.selectbox('Select a Sport', sport_list)
    x=helper.most_successful(df, selected_sport)
    st.table(x)


#yearwise graph

elif user_menu=='Country-wise Analysis':

    st.sidebar.title("Country-Wise Anlaysis")
    country_list= df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country= st.sidebar.selectbox('Select a country',country_list)

    country_df=helper.yearwise_medal_tally(df,selected_country)
    fig=px.line(country_df, x="Year",y="Medal")
    st.title(selected_country+ " Medal Tally over the years")
    st.plotly_chart(fig)

    st.title(selected_country + " excels in the following sports")
    pt= helper.country_event_heatmap(df,selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt,annot=True)
    st.pyplot(fig)

    st.title("Top 10 athletes of "+ selected_country)
    top10_df= helper.most_successful_country_wise(df, selected_country)
    st.table(top10_df)

elif user_menu == 'Athlete-wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],show_hist=False, show_rug=False)
    fig.update_layout(autosize=False,width=1000,height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                   'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                  'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                   'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                    'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                      'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df= helper.weight_v_height(df,selected_sport)
    fig,ax= plt.subplots()
    ax= sns.scatterplot(x=temp_df['Weight'],y= temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'],s=60)

    st.pyplot(fig)

    st.title("Men vs Women Participation over the years")
    final= helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)










