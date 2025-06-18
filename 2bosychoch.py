import pandas as pd
import plotly.graph_objects as go

# Cargar velas H1
df = pd.read_excel("velas_filtradas_EURUSD_H1.xlsx", parse_dates=["time"])
df.sort_values("time", inplace=True)
df.reset_index(drop=True, inplace=True)

# Cargar swings detectados previamente
swings = pd.read_csv("swings.csv", parse_dates=["time"])
ultimo_high = swings[swings["tipo"] == "high"].sort_values("time").iloc[-1]
ultimo_low  = swings[swings["tipo"] == "low"].sort_values("time").iloc[-1]

# Buscar BOS en las velas posteriores
bos = None
choch = None
estructura = None

for i in range(len(df)):
    vela = df.iloc[i]
    if vela["time"] <= max(ultimo_high["time"], ultimo_low["time"]):
        continue

    if vela["close"] > ultimo_high["price"]:
        bos = {"type": "BOS", "time": vela["time"], "price": ultimo_high["price"], "direccion": "alcista"}
        estructura = "alcista"
        break
    elif vela["close"] < ultimo_low["price"]:
        bos = {"type": "BOS", "time": vela["time"], "price": ultimo_low["price"], "direccion": "bajista"}
        estructura = "bajista"
        break

# Buscar CHoCH después del BOS
if bos:
    for i in range(len(df)):
        vela = df.iloc[i]
        if vela["time"] <= bos["time"]:
            continue

        if estructura == "alcista" and vela["close"] < ultimo_low["price"]:
            choch = {"type": "CHoCH", "time": vela["time"], "price": ultimo_low["price"], "direccion": "bajista"}
            break
        elif estructura == "bajista" and vela["close"] > ultimo_high["price"]:
            choch = {"type": "CHoCH", "time": vela["time"], "price": ultimo_high["price"], "direccion": "alcista"}
            break

# Crear gráfico
fig = go.Figure(data=[go.Candlestick(
    x=df["time"], open=df["open"], high=df["high"],
    low=df["low"], close=df["close"]
)])

# Anotar últimos swings
fig.add_shape(type="line", x0=ultimo_high["time"], x1=df["time"].iloc[-1],
              y0=ultimo_high["price"], y1=ultimo_high["price"],
              line=dict(color="crimson", dash="dash", width=2))
fig.add_annotation(x=ultimo_high["time"], y=ultimo_high["price"],
                   text=f"Swing High", showarrow=True, arrowhead=1, ay=-30, font=dict(color="crimson"))

fig.add_shape(type="line", x0=ultimo_low["time"], x1=df["time"].iloc[-1],
              y0=ultimo_low["price"], y1=ultimo_low["price"],
              line=dict(color="skyblue", dash="dash", width=2))
fig.add_annotation(x=ultimo_low["time"], y=ultimo_low["price"],
                   text=f"Swing Low", showarrow=True, arrowhead=1, ay=30, font=dict(color="skyblue"))

# Anotar BOS
if bos:
    fig.add_annotation(
        x=bos["time"], y=bos["price"],
        text=f"BOS ({bos['direccion']})", showarrow=True,
        arrowhead=2, ay=-50 if bos["direccion"] == "alcista" else 50,
        font=dict(color="orange")
    )

# Anotar CHoCH
if choch:
    fig.add_annotation(
        x=choch["time"], y=choch["price"],
        text=f"CHoCH ({choch['direccion']})", showarrow=True,
        arrowhead=3, ay=-70 if choch["direccion"] == "alcista" else 70,
        font=dict(color="green")
    )

# Guardar gráfico HTML
fig.write_html("bos_choch_detectado.html")

# Exportar resultados a Excel
resultados = []
if bos:
    resultados.append(bos)
if choch:
    resultados.append(choch)

if resultados:
    df_resultado = pd.DataFrame(resultados)
else:
    df_resultado = pd.DataFrame([0])

df_resultado.to_excel("bos_choch_resultado.xlsx", index=False)
