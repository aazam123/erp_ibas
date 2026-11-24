frappe.pages["erp_ibas_dashboard"].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("ERP-IBAS Executive Dashboard"),
        single_column: true
    });

    // Hide default frappe page header for full-bleed dark executive look
    $(wrapper).find(".page-head").hide();
    
    // Inject Dashboard View
    render_dashboard(wrapper);
};

function render_dashboard(wrapper) {
    let $container = $(wrapper).find(".layout-main-section");
    $container.empty();

    let html = `
    <div class="erp-ibas-container">
        <div class="ibas-neon-board">
            
            <!-- Left Sidebar -->
            <div class="ibas-sidebar">
                <div>
                    <div class="ibas-brand">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00d2ff" stroke-width="2.5"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                        <span class="ibas-brand-title">ERP-IBAS</span>
                        <span class="ibas-brand-badge">M3 AI</span>
                    </div>

                    <ul class="ibas-menu">
                        <li class="ibas-nav-item active" data-view="overview">
                            <span class="ibas-nav-icon">📊</span>
                            <span>Overview</span>
                        </li>
                        <li class="ibas-nav-item" data-view="operations">
                            <span class="ibas-nav-icon">🏭</span>
                            <span>Operations</span>
                        </li>
                        <li class="ibas-nav-item" data-view="finance">
                            <span class="ibas-nav-icon">📈</span>
                            <span>P&L / Finance</span>
                        </li>
                        <li class="ibas-nav-item" data-route="app/sales-invoice">
                            <span class="ibas-nav-icon">💼</span>
                            <span>Sales</span>
                        </li>
                        <li class="ibas-nav-item" data-route="app/purchase-order">
                            <span class="ibas-nav-icon">🛒</span>
                            <span>Purchasing</span>
                        </li>
                        <li class="ibas-nav-item" data-route="app/item">
                            <span class="ibas-nav-icon">📦</span>
                            <span>Inventory</span>
                        </li>
                        <li class="ibas-nav-item" data-route="app/ibas-financial-forecast">
                            <span class="ibas-nav-icon">🔮</span>
                            <span>AI Forecast</span>
                        </li>
                        <li class="ibas-nav-item" data-route="app/ibas-anomaly-log">
                            <span class="ibas-nav-icon">🛡️</span>
                            <span>Anomalies</span>
                        </li>
                        <li class="ibas-nav-item" data-route="app/ibas-settings">
                            <span class="ibas-nav-icon">⚙️</span>
                            <span>Admin Settings</span>
                        </li>
                    </ul>
                </div>

                <div class="ibas-user-profile">
                    <div class="ibas-avatar">AB</div>
                    <div class="ibas-user-info">
                        <span class="ibas-user-name">${frappe.session.user_fullname || "Administrator"}</span>
                        <span class="ibas-user-role">Executive Admin</span>
                    </div>
                </div>
            </div>

            <!-- Main Executive Area -->
            <div class="ibas-main">

                <!-- VIEW 1: EXECUTIVE OVERVIEW (IMAGE 1) -->
                <div id="view-overview" class="ibas-view-section active">
                    <div class="ibas-header">
                        <h2 class="ibas-page-title">Executive Overview</h2>
                        <select class="ibas-filter-select">
                            <option>This Month</option>
                            <option>Q4 2026</option>
                            <option>Year-to-Date</option>
                        </select>
                    </div>

                    <!-- 5 Top Metric Cards -->
                    <div class="ibas-metrics-row" style="margin-top: 18px;">
                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Total Revenue</div>
                            <div class="ibas-metric-val">$24.8M</div>
                            <div class="ibas-metric-footer">
                                <span class="ibas-trend-badge">↑ 18.6% <span class="ibas-trend-sub">vs last month</span></span>
                                <canvas class="ibas-sparkline-canvas" id="spark-rev"></canvas>
                            </div>
                        </div>

                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Gross Profit</div>
                            <div class="ibas-metric-val">$7.4M</div>
                            <div class="ibas-metric-footer">
                                <span class="ibas-trend-badge">↑ 15.3% <span class="ibas-trend-sub">vs last month</span></span>
                                <canvas class="ibas-sparkline-canvas" id="spark-gp"></canvas>
                            </div>
                        </div>

                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Operating Margin</div>
                            <div class="ibas-metric-val">29.7%</div>
                            <div class="ibas-metric-footer">
                                <span class="ibas-trend-badge">↑ 4.8% <span class="ibas-trend-sub">vs last month</span></span>
                                <canvas class="ibas-sparkline-canvas" id="spark-om"></canvas>
                            </div>
                        </div>

                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">EBITDA</div>
                            <div class="ibas-metric-val">$5.6M</div>
                            <div class="ibas-metric-footer">
                                <span class="ibas-trend-badge">↑ 17.2% <span class="ibas-trend-sub">vs last month</span></span>
                                <canvas class="ibas-sparkline-canvas" id="spark-ebitda"></canvas>
                            </div>
                        </div>

                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Cash Position</div>
                            <div class="ibas-metric-val">$12.6M</div>
                            <div class="ibas-metric-footer">
                                <span class="ibas-trend-badge">↑ 8.9% <span class="ibas-trend-sub">vs last month</span></span>
                                <canvas class="ibas-sparkline-canvas" id="spark-cash"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Middle Grid: Revenue Trend & Donut -->
                    <div class="ibas-grid-mid" style="margin-top: 18px;">
                        <div class="ibas-card-panel">
                            <div class="ibas-panel-header">
                                <h3 class="ibas-panel-title">Revenue Trend</h3>
                                <select class="ibas-filter-select">
                                    <option>Monthly</option>
                                    <option>Weekly</option>
                                </select>
                            </div>
                            <canvas id="chart-revenue-trend" height="180"></canvas>
                        </div>

                        <div class="ibas-card-panel">
                            <div class="ibas-panel-header">
                                <h3 class="ibas-panel-title">Top Revenue by Segment</h3>
                            </div>
                            <div class="ibas-donut-wrapper">
                                <canvas id="chart-segment-donut" width="130" height="130"></canvas>
                                <div class="ibas-donut-legend">
                                    <div class="ibas-legend-item"><span class="ibas-legend-dot" style="background: #3b82f6;"></span> Manufacturing <strong>42%</strong></div>
                                    <div class="ibas-legend-item"><span class="ibas-legend-dot" style="background: #06b6d4;"></span> Oil & Gas <strong>28%</strong></div>
                                    <div class="ibas-legend-item"><span class="ibas-legend-dot" style="background: #10b981;"></span> Real Estate <strong>18%</strong></div>
                                    <div class="ibas-legend-item"><span class="ibas-legend-dot" style="background: #8b5cf6;"></span> Tech / AI <strong>12%</strong></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Bottom Grid: Sales by Region & Margin Analysis -->
                    <div class="ibas-grid-bottom" style="margin-top: 18px;">
                        <div class="ibas-card-panel">
                            <div class="ibas-panel-header">
                                <h3 class="ibas-panel-title">Sales by Region</h3>
                            </div>
                            <div style="position: relative; height: 170px;">
                                <canvas id="chart-world-map" height="170"></canvas>
                                <div class="ibas-heatmap-scale">
                                    <span>High</span>
                                    <div class="ibas-scale-bar"></div>
                                    <span>Low</span>
                                </div>
                            </div>
                        </div>

                        <div class="ibas-card-panel">
                            <div class="ibas-panel-header">
                                <h3 class="ibas-panel-title">Margin Analysis</h3>
                                <div style="display: flex; gap: 14px; align-items: center; font-size: 11.5px;">
                                    <span><span style="color: #10b981;">■</span> Gross Margin</span>
                                    <span><span style="color: #3b82f6;">■</span> Operating Margin</span>
                                    <select class="ibas-filter-select"><option>Monthly</option></select>
                                </div>
                            </div>
                            <canvas id="chart-margin-analysis" height="170"></canvas>
                        </div>
                    </div>
                </div>

                <!-- VIEW 2: OPERATIONS & INDUSTRIAL ERP (IMAGE 2) -->
                <div id="view-operations" class="ibas-view-section">
                    <div class="ibas-header">
                        <h2 class="ibas-page-title">Industrial ERP & Factory Floor Automation</h2>
                        <span class="ibas-brand-badge" style="background: #10b981;">IoT LIVE STREAMING</span>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px;">
                        <div class="ibas-card-panel">
                            <h3 class="ibas-panel-title" style="margin-bottom: 12px;">Production Line & Assembly Telemetry</h3>
                            <canvas id="chart-production-line" height="200"></canvas>
                        </div>
                        <div class="ibas-card-panel">
                            <h3 class="ibas-panel-title" style="margin-bottom: 12px;">OEE Metrics (Overall Equipment Effectiveness)</h3>
                            <div style="display: flex; justify-content: space-around; padding: 25px 0;">
                                <div style="text-align: center;">
                                    <div style="font-size: 28px; font-weight: 700; color: #00d2ff;">94.2%</div>
                                    <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Availability</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 28px; font-weight: 700; color: #3b82f6;">91.8%</div>
                                    <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Performance</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 28px; font-weight: 700; color: #10b981;">98.5%</div>
                                    <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Quality Rate</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="ibas-card-panel" style="margin-top: 16px;">
                        <h3 class="ibas-panel-title" style="margin-bottom: 12px;">IoT Machine Vibration & Thermal Sensors</h3>
                        <canvas id="chart-iot-sensors" height="120"></canvas>
                    </div>
                </div>

                <!-- VIEW 3: CORPORATE P&L & FINANCE (IMAGE 3) -->
                <div id="view-finance" class="ibas-view-section">
                    <div class="ibas-header">
                        <h2 class="ibas-page-title">Corporate P&L & Financial Analytics</h2>
                        <span class="ibas-brand-badge">CONSOLIDATED GROUP</span>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 18px;">
                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Revenue</div>
                            <div class="ibas-metric-val">$181.2M</div>
                            <span class="ibas-trend-badge" style="color: #ef4444;">↓ -4.08% QoQ</span>
                        </div>
                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Cost of Revenue</div>
                            <div class="ibas-metric-val">$92.30M</div>
                            <span class="ibas-trend-badge" style="color: #10b981;">↓ -29.64% QoQ</span>
                        </div>
                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">Gross Margin</div>
                            <div class="ibas-metric-val">25.0%</div>
                            <span class="ibas-trend-badge">Stable Q1 Corridor</span>
                        </div>
                        <div class="ibas-metric-card">
                            <div class="ibas-metric-label">OPEX</div>
                            <div class="ibas-metric-val">$36.10M</div>
                            <span class="ibas-trend-badge" style="color: #ef4444;">Above Target $3.28M</span>
                        </div>
                    </div>

                    <div class="ibas-card-panel" style="margin-top: 16px;">
                        <h3 class="ibas-panel-title" style="margin-bottom: 12px;">Quarterly Revenue & Cost Structure Breakdown</h3>
                        <canvas id="chart-pnl-breakdown" height="180"></canvas>
                    </div>
                </div>

            </div>
        </div>
    </div>
    `;

    $container.html(html);

    // Sidebar navigation handler
    $container.find(".ibas-nav-item").on("click", function() {
        let view = $(this).data("view");
        let route = $(this).data("route");

        if (route) {
            frappe.set_route(route);
            return;
        }

        if (view) {
            $container.find(".ibas-nav-item").removeClass("active");
            $(this).addClass("active");

            $container.find(".ibas-view-section").removeClass("active");
            $container.find("#view-" + view).addClass("active");
        }
    });

    // Render Canvas Charts
    setTimeout(init_all_canvas_charts, 100);
}

