#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import altair as alt
import matplotlib.pyplot as plt

#use config page
st.set_page_config(
    page_title="Automation_Analysis Dashboard",
    page_icon="🚕",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/automation-analysis-cleaned-dataset.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An error occured: {e}")

def create_sidebar_filters(df):
    st.sidebar.header("Automation filters")

    Make = st.sidebar.multiselect(
        "Select Make(s)",
        options=df['Make'].unique(),
        default=df['Make'].unique()
    )

    Condition = st.sidebar.multiselect(
        "Select Condition(s)",
        options=df['Condition'].unique(),
        default=df['Condition'].unique()
    )

    Transmission = st.sidebar.radio(
        "Select Transmission(s)",
        options=['All', 'Automatic', 'Manual'],
        index=0
    )

    return Make, Condition, Transmission

def  filter_data(df, Make, Condition, Transmission):
    filtered_df = df[df['Make'].isin(Make) & df['Condition'].isin(Condition)]
    if Transmission != "All":
        filtered_df = filtered_df[filtered_df['Transmission'] == Transmission]
    return filtered_df

def display_metrics(filtered_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🚕Total cars", len(filtered_df))

    with col2:
        avg_price = filtered_df['Price'].mean() if len(filtered_df) > 0 else 0
        st.metric("💲Average Price", f"₦{avg_price:,.2f}")

    with col3:
        top_brand = filtered_df['Make'].mode()[0] if len(filtered_df) > 0 else "N/A"
        st.metric("🚙 Top Brand", top_brand)

    with col4:
        foreign_pct = ((filtered_df['Condition'] == 'Foreign Used').sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0)
        st.metric("✔ Foreign Percentage", f"{foreign_pct:.1f}%")


def display_chart(filtered_df):
    if len(filtered_df) == 0:
      st.warning("No filter data to display. please adjust the data from the sidebar")
      return
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Count of cars by make")
        brand_count = filtered_df['Make'].value_counts().reset_index()
        brand_count.columns = ['Brand', 'Count']

        fig1 = px.bar(
        brand_count,
        x='Brand',
        y='Count'
        )
        fig1.update_layout(xaxis_title="Brand", yaxis_title="Count")
        st.plotly_chart(fig1, width='stretch')

    with col2:
        st.subheader("Average Price by Make")
        avg_brand_price = (filtered_df.groupby('Make')['Price'].mean().sort_values(ascending=False).reset_index()
        )
        fig2 = px.bar(
        avg_brand_price,
        x='Make',
        y='Price',
        )
        fig2.update_layout(xaxis_title="Make", yaxis_title="Price")
        st.plotly_chart(fig2, width='stretch')

    col3, col4 = st.columns(2)

    with col3:
           st.subheader("Price Distribution by Condition")
           fig3 = px.box(
           avg_brand_price,
           x='Make',
           y='Price'
           )
           st.plotly_chart(fig3, use_container_width=True)
    with col4:
           st.subheader("Car Price vs Year")
           fig4, ax = plt.subplots(figsize=(10, 6))
           sns.scatterplot(
           data=filtered_df,
           x='Year',
           y='Price',
           ax=ax
           )
           ax.set_xlabel("Year")
           ax.set_ylabel("Price")
           st.pyplot(fig4)

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Correlation Heatmap")
        numeric_df = filtered_df.select_dtypes(include=['number'])
        corr_matrix = numeric_df.corr()
        fig5, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=0.5,
        ax=ax
        )
        st.pyplot(fig5)
    with col6:
        fig6 = px.histogram(
        filtered_df,
        x='Price',
        nbins=30,
        title='Distribution of Car Prices'
        )
        fig6.update_layout(
        xaxis_title='Price',
        yaxis_title='Frequency'
        )
        st.plotly_chart(fig6, width='stretch')

def display_table_data(filtered_df):
    if len (filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning("No Automation data to display")

















def main():
    #load dataset
    df = load_data()

    #sidebar
    Make, Condition, Transmission = create_sidebar_filters(df)

    #filtered_data
    filtered_df = filter_data(df, Make, Condition, Transmission)

    st.title("Automation Analysis Dashboard")
    st.markdown("---")

    #display metrics
    display_metrics(filtered_df)

    #display charts
    display_chart(filtered_df)

    #display table_data
    display_table_data(filtered_df)










main()