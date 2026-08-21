import os
from pathlib import Path
from typing import Any

from .catalog import (
    DEFAULT_DATASET_ID,
    DEFAULT_MODEL_ID,
    build_catalog,
    constraint_options,
    find_dataset,
    project_root,
)
from .search import SearchService


def create_app(
    *,
    root: Path | None = None,
    data_dir: Path | None = None,
    qdrant_url: str | None = None,
    search_service: SearchService | None = None,
) -> Any:
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel, Field
    except ImportError as error:  # pragma: no cover - exercised by the CLI path.
        raise RuntimeError(
            "The web app dependencies are not installed. "
            'Install them with `python -m pip install -e ".[web]"`.'
        ) from error

    app_root = root or project_root()
    app_data_dir = data_dir or Path(
        os.getenv("ONTOLOGY_RETRIEVAL_DATA_DIR", str(app_root / "datasets"))
    )
    app_qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
    service = search_service or SearchService(
        root=app_root,
        data_dir=app_data_dir,
        qdrant_url=app_qdrant_url,
    )

    class SearchRequest(BaseModel):
        dataset_id: str
        model_id: str = DEFAULT_MODEL_ID
        query: str
        constraint_uris: list[str] = Field(min_length=1)
        posthoc_cap: int | None = None

    app = FastAPI(title="OCVR Local Search", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return HTML

    @app.get("/api/catalog")
    def catalog() -> dict:
        return build_catalog(root=app_root, qdrant_url=app_qdrant_url)

    @app.get("/api/datasets/{dataset_id}/constraints")
    def constraints(dataset_id: str) -> dict:
        try:
            dataset = find_dataset(dataset_id, root=app_root)
            options = constraint_options(dataset, app_data_dir)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except FileNotFoundError as error:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Dataset file is missing: {error}. "
                    "Run Git LFS pull or verify that ONTOLOGY_RETRIEVAL_DATA_DIR points "
                    "to the repository datasets directory."
                ),
            ) from error
        return {"dataset_id": dataset_id, "constraints": options}

    @app.post("/api/search")
    def search(request: SearchRequest) -> dict:
        try:
            return service.run(
                dataset_id=request.dataset_id,
                model_id=request.model_id,
                query=request.query,
                constraint_uris=request.constraint_uris,
                posthoc_cap=request.posthoc_cap,
            )
        except (KeyError, ValueError) as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Search is not ready: {error}. Confirm Qdrant is running, the "
                    "selected collection is built, and the web dependencies are installed."
                ),
            ) from error

    return app


HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OCVR Local Search</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1c1f23;
      --muted: #5c6672;
      --line: #d9dee5;
      --paper: #f8fafc;
      --panel: #ffffff;
      --accent: #146c72;
      --accent-strong: #0f4f55;
      --warn: #a64312;
      --ok: #146b3a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--paper);
    }}
    header {{
      padding: 22px 28px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{ margin: 0 0 6px; font-size: 24px; letter-spacing: 0; }}
    header p {{ margin: 0; color: var(--muted); }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 22px; }}
    form {{
      display: grid;
      grid-template-columns: repeat(4, minmax(170px, 1fr));
      gap: 14px;
      align-items: end;
      padding: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    label {{ display: grid; gap: 6px; font-size: 13px; font-weight: 700; }}
    select, input, textarea, button {{
      width: 100%;
      font: inherit;
      border: 1px solid #bcc5d0;
      border-radius: 6px;
      padding: 9px 10px;
      background: white;
      color: var(--ink);
    }}
    textarea {{ min-height: 72px; resize: vertical; }}
    .wide {{ grid-column: span 2; }}
    .constraint {{ grid-column: span 2; }}
    #constraintList {{
      min-height: 116px;
      max-height: 210px;
      overflow-y: auto;
      border: 1px solid #bcc5d0;
      border-radius: 6px;
      background: white;
    }}
    .constraint-row {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 28px;
      gap: 6px;
      align-items: center;
      width: 100%;
      padding: 8px 10px;
      border: 0;
      border-bottom: 1px solid #eef1f4;
      background: white;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
    }}
    .constraint-row:hover, .constraint-row.selected {{
      background: #edf7f7;
    }}
    .constraint-row .constraint-name {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .help {{
      display: inline-grid;
      place-items: center;
      width: 20px;
      height: 20px;
      border: 1px solid #9aa6b2;
      border-radius: 50%;
      color: var(--muted);
      background: #f7f9fb;
      font-size: 12px;
      font-weight: 700;
    }}
    #submitButton {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
      font-weight: 700;
      cursor: pointer;
    }}
    #submitButton:hover {{ background: var(--accent-strong); }}
    #submitButton:disabled {{ opacity: .55; cursor: wait; }}
    .status {{ margin: 14px 0; color: var(--muted); min-height: 22px; }}
    .error {{ color: var(--warn); }}
    .results {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    section h2 {{
      margin: 0;
      padding: 13px 14px;
      font-size: 17px;
      border-bottom: 1px solid var(--line);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
    }}
    .hit {{ padding: 13px 14px; border-top: 1px solid #eef1f4; }}
    .hit:first-of-type {{ border-top: 0; }}
    .hit-title {{ display: flex; gap: 8px; align-items: baseline; }}
    .rank {{ color: var(--muted); font-weight: 700; }}
    .valid {{ color: var(--ok); font-weight: 700; }}
    .invalid {{ color: var(--warn); font-weight: 700; }}
    .score, .iri, .types {{ color: var(--muted); font-size: 12px; word-break: break-word; }}
    .iri {{ margin-top: 6px; }}
    .empty {{ padding: 14px; color: var(--muted); }}
    @media (max-width: 980px) {{
      form, .results {{ grid-template-columns: 1fr; }}
      .wide, .constraint {{ grid-column: span 1; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>OCVR Local Search</h1>
    <p>Ontology-constrained vector retrieval over local Qdrant collections.</p>
  </header>
  <main>
    <form id="searchForm">
      <label>Dataset
        <select id="datasetSelect"></select>
      </label>
      <label>Model
        <select id="modelSelect"></select>
      </label>
      <label class="wide">Query
        <textarea id="queryInput">arrival route segment near Newark</textarea>
      </label>
      <label class="constraint">Constraint search
        <input id="constraintSearch" placeholder="AirspaceRouteSegment or URI">
      </label>
      <label class="constraint">Ontology constraint
        <div id="constraintList" role="listbox" aria-label="Ontology constraint"></div>
      </label>
      <button id="submitButton" type="submit">Run Search</button>
    </form>
    <div id="status" class="status"></div>
    <div id="results" class="results"></div>
  </main>
  <script>
    const defaults = {{ dataset_id: "{DEFAULT_DATASET_ID}", model_id: "{DEFAULT_MODEL_ID}" }};
    let catalog = null;
    let constraints = [];

    const datasetSelect = document.getElementById("datasetSelect");
    const modelSelect = document.getElementById("modelSelect");
    const queryInput = document.getElementById("queryInput");
    const constraintSearch = document.getElementById("constraintSearch");
    const constraintList = document.getElementById("constraintList");
    const statusEl = document.getElementById("status");
    const resultsEl = document.getElementById("results");
    const submitButton = document.getElementById("submitButton");
    let selectedConstraint = "";

    function setStatus(message, isError = false) {{
      statusEl.textContent = message;
      statusEl.className = isError ? "status error" : "status";
    }}

    function option(value, label) {{
      const item = document.createElement("option");
      item.value = value;
      item.textContent = label;
      return item;
    }}

    function currentDataset() {{
      return catalog.datasets.find((item) => item.id === datasetSelect.value);
    }}

    function renderModels() {{
      const dataset = currentDataset();
      modelSelect.innerHTML = "";
      catalog.models
        .filter((model) => dataset.models.includes(model.id))
        .forEach((model) => modelSelect.appendChild(option(model.id, model.label)));
      modelSelect.value = dataset.models.includes(defaults.model_id)
        ? defaults.model_id
        : dataset.models[0];
    }}

    function renderConstraints() {{
      const query = constraintSearch.value.trim().toLowerCase();
      constraintList.innerHTML = "";
      const visible = constraints
        .filter((item) =>
          !query ||
          item.label.toLowerCase().includes(query) ||
          item.uri.toLowerCase().includes(query)
        );
      if (!visible.some((item) => item.uri === selectedConstraint)) {{
        const airspace = visible.find((item) => item.uri.endsWith("#AirspaceRouteSegment"));
        selectedConstraint = airspace ? airspace.uri : (visible[0] ? visible[0].uri : "");
      }}
      visible.forEach((item) => {{
        const row = document.createElement("button");
        row.type = "button";
        row.className = `constraint-row ${{item.uri === selectedConstraint ? "selected" : ""}}`;
        row.setAttribute("role", "option");
        row.setAttribute("aria-selected", item.uri === selectedConstraint ? "true" : "false");
        row.dataset.uri = item.uri;
        row.innerHTML = `
          <span class="constraint-name">${{escapeHtml(item.display)}}</span>
          <span class="help" title="${{escapeHtml(item.tooltip || item.uri)}}" aria-label="Constraint definition">?</span>
        `;
        row.addEventListener("click", () => {{
          selectedConstraint = item.uri;
          renderConstraints();
        }});
        constraintList.appendChild(row);
      }});
      if (!visible.length) {{
        constraintList.innerHTML = '<div class="empty">No matching constraints.</div>';
      }}
    }}

    async function loadConstraints() {{
      setStatus("Loading constraints...");
      const response = await fetch(`/api/datasets/${{encodeURIComponent(datasetSelect.value)}}/constraints`);
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Unable to load constraints.");
      constraints = body.constraints;
      selectedConstraint = "";
      renderConstraints();
      setStatus(`${{constraints.length}} constraints loaded.`);
    }}

    function renderResults(body) {{
      resultsEl.innerHTML = "";
      body.results.forEach((group) => {{
        const section = document.createElement("section");
        section.innerHTML = `
          <h2>${{group.strategy}}</h2>
          <div class="metrics">
            <div>valid@${{body.top_k}}: ${{group.valid_at_k.toFixed(2)}}</div>
            <div>mean score: ${{group.mean_score.toFixed(3)}}</div>
            <div>examined: ${{group.examined}}</div>
            <div>requests: ${{group.requests}}</div>
          </div>
        `;
        if (!group.hits.length) {{
          section.insertAdjacentHTML("beforeend", '<div class="empty">No results.</div>');
        }}
        group.hits.forEach((hit) => {{
          const payload = hit.payload || {{}};
          const title = payload.label || payload.iri || hit.point_id;
          const types = (hit.matched_types || []).map((item) => item.label).join(", ");
          const div = document.createElement("div");
          div.className = "hit";
          div.innerHTML = `
            <div class="hit-title">
              <span class="rank">#${{hit.rank}}</span>
              <strong>${{escapeHtml(title)}}</strong>
              <span class="${{hit.valid ? "valid" : "invalid"}}">${{hit.valid ? "valid" : "invalid"}}</span>
            </div>
            <div class="score">score: ${{Number(hit.score).toFixed(4)}}</div>
            <div class="iri">${{escapeHtml(payload.iri || hit.point_id)}}</div>
            <div class="types">${{types ? `matched: ${{escapeHtml(types)}}` : ""}}</div>
          `;
          section.appendChild(div);
        }});
        resultsEl.appendChild(section);
      }});
    }}

    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }}[char]));
    }}

    document.getElementById("searchForm").addEventListener("submit", async (event) => {{
      event.preventDefault();
      submitButton.disabled = true;
      resultsEl.innerHTML = "";
      try {{
        setStatus("Running search...");
        const response = await fetch("/api/search", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            dataset_id: datasetSelect.value,
            model_id: modelSelect.value,
            query: queryInput.value,
            constraint_uris: selectedConstraint ? [selectedConstraint] : [],
          }}),
        }});
        const body = await response.json();
        if (!response.ok) throw new Error(body.detail || "Search failed.");
        renderResults(body);
        setStatus(`Searched ${{body.collection}}.`);
      }} catch (error) {{
        setStatus(error.message, true);
      }} finally {{
        submitButton.disabled = false;
      }}
    }});

    datasetSelect.addEventListener("change", async () => {{
      renderModels();
      await loadConstraints();
    }});
    constraintSearch.addEventListener("input", renderConstraints);

    (async function init() {{
      try {{
        setStatus("Loading catalog...");
        const response = await fetch("/api/catalog");
        catalog = await response.json();
        if (!response.ok) throw new Error(catalog.detail || "Unable to load catalog.");
        catalog.datasets.forEach((dataset) => datasetSelect.appendChild(option(dataset.id, dataset.label)));
        datasetSelect.value = defaults.dataset_id;
        renderModels();
        await loadConstraints();
      }} catch (error) {{
        setStatus(error.message, true);
      }}
    }})();
  </script>
</body>
</html>
"""
