const DEMO_DATA = {
    project: {
        id: "550e8400-e29b-41d4-a716-446655440000",
        title: "My Project"
    },

    reports: [
        {
            date: "2026-07-26",
            total_events: 3210,
            unique_users: 840,
            unique_sessions: 1050,
            events_by_type: {
                page_view: 2200,
                signup: 640,
                purchase: 370
            }
        },
        {
            date: "2026-07-27",
            total_events: 4100,
            unique_users: 1020,
            unique_sessions: 1310,
            events_by_type: {
                page_view: 2800,
                signup: 800,
                purchase: 500
            }
        },
        {
            date: "2026-07-28",
            total_events: 3800,
            unique_users: 950,
            unique_sessions: 1200,
            events_by_type: {
                page_view: 2600,
                signup: 700,
                purchase: 500
            }
        },
        {
            date: "2026-07-29",
            total_events: 5200,
            unique_users: 1300,
            unique_sessions: 1600,
            events_by_type: {
                page_view: 3500,
                signup: 1100,
                purchase: 600
            }
        },
        {
            date: "2026-07-30",
            total_events: 4700,
            unique_users: 1180,
            unique_sessions: 1480,
            events_by_type: {
                page_view: 3100,
                signup: 1000,
                purchase: 600
            }
        },
        {
            date: "2026-07-31",
            total_events: 6100,
            unique_users: 1450,
            unique_sessions: 1780,
            events_by_type: {
                page_view: 4100,
                signup: 1300,
                purchase: 700
            }
        },
        {
            date: "2026-08-01",
            total_events: 5800,
            unique_users: 1380,
            unique_sessions: 1710,
            events_by_type: {
                page_view: 3900,
                signup: 1200,
                purchase: 700
            }
        },
        {
            date: "2026-08-02",
            total_events: 7200,
            unique_users: 1680,
            unique_sessions: 2050,
            events_by_type: {
                page_view: 4900,
                signup: 1500,
                purchase: 800
            }
        },
        {
            date: "2026-08-03",
            total_events: 6800,
            unique_users: 1590,
            unique_sessions: 1980,
            events_by_type: {
                page_view: 4600,
                signup: 1400,
                purchase: 800
            }
        },
        {
            date: "2026-08-04",
            total_events: 7500,
            unique_users: 1750,
            unique_sessions: 2140,
            events_by_type: {
                page_view: 5100,
                signup: 1600,
                purchase: 800
            }
        },
        {
            date: "2026-08-05",
            total_events: 8100,
            unique_users: 1910,
            unique_sessions: 2280,
            events_by_type: {
                page_view: 5500,
                signup: 1700,
                purchase: 900
            }
        }
    ]
};


/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function formatNumber(value) {
    return new Intl.NumberFormat("en-US").format(value);
}


function formatDate(dateString) {

    const date = new Date(dateString);

    return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric"
    });
}


/*
|--------------------------------------------------------------------------
| Summary
|--------------------------------------------------------------------------
*/

function renderSummary(reports) {

    const totalEvents = reports.reduce(
        (sum, report) => sum + report.total_events,
        0
    );

    /*
     * Important:
     *
     * unique_users and unique_sessions cannot simply be summed
     * across days if you want a true period-level unique count.
     *
     * For this MVP we display the sum of daily values.
     *
     * If you later need exact period-level uniques,
     * calculate them from raw events / dedicated aggregation.
     */

    const uniqueUsers = reports.reduce(
        (sum, report) => sum + report.unique_users,
        0
    );

    const uniqueSessions = reports.reduce(
        (sum, report) => sum + report.unique_sessions,
        0
    );


    document.getElementById("totalEvents").textContent =
        formatNumber(totalEvents);

    document.getElementById("uniqueUsers").textContent =
        formatNumber(uniqueUsers);

    document.getElementById("uniqueSessions").textContent =
        formatNumber(uniqueSessions);
}


/*
|--------------------------------------------------------------------------
| Chart
|--------------------------------------------------------------------------
*/

