import streamlit as st
import pandas as pd
from pathlib import Path
import base64

#new_df = pd.read_csv('plants_data.csv')

with st.sidebar:
    page_chosen = st.radio(
        "MENU",
        ("Add Plant", "Log Care", 'View Schedule', 'Search', 'Track Growth') #menu options
    )


#background colors section

with open('sidebar.png', 'rb') as image:
    sidebar_data = base64.b64encode(image.read()).decode()

st.markdown(f"""
<style>
[data-testid="stSidebar"] {{
    background-image: url("data:image/png;base64,{sidebar_data}");
    background-size: cover;
    background-position: center;
}}
</style>
""", unsafe_allow_html=True)

with open('header.png', 'rb') as image:
    header_data = base64.b64encode(image.read()).decode()

st.markdown(f"""
<style>
[data-testid="stHeader"] {{
    background-image: url("data:image/png;base64,{header_data}");
    background-size: cover;
    background-position: center;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp {
    background-color: black;
    background-image: none;
}
</style>
""", unsafe_allow_html=True)
#-----------------------------------------------------------------------------------------------------------------------------

if 'plants' not in st.session_state: #plants is stored variable
    st.session_state.plants = pd.read_csv('plants_data.csv')

if 'care' not in st.session_state: 
    st.session_state.care = pd.read_csv('plants_log.csv') #reference to saved csv if session_state lacks data

plant_df = st.session_state.plants


if 'heights' not in st.session_state:
    if Path('plants_heights.csv').exists():
        st.session_state.heights = pd.read_csv('plants_heights.csv')
    else:
        st.session_state.heights = pd.DataFrame(columns=['Plant name', 'Date', 'Height', 'Expected Height'])


        
if page_chosen == 'Add Plant': #for Add Plant page
    st.title('Add Plant')

    plant_name = st.text_input('Plant Name', ' ')
    location = st.text_input('Location', ' ')
    date_acquired = st.date_input('Date Acquired (YYYY/MM/DD)', format="YYYY/MM/DD")
    watering_freq = st.number_input('Watering Frequency (Every x Days)', step = 1)
    sun_exposure = st.selectbox(
    'Sunlight Needs',
    ('Shaded', 'Semi-Shaded', 'Full Light Exposure')) #assumed requirements
    



    if st.button('Log Plant'):
        st.write('done')
        st.snow()
        
        new_row=pd.DataFrame({'Plant name':[plant_name], 'Location':[location], 'Date Acquired':[date_acquired], 'Watering Frequency':[watering_freq], 'Sun Exposure':[sun_exposure]})


        original_df = pd.read_csv('plants_data.csv')
        new_df = pd.concat([original_df, new_row], ignore_index = True)
        new_df.to_csv('plants_data.csv', index=False)
        new_df
        
#for log care page

if page_chosen == 'Log Care':
    st.title('Log Care')


    plant_treated = st.selectbox('Plant treated', plant_df['Plant name'], index=None)
    
    activity = st.selectbox('Logged Activity',
                            ('Watering', 'Repotting'))

    date_log = st.date_input('Date of Activity (YYYY/MM/DD)', format="YYYY/MM/DD")

    if st.button('Log Activity'):
        st.write('done')

        new_row=pd.DataFrame({'Plant Treated':[plant_treated], 'Activity':[activity], 'Date of Activity':[date_log]})


        original_df2 = pd.read_csv('plants_log.csv')
        new_df2 = pd.concat([original_df2, new_row], ignore_index = True)
        new_df2.to_csv('plants_log.csv', index=False)


#view schedule page

if page_chosen == 'View Schedule':
    st.title('View Schedule')

    schedule = []

    for i, plant in plant_df.iterrows():
        past_logs = st.session_state.care[
            (st.session_state.care['Plant Treated'] == plant['Plant name']) &
            (st.session_state.care['Activity'] == 'Watering')
        ]

        if len(past_logs) > 0:
            last_watered = pd.to_datetime(past_logs['Date of Activity']).max()
        else:
            last_watered = pd.to_datetime(plant['Date Acquired'])

        next_watering = last_watered + pd.Timedelta(days=int(plant['Watering Frequency'])) # reference to inputted freq

        if next_watering.date() <= pd.Timestamp.today().date():
            status = 'Due'
        else:
            status = 'Not Due'

        schedule.append([plant['Plant name'], next_watering.date(), status])

    schedule_df = pd.DataFrame(schedule, columns=['Plant name', 'Next Watering', 'Status'])
    st.dataframe(schedule_df)

if page_chosen == 'Search':
    st.title('Search')

    search = st.text_input('Search by plant name or location')
    plants = st.session_state.plants

    results = plants[
        plants['Plant name'].str.contains(search, case=False, regex=False) |#search by name
        plants['Location'].str.contains(search, case=False, regex=False) #search by location
    ]

    st.dataframe(results)

    st.write('Edit Plants')
    edited_df = st.data_editor(st.session_state.plants)

    if st.button('Save Edits'):
        st.session_state.plants = edited_df
        edited_df.to_csv('plants_data.csv', index=False)
        st.write('done')



# my innovative idea, growth tracker page
if page_chosen == 'Track Growth':
    st.title('Track Growth')

    plant_treated = st.selectbox('Choose Plant', plant_df['Plant name'], index=None)

    height = st.number_input('Current Height (cm)', min_value=0.0)
    expected_height = st.number_input('Expected Final Height (cm)', min_value=1.0)
    date_log = st.date_input('Date Measured')

    if st.button('Log Height'):
        new_row=pd.DataFrame({'Plant name':[plant_treated], 'Date':[date_log], 'Height':[height], 'Expected Height':[expected_height]})

        original_df = st.session_state.heights
        new_df = pd.concat([original_df, new_row], ignore_index=True)
        new_df.to_csv('plants_heights.csv', index=False)
        st.session_state.heights = new_df

        st.write('done')

    plant_heights = st.session_state.heights[
        st.session_state.heights['Plant name'] == plant_treated
    ].copy()

    st.dataframe(plant_heights)

    if len(plant_heights) > 0:
        plant_heights['Date'] = pd.to_datetime(plant_heights['Date'])
        plant_heights = plant_heights.sort_values('Date')

        st.write('Height Over Time')
        st.line_chart(plant_heights.set_index('Date')[['Height', 'Expected Height']])

        if len(plant_heights) > 1:
            plant_heights['Growth Rate'] = plant_heights['Height'].diff() / plant_heights['Date'].diff().dt.days

            st.write('Growth Rate (cm/day)')
            st.line_chart(plant_heights.set_index('Date')['Growth Rate'])

        
    

    
    

    



    
        

    
 