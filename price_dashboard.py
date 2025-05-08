import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
import matplotlib.colors as mcolors

# Set page config
st.set_page_config(page_title="Kalimantan Barat Price Analysis", layout="wide", initial_sidebar_state="expanded")

# Konfigurasi tema warna yang solid (tanpa opacity)
solid_colors = {
    'positive': '#1f77b4',  # Biru solid
    'negative': '#d62728',  # Merah solid
    'neutral': '#2ca02c',   # Hijau solid
    'highlight': '#ff7f0e'  # Oranye solid
}

# Fungsi untuk membuat warna dengan saturasi berbeda berdasarkan nilai
def get_color_scale(values, color_base, is_negative=False):
    normalized = np.abs(values) / np.abs(values).max() if len(values) > 0 and np.abs(values).max() > 0 else np.zeros_like(values)
    
    if is_negative:
        # Untuk nilai negatif, gunakan warna merah dengan saturasi berbeda
        base_rgb = mcolors.to_rgb(solid_colors['negative'])
        return [f'rgba({int(base_rgb[0]*255)}, {int(base_rgb[1]*255)}, {int(base_rgb[2]*255)}, {0.3 + 0.7*n})' for n in normalized]
    else:
        # Untuk nilai positif, gunakan warna biru dengan saturasi berbeda
        base_rgb = mcolors.to_rgb(solid_colors['positive'])
        return [f'rgba({int(base_rgb[0]*255)}, {int(base_rgb[1]*255)}, {int(base_rgb[2]*255)}, {0.3 + 0.7*n})' for n in normalized]

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

# Opsi tampilan
st.sidebar.title("Opsi Tampilan")
show_values = st.sidebar.checkbox("Tampilkan Nilai pada Grafik", value=True)

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

# Create an interactive bar chart using Plotly
if not filtered_df.empty and not filtered_df['Indikator Perubahan Harga (%)'].isna().all():
    # Sort data for better visualization
    sorted_df = filtered_df.sort_values('Indikator Perubahan Harga (%)', ascending=False)
    
    # Create color array based on values with saturation
    positive_values = sorted_df['Indikator Perubahan Harga (%)'] >= 0
    negative_values = sorted_df['Indikator Perubahan Harga (%)'] < 0
    
    positive_colors = get_color_scale(sorted_df.loc[positive_values, 'Indikator Perubahan Harga (%)'], solid_colors['positive'])
    negative_colors = get_color_scale(sorted_df.loc[negative_values, 'Indikator Perubahan Harga (%)'], solid_colors['negative'], is_negative=True)
    
    # Combine colors
    colors = []
    pos_idx = 0
    neg_idx = 0
    for val in sorted_df['Indikator Perubahan Harga (%)']:
        if val >= 0:
            colors.append(positive_colors[pos_idx] if pos_idx < len(positive_colors) else solid_colors['positive'])
            pos_idx += 1
        else:
            colors.append(negative_colors[neg_idx] if neg_idx < len(negative_colors) else solid_colors['negative'])
            neg_idx += 1
    
    # Create interactive bar chart with Plotly
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=sorted_df['Kab/Kota'],
        y=sorted_df['Indikator Perubahan Harga (%)'],
        marker_color=colors,
        text=[f"{x:.2f}%" for x in sorted_df['Indikator Perubahan Harga (%)']] if show_values else None,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Perubahan: %{y:.2f}%<br>Bulan: %{customdata[0]}<br>Tahun: %{customdata[1]}<extra></extra>',
        customdata=sorted_df[['Bulan_Nama', 'Tahun']]
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Perubahan Harga per Kabupaten/Kota',
            'font': {'size': 24, 'color': 'black', 'family': 'Arial, sans-serif'}
        },
        xaxis_title={
            'text': 'Kabupaten/Kota',
            'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
        },
        yaxis_title={
            'text': 'Perubahan Harga (%)',
            'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
        },
        xaxis={'categoryorder': 'total descending', 'tickangle': -45},
        plot_bgcolor='white',
        height=600,
        margin=dict(t=100, b=100, l=70, r=40),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial, sans-serif"),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )
    
    # Adjust y-axis range to accommodate text labels
    max_val = sorted_df['Indikator Perubahan Harga (%)'].max()
    min_val = sorted_df['Indikator Perubahan Harga (%)'].min()
    padding = (max_val - min_val) * 0.15  # Add 15% padding
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        range=[min_val - padding if min_val < 0 else min_val * 0.9, max_val * 1.15]
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Tidak ada data yang cukup untuk visualisasi perubahan harga.")

