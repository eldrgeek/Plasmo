#!/usr/bin/env python3
"""
Plasmo Dashboard – clean modern restyle
"""

import logging
from fasthtml.common import *
from service_manager import ServiceManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1.  SHARED <head>  ---------------------------------------------------------
# ---------------------------------------------------------------------------
COMMON_HEAD = [
    Title("Plasmo Dashboard"),
    Meta(charset="utf-8"),
    Meta(name="viewport", content="width=device-width,initial-scale=1"),
    Link(rel="preconnect", href="https://fonts.googleapis.com"),
    Link(rel="stylesheet",
         href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap"),
    Link(rel="stylesheet",
         href="https://fonts.googleapis.com/icon?family=Material+Icons+Round"),
    Style(
        r"""
/* ==========  TOKENS  ========== */
:root{
  --clr-bg-0:#0d1117; --clr-bg-1:#161b22; --clr-bg-2:#21262d;
  --clr-card:#1c2128; --clr-accent:#3b82f6; --clr-error:#ef4444;
  --clr-ok:#10b981;   --clr-text-0:#f0f6fc; --clr-text-1:#8b949e;
  --radius:0.75rem;   --gap:1.25rem;         --ts:150ms ease;
}
[data-theme="light"]{
  --clr-bg-0:#f3f4f6; --clr-bg-1:#ffffff; --clr-bg-2:#f1f5f9;
  --clr-card:#ffffff; --clr-text-0:#111827; --clr-text-1:#4b5563;
}

/* ==========  RESET  ========== */
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:'Inter',system-ui,sans-serif;
  background:var(--clr-bg-0); color:var(--clr-text-0);
  min-height:100vh; display:flex; flex-direction:column;
}
.material-icons-round{font-size:1.2rem;display:inline-flex}

/* ==========  LAYOUT  ========== */
.app-container{display:flex; flex:1}
.header{
  position:fixed;top:0;left:0;right:0;height:3.5rem;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 var(--gap);background:var(--clr-bg-1);z-index:100;
  border-bottom:1px solid var(--clr-bg-2);
}
.sidebar{
  width:14rem; padding:calc(var(--gap)*1.2) var(--gap);
  background:var(--clr-bg-1); border-right:1px solid var(--clr-bg-2);
  position:fixed;top:3.5rem;bottom:0;overflow-y:auto;
}
.main-content{
  margin-top:3.5rem;margin-left:14rem;padding:calc(var(--gap)*1.5);
  width:calc(100% - 14rem);
}

/* ==========  NAV  ========== */
.nav-item{
  display:flex;align-items:center;gap:.75rem;padding:.5rem .75rem;
  color:var(--clr-text-1); border-radius:var(--radius);
  transition:background var(--ts),color var(--ts),transform var(--ts);
  cursor:pointer; border:none;background:none;width:100%;text-align:left
}
.nav-item.active,
.nav-item:hover{color:var(--clr-text-0);background:var(--clr-bg-2)}
.nav-section-title{font-size:.7rem;text-transform:uppercase;
  letter-spacing:.05em;margin:1rem 0 .5rem;color:var(--clr-text-1)}

/* ==========  CARDS  ========== */
.card-grid{
  display:grid;gap:var(--gap);
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
}
.card{
  background:var(--clr-card);border:1px solid var(--clr-bg-2);
  border-radius:var(--radius);padding:var(--gap);
  transition:transform var(--ts),box-shadow var(--ts);
}
.card:hover{transform:translateY(-4px);
  box-shadow:0 6px 18px rgba(0,0,0,.25)}
.status-badge{
  font-size:.75rem;font-weight:600;padding:.15rem .5rem;
  border-radius:999px;color:#fff;display:inline-flex;align-items:center;
}
.status-running{background:var(--clr-ok)}
.status-stopped{background:var(--clr-error)}
.btn{
  display:inline-flex;align-items:center;gap:.4rem;
  font-size:.85rem;font-weight:600;padding:.55rem 1rem;
  border-radius:var(--radius);border:none;cursor:pointer;
  transition:background var(--ts),transform var(--ts);color:#fff
}
.btn:disabled{opacity:.5;cursor:not-allowed}
.btn-primary{background:var(--clr-accent)}
.btn-error{background:var(--clr-error)}
.btn-warning{background:#f59e0b}
.btn-success{background:var(--clr-ok)}
.btn:hover:not(:disabled){transform:translateY(-2px)}
/* ==========  RESPONSIVE  ========== */
@media(max-width:768px){
  .sidebar{transform:translateX(-110%);transition:transform var(--ts)}
  .sidebar.open{transform:translateX(0)}
  .main-content{margin-left:0;width:100%}
}
""")
]

# ---------------------------------------------------------------------------
# 2.  FAST APP  --------------------------------------------------------------
# ---------------------------------------------------------------------------
app, rt = fast_app(live=True)

service_manager = ServiceManager()


# ---------------------------------------------------------------------------
# 3.  COMPONENT BUILDERS  ----------------------------------------------------
# ---------------------------------------------------------------------------
def AppHeader():
    return Header(
        Div(
            Div("🚀", cls="logo"),
            "Plasmo Dashboard",
            cls="header-brand"),
        Div(
            Button(I("light_mode", cls="material-icons-round"),
                   cls="btn btn-primary", onclick="toggleTheme()", title="Toggle theme"),
            Button(I("refresh", cls="material-icons-round"),
                   cls="btn", onclick="refreshAll()", title="Refresh all"),
        ),
        cls="header")


def Sidebar():
    def item(icon, label, target, active=False):
        return Button(I(icon, cls="material-icons-round"), label,
                      cls=f"nav-item{' active' if active else ''}",
                      onclick=f"showSection('{target}')", id=f"nav-{target}")
    return Nav(
        Div(H3("Overview", cls="nav-section-title"),
            item("dashboard", "Dashboard", "dashboard", True),
            item("settings", "Services", "services"),
            cls="nav-section"),
        cls="sidebar", id="sidebar"
    )


def DashboardSection():
    return Div(
        H1("Service Overview", cls="page-title"),
        P("Monitor and control all services", cls="page-subtitle"),
        Div(
            Button(I("play_arrow", cls="material-icons-round"), "Start all",
                   cls="btn btn-success", onclick="controlAllServices('start')"),
            Button(I("stop", cls="material-icons-round"), "Stop all",
                   cls="btn btn-error", onclick="controlAllServices('stop')"),
            Button(I("refresh", cls="material-icons-round"), "Restart all",
                   cls="btn btn-warning", onclick="controlAllServices('restart')"),
            style="display:flex;gap:var(--gap);flex-wrap:wrap;justify-content:center",
        ),
        Div(id="services-grid", cls="card-grid"),
        cls="page-section active", id="dashboard-section"
    )


# ---------------------------------------------------------------------------
# 4.  API ROUTES  ------------------------------------------------------------
# ---------------------------------------------------------------------------
@rt("/api/services/status")
def get_services_status():
    try:
        return service_manager.get_all_status()
    except Exception as e:                  # pragma: no cover
        logger.exception(e)
        return {"error": str(e)}


@rt("/api/services/{name}/{action}", methods=["POST"])
def control_service(name: str, action: str):
    try:
        fn = dict(start=service_manager.start_service,
                  stop=service_manager.stop_service,
                  restart=service_manager.restart_service).get(action)
        if not fn:
            return {"error": f"unknown action {action}"}
        fn(name)
        return {"success": True}
    except Exception as e:                  # pragma: no cover
        logger.exception(e)
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# 5.  SPA ROUTE  -------------------------------------------------------------
# ---------------------------------------------------------------------------
@rt("/")
def get():
    return Html(
        Head(*COMMON_HEAD),
        Body(
            AppHeader(),
            Div(
                Sidebar(),
                Main(DashboardSection(), cls="main-content"),
                cls="app-container"
            ),
            # -------------  Small inline JS for demo  ------------------
            Script("""
const saved = localStorage.getItem('theme')||'dark';
document.body.dataset.theme=saved;
function toggleTheme(){
  const t=document.body.dataset.theme==='dark'?'light':'dark';
  document.body.dataset.theme=t;localStorage.setItem('theme',t);
}
""")
        )
    )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("Open http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
