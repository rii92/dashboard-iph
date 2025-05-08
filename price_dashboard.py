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
    data = {
        'Tahun': [2022, 2022, 2022, 2022, 2022, 2022, 2022, 2022],
        'Bulan': [10, 10, 10, 10, 10, 10, 10, 10],
        'Minggu': [4, 4, 4, 4, 4, 4, 4, 4],
        'No': [6101, 6102, 6103, 6104, 6105, 6106, 6107, 6108],
        'Provinsi': ['KALIMANTAN BARAT'] * 8,
        'Kab/Kota': ['SAMBAS', 'BENGKAYANG', 'LANDAK', 'MEMPAWAH', 'SANGGAU', 'KETAPANG', 'SINTANG', 'KAPUAS HULU'],
        'Indikator Perubahan Harga (%)': [-0.09, 4.44, 10.45, -0.8, 2.37, 4.55, 1.52, 14.07],
        'Komoditas Andil Perubahan Harga': [
            'TELUR AYAM RAS (0.4229); BAWANG PUTIH (0.0045); BERAS (0)',
            'BERAS (3.8698); GULA PASIR (0.3024); MINYAK GORENG (0.0904)',
            'BERAS (6.0825); MINYAK GORENG (4.9103); DAGING AYAM RAS (0.1072)',
            'TELUR AYAM RAS (0.0598); BERAS (0); MIE KERING INSTANT (0)',
            'BERAS (3.2748); MINYAK GORENG (0.9413); GULA PASIR (0.2304)',
            'BERAS (2.8698); MINYAK GORENG (1.5243); GULA PASIR (0.3689)',
            'BERAS (3.2748); TELUR AYAM RAS (0.1174); BAWANG MERAH (0.0722)',
            'BERAS (5.4848); MINYAK GORENG (4.9974); BAWANG MERAH (0.9562)'
        ],
        'Fluktuasi Harga Tertinggi': ['CABAI MERAH', 'SUSU BUBUK UNTUK BALITA', 'DAGING AYAM RAS', 'STABIL', 'MIE KERING INSTANT', 'BAWANG PUTIH', 'CABAI RAWIT', 'STABIL'],
        'Nilai': [0.060, 0.140, 0.040, np.nan, 0.160, 0.070, 0.200, np.nan],
        'Disparitas Harga Antar Daerah': [120.17, 109.48, 111.99, 107.64, 113.42, 107.89, 102.52, 115.99]
    }
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Add date column for time series analysis - fixed version
    df['Tanggal'] = pd.to_datetime(dict(year=df['Tahun'], month=df['Bulan'], day=1))
    df['Bulan_Nama'] = df['Tanggal'].dt.strftime('%B')
    
    return df

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
st.markdown("Dashboard ini menampilkan analisis perubahan harga komoditas di Kalimantan Barat pada Minggu ke-4 Oktober 2022")

# Overview metrics
st.header("Ringkasan")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rata-rata Perubahan Harga", f"{filtered_df['Indikator Perubahan Harga (%)'].mean():.2f}%")
with col2:
    st.metric("Perubahan Harga Tertinggi", f"{filtered_df['Indikator Perubahan Harga (%)'].max():.2f}%", 
              f"Kabupaten {filtered_df.loc[filtered_df['Indikator Perubahan Harga (%)'].idxmax()]['Kab/Kota']}")
with col3:
    st.metric("Perubahan Harga Terendah", f"{filtered_df['Indikator Perubahan Harga (%)'].min():.2f}%",
              f"Kabupaten {filtered_df.loc[filtered_df['Indikator Perubahan Harga (%)'].idxmin()]['Kab/Kota']}")

# Price change by region
st.header("Perubahan Harga per Kabupaten/Kota")
fig = px.bar(filtered_df, x='Kab/Kota', y='Indikator Perubahan Harga (%)', 
             color='Indikator Perubahan Harga (%)',
             color_continuous_scale=px.colors.diverging.RdBu_r,
             labels={'Indikator Perubahan Harga (%)': 'Perubahan Harga (%)'})
fig.update_layout(xaxis_title="Kabupaten/Kota", yaxis_title="Perubahan Harga (%)")
st.plotly_chart(fig, use_container_width=True)

# Price disparity analysis
st.header("Disparitas Harga Antar Daerah")
fig2 = px.bar(filtered_df, x='Kab/Kota', y='Disparitas Harga Antar Daerah',
              color='Disparitas Harga Antar Daerah',
              labels={'Disparitas Harga Antar Daerah': 'Disparitas Harga'})
fig2.update_layout(xaxis_title="Kabupaten/Kota", yaxis_title="Disparitas Harga")
st.plotly_chart(fig2, use_container_width=True)

# Commodity contribution analysis
st.header("Analisis Komoditas Utama")
# Extract main commodities from the data
commodities = []
for item in filtered_df['Komoditas Andil Perubahan Harga']:
    for commodity in item.split(';'):
        if '(' in commodity:
            name = commodity.split('(')[0].strip()
            if name not in commodities and name:
                commodities.append(name)

selected_commodity = st.selectbox("Pilih Komoditas", commodities)

# Create a function to check if a commodity is in the list and extract its value
def get_commodity_value(commodity_string, target):
    for item in commodity_string.split(';'):
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
    value = get_commodity_value(row['Komoditas Andil Perubahan Harga'], selected_commodity)
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


