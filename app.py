#import libraries
import streamlit as st
import matplotlib.pyplot as plt
import time
import numpy as np
import pandas as pd
import pydeck as pdk
import pathlib
import streamlit as st


#Select box to select which plot do you want
add_selectbox = st.sidebar.selectbox(
    'What kind of plot do you want ?',
    ('-', 'Graph Plot', 'World map Plot')
    )


#initial selectbox
if(add_selectbox =='-'):
    st.sidebar.warning('Select a type of plot')
    st.title("COVID-19 Visualization App")
    st.markdown(
    """
    This is a project made by Jordan FLON , with the streamlit librairy,
    select the type of plot that you want in the scroll menu on the left
    """)


#graph plot (import the csv and the graph of the country selected, also the graph of the mortity in the country)
elif(add_selectbox=='Graph Plot'):
    st.title("COVID-19 Visualization App")
    st.header("Chart plot of the COVID-19 ")
    st.markdown(
    """
    This app displays the spread of the Coronavirus in select countries of the world.


    Select or deselect countries.
    """)

    # You can choose multiple countries, and what kind of data you want to display : Number of cases , number of death , number of recovered

    data = pd.read_csv('covid.csv')




    countries = st.multiselect(
    "Choose countries", list(data['Country/Region'].unique() ) , ['France']
)
    if not countries:
        st.error("Please select at least one country")


    st.markdown(
    """
    Choose what kind of data you want to display (Cases , Recoveries , Deaths).
    """)


    cases = st.checkbox('Cases' , value=True)
    recovered = st.checkbox("Recoveries")
    death = st.checkbox("Deaths")



    data['Date'] = pd.to_datetime(data['Date'])
    temporaire = data.groupby(['Country/Region','Date'])['Confirmed','Deaths','Recovered'].sum()
    temporaire = temporaire.reset_index()
    liste_date = temporaire[temporaire['Country/Region']=='Italy']['Date'][:]
    dico = {}

    titre = ''
    dico_morta = {}
    for city in countries:
        liste_valeur = np.array(temporaire[temporaire['Country/Region']==city]['Deaths'][:]  / temporaire[temporaire['Country/Region']==city]['Confirmed'][:]*100)
        liste_valeur = np.nan_to_num(liste_valeur)
        dico_morta[str(city) + ' Mortality' ] = np.array(liste_valeur)
        titre += ', ' +str(city) + ' '
        if cases:
            liste_valeur = temporaire[temporaire['Country/Region']==city]['Confirmed'][:]
            dico[str(city) + ' Cases' ] = np.array(liste_valeur)
        if recovered:
            liste_valeur = temporaire[temporaire['Country/Region']==city]['Recovered'][:]
            dico[str(city) + ' Recoveries' ] = np.array(liste_valeur)
        if death:
            liste_valeur = temporaire[temporaire['Country/Region']==city]['Deaths'][:]
            dico[str(city) + ' Deaths'] = np.array(liste_valeur)

    by = ''
    if cases :
        by += ', Cases '
    if recovered:
        by+= ', Recoveries '
    if death:
        by+= ', Deaths '

    if (len(by)> 0 and len(countries)>0 ):
        st.subheader("Line chart of  "+ titre[1:] + '|  by '+ by[1:])
        chart_data = pd.DataFrame(dico , index = liste_date)
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        last_rows = chart_data.head(1)
        chart = st.line_chart(last_rows)
        progress = np.linspace(0, 100, chart_data.shape[0])
        for i in range(1, chart_data.shape[0]):
            new_rows = chart_data.iloc[i:i+2, :]
            status_text.text("%i%% Complete" % int(round(progress[i])))
            chart.add_rows(new_rows)
            progress_bar.progress(int(round(progress[i])))
            time.sleep(0.05)
        progress_bar.empty()
        st.button("Re-run")
        st.header("Mortality of the COVID-19 in each country ")
        st.markdown(
        """
        The percentage of mortality is defined by the number of deaths divided by the number of cases in the country :

        $$
            Mortality = \\frac{Number \ of \ Deaths}{\\textit{Number \ of \ Cases}}
            $$
        """)
        st.subheader("Mortality in "+ titre[1:] )
        chart_morta = pd.DataFrame(dico_morta , index = liste_date)
        st.line_chart(chart_morta)




