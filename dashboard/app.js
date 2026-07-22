const DATASET_RELEASE_BASE = "https://github.com/gsmkev/hepy/releases/download/dataset";

async function loadIndexData() {
  const res = await fetch(`${DATASET_RELEASE_BASE}/index.json`);
  return res.json();
}

function lineChart(canvasId, labels, values, label) {
  new Chart(document.getElementById(canvasId), {
    type: "line",
    data: { labels, datasets: [{ label, data: values }] },
  });
}

async function main() {
  const data = await loadIndexData();
  const indexDaily = data.index_daily || [];

  const aggregate = indexDaily.filter(r => r.supermarket === "AGREGADO");
  if (aggregate.length === 0) {
    document.body.insertAdjacentHTML("beforeend", "<p>Todavía no hay datos del índice agregado.</p>");
  } else {
    lineChart("aggregate-chart", aggregate.map(r => r.date), aggregate.map(r => r.value), "Índice");
  }

  const supermarkets = [...new Set(indexDaily.map(r => r.supermarket).filter(s => s !== "AGREGADO"))].sort();
  const container = document.getElementById("supermarket-charts");
  for (const sm of supermarkets) {
    const canvas = document.createElement("canvas");
    canvas.id = `chart-${sm}`;
    container.appendChild(canvas);
    const series = indexDaily.filter(r => r.supermarket === sm);
    lineChart(canvas.id, series.map(r => r.date), series.map(r => r.value), sm);
  }

  const downloads = document.getElementById("downloads");
  for (const [fname, label] of [["prices.db", "SQLite"], ["prices.csv", "CSV"], ["prices.json", "JSON (precios)"], ["index.json", "JSON (índice)"]]) {
    downloads.insertAdjacentHTML("beforeend", `<li><a href="${DATASET_RELEASE_BASE}/${fname}">${label}</a></li>`);
  }
}

main().catch(() => {
  document.body.insertAdjacentHTML("beforeend", "<p>Todavía no hay datos del índice agregado.</p>");
});