# Price disparity analysis
st.header("Disparitas Harga Antar Daerah")

# Create a more attractive bar chart for price disparity using Plotly
if not filtered_df.empty and not filtered_df['Disparitas Harga Antar Daerah'].isna().all():
    # Filter out NaN values
    disparity_df = filtered_df.dropna(subset=['Disparitas Harga Antar Daerah'])
    
    if not disparity_df.empty:
        # Sort data for better visualization
        sorted_disparity_df = disparity_df.sort_values('Disparitas Harga Antar Daerah', ascending=False)
        
        # Create color array with saturation
        colors = get_color_scale(sorted_disparity_df['Disparitas Harga Antar Daerah'], solid_colors['highlight'])
        
        # Create interactive bar chart with Plotly
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=sorted_disparity_df['Kab/Kota'],
            y=sorted_disparity_df['Disparitas Harga Antar Daerah'],
            marker_color=colors,
            text=[f"{x:.2f}" for x in sorted_disparity_df['Disparitas Harga Antar Daerah']] if show_values else None,
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Disparitas: %{y:.2f}<br>Bulan: %{customdata[0]}<br>Tahun: %{customdata[1]}<extra></extra>',
            customdata=sorted_disparity_df[['Bulan_Nama', 'Tahun']]
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Disparitas Harga Antar Daerah',
                'font': {'size': 24, 'color': 'black', 'family': 'Arial, sans-serif'}
            },
            xaxis_title={
                'text': 'Kabupaten/Kota',
                'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
            },
            yaxis_title={
                'text': 'Disparitas Harga (%)',
                'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
            },
            xaxis={'categoryorder': 'total descending', 'tickangle': -45},
            plot_bgcolor='white',
            height=600,
            margin=dict(t=100, b=100, l=70, r=40),
            hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial, sans-serif"),
            uniformtext_minsize=10,
            uniformtext_mode='hide'
        )
        
        # Adjust y-axis range to accommodate text labels
        max_val = sorted_disparity_df['Disparitas Harga Antar Daerah'].max()
        padding = max_val * 0.15  # Add 15% padding
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            range=[0, max_val * 1.15]
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data disparitas harga yang tersedia.")
else:
    st.warning("Tidak ada data yang cukup untuk visualisasi disparitas harga.")

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
                'Indikator Perubahan Harga (%)': row['Indikator Perubahan Harga (%)'],
                'Bulan_Nama': row['Bulan_Nama'],
                'Tahun': row['Tahun']
            })

        commodity_df = pd.DataFrame(commodity_data)
        
        # Create a more attractive visualization for commodity contribution using Plotly
        if not commodity_df.empty and not commodity_df['Kontribusi'].isna().all() and not (commodity_df['Kontribusi'] == 0).all():
            # Sort data for better visualization
            sorted_commodity_df = commodity_df.sort_values('Kontribusi', ascending=False)
            
            # Create color array based on values with saturation
            positive_values = sorted_commodity_df['Kontribusi'] >= 0
            negative_values = sorted_commodity_df['Kontribusi'] < 0
            
            positive_colors = get_color_scale(sorted_commodity_df.loc[positive_values, 'Kontribusi'], solid_colors['positive'])
            negative_colors = get_color_scale(sorted_commodity_df.loc[negative_values, 'Kontribusi'], solid_colors['negative'], is_negative=True)
            
            # Combine colors
            colors = []
            pos_idx = 0
            neg_idx = 0
            for val in sorted_commodity_df['Kontribusi']:
                if val >= 0:
                    colors.append(positive_colors[pos_idx] if pos_idx < len(positive_colors) else solid_colors['positive'])
                    pos_idx += 1
                else:
                    colors.append(negative_colors[neg_idx] if neg_idx < len(negative_colors) else solid_colors['negative'])
                    neg_idx += 1
            
            # Create interactive bar chart with Plotly
            fig = go.Figure()
            
            # Add bars
            fig.add_trace(go.Bar(
                x=sorted_commodity_df['Kab/Kota'],
                y=sorted_commodity_df['Kontribusi'],
                marker_color=colors,
                text=[f"{x:.2f}" for x in sorted_commodity_df['Kontribusi']] if show_values else None,
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Kontribusi: %{y:.2f}<br>Perubahan Harga: %{customdata[0]:.2f}%<br>Bulan: %{customdata[1]}<br>Tahun: %{customdata[2]}<extra></extra>',
                customdata=sorted_commodity_df[['Indikator Perubahan Harga (%)', 'Bulan_Nama', 'Tahun']]
            ))
            
            # Update layout
            fig.update_layout(
                title={
                    'text': f'Kontribusi {selected_commodity} terhadap Perubahan Harga',
                    'font': {'size': 24, 'color': 'black', 'family': 'Arial, sans-serif'}
                },
                xaxis_title={
                    'text': 'Kabupaten/Kota',
                    'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
                },
                yaxis_title={
                    'text': 'Kontribusi',
                    'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
                },
                xaxis={'categoryorder': 'total descending', 'tickangle': -45},
                plot_bgcolor='white',
                height=600,
                margin=dict(t=100, b=100, l=70, r=40),
                hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial, sans-serif"),
                uniformtext_minsize=10,
                uniformtext_mode='hide'
            )
            
            # Adjust y-axis range to accommodate text labels
            max_val = sorted_commodity_df['Kontribusi'].max()
            min_val = sorted_commodity_df['Kontribusi'].min()
            padding = (max_val - min_val) * 0.15  # Add 15% padding
            
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                range=[min_val - padding if min_val < 0 else min_val * 0.9, max_val * 1.15]
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Tidak ada data kontribusi yang tersedia untuk {selected_commodity}.")
    else:
        st.warning("Tidak ada data komoditas yang tersedia.")

