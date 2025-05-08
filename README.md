# Kalimantan Barat Price Analysis Dashboard

## Overview
This dashboard visualizes and analyzes price changes of essential commodities across districts in West Kalimantan (Kalimantan Barat), Indonesia. It provides insights into price trends, disparities, and the impact of specific commodities on overall price changes.

## Formulas and Methodologies

### 1. Price Change Indicator (Indikator Perubahan Harga)
The percentage change in prices compared to the previous period:

```
Indikator Perubahan Harga (%) = ((P₁ - P₀) / P₀) × 100
```
Where:
- P₁ = Current period price
- P₀ = Previous period price

### 2. Commodity Contribution to Price Change (Andil Komoditas)
The contribution of a specific commodity to the overall price change:

```
Andil Komoditas = (w × (P₁ - P₀) / P₀) × 100
```
Where:
- w = Weight of the commodity in the consumption basket
- P₁ = Current period price of the commodity
- P₀ = Previous period price of the commodity

### 3. Price Disparity Between Regions (Disparitas Harga Antar Daerah)
The relative difference in prices between regions, expressed as a percentage:

```
Disparitas Harga = (P_max / P_min) × 100
```
Where:
- P_max = Maximum price of a commodity basket in the region
- P_min = Minimum price of the same commodity basket in the region

A value of 100 indicates no disparity, while values above 100 indicate higher disparity.

### 4. Trend Analysis
For time series with multiple periods, linear regression is used to determine price trends:

```
y = mx + b
```
Where:
- y = Price change indicator
- x = Time (in days)
- m = Slope (trend direction and magnitude)
- b = Intercept

The trend direction is determined by the sign of the slope (m):
- Positive slope (m > 0): Upward trend (prices increasing)
- Negative slope (m < 0): Downward trend (prices decreasing)

### 5. Volatility Measurement
Standard deviation is used to measure price volatility:

```
σ = √(Σ(x - μ)² / n)
```
Where:
- σ = Standard deviation
- x = Individual price change values
- μ = Mean of price changes
- n = Number of observations

## Data Sources
The dashboard uses price data collected by the Statistics Indonesia (BPS) for West Kalimantan province. The data includes weekly price observations for essential commodities across different districts.

## Technical Implementation
The dashboard is built using:
- Streamlit for the web interface
- Pandas for data manipulation
- Plotly for interactive visualizations
- NumPy for numerical calculations

## Usage
1. Select districts using the sidebar filter
2. Explore different visualizations and analyses
3. Select specific commodities to analyze their contribution to price changes
4. Download the filtered data as CSV for further analysis