#plot the map with circle in each country that follows the number of cases , deaths or revoveries
elif(add_selectbox=='World map Plot'):
    st.title("COVID-19 Visualization App")
    st.header("Map plot of the COVID-19 ")
    st.markdown(
    """
    This app displays the spread of the Coronavirus in all the countries of the world on the map.
    """)

    data = pd.read_csv('covid.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    temporaire = data.groupby(['Country/Region' , 'Date'])['Confirmed','Deaths','Recovered'].sum()
    temporaire = temporaire.reset_index()
    d = data.groupby(['Country/Region', 'Lat' , 'Long' ])['Confirmed','Deaths','Recovered'].sum()
    d = d.reset_index()
    dico = {}
    Country = []
    lat = []
    long = []
    confirmed = []
    deaths = []
    recovered =[]
    for x in d['Country/Region'].unique():
        Country.append(x)
        temp = temporaire[temporaire['Country/Region']==x].iloc[-1,:]
        confirmed.append(temp['Confirmed'])
        deaths.append(temp['Deaths'])
        recovered.append(temp['Recovered'])
        lat.append(float(d[(d['Country/Region'] == x) &  (d['Confirmed'] == max(d[d['Country/Region'] == x]['Confirmed']))]['Lat']))
        long.append(float(d[(d['Country/Region'] == x) &  (d['Confirmed'] == max(d[d['Country/Region'] == x]['Confirmed']))]['Long']))

    dico['Country/Region'] = np.array(Country)
    dico['Confirmed'] = np.array(confirmed)
    dico['Deaths'] = np.array(deaths)
    dico['Recovered'] = np.array(recovered)
    dico['Lat'] = np.array(lat)
    dico['Long'] = np.array(long)

    df = pd.DataFrame(dico)
    st.subheader("World map of COVID-19 Cases")
    st.markdown(
    """
    The radius is proportional to the number of cases. (Put your mouse on a circle the exact number will be disp)
    """)
    st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
    latitude=46.227638,
    longitude=-2.213749,
    zoom=1,
    pitch=50,
    ),
    layers=[
     pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position="[Long,Lat]",
        get_radius="Confirmed*1.5",
        opacity=0.8,
        get_color='[200, 30, 0, 160]',
        elevation_scale=1,
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
     )],
     tooltip={"html": "<b>Number of Cases : </b> {Confirmed} <b> in </b> {Country/Region}", "style": {"color": "white"}},
    ))

    st.markdown(
    """
    Select / deselect if you want to display the world map of Recoveries or/and Deaths
    """)
    recovered = st.checkbox("Recoveries")
    death = st.checkbox("Deaths")


    if(death):
        st.subheader("World map of COVID-19 Deaths")
        st.markdown(
        """
        The radius is proportional to the number of Deaths. (Put your mouse on a circle the exact number will be disp)
        """)
        st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
        latitude=46.227638,
        longitude=-2.213749,
        zoom=1,
        pitch=50,
        ),
        layers=[
         pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position="[Long,Lat]",
            get_radius="Deaths*15",
            opacity=0.8,
            get_color='[200, 30, 0, 160]',
            elevation_scale=1,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
         )],
         tooltip={"html": "<b>Number of Deaths : </b> {Deaths} <b> in </b> {Country/Region}", "style": {"color": "white"}},
        ))

    if(recovered):
        st.subheader("""


        World map of COVID-19 Recoveries


        """)
        st.markdown(
        """
        The radius is proportional to the number of Recoveries. (Put your mouse on a circle the exact number will be disp)
        """)

        st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
        latitude=46.227638,
        longitude=-2.213749,
        zoom=1,
        pitch=50,
        ),
        layers=[
         pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position="[Long,Lat]",
            get_radius="Deaths*15",
            opacity=0.8,
            get_color='[200, 30, 0, 160]',
            elevation_scale=1,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
         )],
         tooltip={"html": "<b>Number of Recoveries : </b> {Recovered}  <b> in </b> {Country/Region}", "style": {"color": "white"}},
        ))