function init_all_canvas_charts() {
    render_sparklines();
    render_revenue_trend();
    render_segment_donut();
    render_world_map();
    render_margin_analysis();
    render_operations_chart();
    render_iot_chart();
    render_pnl_chart();
}

function render_sparklines() {
    draw_sparkline("spark-rev", [12, 14, 13, 17, 19, 21, 24.8], "#00d2ff");
    draw_sparkline("spark-gp", [4.2, 4.8, 5.1, 5.8, 6.2, 7.4], "#10b981");
    draw_sparkline("spark-om", [22, 24, 25, 27, 26, 29.7], "#a855f7");
    draw_sparkline("spark-ebitda", [3.2, 3.8, 4.0, 4.5, 4.9, 5.6], "#818cf8");
    draw_sparkline("spark-cash", [8.5, 9.2, 9.8, 10.4, 11.2, 12.6], "#4ade80");
}

function draw_sparkline(canvasId, data, color) {
    let canvas = document.getElementById(canvasId);
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = 60;
    let h = canvas.height = 24;

    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();

    let min = Math.min(...data);
    let max = Math.max(...data);
    let range = (max - min) || 1;

    data.forEach((val, idx) => {
        let x = (idx / (data.length - 1)) * (w - 4) + 2;
        let y = h - ((val - min) / range) * (h - 6) - 3;
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
}

function render_revenue_trend() {
    let canvas = document.getElementById("chart-revenue-trend");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = canvas.parentElement.clientWidth - 40;
    let h = canvas.height = 180;

    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    let data = [7, 10, 11, 14, 13, 17, 14, 19, 17, 20, 22, 24.8]; // in Millions

    let max = 30;
    let padLeft = 45;
    let padBottom = 25;
    let chartW = w - padLeft - 20;
    let chartH = h - padBottom - 10;

    // Grid lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.06)";
    ctx.lineWidth = 1;
    ctx.fillStyle = "#64748b";
    ctx.font = "10px sans-serif";

    for (let i = 0; i <= 3; i++) {
        let y = 10 + (chartH / 3) * i;
        ctx.beginPath();
        ctx.moveTo(padLeft, y);
        ctx.lineTo(w - 20, y);
        ctx.stroke();

        let valLabel = "$" + (max - (i * 10)) + "M";
        ctx.fillText(valLabel, 8, y + 3);
    }

    // Points calculation
    let points = data.map((val, idx) => {
        let x = padLeft + (idx / (data.length - 1)) * chartW;
        let y = 10 + chartH - (val / max) * chartH;
        return { x, y, label: months[idx] };
    });

    // Gradient fill under curve
    let grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, "rgba(0, 170, 255, 0.4)");
    grad.addColorStop(1, "rgba(0, 170, 255, 0.0)");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.lineTo(points[points.length - 1].x, 10 + chartH);
    ctx.lineTo(points[0].x, 10 + chartH);
    ctx.closePath();
    ctx.fill();

    // Glowing stroke
    ctx.strokeStyle = "#00d2ff";
    ctx.shadowColor = "#00d2ff";
    ctx.shadowBlur = 10;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    points.forEach((p, idx) => {
        if (idx === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.stroke();
    ctx.shadowBlur = 0; // reset

    // Draw dots & x labels
    points.forEach(p => {
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#94a3b8";
        ctx.fillText(p.label, p.x - 9, h - 8);
    });
}

function render_segment_donut() {
    let canvas = document.getElementById("chart-segment-donut");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let cx = 65, cy = 65, radius = 55, innerRadius = 38;

    let segments = [
        { pct: 0.42, color: "#3b82f6" },
        { pct: 0.28, color: "#06b6d4" },
        { pct: 0.18, color: "#10b981" },
        { pct: 0.12, color: "#8b5cf6" }
    ];

    let start = -Math.PI / 2;
    segments.forEach(seg => {
        let end = start + (seg.pct * Math.PI * 2);
        ctx.beginPath();
        ctx.arc(cx, cy, radius, start, end);
        ctx.arc(cx, cy, innerRadius, end, start, true);
        ctx.closePath();
        ctx.fillStyle = seg.color;
        ctx.shadowColor = seg.color;
        ctx.shadowBlur = 8;
        ctx.fill();
        start = end;
    });
    ctx.shadowBlur = 0;

    // Center total label
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 13px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("$24.8M", cx, cy + 2);
    ctx.font = "9px sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("Total", cx, cy + 14);
}

function render_world_map() {
    let canvas = document.getElementById("chart-world-map");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = canvas.parentElement.clientWidth - 40;
    let h = canvas.height = 170;

    // Dark continent dots grid
    ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
    for (let x = 10; x < w - 40; x += 10) {
        for (let y = 10; y < h - 10; y += 10) {
            // Rough continental bounds
            if ((x > 30 && x < 120 && y > 30 && y < 110) || // Americas
                (x > 140 && x < 230 && y > 20 && y < 90) ||  // EMEA
                (x > 210 && x < 320 && y > 30 && y < 140)) { // APAC
                ctx.beginPath();
                ctx.arc(x, y, 1.2, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // Glowing sales hubs
    let hubs = [
        { x: 80, y: 55, r: 5, col: "#00d2ff" },   // New York
        { x: 60, y: 70, r: 4, col: "#3b82f6" },   // West Coast
        { x: 175, y: 45, r: 6, col: "#00d2ff" },  // London / Frankfurt
        { x: 270, y: 75, r: 6, col: "#00d2ff" },  // Singapore / Tokyo
        { x: 215, y: 70, r: 4, col: "#06b6d4" }   // Dubai
    ];

    hubs.forEach(hub => {
        ctx.fillStyle = hub.col;
        ctx.shadowColor = hub.col;
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(hub.x, hub.y, hub.r, 0, Math.PI * 2);
        ctx.fill();
    });
    ctx.shadowBlur = 0;
}

function render_margin_analysis() {
    let canvas = document.getElementById("chart-margin-analysis");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = canvas.parentElement.clientWidth - 40;
    let h = canvas.height = 170;

    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    let grossMargin = [15, 17, 18, 16, 17, 19, 18, 17, 18, 19, 20, 21];
    let opMargin = [8, 9, 10, 8, 9, 10, 9, 8, 10, 10, 11, 12];

    let padLeft = 35;
    let chartW = w - padLeft - 10;
    let barWidth = Math.max(6, (chartW / months.length) - 8);

    months.forEach((m, i) => {
        let x = padLeft + (i * (chartW / months.length)) + 4;
        let gmHeight = (grossMargin[i] / 40) * 120;
        let omHeight = (opMargin[i] / 40) * 120;

        // Gross margin bar (Green)
        ctx.fillStyle = "#10b981";
        ctx.fillRect(x, 140 - gmHeight, barWidth, gmHeight);

        // Operating margin stacked bar (Blue)
        ctx.fillStyle = "#3b82f6";
        ctx.fillRect(x, 140 - gmHeight - omHeight, barWidth, omHeight);

        // Label
        ctx.fillStyle = "#64748b";
        ctx.font = "9px sans-serif";
        ctx.fillText(m, x - 2, 155);
    });

    // Overlaid trend line (Green)
    ctx.strokeStyle = "#4ade80";
    ctx.lineWidth = 2;
    ctx.beginPath();
    months.forEach((m, i) => {
        let x = padLeft + (i * (chartW / months.length)) + 4 + (barWidth / 2);
        let y = 140 - ((grossMargin[i] + opMargin[i] + 4) / 40) * 120;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
}

function render_operations_chart() {
    let canvas = document.getElementById("chart-production-line");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = canvas.parentElement.clientWidth - 40;
    let h = canvas.height = 200;

    // Production Line waveform
    ctx.strokeStyle = "#00d2ff";
    ctx.lineWidth = 2;
    ctx.shadowColor = "#00d2ff";
    ctx.shadowBlur = 10;
    ctx.beginPath();
    for (let x = 0; x < w; x += 10) {
        let y = 100 + Math.sin(x * 0.05) * 40 + Math.cos(x * 0.02) * 20;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
}

function render_iot_chart() {
    let canvas = document.getElementById("chart-iot-sensors");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = canvas.parentElement.clientWidth - 40;
    let h = canvas.height = 120;

    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let x = 0; x < w; x += 8) {
        let y = 60 + (Math.random() - 0.5) * 35;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
}

function render_pnl_chart() {
    let canvas = document.getElementById("chart-pnl-breakdown");
    if (!canvas) return;
    let ctx = canvas.getContext("2d");
    let w = canvas.width = canvas.parentElement.clientWidth - 40;
    let h = canvas.height = 180;

    let quarters = ["2022 Q1", "2022 Q2", "2022 Q3", "2022 Q4", "2023 Q1"];
    let barW = 35;
    let padLeft = 40;

    quarters.forEach((q, i) => {
        let x = padLeft + i * (w / 5);
        ctx.fillStyle = "#0d9488";
        ctx.fillRect(x, 140 - 70, barW, 70);

        ctx.fillStyle = "#d97706";
        ctx.fillRect(x, 140 - 70 - 25, barW, 25);

        ctx.fillStyle = "#1e293b";
        ctx.fillRect(x, 140 - 70 - 25 - 35, barW, 35);

        ctx.fillStyle = "#94a3b8";
        ctx.font = "10px sans-serif";
        ctx.fillText(q, x - 5, 160);
    });
}
