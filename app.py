import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(page_title="Population Dynamics in the Netherlands", page_icon="👥", layout="wide")

# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv("250112_CLEAN_population_regional_NL.csv")
    return df[df['Sex Label'] == 'Total male and female']

def format_number(num: float) -> str:
    if pd.isna(num):
        return "N/A"
    return f"{int(num):,}"

def create_population_chart(data: pd.DataFrame, region_name: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Periods Label'],
        y=data['PopulationOn31December_20'],
        mode='lines+markers',
        name='Population',
        line=dict(width=2, color='rgb(0, 123, 255)')
    ))
    fig.update_layout(
        title=f'Population Growth ({region_name})',
        xaxis_title='Year',
        yaxis_title='Population',
        yaxis=dict(tickformat=','),
        hovermode='x unified',
        showlegend=False,
        height=600
    )
    return fig

def create_natural_change_chart(data: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data['Periods Label'],
        y=data['LiveBornChildren_3'],
        name='Births',
        marker_color='rgb(40, 167, 69)'  # Green
    ))
    fig.add_trace(go.Bar(
        x=data['Periods Label'],
        y=-data['Deaths_5'],
        name='Deaths',
        marker_color='rgb(220, 53, 69)'  # Red
    ))
    fig.add_trace(go.Scatter(
        x=data['Periods Label'],
        y=data['NaturalIncrease_7'],
        name='Natural change',
        line=dict(color='rgb(255, 165, 0)', width=2),  # Orange color
        mode='lines+markers'
    ))
    fig.update_layout(
        title='Natural Population Change',
        xaxis_title='Year',
        yaxis_title='Number of People',
        barmode='relative',
        yaxis=dict(tickformat=','),
        xaxis=dict(dtick=1),  # Show all years
        height=400
    )
    return fig