function renderChart(reports) {

    const svg = document.getElementById("eventsChart");

    const line = document.getElementById("chartLine");

    const area = document.getElementById("chartArea");

    const pointsGroup =
        document.getElementById("chartPoints");

    const yAxis =
        document.getElementById("yAxis");

    const xAxis =
        document.getElementById("xAxis");


    pointsGroup.innerHTML = "";
    yAxis.innerHTML = "";
    xAxis.innerHTML = "";


    if (!reports.length) {
        line.setAttribute("points", "");
        area.setAttribute("d", "");
        return;
    }


    const width = 1000;
    const height = 295;

    const padding = 10;

    const values = reports.map(
        report => report.total_events
    );

    const maxValue = Math.max(...values);

    const minValue = Math.min(...values);

    const range = maxValue - minValue || 1;


    const points = reports.map((report, index) => {

        const x =
            reports.length === 1
                ? width / 2
                : (index / (reports.length - 1)) *
                  (width - padding * 2) +
                  padding;

        const y =
            height -
            ((report.total_events - minValue) / range) *
                (height - padding * 2) -
            padding;

        return {
            x,
            y,
            report
        };
    });


    /*
     * Line
     */

    line.setAttribute(
        "points",
        points
            .map(point => `${point.x},${point.y}`)
            .join(" ")
    );


    /*
     * Area
     */

    const areaPath = [
        `M ${points[0].x} ${height}`,

        ...points.map(
            point => `L ${point.x} ${point.y}`
        ),

        `L ${points[points.length - 1].x} ${height}`,

        "Z"
    ].join(" ");

    area.setAttribute("d", areaPath);


    /*
     * Points
     */

    points.forEach((point) => {

        const circle =
            document.createElementNS(
                "http://www.w3.org/2000/svg",
                "circle"
            );

        circle.setAttribute("cx", point.x);

        circle.setAttribute("cy", point.y);

        circle.setAttribute("r", "4");

        circle.classList.add("chart-point");


        circle.addEventListener("mouseenter", (event) => {

            const tooltip =
                document.getElementById(
                    "chartTooltip"
                );

            const chartRect =
                document
                    .querySelector(".chart-area")
                    .getBoundingClientRect();

            const svgRect =
                svg.getBoundingClientRect();


            tooltip.style.display = "block";


            const left =
                svgRect.left -
                chartRect.left +
                (point.x / width) *
                    svgRect.width;


            const top =
                (point.y / height) *
                    svgRect.height;


            tooltip.style.left =
                `${left}px`;

            tooltip.style.top =
                `${top - 60}px`;


            tooltip.querySelector(
                ".tooltip-date"
            ).textContent =
                formatDate(point.report.date);


            tooltip.querySelector(
                ".tooltip-value"
            ).textContent =
                `${formatNumber(
                    point.report.total_events
                )} events`;
        });


        circle.addEventListener("mouseleave", () => {

            document.getElementById(
                "chartTooltip"
            ).style.display = "none";

        });


        pointsGroup.appendChild(circle);
    });


    /*
     * Y axis
     */

    const step = maxValue / 4;

    for (let i = 4; i >= 0; i--) {

        const value = Math.round(
            step * i
        );

        const element =
            document.createElement("span");

        element.textContent =
            formatNumber(value);

        yAxis.appendChild(element);
    }


    /*
     * X axis
     */

    const labelCount = Math.min(
        6,
        reports.length
    );

    const interval =
        Math.floor(
            (reports.length - 1) /
            (labelCount - 1)
        );


    for (
        let i = 0;
        i < reports.length;
        i += interval || 1
    ) {

        const label =
            document.createElement("span");

        label.textContent =
            formatDate(
                reports[i].date
            );

        xAxis.appendChild(label);
    }
}


/*
|--------------------------------------------------------------------------
| Event Types
|--------------------------------------------------------------------------
*/

