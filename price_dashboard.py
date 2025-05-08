import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import calendar

# Set page config
st.set_page_config(page_title="Kalimantan Barat Price Analysis", layout="wide", initial_sidebar_state="expanded")

# Load data
@st.cache_data
def load_data():
    try:
        # Load data from CSV file
        df = pd.read_csv('data.csv')
        
        # Check column names and fix if needed
        if 'Komoditas Andil Perubahan Harga ' in df.columns:
            # Note the space at the end of the column name
            df = df.rename(columns={'Komoditas Andil Perubahan Harga ': 'Komoditas Andil Perubahan Harga'})
        
        # Handle missing values and convert numeric columns
        df['Indikator Perubahan Harga (%)'] = pd.to_numeric(df['Indikator Perubahan Harga (%)'], errors='coerce')
        df['Nilai'] = pd.to_numeric(df['Nilai'], errors='coerce')
        df['Disparitas Harga Antar Daerah'] = pd.to_numeric(df['Disparitas Harga Antar Daerah'], errors='coerce')
        
        # Add date column for time series analysis
        df['Tanggal'] = pd.to_datetime(dict(year=df['Tahun'], month=df['Bulan'], day=1))
        df['Bulan_Nama'] = df['Tanggal'].dt.strftime('%B')
        
        # Print column names for debugging
        print("Available columns:", df.columns.tolist())
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty DataFrame with expected columns if file not found
        return pd.DataFrame(columns=['Tahun', 'Bulan', 'Minggu', 'No', 'Provinsi', 'Kab/Kota', 
                                    'Indikator Perubahan Harga (%)', 'Komoditas Andil Perubahan Harga',
                                    'Fluktuasi Harga Tertinggi', 'Nilai', 'Disparitas Harga Antar Daerah',
                                    'Tanggal', 'Bulan_Nama'])

df = load_data()

# Sidebar filters
st.sidebar.title("Filter Data")

# District selection (multi-select)
all_districts = df['Kab/Kota'].unique().tolist()
selected_districts = st.sidebar.multiselect(
    "Pilih Kabupaten/Kota",
    options=all_districts,
    default=all_districts
)

# Filter data based on selection
if selected_districts:
    filtered_df = df[df['Kab/Kota'].isin(selected_districts)]
else:
    filtered_df = df

# Main content
st.title("Analisis Perubahan Harga di Kalimantan Barat")
st.markdown("Dashboard ini menampilkan analisis perubahan harga komoditas di Kalimantan Barat")

# Overview metrics
st.header("Ringkasan")
col1, col2, col3 = st.columns(3)
with col1:
    # Handle potential NaN values in the mean calculation
    mean_value = filtered_df['Indikator Perubahan Harga (%)'].mean()
    if pd.isna(mean_value):
        st.metric("Rata-rata Perubahan Harga", "Data tidak tersedia")
    else:
        st.metric("Rata-rata Perubahan Harga", f"{mean_value:.2f}%")
with col2:
    # Handle potential NaN values or empty DataFrame
    if filtered_df.empty or filtered_df['Indikator Perubahan Harga (%)'].isna().all():
        st.metric("Perubahan Harga Tertinggi", "Data tidak tersedia")
    else:
        max_idx = filtered_df['Indikator Perubahan Harga (%)'].idxmax()
        max_val = filtered_df.loc[max_idx, 'Indikator Perubahan Harga (%)']
        max_district = filtered_df.loc[max_idx, 'Kab/Kota']
        st.metric("Perubahan Harga Tertinggi", f"{max_val:.2f}%", f"{max_district}")
with col3:
    # Handle potential NaN values or empty DataFrame
    if filtered_df.empty or filtered_df['Indikator Perubahan Harga (%)'].isna().all():
        st.metric("Perubahan Harga Terendah", "Data tidak tersedia")
    else:
        min_idx = filtered_df['Indikator Perubahan Harga (%)'].idxmin()
        min_val = filtered_df.loc[min_idx, 'Indikator Perubahan Harga (%)']
        min_district = filtered_df.loc[min_idx, 'Kab/Kota']
        st.metric("Perubahan Harga Terendah", f"{min_val:.2f}%", f"{min_district}")

