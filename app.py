import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="Crime in Netherlands", page_icon="💀", layout="centered")

def load_data():
    df = pd.read_csv("250111_CLEAN_murders_NL.csv")
    return df

def main():
    df = load_data()

    # ------------------------------------------------------------------
    # Preprocess data for the Overall Trend and Yearly Statistics
    # ------------------------------------------------------------------
    # Keep only totals for sex == 'Total male and female' and 'Characteristics Label' == 'Total'
    yearly_totals = df[
        (df['Sex Label'] == 'Total male and female') &
        (df['Characteristics Label'] == 'Total')
    ].copy()

    # Rename columns and ensure Year is integer
    yearly_totals['Period Label'] = yearly_totals['Period Label'].astype(int)
    yearly_totals.sort_values(by='Period Label', inplace=True)
    yearly_totals.rename(columns={
        'Period Label': 'Year',
        'VictimsMurderManslaughter_1': 'Victims',
        'VictimsMurderManslaughterRelative_2': 'RatePerMillion'
    }, inplace=True)

    # ------------------------------------------------------------------
    # SECTION 1: Overall Trend and Yearly Statistics (NO Year Selection)
    # ------------------------------------------------------------------
    st.title("Crime in NL (Murders) from 1996 - 2023")
    st.header("Overall trend")

    chart_choice = st.radio(
        "Select which metric(s) to display:",
        ("Total victims", "Rate per million", "Both")
    )

    # Base line chart
    base_chart = alt.Chart(yearly_totals).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year')
    )

    layers = []
    if chart_choice in ("Total victims", "Both"):
        line_victims = base_chart.encode(
            y=alt.Y('Victims:Q', title='Number of victims'),
            color=alt.value('#8884d8'),
            tooltip=[alt.Tooltip('Year:O'), alt.Tooltip('Victims:Q')]
        ).properties(title="Total victims")
        layers.append(line_victims)

    if chart_choice in ("Rate per million", "Both"):
        line_rate = base_chart.encode(
            y=alt.Y('RatePerMillion:Q', title='Rate per million'),
            color=alt.value('#82ca9d'),
            tooltip=[alt.Tooltip('Year:O'), alt.Tooltip('RatePerMillion:Q')]
        ).properties(title="Rate per million")
        layers.append(line_rate)

    if layers:
        combined_chart = alt.layer(*layers).resolve_scale(y='independent').properties(
            width='container',
            height=400
        )
        st.altair_chart(combined_chart, use_container_width=True)

    # ------------------------------------------------------------------
    # SECTION intro: insights
    # ------------------------------------------------------------------
    st.header("Insights from dataset")
    st.markdown("""
        Based on the data analysis of murder and manslaughter cases in the Netherlands from 1996 to 2023, there has been a significant overall decline in both total victims and rate per million inhabitants. 
                
        The numbers dropped from a peak of 264 victims (16.5 per million) in 2001 to 125 victims (7.0 per million) in 2023, representing nearly a 53% decrease.

        Stabbing has consistently been the most common method, while private residences remain the primary location for these incidents.

        Age-wise, victims between 20-49 years have been most affected throughout the period, though the proportion of elderly victims (60+ years) has shown concerning increases in recent years.

        There's also a persistent gender disparity, with males consistently representing the majority of victims, though the gap has narrowed somewhat in recent years.
    """)

    # ------------------------------------------------------------------
    # SECTION 2: Detailed Statistics (BY YEAR)
    # ------------------------------------------------------------------
    st.header("Detailed statistics by year")

    all_years = sorted(yearly_totals['Year'].unique())
    selected_year = st.selectbox("Select year:", all_years, index=len(all_years) - 1)

    # Extract overall metrics for the selected year
    row_for_selected = yearly_totals[yearly_totals["Year"] == selected_year]
    if not row_for_selected.empty:
        year_victims = int(row_for_selected["Victims"].values[0])
        year_rate = float(row_for_selected["RatePerMillion"].values[0])
    else:
        year_victims = None
        year_rate = None

    # Compare to previous year
    row_for_previous = yearly_totals[yearly_totals["Year"] == (selected_year - 1)]
    comparison_text = "N/A"
    if not row_for_selected.empty and not row_for_previous.empty:
        prev_victims = row_for_previous["Victims"].values[0]
        if prev_victims != 0:
            change = ((year_victims - prev_victims) / prev_victims) * 100
            sign = "+" if change > 0 else ""
            comparison_text = f"{sign}{change:.1f}%"

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total victims", year_victims if year_victims is not None else "N/A")
    with col2:
        st.metric("Rate per million", f"{year_rate:.1f}" if year_rate is not None else "N/A")
    with col3:
        st.metric("Compared to previous year", comparison_text)

    # Breakdown bar charts for the selected year
    df_year = df[df["Period Label"] == selected_year]

    # 1) Murder Methods
    df_methods = df_year[
        (df_year["Sex Label"] == "Total male and female") &
        (df_year["Characteristics Label"].str.contains("Method:"))
    ].copy()
    df_methods["Method"] = df_methods["Characteristics Label"].str.replace("Method:", "").str.strip()

    # 2) Victims by Age Group
    df_age = df_year[
        (df_year["Sex Label"] == "Total male and female") &
        (df_year["Characteristics Label"].str.contains("Age:"))
    ].copy()
    df_age["AgeGroup"] = df_age["Characteristics Label"].str.replace("Age:", "").str.strip()

    # 3) Murder Locations
    df_location = df_year[
        (df_year["Sex Label"] == "Total male and female") &
        (df_year["Characteristics Label"].str.contains("Location:"))
    ].copy()
    df_location["Location"] = df_location["Characteristics Label"].str.replace("Location:", "").str.strip()

    # 4) Victims by Gender
    df_gender = df_year[
        (df_year["Characteristics Label"] == "Total") &
        (df_year["Sex Label"] != "Total male and female")
    ].copy()

    st.subheader(f"Breakdown for {selected_year}")
    # Methods
    if not df_methods.empty:
        st.caption("Murder methods")
        c_meth = alt.Chart(df_methods).mark_bar().encode(
            y=alt.Y("Method:N", sort="-x", title="method"),
            x=alt.X("VictimsMurderManslaughter_1:Q", title="victims"),
            tooltip=["Method:N", "VictimsMurderManslaughter_1:Q"]
        ).properties(width="container", height=300)
        st.altair_chart(c_meth, use_container_width=True)

    # Age
    if not df_age.empty:
        st.caption("Victims by age group")
        c_age = alt.Chart(df_age).mark_bar().encode(
            y=alt.Y("AgeGroup:N", sort="-x", title="age group"),
            x=alt.X("VictimsMurderManslaughter_1:Q", title="victims"),
            tooltip=["AgeGroup:N", "VictimsMurderManslaughter_1:Q"]
        ).properties(width="container", height=300)
        st.altair_chart(c_age, use_container_width=True)

    # Location
    if not df_location.empty:
        st.caption("Murder locations")
        c_loc = alt.Chart(df_location).mark_bar().encode(
            y=alt.Y("Location:N", sort="-x", title="location"),
            x=alt.X("VictimsMurderManslaughter_1:Q", title="victims"),
            tooltip=["Location:N", "VictimsMurderManslaughter_1:Q"]
        ).properties(width="container", height=300)
        st.altair_chart(c_loc, use_container_width=True)

    # Gender
    if not df_gender.empty:
        st.caption("Victims by gender")
        c_gen = alt.Chart(df_gender).mark_bar().encode(
            y=alt.Y("Sex Label:N", sort="-x", title="gender"),
            x=alt.X("VictimsMurderManslaughter_1:Q", title="victims"),
            tooltip=["Sex Label:N", "VictimsMurderManslaughter_1:Q"]
        ).properties(width="container", height=300)
        st.altair_chart(c_gen, use_container_width=True)

    # ------------------------------------------------------------------
    # SECTION 3: Detailed View (All Years) -- Now with Year on X-axis
    # and a toggle (raw vs. 100%) for each of the four metrics
    # ------------------------------------------------------------------
    st.header("Detailed view (all years)")

    bar_chart_type = st.radio(
        "Select bar chart view type:",
        ("Percentage of total", "Totals"),  # Swapped order to make percentage default
    )
    stack_type = None if bar_chart_type == "Totals" else "normalize"

    # 1) Methods
    df_methods_all = df[
        (df['Sex Label'] == 'Total male and female') &
        (df['Characteristics Label'].str.contains('Method:'))
    ].copy()
    df_methods_all["Year"] = df_methods_all["Period Label"].astype(int)
    df_methods_all["Method"] = df_methods_all["Characteristics Label"].str.replace("Method:", "").str.strip()

    c_methods_all = alt.Chart(df_methods_all).mark_bar().encode(
        x=alt.X("Year:O", title="Year", sort=[]),
        y=alt.Y("VictimsMurderManslaughter_1:Q", stack=stack_type, title="Victims"),
        color=alt.Color("Method:N", legend=alt.Legend(title="Method")),
        tooltip=[alt.Tooltip("Year:O"), alt.Tooltip("Method:N"), alt.Tooltip("VictimsMurderManslaughter_1:Q")]
    ).properties(width="container", height=300, title="Murder Methods Over Years")

    st.altair_chart(c_methods_all, use_container_width=True)

    # 2) Age Groups
    df_age_all = df[
        (df['Sex Label'] == 'Total male and female') &
        (df['Characteristics Label'].str.contains('Age:'))
    ].copy()
    df_age_all["Year"] = df_age_all["Period Label"].astype(int)
    df_age_all["AgeGroup"] = df_age_all["Characteristics Label"].str.replace("Age:", "").str.strip()

    c_age_all = alt.Chart(df_age_all).mark_bar().encode(
        x=alt.X("Year:O", title="Year", sort=[]),
        y=alt.Y("VictimsMurderManslaughter_1:Q", stack=stack_type, title="Victims"),
        color=alt.Color("AgeGroup:N", legend=alt.Legend(title="Age Group")),
        tooltip=[alt.Tooltip("Year:O"), alt.Tooltip("AgeGroup:N"), alt.Tooltip("VictimsMurderManslaughter_1:Q")]
    ).properties(width="container", height=300, title="Victims by Age Group Over Years")

    st.altair_chart(c_age_all, use_container_width=True)

    # 3) Locations
    df_loc_all = df[
        (df['Sex Label'] == 'Total male and female') &
        (df['Characteristics Label'].str.contains('Location:'))
    ].copy()
    df_loc_all["Year"] = df_loc_all["Period Label"].astype(int)
    df_loc_all["Location"] = df_loc_all["Characteristics Label"].str.replace("Location:", "").str.strip()

    c_loc_all = alt.Chart(df_loc_all).mark_bar().encode(
        x=alt.X("Year:O", title="Year", sort=[]),
        y=alt.Y("VictimsMurderManslaughter_1:Q", stack=stack_type, title="Victims"),
        color=alt.Color("Location:N", legend=alt.Legend(title="Location")),
        tooltip=[alt.Tooltip("Year:O"), alt.Tooltip("Location:N"), alt.Tooltip("VictimsMurderManslaughter_1:Q")]
    ).properties(width="container", height=300, title="Murder Locations Over Years")

    st.altair_chart(c_loc_all, use_container_width=True)

    # 4) Gender
    df_gender_all = df[
        (df['Characteristics Label'] == 'Total') &
        (df['Sex Label'] != 'Total male and female')
    ].copy()
    df_gender_all["Year"] = df_gender_all["Period Label"].astype(int)

    c_gen_all = alt.Chart(df_gender_all).mark_bar().encode(
        x=alt.X("Year:O", title="Year", sort=[]),
        y=alt.Y("VictimsMurderManslaughter_1:Q", stack=stack_type, title="Victims"),
        color=alt.Color("Sex Label:N", legend=alt.Legend(title="Gender")),
        tooltip=[alt.Tooltip("Year:O"), alt.Tooltip("Sex Label:N"), alt.Tooltip("VictimsMurderManslaughter_1:Q")]
    ).properties(width="container", height=300, title="Victims by Gender Over Years")

    st.altair_chart(c_gen_all, use_container_width=True)

    # Gender Trend Over Time
    # Empty line to maintain spacing with chart title in properties below
    # Filter to totals for characteristics label = 'Total' but separate male/female
    df_g = df[
        (df['Characteristics Label'] == 'Total') &
        (df['Sex Label'] != 'Total male and female')
    ].copy()
    df_g["Year"] = df_g["Period Label"].astype(int)

    # Summarize total victims by Year and Gender
    grouped_gender = df_g.groupby(["Year", "Sex Label"])["VictimsMurderManslaughter_1"].sum().reset_index()

    # Create a line chart that color-codes by gender
    c_gender_trend = alt.Chart(grouped_gender).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("VictimsMurderManslaughter_1:Q", title="Number of Victims"),
        color=alt.Color("Sex Label:N", title="Gender"),
        tooltip=["Year", "Sex Label", "VictimsMurderManslaughter_1"]
    ).properties(width="container", height=400)

    st.altair_chart(c_gender_trend, use_container_width=True)

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    st.markdown(
        'Made by [Valentin Mendez](https://www.linkedin.com/in/valentemendez/) using information from the [CBS StatLine](https://opendata.cbs.nl/statline/portal.html?_la=en&_catalog=CBS&tableId=84726ENG&_theme=1152)'
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