# Time series analysis
st.header("Analisis Tren Perubahan Harga")

# Pilihan tampilan tren
trend_view = st.radio(
    "Tampilkan tren untuk:",
    ["Kalimantan Barat (Agregat)", "Per Kabupaten/Kota"],
    horizontal=True
)

# Group by date and calculate average price change
if not filtered_df.empty:
    # Check if we have enough time periods for analysis
    time_periods = filtered_df['Tanggal'].nunique()
    
    if time_periods > 1:
        if trend_view == "Kalimantan Barat (Agregat)":
            # Group by date and calculate average for all districts
            time_series_df = filtered_df.groupby('Tanggal')['Indikator Perubahan Harga (%)'].mean().reset_index()
            time_series_df['Bulan-Tahun'] = time_series_df['Tanggal'].dt.strftime('%b %Y')
            
            # Create interactive line chart with Plotly
            fig = go.Figure()
            
            # Add line and markers
            fig.add_trace(go.Scatter(
                x=time_series_df['Tanggal'],
                y=time_series_df['Indikator Perubahan Harga (%)'],
                mode='lines+markers' + ('+text' if show_values else ''),
                name='Perubahan Harga',
                line=dict(color=solid_colors['positive'], width=4),
                marker=dict(size=12, color=solid_colors['positive']),
                text=[f"{y:.2f}%" for y in time_series_df['Indikator Perubahan Harga (%)']] if show_values else None,
                textposition="top center",
                textfont=dict(size=12, color='black'),
                hovertemplate='<b>%{customdata}</b><br>Perubahan: %{y:.2f}%<extra></extra>',
                customdata=time_series_df['Bulan-Tahun']
            ))
            
            # Add horizontal line at y=0
            fig.add_shape(
                type="line",
                x0=time_series_df['Tanggal'].min(),
                y0=0,
                x1=time_series_df['Tanggal'].max(),
                y1=0,
                line=dict(color="gray", width=2, dash="dash")
            )
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Tren Perubahan Harga Kalimantan Barat',
                    'font': {'size': 24, 'color': 'black', 'family': 'Arial, sans-serif'}
                },
                xaxis_title={
                    'text': 'Periode',
                    'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
                },
                yaxis_title={
                    'text': 'Rata-rata Perubahan Harga (%)',
                    'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
                },
                xaxis=dict(
                    tickformat='%b %Y',
                    tickangle=-45
                ),
                plot_bgcolor='white',
                height=600,
                margin=dict(t=100, b=100, l=70, r=40),
                hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial, sans-serif")
            )
            
            # Add grid lines
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # Per Kabupaten/Kota
            # Pilih kabupaten/kota untuk ditampilkan (maksimal 5)
            if len(selected_districts) > 5:
                st.warning("Menampilkan terlalu banyak kabupaten/kota dapat membuat grafik sulit dibaca. Silakan pilih maksimal 5 kabupaten/kota.")
                districts_for_trend = st.multiselect(
                    "Pilih maksimal 5 kabupaten/kota untuk ditampilkan:",
                    options=selected_districts,
                    default=selected_districts[:5] if len(selected_districts) > 5 else selected_districts
                )
            else:
                districts_for_trend = selected_districts
            
            if districts_for_trend:
                # Filter data for selected districts
                trend_df = filtered_df[filtered_df['Kab/Kota'].isin(districts_for_trend)]
                
                # Create interactive line chart with Plotly
                fig = go.Figure()
                
                # Color palette for multiple lines
                colors = px.colors.qualitative.Plotly
                
                # Add lines for each district
                for i, district in enumerate(districts_for_trend):
                    district_df = trend_df[trend_df['Kab/Kota'] == district]
                    
                    # Sort by date
                    district_df = district_df.sort_values('Tanggal')
                    
                    # Skip if less than 2 data points
                    if len(district_df) < 2:
                        continue
                    
                    # Add line and markers
                    fig.add_trace(go.Scatter(
                        x=district_df['Tanggal'],
                        y=district_df['Indikator Perubahan Harga (%)'],
                        mode='lines+markers' + ('+text' if show_values else ''),
                        name=district,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=10, color=colors[i % len(colors)]),
                        text=[f"{y:.2f}%" for y in district_df['Indikator Perubahan Harga (%)']] if show_values else None,
                        textposition="top center",
                        textfont=dict(size=10, color=colors[i % len(colors)]),
                        hovertemplate='<b>%{text}</b><br>Perubahan: %{y:.2f}%<br>%{customdata}<extra></extra>',
                        customdata=district_df['Bulan_Nama'] + ' ' + district_df['Tahun'].astype(str),
                        hovertext=[district] * len(district_df)  # District name for hover
                    ))
                
                # Add horizontal line at y=0
                fig.add_shape(
                    type="line",
                    x0=filtered_df['Tanggal'].min(),
                    y0=0,
                    x1=filtered_df['Tanggal'].max(),
                    y1=0,
                    line=dict(color="gray", width=2, dash="dash")
                )
                
                # Update layout
                fig.update_layout(
                    title={
                        'text': 'Tren Perubahan Harga per Kabupaten/Kota',
                        'font': {'size': 24, 'color': 'black', 'family': 'Arial, sans-serif'}
                    },
                    xaxis_title={
                        'text': 'Periode',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
                    },
                    yaxis_title={
                        'text': 'Perubahan Harga (%)',
                        'font': {'size': 16, 'color': 'black', 'family': 'Arial, sans-serif'}
                    },
                    xaxis=dict(
                        tickformat='%b %Y',
                        tickangle=-45
                    ),
                    plot_bgcolor='white',
                    height=600,
                    margin=dict(t=100, b=100, l=70, r=40),
                    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial, sans-serif"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Add grid lines
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray'
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Silakan pilih minimal satu kabupaten/kota untuk melihat tren.")
    else:
        st.info("Diperlukan lebih dari satu periode waktu untuk analisis tren.")
else:
    st.warning("Tidak ada data yang cukup untuk analisis tren.")

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











