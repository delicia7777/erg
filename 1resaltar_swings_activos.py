import pandas as pd
import plotly.graph_objects as go

# Cargar velas H1
df = pd.read_excel("velas_filtradas_EURUSD_H1.xlsx", parse_dates=["time"])
df.sort_values("time", inplace=True)
df.reset_index(drop=True, inplace=True)

# Parámetros
n = 5
min_separation = 8
threshold_reaccion = 0.0005

# Detectar pivotes básicos
swing_high_idxs = []
swing_low_idxs = []
for i in range(n, len(df) - n):
    prev_highs = df["high"].iloc[i-n:i]
    next_highs = df["high"].iloc[i+1:i+n+1]
    if df["high"].iat[i] > prev_highs.max() and df["high"].iat[i] > next_highs.max():
        swing_high_idxs.append(i)
    prev_lows = df["low"].iloc[i-n:i]
    next_lows = df["low"].iloc[i+1:i+n+1]
    if df["low"].iat[i] < prev_lows.min() and df["low"].iat[i] < next_lows.min():
        swing_low_idxs.append(i)

# Filtrar pivotes por reacción y separación
filtered_highs = []
filtered_lows = []
for i in swing_high_idxs:
    price = df.at[i, "high"]
    max_after = df["high"].iloc[i+1:i+6].max()
    if max_after < price - threshold_reaccion:
        if not filtered_highs or i - filtered_highs[-1] > min_separation:
            filtered_highs.append(i)
for i in swing_low_idxs:
    price = df.at[i, "low"]
    min_after = df["low"].iloc[i+1:i+6].min()
    if min_after > price + threshold_reaccion:
        if not filtered_lows or i - filtered_lows[-1] > min_separation:
            filtered_lows.append(i)

# Obtener últimos pivotes detectados
last_swing_high = df.loc[filtered_highs[-1]] if filtered_highs else None
last_swing_low = df.loc[filtered_lows[-1]] if filtered_lows else None

# Corregir pivotes invertidos automáticamente
if last_swing_high is not None and last_swing_low is not None:
    if last_swing_high["high"] < last_swing_low["low"]:
        last_swing_high, last_swing_low = last_swing_low, last_swing_high

# Crear gráfico de velas
fig = go.Figure(data=[go.Candlestick(
    x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"]
)])

# Añadir líneas y anotaciones de pivote
if last_swing_high is not None:
    fig.add_shape(
        type="line",
        x0=last_swing_high["time"], x1=df["time"].iloc[-1],
        y0=last_swing_high["high"], y1=last_swing_high["high"],
        line=dict(color="crimson", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=last_swing_high["time"], y=last_swing_high["high"],
        text=f"Último Swing High: {last_swing_high['high']:.5f}",
        showarrow=True, arrowhead=1, ax=0, ay=-30,
        font=dict(color="crimson"),
    )

if last_swing_low is not None:
    fig.add_shape(
        type="line",
        x0=last_swing_low["time"], x1=df["time"].iloc[-1],
        y0=last_swing_low["low"], y1=last_swing_low["low"],
        line=dict(color="skyblue", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=last_swing_low["time"], y=last_swing_low["low"],
        text=f"Último Swing Low: {last_swing_low['low']:.5f}",
        showarrow=True, arrowhead=1, ax=0, ay=30,
        font=dict(color="skyblue"),
    )

# Configuración del layout
fig.update_layout(
    title="Últimos Swing High y Low Activos - EUR/USD H1",
    xaxis_title="Fecha",
    yaxis_title="Precio",
    xaxis_rangeslider_visible=False
)

# Guardar HTML
fig.write_html("ultimo_swing_high_low_activos.html")

# --------------------------------------
# ✅ NUEVO: Guardar swings en CSV
# --------------------------------------
swings = []

for i in filtered_highs:
    swings.append({
        "time": df.at[i, "time"],
        "price": df.at[i, "high"],
        "tipo": "high"
    })

for i in filtered_lows:
    swings.append({
        "time": df.at[i, "time"],
        "price": df.at[i, "low"],
        "tipo": "low"
    })

swings_df = pd.DataFrame(swings)
swings_df.to_csv("swings.csv", index=False)