# Price change by region
st.header("Perubahan Harga per Kabupaten/Kota")
try:
    # Try using Plotly with json instead of orjson
    import json
    import plotly.io as pio
    
    # Override the default JSON encoder to avoid orjson
    pio.json.config.default_engine = 'json'
    pio.json.config.default_encoder = json.dumps
    
    fig = px.bar(filtered_df, x='Kab/Kota', y='Indikator Perubahan Harga (%)', 
                color='Indikator Perubahan Harga (%)',
                color_continuous_scale=px.colors.diverging.RdBu_r,
                labels={'Indikator Perubahan Harga (%)': 'Perubahan Harga (%)'})
    fig.update_layout(xaxis_title="Kabupaten/Kota", yaxis_title="Perubahan Harga (%)")
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error creating chart: {e}")
    st.info("Menggunakan chart alternatif karena masalah dengan Plotly.")
    
    # Fallback to simple bar chart using Streamlit
    st.bar_chart(filtered_df.set_index('Kab/Kota')['Indikator Perubahan Harga (%)'])

# Price disparity analysis
st.header("Disparitas Harga Antar Daerah")
fig2 = px.bar(filtered_df, x='Kab/Kota', y='Disparitas Harga Antar Daerah',
              color='Disparitas Harga Antar Daerah',
              labels={'Disparitas Harga Antar Daerah': 'Disparitas Harga'})
fig2.update_layout(xaxis_title="Kabupaten/Kota", yaxis_title="Disparitas Harga")
st.plotly_chart(fig2, use_container_width=True)

# Commodity contribution analysis
st.header("Analisis Komoditas Utama")

# Check if the column exists
commodity_column = None
for col in df.columns:
    if 'Komoditas Andil' in col:
        commodity_column = col
        break

if commodity_column is None:
    st.error("Kolom 'Komoditas Andil Perubahan Harga' tidak ditemukan dalam data.")
else:
    # Extract main commodities from the data
    commodities = []
    for item in filtered_df[commodity_column]:
        if pd.notna(item):  # Check if the value is not NaN
            for commodity in str(item).split(';'):
                if '(' in commodity:
                    name = commodity.split('(')[0].strip()
                    if name not in commodities and name:
                        commodities.append(name)

    if commodities:
        selected_commodity = st.selectbox("Pilih Komoditas", commodities)

        # Create a function to check if a commodity is in the list and extract its value
        def get_commodity_value(commodity_string, target):
            if pd.isna(commodity_string):
                return 0
            for item in str(commodity_string).split(';'):
                if target in item:
                    try:
                        value = float(item.split('(')[1].split(')')[0])
                        return value
                    except:
                        return 0
            return 0

        # Create a new dataframe with the contribution of the selected commodity
        commodity_data = []
        for _, row in filtered_df.iterrows():
            value = get_commodity_value(row[commodity_column], selected_commodity)
            commodity_data.append({
                'Kab/Kota': row['Kab/Kota'],
                'Kontribusi': value,
                'Indikator Perubahan Harga (%)': row['Indikator Perubahan Harga (%)']
            })

        commodity_df = pd.DataFrame(commodity_data)
        fig3 = px.bar(commodity_df, x='Kab/Kota', y='Kontribusi',
                    title=f"Kontribusi {selected_commodity} terhadap Perubahan Harga",
                    color='Indikator Perubahan Harga (%)',
                    color_continuous_scale=px.colors.diverging.RdBu_r)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Tidak ada data komoditas yang tersedia.")

# Time Series Analysis for Price Trends
st.header("Analisis Trend Harga")

