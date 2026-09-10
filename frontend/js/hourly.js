/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function formatNumber(value) {

    return new Intl.NumberFormat(
        "en-US"
    ).format(value);

}


function formatHour(hour) {

    return `${String(hour).padStart(2, "0")}`;

}


function formatToday() {

    const date = new Date();

    return date.toLocaleDateString(
        "en-US",
        {
            month: "short",
            day: "numeric",
            year: "numeric"
        }
    );

}


/*
|--------------------------------------------------------------------------
| Summary
|--------------------------------------------------------------------------
*/

function renderSummary(reports) {

    const totalEvents =
        reports.reduce(
            (sum, report) =>
                sum + report.total_events,
            0
        );


    /*
     * Same MVP approach as Daily Analytics:
     *
     * We sum hourly values.
     *
     * Exact period-level unique users would require
     * aggregation from raw events.
     */

    const uniqueUsers =
        reports.reduce(
            (sum, report) =>
                sum + report.unique_users,
            0
        );


    const uniqueSessions =
        reports.reduce(
            (sum, report) =>
                sum + report.unique_sessions,
            0
        );


    document.getElementById(
        "totalEvents"
    ).textContent =
        formatNumber(totalEvents);


    document.getElementById(
        "uniqueUsers"
    ).textContent =
        formatNumber(uniqueUsers);


    document.getElementById(
        "uniqueSessions"
    ).textContent =
        formatNumber(uniqueSessions);

}


/*
|--------------------------------------------------------------------------
| Chart
|--------------------------------------------------------------------------
*/

function renderChart(reports) {

    const svg =
        document.getElementById(
            "eventsChart"
        );

    const line =
        document.getElementById(
            "chartLine"
        );

    const area =
        document.getElementById(
            "chartArea"
        );

    const pointsGroup =
        document.getElementById(
            "chartPoints"
        );

    const yAxis =
        document.getElementById(
            "yAxis"
        );

    const xAxis =
        document.getElementById(
            "xAxis"
        );


    pointsGroup.innerHTML = "";
    yAxis.innerHTML = "";
    xAxis.innerHTML = "";


    if (!reports.length) {

        line.setAttribute(
            "points",
            ""
        );

        area.setAttribute(
            "d",
            ""
        );

        return;
    }


    const width = 1000;
    const height = 295;
    const padding = 10;


    const values =
        reports.map(
            report =>
                report.total_events
        );


    const maxValue =
        Math.max(...values);


    /*
     * Keep the bottom of the graph at zero.
     */

    const range =
        maxValue || 1;


    const points =
        reports.map(
            (report, index) => {

                const x =
                    (index / 23) *
                    (width - padding * 2) +
                    padding;


                const y =
                    height -
                    (
                        report.total_events /
                        range
                    ) *
                    (height - padding * 2) -
                    padding;


                return {
                    x,
                    y,
                    report
                };

            }
        );


    /*
     * Line
     */

    line.setAttribute(
        "points",
        points
            .map(
                point =>
                    `${point.x},${point.y}`
            )
            .join(" ")
    );


    /*
     * Area
     */

    const areaPath = [

        `M ${points[0].x} ${height}`,

        ...points.map(
            point =>
                `L ${point.x} ${point.y}`
        ),

        `L ${points[points.length - 1].x} ${height}`,

        "Z"

    ].join(" ");


    area.setAttribute(
        "d",
        areaPath
    );


    /*
     * Points
     */

    points.forEach(
        point => {

            const circle =
                document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "circle"
                );


            circle.setAttribute(
                "cx",
                point.x
            );


            circle.setAttribute(
                "cy",
                point.y
            );


            circle.setAttribute(
                "r",
                "4"
            );


            circle.classList.add(
                "chart-point"
            );


            circle.addEventListener(
                "mouseenter",
                () => {

                    const tooltip =
                        document.getElementById(
                            "chartTooltip"
                        );


                    const chartRect =
                        document
                            .querySelector(
                                ".chart-area"
                            )
                            .getBoundingClientRect();


                    const svgRect =
                        svg.getBoundingClientRect();


                    tooltip.style.display =
                        "block";


                    const left =
                        svgRect.left -
                        chartRect.left +
                        (
                            point.x / width
                        ) *
                        svgRect.width;


                    const top =
                        (
                            point.y / height
                        ) *
                        svgRect.height;


                    tooltip.style.left =
                        `${left}px`;


                    tooltip.style.top =
                        `${top - 60}px`;


                    tooltip.querySelector(
                        ".tooltip-hour"
                    ).textContent =
                        formatHour(
                            point.report.hour
                        );


                    tooltip.querySelector(
                        ".tooltip-value"
                    ).textContent =
                        `${formatNumber(
                            point.report.total_events
                        )} events`;

                }
            );


            circle.addEventListener(
                "mouseleave",
                () => {

                    document.getElementById(
                        "chartTooltip"
                    ).style.display =
                        "none";

                }
            );


            pointsGroup.appendChild(
                circle
            );

        }
    );


    /*
     * Y axis
     */

    const step =
        maxValue / 4;


    for (
        let i = 4;
        i >= 0;
        i--
    ) {

        const value =
            Math.round(
                step * i
            );


        const element =
            document.createElement(
                "span"
            );


        element.textContent =
            formatNumber(value);


        yAxis.appendChild(
            element
        );

    }


    /*
     * X axis
     *
     * 00, 04, 08, 12, 16, 20, 24
     */

    const labels = [
        0,
        4,
        8,
        12,
        16,
        20,
        23
    ];


    labels.forEach(
        hour => {

            const label =
                document.createElement(
                    "span"
                );


            label.textContent =
                hour === 23
                    ? "24:00"
                    : formatHour(hour);


            xAxis.appendChild(
                label
            );

        }
    );

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


    reports.forEach(
        report => {

            Object.entries(
                report.events_by_type || {}
            ).forEach(
                ([type, value]) => {

                    totals[type] =
                        (
                            totals[type] || 0
                        ) + value;

                }
            );

        }
    );


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


    sorted.forEach(
        ([type, value]) => {

            const percentage =
                total
                    ? (
                        value / total
                    ) * 100
                    : 0;


            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "event-type-row";


            row.innerHTML = `

                <span
                    class="event-type-name"
                >
                    ${escapeHtml(type)}
                </span>

                <div
                    class="event-bar-wrapper"
                >

                    <div
                        class="event-bar"
                        style="width: ${percentage}%"
                    ></div>

                </div>

                <span
                    class="event-percentage"
                >
                    ${percentage.toFixed(1)}%
                </span>

            `;


            container.appendChild(
                row
            );

        }
    );

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


    reports
        .slice()
        .sort(
            (a, b) =>
                a.hour - b.hour
        )
        .forEach(
            report => {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${formatHour(
                            report.hour
                        )}
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


                tbody.appendChild(
                    row
                );

            }
        );

}



