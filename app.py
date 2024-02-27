# Streamlit live coding script
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy


st.image('./data/header.png', caption='green times ahead')





#whatever comes out of the function should be cached
@st.cache_data #this is a decorator
def load_data(path):
    df = pd.read_csv(path)
    return df


power_plants_ch_raw = load_data(path="./data/renewable_power_plants_CH_with_kan_code.csv") #wird in cache geladen
power_plants_ch = deepcopy(power_plants_ch_raw)   #erstelle copie weil die anderen daten im cache sind

# Add title and header
st.title("Analysis of Swiss renewable energy")
st.text("We are analysing four powerfull technolgies")

#'Bioenergy', 'Hydro', 'Solar', 'Wind']
col1, col2, col3, col4 = st.columns(4)
with col1:
   st.header("Bioenergy")
   st.image("./data/biogas.png")

with col2:
   st.header("Hydro")
   st.image("./data/hydro.png")

with col3:
   st.header("Solar")
   st.image("./data/solar.png")

with col4:
   st.header("Wind")
   st.image("./data/wind.png") 




# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=power_plants_ch) # this looks more nice
    #st.table(data=power_plants_ch)

# Setting up columns
left_column, right_column = st.columns([1,1])



# Sample Streamlit Map
st.subheader("See all these dots? Every dot generetas some renewable power")
cleaned_power_plants = power_plants_ch.dropna(subset=['lat', 'lon']) #there are empty rows - that need to be droped
locations_power_plants = cleaned_power_plants[['lat', 'lon']]
st.map(locations_power_plants) #st.map needs the lat and lon colomns to print the locations







#get all data from files:
import json
with open("./data/georef-switzerland-kanton.geojson", 'r') as file:
    geojson_swz = json.load(file)

#geojson_swz
    



#map df to geojson with this helper dict
canton_names = {
'TG':'Thurgau', 
'GR':'Graubünden', 
'LU':'Luzern', 
'BE':'Bern', 
'VS':'Valais',                
'BL':'Basel-Landschaft', 
'SO':'Solothurn', 
'VD':'Vaud', 
'SH':'Schaffhausen', 
'ZH':'Zürich', 
'AG':'Aargau', 
'UR':'Uri', 
'NE':'Neuchâtel', 
'TI':'Ticino', 
'SG':'St. Gallen', 
'GE':'Genève',
'GL':'Glarus', 
'JU':'Jura', 
'ZG':'Zug', 
'OW':'Obwalden', 
'FR':'Fribourg', 
'SZ':'Schwyz', 
'AR':'Appenzell Ausserrhoden', 
'AI':'Appenzell Innerrhoden', 
'NW':'Nidwalden', 
'BS':'Basel-Stadt'}
# Sample Choropleth mapbox using Plotly GO
st.subheader("Lets find out which canton produces most renewable Energy per year")
#df['kan_code'] = df['canton'].map(canton_numbers).astype(str)
power_plants_ch['kan_name'] = power_plants_ch['canton'].map(canton_names).astype(str)

fig = go.Figure(go.Choroplethmapbox(geojson=geojson_swz, locations=power_plants_ch['kan_name'], z=power_plants_ch['production'], featureidkey="properties.kan_name",
                                    colorscale="Viridis", zmin=1, zmax=3500,
                                    marker_opacity=0.5, marker_line_width=0.5,
                                    colorbar_title="Yearly production in [MWh]"))

fig.update_layout(mapbox_style="carto-positron",
                         mapbox_zoom=6,
                         mapbox_center = {"lat": 46.91562540363795, "lon": 8.075764708993756},
                         margin={"r": 0, "t": 0, "l": 0, "b": 0})

st.plotly_chart(fig)


st.subheader("What is going on in Ticino?")
only_TI_data = power_plants_ch[power_plants_ch['canton'] == "TI"]
only_TI_data_filtered = only_TI_data.groupby('energy_source_level_2')['production'].sum().reset_index()
# Scale the 'production' column by dividing by 1000 to convert to thousands [MWh]
only_TI_data_filtered['production'] = only_TI_data_filtered['production'] / 1000

