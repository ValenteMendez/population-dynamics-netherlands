import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import datetime

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
    st.subheader("Population stats")
    
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

def create_prediction_chart(df: pd.DataFrame):
    # Get provinces data (excluding national data)
    provinces = df[df['Regions Label'].str.contains('\\(PV\\)')].copy()
    
    # Get the last year from historical data and create future years list
    last_historical_year = df['Periods Label'].max()
    future_years = list(range(last_historical_year + 1, last_historical_year + 11))
    
    # Create predictions for each province
    all_predictions = []
    
    for province in provinces['Regions Label'].unique():
        province_data = provinces[provinces['Regions Label'] == province].copy()
        
        # Prepare X (years) and y (population)
        X = province_data['Periods Label'].values.reshape(-1, 1)
        y = province_data['PopulationOn31December_20'].values
        
        # Create and fit polynomial model (degree=2 for curved predictions)
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Generate future predictions
        future_X = np.array(future_years).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        predictions = model.predict(future_X_poly)
        
        all_predictions.append(predictions)
    
    # Sum up all provincial predictions
    total_predictions = np.sum(all_predictions, axis=0)
    
    # Create the prediction chart
    fig = go.Figure()
    
    # Historical national data
    national_data = df[df['Regions Label'] == 'The Netherlands'].sort_values('Periods Label')
    
    # Add historical data
    fig.add_trace(go.Scatter(
        x=national_data['Periods Label'],
        y=national_data['PopulationOn31December_20'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='rgb(0, 123, 255)'),
        hovertemplate='Year: %{x}<br>Population: %{y:,.0f}<extra></extra>'
    ))
    
    # Add prediction line
    fig.add_trace(go.Scatter(
        x=future_years,
        y=total_predictions,
        mode='lines+markers',
        name='Prediction',
        line=dict(color='rgb(255, 99, 132)', dash='dash'),
        hovertemplate='Year: %{x}<br>Population: %{y:,.0f}<extra></extra>'
    ))
    
    # Add confidence interval with no hover info
    confidence_x = future_years + future_years[::-1]
    confidence_y = np.concatenate([total_predictions * 1.05, (total_predictions * 0.95)[::-1]])
    fig.add_trace(go.Scatter(
        x=confidence_x,
        y=confidence_y,
        fill='toself',
        fillcolor='rgba(255, 99, 132, 0.2)',
        line=dict(color='rgba(255, 99, 132, 0)'),
        name='Confidence Interval',
        showlegend=True,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title='Population Projection for the Netherlands',
        xaxis_title='Year',
        yaxis_title='Population',
        yaxis=dict(tickformat=','),
        hovermode='x unified',
        height=600
    )
    
    return fig

def create_provincial_prediction_chart(df: pd.DataFrame, selected_provinces):
    fig = go.Figure()
    
    # Get the last year from historical data and create future years list
    last_historical_year = df['Periods Label'].max()
    future_years = list(range(last_historical_year + 1, last_historical_year + 11))
    
    for province in selected_provinces:
        # Get historical data for the province
        province_data = df[df['Regions Label'] == province].sort_values('Periods Label')
        
        # Prepare data for prediction
        X = province_data['Periods Label'].values.reshape(-1, 1)
        y = province_data['PopulationOn31December_20'].values
        
        # Create and fit polynomial model
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Generate predictions
        future_X = np.array(future_years).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        predictions = model.predict(future_X_poly)
        
        # Add historical data
        fig.add_trace(go.Scatter(
            x=province_data['Periods Label'],
            y=province_data['PopulationOn31December_20'],
            mode='lines+markers',
            name=f'{province} (Historical)',
            hovertemplate='Year: %{x}<br>Population: %{y:,.0f}<extra></extra>'
        ))
        
        # Add prediction line
        fig.add_trace(go.Scatter(
            x=future_years,
            y=predictions,
            mode='lines+markers',
            name=f'{province} (Prediction)',
            line=dict(dash='dash'),
            hovertemplate='Year: %{x}<br>Population: %{y:,.0f}<extra></extra>'
        ))
    
    # Add shading to distinguish historical from predicted data
    fig.add_vrect(
        x0=last_historical_year,
        x1=max(future_years),
        fillcolor="rgba(128, 128, 128, 0.1)",
        layer="below",
        line_width=0,
        annotation_text="Predicted",
        annotation_position="top left",
    )
    
    fig.update_layout(
        title='Provincial Population Projections',
        xaxis_title='Year',
        yaxis_title='Population',
        yaxis=dict(tickformat=','),
        hovermode='x unified',
        height=600
    )
    
    return fig

def create_municipal_prediction_chart(df: pd.DataFrame, selected_municipalities):
    fig = go.Figure()
    
    # Get the last year from historical data and create future years list
    last_historical_year = df['Periods Label'].max()
    future_years = list(range(last_historical_year + 1, last_historical_year + 11))
    
    for municipality in selected_municipalities:
        # Get historical data for the municipality
        muni_data = df[df['Regions Label'] == municipality].sort_values('Periods Label')
        
        # Prepare data for prediction
        X = muni_data['Periods Label'].values.reshape(-1, 1)
        y = muni_data['PopulationOn31December_20'].values
        
        # Create and fit polynomial model
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Generate predictions
        future_X = np.array(future_years).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        predictions = model.predict(future_X_poly)
        
        # Add historical data
        fig.add_trace(go.Scatter(
            x=muni_data['Periods Label'],
            y=muni_data['PopulationOn31December_20'],
            mode='lines+markers',
            name=f'{municipality} (Historical)',
            hovertemplate='Year: %{x}<br>Population: %{y:,.0f}<extra></extra>'
        ))
        
        # Add prediction line
        fig.add_trace(go.Scatter(
            x=future_years,
            y=predictions,
            mode='lines+markers',
            name=f'{municipality} (Prediction)',
            line=dict(dash='dash'),
            hovertemplate='Year: %{x}<br>Population: %{y:,.0f}<extra></extra>'
        ))
    
    # Add shading to distinguish historical from predicted data
    fig.add_vrect(
        x0=last_historical_year,
        x1=max(future_years),
        fillcolor="rgba(128, 128, 128, 0.1)",
        layer="below",
        line_width=0,
        annotation_text="Predicted",
        annotation_position="top left",
    )
    
    fig.update_layout(
        title='Municipal Population Projections',
        xaxis_title='Year',
        yaxis_title='Population',
        yaxis=dict(tickformat=','),
        hovermode='x unified',
        height=600
    )
    
    return fig

def main():
    st.title('Population Dynamics in the Netherlands')
    
    # Modified view selector to use "Forecast" instead of "Prediction"
    view_type = st.radio("Select View", ["National", "Regional", "Forecast"], horizontal=True)
    
    if view_type == "Forecast":
        st.subheader("Population projections")
        st.markdown("""
        This projection is based on historical trends from provincial data and uses a polynomial regression model. 
        The prediction:
        - Aggregates individual predictions for each province
        - Shows a confidence interval (±5%)
        - Takes into account regional growth patterns
        
        **Note**: This is a simplified model for illustration. Actual population projections should consider many 
        additional factors such as:
        - Immigration policies
        - Economic conditions
        - Housing availability
        - Birth/death rates
        - Age distribution
        """)
        
        # Load data and create national prediction chart
        df = load_data()
        st.plotly_chart(create_prediction_chart(df), use_container_width=True)
        
        # Provincial comparison with specific defaults
        st.subheader("Provincial Comparisons")
        provinces = sorted(df[df['Regions Label'].str.contains('\\(PV\\)')]['Regions Label'].unique())
        default_provinces = [
            'Noord-Holland (PV)',
            'Zuid-Holland (PV)',
            'Fryslân (PV)'
        ]
        selected_provinces = st.multiselect(
            "Select provinces to compare",
            provinces,
            default=default_provinces
        )
        
        if selected_provinces:
            st.plotly_chart(create_provincial_prediction_chart(df, selected_provinces), use_container_width=True)
        else:
            st.info("Please select at least one province to see the comparison.")
        
        # Municipal comparison with specific defaults
        st.subheader("Municipal Comparisons")
        # Filter municipalities more carefully to avoid confusion with provinces
        municipalities = sorted(df[
            (~df['Regions Label'].str.contains('\\(', na=False)) &  # No parentheses (not a region/province)
            (df['Regions Label'] != 'The Netherlands') &  # Not the country
            (~df['Regions Label'].str.contains('\\(PV\\)', na=False))  # Not a province
        ]['Regions Label'].unique())
        
        search_term = st.text_input("Search municipalities")
        filtered_municipalities = [m for m in municipalities 
                                 if search_term.lower() in m.lower()] if search_term else municipalities
        
        default_municipalities = ['Amsterdam', 'Rotterdam', 'The Hague']
        selected_municipalities = st.multiselect(
            "Select municipalities to compare",
            filtered_municipalities,
            default=default_municipalities
        )
        
        if selected_municipalities:
            st.plotly_chart(create_municipal_prediction_chart(df, selected_municipalities), use_container_width=True)
        else:
            st.info("Please select at least one municipality to see the comparison.")
        
    else:
        # Only show General insights in National view
        if view_type == "National":
            st.subheader("General insights")
            st.markdown("The Netherlands has experienced significant demographic shifts from 2012 to 2023, with population growth increasingly driven by international migration rather than natural change."
                
                " A striking turning point occurred in 2022 when the country saw its first negative natural population change (-2,608) since records began, as deaths (170,112) exceeded births (167,504)."
                
                " This demographic milestone coincided with unprecedented levels of international migration, with net migration reaching +158,992 people in 2022. The trend continued into 2023 with an even larger natural population decline (-5,034) and record-high immigration levels. Municipal movements have remained relatively stable, suggesting internal population distribution patterns are consistent despite external pressures."
                
                " The population density has increased from 496 people/km² in 2012 to 529 people/km² in 2023, reflecting growing urbanization pressures. These trends indicate a fundamental shift in Dutch population dynamics, where future growth is becoming increasingly dependent on international migration to offset the declining natural population growth."
                )

        # Load data
        df = load_data()
        
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
        
        # Total Moves Chart with Components
        st.plotly_chart(create_total_moves_chart(data_to_plot),
                        use_container_width=True,
                        key="total_moves_chart")
        
        # Natural Change Chart
        st.plotly_chart(create_natural_change_chart(data_to_plot), 
                        use_container_width=True,
                        key="natural_change_chart")
        
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