/*
|--------------------------------------------------------------------------
| Security
|--------------------------------------------------------------------------
*/

function escapeHtml(value) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}




/*
|--------------------------------------------------------------------------
| Load data
|--------------------------------------------------------------------------
*/

async function loadReports() {

    const pathParts =
        window.location.pathname
            .split("/")
            .filter(String);


    const projectId =
        pathParts[pathParts.length - 2];


    console.log(
        "Project ID:",
        projectId
    );


    document.getElementById(
        "projectIdLabel"
    ).textContent =
        `${projectId.slice(0, 8)}...`;


    const response =
        await fetch(
            `/api/v1/analytics/${projectId}/hourly`
        );


    if (!response.ok) {

        throw new Error(
            `Failed to load analytics: ${response.status}`
        );

    }


    const data =
        await response.json()
    console.log(data)


    console.log(
        "Hourly data:",
        data
    );


    return data.reports;

}

/*
|--------------------------------------------------------------------------
| Render
|--------------------------------------------------------------------------
*/

async function init() {

    try {

        document.getElementById(
            "todayLabel"
        ).textContent =
            formatToday();


        const reports =
            await loadReports();


        renderSummary(
            reports
        );

        renderChart(
            reports
        );

        renderEventTypes(
            reports
        );


        renderTable(
            reports
        );



    } catch (error) {

        console.error(
            "Failed to load hourly analytics:",
            error
        );

    }

}


/*
|--------------------------------------------------------------------------
| Refresh
|--------------------------------------------------------------------------
*/

document
    .getElementById(
        "refreshButton"
    )
    .addEventListener(
        "click",
        async () => {

            const button =
                document.getElementById(
                    "refreshButton"
                );


            button.style.transform =
                "rotate(360deg)";


            setTimeout(
                () => {

                    button.style.transform =
                        "";

                },
                400
            );


            await init();

        }
    );


/*
|--------------------------------------------------------------------------
| Navigation
|--------------------------------------------------------------------------
*/

document
    .getElementById(
        "overviewLink"
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
                    pathParts.length - 2
                ];


            window.location.href =
                `/dashboard/${projectId}`;

        }
    );


/*
|--------------------------------------------------------------------------
| Start
|--------------------------------------------------------------------------
*/

init();