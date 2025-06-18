import pandas as pd
import plotly.graph_objects as go

# === 1. Cargar datos ===
df_m15 = pd.read_excel("velas_filtradas_EURUSD_M15.xlsx", parse_dates=["time"])
df_m15.sort_values("time", inplace=True)
df_m15.reset_index(drop=True, inplace=True)

bos_df = pd.read_excel("bos_choch_resultado.xlsx")
bos_df = bos_df[bos_df["type"] == "BOS"]

# === 2. Extraer info del BOS ===
if not bos_df.empty:
    bos_time = pd.to_datetime(bos_df.iloc[0]["time"])
    bos_direccion = bos_df.iloc[0]["direccion"]

    prev_velas = df_m15[df_m15["time"] < bos_time]

    if bos_direccion == "alcista":
        ob_candidatas = prev_velas[prev_velas["close"] < prev_velas["open"]]  # vela bajista
    else:
        ob_candidatas = prev_velas[prev_velas["close"] > prev_velas["open"]]  # vela alcista

    order_block = ob_candidatas.iloc[-1] if not ob_candidatas.empty else None
else:
    order_block = None

# === 3. Guardar resultado a Excel ===
if order_block is not None:
    ob_result = pd.DataFrame([{
        "time": order_block["time"],
        "open": order_block["open"],
        "high": order_block["high"],
        "low": order_block["low"],
        "close": order_block["close"],
        "tipo": "OrderBlock",
        "direccion": bos_direccion
    }])
else:
    ob_result = pd.DataFrame([{"OrderBlock": 0}])

ob_result.to_excel("order_block_m15.xlsx", index=False)

# === 4. Visualizar en HTML ===
fig = go.Figure(data=[go.Candlestick(
    x=df_m15["time"],
    open=df_m15["open"],
    high=df_m15["high"],
    low=df_m15["low"],
    close=df_m15["close"]
)])

if order_block is not None:
    fig.add_shape(
        type="rect",
        x0=order_block["time"],
        x1=df_m15["time"].iloc[-1],
        y0=order_block["low"],
        y1=order_block["high"],
        fillcolor="rgba(255,165,0,0.2)",
        line=dict(color="orange", width=1),
        layer="below"
    )
    fig.add_annotation(
        x=order_block["time"],
        y=order_block["high"],
        text=f"OB ({bos_direccion})",
        showarrow=True,
        arrowhead=1,
        ay=-40,
        font=dict(color="orange")
    )

fig.update_layout(
    title="Último Order Block en M15 antes del BOS H1",
    xaxis_title="Fecha",
    yaxis_title="Precio",
    xaxis_rangeslider_visible=False
)

fig.write_html("order_block_m15_visual.html")
