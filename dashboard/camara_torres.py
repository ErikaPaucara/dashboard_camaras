import requests
import plotly.graph_objects as go
from dashboard.reporte_pdf import generar_pdf
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc


ZABBIX_URL = "http://loop21.miteleferico.bo:8080/api_jsonrpc.php"
API_TOKEN = "e5a3d40624a3d73ed3239f14a49644edbecaae39310ca8f3d60ae18d7fc9ce2e"

HEADERS = {"Content-Type": "application/json-rpc"}

LINEAS = [
    "Azul", "Blanca", "Cafe",
    "Celeste", "Morada",
    "Naranja", "Plateada"
]


def zabbix_api(method, params):

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "auth": API_TOKEN,
        "id": 1
    }

    r = requests.post(
        ZABBIX_URL,
        json=payload,
        headers=HEADERS,
        timeout=20
    )

    data = r.json()

    if "error" in data:
        return None

    return data["result"]


def get_group_id(name):

    res = zabbix_api(
        "hostgroup.get",
        {"filter": {"name": [name]}}
    )

    return res[0]["groupid"] if res else None


def contar_hosts(groupid):

    hosts = zabbix_api("host.get", {
        "groupids": groupid,
        "output": ["hostid"],
        "selectItems": ["key_", "lastvalue"]
    })

    up = 0
    down = 0

    if not hosts:
        return up, down

    for h in hosts:

        for i in h.get("items", []):

            if i["key_"] == "icmpping":

                if i["lastvalue"] == "1":
                    up += 1
                else:
                    down += 1

    return up, down


def layout():

    figuras_reporte = []
    graficas = []

    total_up = 0
    total_down = 0

    # DATOS PARA GRAFICO DE BARRAS
    nombres_lineas = []
    operativas = []
    no_operativas = []

    for linea in LINEAS:

        grupo = f"camaras Linea {linea}"

        gid = get_group_id(grupo)

        if not gid:
            continue

        up, down = contar_hosts(gid)

        total_up += up
        total_down += down

        # GUARDAR DATOS PARA BARRAS
        nombres_lineas.append(linea)
        operativas.append(up)
        no_operativas.append(down)

        # ================= GRAFICO INDIVIDUAL =================

        fig = go.Figure(go.Pie(
            labels=["Operativas", "No operativas"],
            values=[up, down],
            hole=0.55,
            marker=dict(colors=["#2ecc71", "#e74c3c"])
        ))

        fig.update_layout(
            title=f"Línea {linea}",
            height=300
        )

        figuras_reporte.append(fig)


        graficas.append(

            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        dcc.Graph(
                            figure=fig,
                            style={"height": "400px"},
                            config={"displayModeBar": False}
                        )

                    ]),

                    style={
                        "border-radius": "15px",
                        "box-shadow": "0px 4px 15px rgba(0,0,0,0.15)",
                        "background-color": "white",
                        "border": "1px solid #ddd"
                    }

                ),

                xs=12,
                sm=12,
                md=6,
                lg=6,
                xl=4,

                className="mb-4"

            )

        )

    # ================= GRAFICO GENERAL =================

    fig_general = go.Figure(go.Pie(
        labels=["Operativas", "No operativas"],
        values=[total_up, total_down],
        hole=0.55,
        marker=dict(colors=["#2ecc71", "#e74c3c"]),
    ))

   
    fig_general.update_layout(
        title="ESTADO GENERAL DE CAMARAS DE TORRES",
        height=400
    )

    figuras_reporte.append(fig_general)



    # ================= GRAFICO DE BARRAS =================

    fig_barras = go.Figure()

    # BARRAS OPERATIVAS
    fig_barras.add_trace(go.Bar(
        x=nombres_lineas,
        y=operativas,
        name="Operativas",
        marker_color="#2ecc71",
        text=operativas,
        textposition="outside"
    ))

    # BARRAS NO OPERATIVAS
    fig_barras.add_trace(go.Bar(
        x=nombres_lineas,
        y=no_operativas,
        name="No operativas",
        marker_color="#e74c3c",
        text=no_operativas,
        textposition="outside"
    ))

    fig_barras.update_layout(
        title="ESTADO DE CAMARAS EN TORRES POR LÍNEA",
        barmode='group',
        height=400,
        xaxis_title="Líneas",
        yaxis_title="Cantidad",
        legend_title="Estado"
    )

    figuras_reporte.append(fig_barras)
    # ================= LAYOUT =================
    print("Cantidad de gráficos:", len(figuras_reporte))

    global GRAFICOS_PDF
    GRAFICOS_PDF = figuras_reporte

    return html.Div([
        dbc.Button(
            "📄 Generar PDF",
            id="btn-pdf",
            color="danger",
            className="mb-3"
        ),

        dcc.Download(id="download-pdf"),
        html.H1(
            "CAMARAS TORRES MI TELEFERICO",
            style={
                "textAlign": "center",
                "marginBottom": "30px",
                "fontWeight": "bold"
            }
        ),

        # ================= FILA SUPERIOR =================

        dbc.Row([

            # PIE GENERAL
            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        dcc.Graph(
                            figure=fig_general,
                            config={"displayModeBar": False}
                        )

                    ]),

                    style={
                        "border-radius": "10px",
                        "box-shadow": "0px 4px 20px rgba(0,0,0,0.15)",
                        "padding": "15px",
                        "background-color": "white",
                        "border": "1px solid #ddd"
                    }

                ),

                xs=12,
                md=5,

                className="mb-4"

            ),

            # BARRAS
            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        dcc.Graph(
                            figure=fig_barras,
                            config={"displayModeBar": False}
                        )

                    ]),

                    style={
                        "border-radius": "10px",
                        "box-shadow": "0px 4px 20px rgba(0,0,0,0.15)",
                        "padding": "15px",
                        "background-color": "white",
                        "border": "1px solid #ddd"
                    }

                ),

                xs=12,
                md=7,

                className="mb-4"

            )

        ]),

        # ================= GRAFICOS INDIVIDUALES =================

        dbc.Row(graficas)

    ],

    style={
        "background-color": "#f4f6f9",
        "padding": "10px",
        "minHeight": "100vh"
    })

@callback(
    Output("download-pdf", "data"),
    Input("btn-pdf", "n_clicks"),
    prevent_initial_call=True
)
def descargar_pdf(n_clicks):

    print("BOTON PDF PRESIONADO")
    print("CANTIDAD DE GRAFICOS:", len(GRAFICOS_PDF))

    pdf = generar_pdf(GRAFICOS_PDF)

    return dcc.send_file(pdf)

    