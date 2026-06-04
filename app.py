import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from dash import clientside_callback

# IMPORTAR LOS LAYOUTS
from dashboard.torres import layout as torres_layout
from dashboard.cabinas import layout as cabinas_layout
from dashboard.estaciones import layout as estaciones_layout
from dashboard.camara_torres import layout as camaras_layout

# =========================
# APP
# =========================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME
    ],
    suppress_callback_exceptions=True
)

server = app.server

# =========================
# SIDEBAR
# =========================
sidebar = html.Div(
    [
        html.Div(
            [
                html.H2("Mi Teleférico", className="display-6"),
            ],
            className="sidebar-header",
        ),

        html.Hr(),

        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.I(className="fas fa-broadcast-tower me-2"),
                        html.Span("Torres"),
                    ],
                    href="/torres",
                    active="exact",
                ),

                dbc.NavLink(
                    [
                        html.I(className="fas fa-elevator me-2"),
                        html.Span("Cabinas"),
                    ],
                    href="/cabinas",
                    active="exact",
                ),

                dbc.NavLink(
                    [
                        html.I(className="fas fa-building me-2"),
                        html.Span("Estaciones"),
                    ],
                    href="/estaciones",
                    active="exact",
                ),

                dbc.NavLink(
                    [
                        html.I(className="fas fa-video me-2"),
                        html.Span("Cámaras"),
                    ],
                    href="/camara_torres",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

# =========================
# CONTENIDO
# =========================
#content = html.Div(id="page-content", className="content")
content = html.Div(
    id="page-content", 
    className="content",
    style={"padding": "20px"} # Ajusta padding a tu gusto
)

# =========================
# LAYOUT PRINCIPAL
# =========================
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        content,
        html.Div(id="print-output", style={"display": "none"})
    ]
)

# =========================
# CALLBACK DE PAGINAS
# =========================
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):

    if pathname == "/torres":
        return torres_layout()

    elif pathname == "/cabinas":
        return cabinas_layout()

    elif pathname == "/estaciones":
        return estaciones_layout()

    elif pathname == "/camara_torres":
        return camaras_layout()

    else:
        return torres_layout
clientside_callback(
    """
    function(n_clicks){
        if(n_clicks){
            window.print();
        }
        return "";
    }
    """,
    Output("print-output", "children"),
    Input("print-btn", "n_clicks")
)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)