# Since we only have one time point in the sample data, let's create a note about this
if len(filtered_df['Tanggal'].unique()) <= 1:
    st.info("Data saat ini hanya tersedia untuk satu periode waktu (Minggu ke-4 Oktober 2022). Visualisasi trend akan tersedia ketika data dari beberapa periode waktu telah ditambahkan.")
    
    # Add a sample visualization with simulated data for demonstration
    st.subheader("Contoh Visualisasi Trend (Data Simulasi)")
    
    # Create sample data for demonstration - ensure we have districts to work with
    if selected_districts:
        sample_dates = pd.date_range(start='2022-07-01', end='2022-10-31', freq='W-MON')
        sample_districts = selected_districts[:3] if len(selected_districts) > 3 else selected_districts
        
        sample_data = []
        for district in sample_districts:
            base_value = np.random.uniform(0, 5)  # Random starting point
            trend = np.random.choice([-0.1, 0, 0.1])  # Random trend direction
            volatility = np.random.uniform(0.2, 1.5)  # Random volatility
            
            for date in sample_dates:
                value = base_value + trend * (date.dayofyear - sample_dates[0].dayofyear)/7
                value += np.random.normal(0, volatility)  # Add some noise
                sample_data.append({
                    'Tanggal': date,
                    'Kab/Kota': district,
                    'Indikator Perubahan Harga (%)': value
                })
        
        # Only create and display the plot if we have data
        if sample_data:
            sample_df = pd.DataFrame(sample_data)
            
            # Create time series plot
            fig_trend = px.line(sample_df, x='Tanggal', y='Indikator Perubahan Harga (%)', 
                                color='Kab/Kota', markers=True,
                                title="Simulasi Trend Perubahan Harga per Kabupaten/Kota")
            fig_trend.update_layout(
                xaxis_title="Periode Waktu",
                yaxis_title="Perubahan Harga (%)",
                legend_title="Kabupaten/Kota"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.caption("Catatan: Visualisasi di atas menggunakan data simulasi untuk tujuan demonstrasi.")
        else:
            st.warning("Pilih setidaknya satu kabupaten/kota untuk melihat visualisasi trend.")
    else:
        st.warning("Pilih setidaknya satu kabupaten/kota untuk melihat visualisasi trend.")
    
else:
    # If we have multiple time points, create actual time series visualization
    fig_trend = px.line(filtered_df, x='Tanggal', y='Indikator Perubahan Harga (%)', 
                       color='Kab/Kota', markers=True,
                       title="Trend Perubahan Harga per Kabupaten/Kota")
    fig_trend.update_layout(
        xaxis_title="Periode Waktu",
        yaxis_title="Perubahan Harga (%)",
        legend_title="Kabupaten/Kota"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Add trend analysis
    if len(selected_districts) == 1:
        district = selected_districts[0]
        district_data = filtered_df[filtered_df['Kab/Kota'] == district]
        
        if len(district_data) > 1:
            # Calculate trend
            x = np.array((district_data['Tanggal'] - district_data['Tanggal'].min()).dt.days)
            y = district_data['Indikator Perubahan Harga (%)'].values
            slope, intercept = np.polyfit(x, y, 1)
            
            trend_direction = "naik" if slope > 0 else "turun"
            st.markdown(f"**Analisis Trend untuk {district}:**")
            st.markdown(f"- Trend perubahan harga cenderung **{trend_direction}** selama periode yang ditampilkan.")
            st.markdown(f"- Rata-rata perubahan: **{district_data['Indikator Perubahan Harga (%)'].mean():.2f}%**")
            st.markdown(f"- Volatilitas (standar deviasi): **{district_data['Indikator Perubahan Harga (%)'].std():.2f}**")

# Advanced Analysis Section
st.header("Analisis Mendalam")

# If only one district is selected, show detailed analysis
if len(selected_districts) == 1:
    district = selected_districts[0]
    district_data = filtered_df[filtered_df['Kab/Kota'] == district]
    
    st.subheader(f"Analisis Data Harga Komoditas di Kabupaten {district}")
    
    # Inflation/Deflation Analysis
    inflation_status = "inflasi" if district_data['Indikator Perubahan Harga (%)'].iloc[0] > 0 else "deflasi"
    inflation_value = abs(district_data['Indikator Perubahan Harga (%)'].iloc[0])
    
    st.markdown(f"""
    ### Analisis Umum
    
    #### Tren Inflasi dan Deflasi:
    - {district} mengalami **{inflation_status}** sebesar **{inflation_value:.2f}%** pada periode ini.
    """)
    
    # Commodity Analysis
    st.markdown("#### Komoditas Penggerak Utama:")
    
    # Extract top 3 commodities
    commodity_list = district_data['Komoditas Andil Perubahan Harga'].iloc[0].split(';')
    top_commodities = []
    
    for commodity in commodity_list:
        if '(' in commodity:
            name = commodity.split('(')[0].strip()
            value = float(commodity.split('(')[1].split(')')[0])
            top_commodities.append((name, value))
    
    top_commodities.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for i, (name, value) in enumerate(top_commodities[:3], 1):
        st.markdown(f"- **{name}**: Andil {value:.4f}% ({i})")
    
    # Price Fluctuation Analysis
    st.markdown("#### Fluktuasi Harga Tertinggi:")
    highest_fluctuation = district_data['Fluktuasi Harga Tertinggi'].iloc[0]
    fluctuation_value = district_data['Nilai'].iloc[0]
    
    if highest_fluctuation == "STABIL":
        st.markdown(f"- Harga komoditas di {district} relatif **stabil** pada periode ini.")
    else:
        st.markdown(f"- **{highest_fluctuation}** mengalami fluktuasi tertinggi dengan nilai **{fluctuation_value:.3f}**.")
    
    # Price Disparity Analysis
    st.markdown("#### Disparitas Harga Antar Daerah:")
    disparity_value = district_data['Disparitas Harga Antar Daerah'].iloc[0]
    st.markdown(f"- Disparitas harga di {district} mencapai **{disparity_value:.2f}%**, menunjukkan perbedaan harga yang {'signifikan' if disparity_value > 110 else 'moderat'} dibandingkan daerah lain.")
    
    # Recommendations
    st.markdown("""
    ### Rekomendasi untuk BPS dan Pemda
    
    #### Untuk BPS:
    - Lakukan pemantauan lebih intensif terhadap komoditas dengan andil perubahan harga tertinggi
    - Tingkatkan kualitas data dengan pengumpulan yang lebih konsisten
    - Kembangkan indikator dini untuk komoditas dengan fluktuasi tinggi
    
    #### Untuk Pemda:
    - Fokus pada stabilisasi harga komoditas penggerak utama inflasi/deflasi
    - Pertimbangkan intervensi pasar untuk komoditas dengan fluktuasi tinggi
    - Tingkatkan koordinasi dengan daerah lain untuk mengurangi disparitas harga
    """)

# Comparative Analysis (when multiple districts are selected)
elif len(selected_districts) > 1:
    st.subheader("Analisis Perbandingan Antar Kabupaten/Kota")
    
    # Comparative bar chart for price changes
    fig_comp = px.bar(filtered_df, x='Kab/Kota', y='Indikator Perubahan Harga (%)', 
                      title="Perbandingan Perubahan Harga",
                      color='Indikator Perubahan Harga (%)',
                      color_continuous_scale=px.colors.diverging.RdBu_r)
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Comparative analysis of top commodities
    st.markdown("#### Komoditas Utama per Kabupaten/Kota:")
    
    for district in selected_districts:
        district_data = filtered_df[filtered_df['Kab/Kota'] == district]
        commodity_list = district_data['Komoditas Andil Perubahan Harga'].iloc[0].split(';')
        top_commodity = commodity_list[0].split('(')[0].strip()
        top_value = float(commodity_list[0].split('(')[1].split(')')[0])
        
        st.markdown(f"- **{district}**: {top_commodity} (andil {top_value:.4f}%)")
    
    # Correlation analysis
    st.markdown("#### Korelasi Antar Daerah:")
    
    # Create a comparison table instead of a correlation matrix
    st.markdown("""
    Perbandingan indikator perubahan harga antar daerah:
    """)
    
    comparison_df = filtered_df[['Kab/Kota', 'Indikator Perubahan Harga (%)', 'Disparitas Harga Antar Daerah']]
    st.dataframe(comparison_df.sort_values('Indikator Perubahan Harga (%)', ascending=False))
    
    st.markdown("""
    Daerah dengan pola perubahan harga serupa mungkin memiliki karakteristik ekonomi atau rantai pasok yang mirip.
    Pemda dapat berkolaborasi dengan daerah yang memiliki pola serupa untuk mengatasi masalah bersama.
    """)

# Data table
st.header("Data Lengkap")
st.dataframe(filtered_df)

# Download data
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Data CSV",
    data=csv,
    file_name=f"price_data_{'_'.join(selected_districts)}.csv",
    mime="text/csv",
)



