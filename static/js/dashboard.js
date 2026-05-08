// Dashboard client-side interactions:
// - loader animation
// - sidebar collapse
// - export button wiring
// - auto-refresh metrics

function currentQuery() {
    return window.location.search || "";
}

window.addEventListener("load", () => {
    const loader = document.getElementById("loader");
    if (loader) {
        loader.style.opacity = "0";
        setTimeout(() => {
            loader.style.display = "none";
        }, 250);
    }
});

const sidebar = document.getElementById("sidebar");
const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
if (toggleSidebarBtn && sidebar) {
    toggleSidebarBtn.addEventListener("click", () => {
        if (window.innerWidth <= 992) {
            sidebar.classList.toggle("show-mobile");
            return;
        }
        sidebar.classList.toggle("collapsed");
    });
}

const exportBtn = document.getElementById("exportCsvBtn");
if (exportBtn) {
    exportBtn.setAttribute("href", `/export/csv${currentQuery()}`);
}

const refreshBtn = document.getElementById("refreshBtn");
if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing';
        try {
            const response = await fetch(`/api/refresh${currentQuery()}`);
            if (!response.ok) {
                throw new Error("Refresh failed");
            }
            // Keep behavior simple for beginners:
            // refresh page to redraw all Plotly charts with latest data.
            window.location.reload();
        } catch (error) {
            alert("Unable to refresh right now. Please try again.");
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Auto Refresh';
        }
    });
}