function renderEventTypes(reports) {

    const container =
        document.getElementById(
            "eventTypes"
        );

    container.innerHTML = "";


    const totals = {};


    reports.forEach(report => {

        Object.entries(
            report.events_by_type || {}
        ).forEach(([type, value]) => {

            totals[type] =
                (totals[type] || 0) +
                value;

        });

    });


    const total =
        Object.values(totals)
            .reduce(
                (sum, value) =>
                    sum + value,
                0
            );


    const sorted =
        Object.entries(totals)
            .sort(
                ([, a], [, b]) =>
                    b - a
            );


    sorted.forEach(([type, value]) => {

        const percentage =
            total
                ? (value / total) * 100
                : 0;


        const row =
            document.createElement("div");

        row.className =
            "event-type-row";


        row.innerHTML = `
            <span class="event-type-name">
                ${escapeHtml(type)}
            </span>

            <div class="event-bar-wrapper">
                <div
                    class="event-bar"
                    style="width: ${percentage}%"
                ></div>
            </div>

            <span class="event-percentage">
                ${percentage.toFixed(1)}%
            </span>
        `;


        container.appendChild(row);
    });
}


/*
|--------------------------------------------------------------------------
| Table
|--------------------------------------------------------------------------
*/

function renderTable(reports) {

    const tbody =
        document.getElementById(
            "reportsTable"
        );

    tbody.innerHTML = "";


    const latestReports =
        [...reports]
            .sort(
                (a, b) =>
                    new Date(b.date) -
                    new Date(a.date)
            )
            .slice(0, 7);


    latestReports.forEach(report => {

        const row =
            document.createElement("tr");


        row.innerHTML = `
            <td>
                ${formatDate(report.date)}
            </td>

            <td>
                ${formatNumber(
                    report.total_events
                )}
            </td>

            <td>
                ${formatNumber(
                    report.unique_users
                )}
            </td>

            <td>
                ${formatNumber(
                    report.unique_sessions
                )}
            </td>
        `;


        tbody.appendChild(row);
    });
}


/*
|--------------------------------------------------------------------------
| Security helper
|--------------------------------------------------------------------------
*/

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/*
|--------------------------------------------------------------------------
| Load data
|--------------------------------------------------------------------------
*/

/*
|--------------------------------------------------------------------------
| Load data
|--------------------------------------------------------------------------
*/

async function loadReports() {

    const projectId =
        window.location.pathname
            .split("/")
            .filter(String)
            .pop();
    console.log(projectId)


    const response = await fetch(
        `/api/v1/analytics/${projectId}/daily`
    );



    if (!response.ok) {

        throw new Error(
            `Failed to load analytics: ${response.status}`
        );

    }


    const data = await response.json();
    console.log(data)
    return data.reports;
}



/*
|--------------------------------------------------------------------------
| Render
|--------------------------------------------------------------------------
*/

async function init() {

    try {

        const reports =
            await loadReports();

        renderSummary(reports);
        renderChart(reports);
        renderEventTypes(reports);
        renderTable(reports);

    } catch (error) {

        console.error(
            "Failed to load analytics:",
            error
        );

    }
}


/*
|--------------------------------------------------------------------------
| Navigation
|--------------------------------------------------------------------------
*/

document
    .getElementById(
        "hourlyLink"
    )
    .addEventListener(
        "click",
        event => {

            event.preventDefault();


            const pathParts =
                window.location.pathname
                    .split("/")
                    .filter(String);


            const projectId =
                pathParts[
                    pathParts.length - 1
                ];


            window.location.href =
                `/dashboard/${projectId}/hourly`;

        }
    );




/*
|--------------------------------------------------------------------------
| Refresh
|--------------------------------------------------------------------------
*/

document
    .getElementById("refreshButton")
    .addEventListener("click", async () => {

        const button =
            document.getElementById(
                "refreshButton"
            );

        button.style.transform =
            "rotate(360deg)";


        setTimeout(() => {

            button.style.transform = "";

        }, 400);


        await init();
    });


/*
|--------------------------------------------------------------------------
| Start
|--------------------------------------------------------------------------
*/

init();