# Create a bar plot
sources_TI = go.Figure(data=go.Bar(
    x=only_TI_data_filtered['energy_source_level_2'],  # 'energy' categories as x-axis
    y=only_TI_data_filtered['production'],  # Summed 'production' values as y-axis
    marker_color='indigo',  # Optional: customize the bar color
))
# Update layout for readability
sources_TI.update_layout(
    title="Yearly production per energy source",
    xaxis_title="Energy Source",
    yaxis_title="Yearly production in [GWh]",
    template="plotly_white",  # Optional: choose a template that fits your aesthetic preferences
    yaxis=dict(
        type="linear",  # Assuming you're using a linear scale; adjust as necessary
        tickformat='GWh')  # Use a comma as a thousand separator without any shorthand notation like 'k' for thousands

)
# Show the figure
st.plotly_chart(sources_TI)

#New Chapter Hydro Wins
st.subheader("Hydro wins! Lets see how many power stations this is")

hydro_data_in_TI = only_TI_data[only_TI_data['energy_source_level_2'] == 'Hydro']

st.dataframe(data=hydro_data_in_TI)

hydro_count = len(hydro_data_in_TI)
st.subheader(f"There are {hydro_count} Power Station in Ticin")





grouped_data = power_plants_ch.groupby('energy_source_level_2')['production'].sum().reset_index()
# Create a bar plot
compare_sources_fig = go.Figure(data=go.Bar(
    x=grouped_data['energy_source_level_2'],  # 'energy' categories as x-axis
    y=grouped_data['production'],  # Summed 'production' values as y-axis
    marker_color='indigo',  # Optional: customize the bar color
))
# Update layout for readability
compare_sources_fig.update_layout(
    title="Total Production by Energy Source",
    xaxis_title="Energy Source",
    yaxis_title="Yearly production in [MWh]",
    template="plotly_white",  # Optional: choose a template that fits your aesthetic preferences
)
# Show the figure
st.plotly_chart(compare_sources_fig)









st.subheader("Growth of installed Power output per Source ")
#save all possible energies into variable for radio etc
unique_energies = power_plants_ch["energy_source_level_2"].unique()

# Widgets: radio buttons / selection gets saved to variable
energy_choice = st.radio(
    label='Which Energy Source?', options=unique_energies)


 # Filter the DataFrame to only include rows for the current energy source
cum_energy = power_plants_ch[power_plants_ch['energy_source_level_2'] == energy_choice].copy()

# Convert 'commissioning_date' to datetime format (if not already done)
cum_energy['commissioning_date'] = pd.to_datetime(cum_energy['commissioning_date'])

# Extract the year from 'commissioning_date' and create a new column for it
cum_energy['year'] = cum_energy['commissioning_date'].dt.year

# Group by the new year column, sum the 'production' column, and reset index to flatten DataFrame
annual_production_sum = cum_energy.groupby('year')['production'].sum().reset_index()

# Calculate the cumulative sum of the annual production sums
annual_production_sum['cumulative_production'] = annual_production_sum['production'].cumsum()

# Proceed with plotting the cumulative annual production sum
fig_growth = go.Figure(data=go.Scatter(
            x=annual_production_sum['year'],  # Years as x-axis
            y=annual_production_sum['cumulative_production'],  # Cumulative production values as y-axis
            mode='lines+markers',  # Line chart with markers
            marker=dict(color='royalblue'),  # Customize marker color
            line=dict(color='royalblue')  # Customize line color
        ))

        # Dynamically update layout based on the energy source
fig_growth.update_layout(
            title=f"Cumulative Annual Production",
            xaxis_title="Year",
            yaxis_title="Yearly production in [MWh]",
            template="plotly_white"
        )
        
st.plotly_chart(fig_growth)