from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import plotly.graph_objects as go

# ================== ZABBIX ==================
ZABBIX_URL = "http://loop21.miteleferico.bo:8080/api_jsonrpc.php"
API_TOKEN = "e5a3d40624a3d73ed3239f14a49644edbecaae39310ca8f3d60ae18d7fc9ce2e"
HEADERS = {"Content-Type": "application/json-rpc"}

LINEAS = ["Azul", "Blanca", "Cafe", "Celeste", "Morada", "Naranja", "Plateada"]

# ============================================

def zabbix_api(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "auth": API_TOKEN,
        "id": 1
    }
    r = requests.post(ZABBIX_URL, json=payload, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        return None
    return data["result"]

def get_group_id(name):
    res = zabbix_api("hostgroup.get", {"filter": {"name": [name]}})
    return res[0]["groupid"] if res else None

def contar_hosts(groupid):
    hosts = zabbix_api("host.get", {
        "groupids": groupid,
        "output": ["hostid"],
        "selectItems": ["key_", "lastvalue"]
    })

    up = down = 0
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

# ===================== APP ===================

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def dashboard():

    charts_html = ""
    total_up = total_down = 0

    # --------- POR CADA LÍNEA ----------
    for linea in LINEAS:
        grupo = f"camaras Linea {linea}"
        gid = get_group_id(grupo)

        if not gid:
            continue

        up, down = contar_hosts(gid)
        total_up += up
        total_down += down

        fig = go.Figure(go.Pie(
            labels=["Operativas", "No operativas"],
            values=[up, down],
            hole=0.55,
            marker=dict(colors=["#2ecc71", "#e74c3c"])
        ))

        fig.update_layout(
            title=f"Línea {linea}",
            height=300,
            margin=dict(t=40, b=10)
        )

        charts_html += fig.to_html(full_html=False)

    # --------- GENERAL (PIE) ----------
    total = total_up + total_down
    fig_general = go.Figure(go.Pie(
        labels=["Operativas", "No operativas"],
        values=[total_up, total_down],
        hole=0.55,
        marker=dict(colors=["#2ecc71", "#e74c3c"])
    ))
    fig_general.update_layout(
        title="GENERAL - Todas las líneas",
        height=350,
        margin=dict(t=40, b=10)
    )

    # --------- HTML ----------
    return f"""
    <html>
    <head>
        <title>Dashboard Cámaras</title>
        <style>
            body {{
                font-family: Arial;
                background:#f4f4f4;
                text-align:center;
            }}
            .grid {{
                display:grid;
                grid-template-columns: repeat(3, 1fr);
                gap:20px;
                padding:20px;
            }}
            .general {{
                width: 500px;
                margin: 30px auto;
            }}
        </style>
    </head>
    <body>
        <h1> Estado General de Cámaras</h1>

        <!-- PIE GENERAL -->
        <div class="general">
            {fig_general.to_html(full_html=False)}
        </div>

        <h2>Cámaras por Línea</h2>

        <!-- GRÁFICAS DE LÍNEAS -->
        <div class="grid">
            {charts_html}
        </div>
    </body>
    </html>
    """