def create_total_moves_chart(data: pd.DataFrame):
    fig = go.Figure()
    
    # Total Arrivals and components
    fig.add_trace(go.Bar(
        x=data['Periods Label'],
        y=data['DueToImmigration_10'],
        name='International Immigration',
        marker_color='rgb(135, 206, 250)',  # Light blue
        offsetgroup=0
    ))
    fig.add_trace(go.Bar(
        x=data['Periods Label'],
        y=data['DueToIntermunicipalMoves_11'],
        name='Municipal Arrivals',
        marker_color='rgb(30, 144, 255)',  # Darker blue
        offsetgroup=0
    ))
    
    # Total Departures and components (negative values)
    fig.add_trace(go.Bar(
        x=data['Periods Label'],
        y=-data['DueToEmigrationIncludingAdministr_14'],
        name='International Emigration',
        marker_color='rgb(0, 51, 153)',  # Dark blue
        offsetgroup=1
    ))
    fig.add_trace(go.Bar(
        x=data['Periods Label'],
        y=-data['DueToIntermunicipalMoves_16'],
        name='Municipal Departures',
        marker_color='rgb(25, 25, 112)',  # Midnight blue
        offsetgroup=1
    ))
    
    # Balance line
    fig.add_trace(go.Scatter(
        x=data['Periods Label'],
        y=data['TotalArrivals_8'] - data['TotalDeparturesIncludingAdministra_12'],
        name='Net Flow',
        line=dict(color='rgb(255, 165, 0)', width=2),  # Orange
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='Population Flows',
        xaxis_title='Year',
        yaxis_title='Number of People',
        barmode='relative',
        yaxis=dict(tickformat=','),
        xaxis=dict(dtick=1),  # Show all years
        height=400
    )
    return fig

def display_metrics(year_data, prev_year_data, is_first_year=False):
    # Population and Density
    st.subheader("Population")
    
    # Total Population with density below
    pop_change = year_data['PopulationOn31December_20'] - prev_year_data['PopulationOn31December_20']
    pop_change_pct = (pop_change / prev_year_data['PopulationOn31December_20']) * 100
    st.metric(
        "Total Population",
        format_number(year_data['PopulationOn31December_20']),
        "-" if is_first_year else f"{format_number(pop_change)} ({pop_change_pct:.1f}%)"
    )
    st.markdown(
        f"<p style='font-size: 1rem; color: #666; margin-top: -1rem; margin-left: 1rem;'>{format_number(year_data['PopulationDensity_2'])} people/km²</p>",
        unsafe_allow_html=True
    )
    
    # Natural Change
    st.subheader("Natural change")
    col1, col2, col3 = st.columns(3)
    with col1:
        nat_change = year_data['NaturalIncrease_7'] - prev_year_data['NaturalIncrease_7']
        st.metric(
            "natural change",
            format_number(year_data['NaturalIncrease_7']),
            "-" if is_first_year else format_number(nat_change)
        )
    with col2:
        births_change = year_data['LiveBornChildren_3'] - prev_year_data['LiveBornChildren_3']
        st.metric(
            "births",
            format_number(year_data['LiveBornChildren_3']),
            "-" if is_first_year else format_number(births_change)
        )
    with col3:
        deaths_change = year_data['Deaths_5'] - prev_year_data['Deaths_5']
        st.metric(
            "deaths",
            format_number(year_data['Deaths_5']),
            "-" if is_first_year else format_number(deaths_change)
        )

    # Arrivals Section
    st.subheader("Population movement - people arriving")
    col1, col2, col3 = st.columns(3)
    with col1:
        arrivals_change = year_data['TotalArrivals_8'] - prev_year_data['TotalArrivals_8']
        st.metric(
            "total arrivals",
            format_number(year_data['TotalArrivals_8']),
            "-" if is_first_year else format_number(arrivals_change)
        )
    with col2:
        imm_change = year_data['DueToImmigration_10'] - prev_year_data['DueToImmigration_10']
        st.metric(
            "international immigration",
            format_number(year_data['DueToImmigration_10']),
            "-" if is_first_year else format_number(imm_change)
        )
    with col3:
        mun_arr_change = year_data['DueToIntermunicipalMoves_11'] - prev_year_data['DueToIntermunicipalMoves_11']
        st.metric(
            "municipal arrivals",
            format_number(year_data['DueToIntermunicipalMoves_11']),
            "-" if is_first_year else format_number(mun_arr_change)
        )

    # Departures Section
    st.subheader("Population movement - people leaving")
    col1, col2, col3 = st.columns(3)
    with col1:
        departures_change = year_data['TotalDeparturesIncludingAdministra_12'] - prev_year_data['TotalDeparturesIncludingAdministra_12']
        st.metric(
            "total departures",
            format_number(year_data['TotalDeparturesIncludingAdministra_12']),
            "-" if is_first_year else format_number(departures_change)
        )
    with col2:
        em_change = year_data['DueToEmigrationIncludingAdministr_14'] - prev_year_data['DueToEmigrationIncludingAdministr_14']
        st.metric(
            "international emigration",
            format_number(year_data['DueToEmigrationIncludingAdministr_14']),
            "-" if is_first_year else format_number(em_change)
        )
    with col3:
        mun_dep_change = year_data['DueToIntermunicipalMoves_16'] - prev_year_data['DueToIntermunicipalMoves_16']
        st.metric(
            "municipal departures",
            format_number(year_data['DueToIntermunicipalMoves_16']),
            "-" if is_first_year else format_number(mun_dep_change)
        )

    # Migration Balances
    st.subheader("Balances (net effect)")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_balance = year_data['TotalArrivals_8'] - year_data['TotalDeparturesIncludingAdministra_12']
        prev_total_balance = prev_year_data['TotalArrivals_8'] - prev_year_data['TotalDeparturesIncludingAdministra_12']
        balance_change = total_balance - prev_total_balance
        st.metric(
            "total movement balance",
            format_number(total_balance),
            "-" if is_first_year else format_number(balance_change)
        )
    with col2:
        int_balance = year_data['DueToImmigration_10'] - year_data['DueToEmigrationIncludingAdministr_14']
        prev_int_balance = prev_year_data['DueToImmigration_10'] - prev_year_data['DueToEmigrationIncludingAdministr_14']
        int_balance_change = int_balance - prev_int_balance
        st.metric(
            "international migration balance",
            format_number(int_balance),
            "-" if is_first_year else format_number(int_balance_change)
        )
    with col3:
        mun_balance = year_data['DueToIntermunicipalMoves_11'] - year_data['DueToIntermunicipalMoves_16']
        prev_mun_balance = prev_year_data['DueToIntermunicipalMoves_11'] - prev_year_data['DueToIntermunicipalMoves_16']
        mun_balance_change = mun_balance - prev_mun_balance
        st.metric(
            "municipal migration balance",
            format_number(mun_balance),
            "-" if is_first_year else format_number(mun_balance_change)
        )

def main():
    st.title('Population Dynamics in the Netherlands')

    st.subheader("General insights")
    st.markdown("The Netherlands has experienced significant demographic shifts from 2012 to 2023, with population growth increasingly driven by international migration rather than natural change."
            
            "A striking turning point occurred in 2022 when the country saw its first negative natural population change (-2,608) since records began, as deaths (170,112) exceeded births (167,504)."
            
            "This demographic milestone coincided with unprecedented levels of international migration, with net migration reaching +158,992 people in 2022. The trend continued into 2023 with an even larger natural population decline (-5,034) and record-high immigration levels. Municipal movements have remained relatively stable, suggesting internal population distribution patterns are consistent despite external pressures."
            
            "The population density has increased from 496 people/km² in 2012 to 529 people/km² in 2023, reflecting growing urbanization pressures. These trends indicate a fundamental shift in Dutch population dynamics, where future growth is becoming increasingly dependent on international migration to offset the declining natural population growth."
            )

    # Load data
    df = load_data()
    
    # View selector
    view_type = st.radio("Select View", ["National", "Regional"], horizontal=True)
    
    if view_type == "National":
        data_to_plot = df[df['Regions Label'] == 'The Netherlands'].sort_values('Periods Label')
        region_name = "The Netherlands"
    else:
        # Region type selector
        region_type = st.selectbox(
            "Select Region Level",
            ["Landsdelen (LD)", "Provinces (PV)", "COROP Regions (CR)", "Municipalities"]
        )
        
        # Filter regions based on type
        if region_type == "Municipalities":
            regions = df[~df['Regions Label'].str.contains('\\(') & 
                       (df['Regions Label'] != 'The Netherlands')]
            search_term = st.text_input("Search municipality")
            filtered_regions = [r for r in sorted(regions['Regions Label'].unique())
                              if search_term.lower() in r.lower()] if search_term else sorted(regions['Regions Label'].unique())
            selected_region = st.selectbox("Select Municipality", filtered_regions)
        else:
            type_code = region_type[-3:-1]
            regions = df[df['Regions Label'].str.contains(f'\\({type_code}\\)')]
            selected_region = st.selectbox(
                f"Select {region_type.split(' ')[0]}", 
                sorted(regions['Regions Label'].unique())
            )
        
        data_to_plot = df[df['Regions Label'] == selected_region].sort_values('Periods Label')
        region_name = selected_region
    
    # Population Development Chart
    st.plotly_chart(create_population_chart(data_to_plot, region_name), 
                    use_container_width=True, 
                    key="population_chart")
    
    # Natural Change Chart
    st.plotly_chart(create_natural_change_chart(data_to_plot), 
                    use_container_width=True,
                    key="natural_change_chart")
    
    # Total Moves Chart with Components
    st.plotly_chart(create_total_moves_chart(data_to_plot),
                    use_container_width=True,
                    key="total_moves_chart")
    
    # Year selector below charts
    available_years = sorted(data_to_plot['Periods Label'].unique(), reverse=True)
    selected_year = st.selectbox("Select year for detailed statistics", available_years)
    
    # Get selected year data and previous year for comparisons
    year_data = data_to_plot[data_to_plot['Periods Label'] == selected_year].iloc[0]
    
    # Handle case when previous year doesn't exist
    prev_year_df = data_to_plot[data_to_plot['Periods Label'] == selected_year - 1]
    if len(prev_year_df) > 0:
        prev_year_data = prev_year_df.iloc[0]
        # Display metrics with comparison
        display_metrics(year_data, prev_year_data, is_first_year=False)
    else:
        # Create a copy of current year data for comparison, setting all values to 0
        prev_year_data = year_data.copy()
        for col in prev_year_data.index:
            if isinstance(prev_year_data[col], (int, float)):
                prev_year_data[col] = 0
        
        st.warning(f"No data available for year {selected_year - 1}. Showing current year values without comparisons.")
        display_metrics(year_data, prev_year_data, is_first_year=True)

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    st.markdown(
        'Made by [Valentin Mendez](https://www.linkedin.com/in/valentemendez/) using information from the [CBS StatLine](https://opendata.cbs.nl/statline/portal.html?_la=en&_catalog=CBS&tableId=37259eng&_theme=1177)'
    )

    # Hide the "Made with Streamlit" footer
    hide_streamlit_style = """
    <style>
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()