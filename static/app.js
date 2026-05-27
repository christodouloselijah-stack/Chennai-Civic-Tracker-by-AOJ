document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const constituencySelect = document.getElementById("constituency-select");
    const updatesFeed = document.getElementById("updates-feed");
    const downloadBtn = document.getElementById("download-btn");
    const dashboardContent = document.getElementById("dashboard-content");
    const emptyState = document.getElementById("empty-state");
    const monthSelect = document.getElementById("month-select");

    const statTotal = document.getElementById("stat-total");
    const statReported = document.getElementById("stat-reported");
    const statInProgress = document.getElementById("stat-inprogress");
    const statResolved = document.getElementById("stat-resolved");

    const navDashboard = document.getElementById("nav-dashboard");
    const navReports = document.getElementById("nav-reports");
    const navTeams = document.getElementById("nav-teams");

    const reportsContent = document.getElementById("reports-content");
    const teamsContent = document.getElementById("teams-content");
    const reportsGrid = document.getElementById("reports-grid");
    const teamsGrid = document.getElementById("teams-grid");
    const teamSearch = document.getElementById("team-search");
    const headerTitle = document.querySelector("header h2");

    const updatesOfTheDaySection = document.getElementById("updates-of-the-day-section");
    const updatesOfTheDayGrid = document.getElementById("updates-of-the-day-grid");

    let statusChartInstance = null;
    let currentTab = "dashboard";

    // Set default month to current
    const now = new Date();
    monthSelect.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

    // Mock Teams Data
    const teamsData = [
        {
            name: "Dr. K. Vijayakarthikeyan, IAS",
            role: "Zonal Commissioner (North)",
            email: "comm.north@chennaicorporation.gov.in",
            phone: "+91 44 2561 9301",
            zones: "Royapuram, Harbour, Egmore",
            constituencyId: 7, // Royapuram
            status: "On Duty"
        },
        {
            name: "Smt. M. Priyadarshini",
            role: "Assistant Executive Engineer (Roads)",
            email: "aee.roads@chennaicorporation.gov.in",
            phone: "+91 94451 90022",
            zones: "Anna Nagar, Kolathur, Villivakkam",
            constituencyId: 3, // Kolathur
            status: "In Field"
        },
        {
            name: "Shri. R. Balaji",
            role: "Superintending Engineer (SWD)",
            email: "se.swd@chennaicorporation.gov.in",
            phone: "+91 94451 90115",
            zones: "Velachery, Mylapore, Saidapet",
            constituencyId: 16, // Velachery
            status: "On Duty"
        },
        {
            name: "Dr. Sandeep Kumar, IRS",
            role: "Regional Deputy Commissioner (Central)",
            email: "rdc.central@chennaicorporation.gov.in",
            phone: "+91 44 2561 9305",
            zones: "Thousand Lights, Virugampakkam, T. Nagar",
            constituencyId: 10, // Thousand Lights
            status: "On Duty"
        },
        {
            name: "Smt. K. Latha",
            role: "Zonal Officer (Zone 13)",
            email: "zo13@chennaicorporation.gov.in",
            phone: "+91 94451 90013",
            zones: "Velachery, Mylapore, Saidapet",
            constituencyId: 15, // Mylapore
            status: "In Field"
        },
        {
            name: "Shri. G. Vignesh",
            role: "Assistant Engineer (Sanitation)",
            email: "ae.sanitation@chennaicorporation.gov.in",
            phone: "+91 94451 90289",
            zones: "Thiru-Vi-Ka-Nagar, Egmore",
            constituencyId: 5, // Thiru-Vi-Ka-Nagar
            status: "On Leave"
        }
    ];

    // Fetch constituencies for dropdown
    fetch("/api/constituencies")
        .then(response => response.json())
        .then(data => {
            constituencySelect.innerHTML = '<option value="all">Overall Chennai (All Constituencies)</option>';
            data.forEach(c => {
                const option = document.createElement("option");
                option.value = c.id;
                option.textContent = c.name;
                constituencySelect.appendChild(option);
            });
            // Initial load of dashboard
            loadData();
        })
        .catch(err => {
            console.error("Error loading constituencies:", err);
            loadData();
        });

    // Dashboard Data Loading
    function loadData() {
        const constituencyId = constituencySelect.value || "all";
        const monthVal = monthSelect.value;
        updatesFeed.innerHTML = "";
        updatesOfTheDayGrid.innerHTML = "";
        updatesOfTheDaySection.classList.add("hidden");
        
        emptyState.classList.add("hidden");
        dashboardContent.classList.remove("hidden");
        downloadBtn.classList.remove("hidden");
        
        let statsUrl = "";
        let updatesUrl = "";
        
        if (constituencyId === "all") {
            statsUrl = `/api/stats/all_aggregate`;
            updatesUrl = `/api/updates/all`;
            
            downloadBtn.onclick = () => {
                let url = `/api/reports/all_aggregate/download`;
                if(monthVal) url += `?month=${monthVal}`;
                window.location.href = url;
            };
        } else {
            statsUrl = `/api/stats/${constituencyId}`;
            updatesUrl = `/api/updates/${constituencyId}`;
            
            downloadBtn.onclick = () => {
                let url = `/api/reports/${constituencyId}/download`;
                if(monthVal) url += `?month=${monthVal}`;
                window.location.href = url;
            };
        }

        if (monthVal) {
            statsUrl += (statsUrl.includes("?") ? "&" : "?") + `month=${monthVal}`;
            updatesUrl += (updatesUrl.includes("?") ? "&" : "?") + `month=${monthVal}`;
        }

        // Fetch Stats
        fetch(statsUrl)
            .then(res => res.json())
            .then(stats => {
                statTotal.textContent = stats.total;
                statReported.textContent = stats.reported;
                statInProgress.textContent = stats.in_progress;
                statResolved.textContent = stats.resolved;

                updateChart(stats.resolved, stats.in_progress, stats.reported);
            })
            .catch(err => console.error("Error loading stats:", err));

        // Fetch Feed
        fetch(updatesUrl)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    updatesFeed.innerHTML = "<p class='col-span-full text-gray-500 text-center py-8'>No updates available for the selected month.</p>";
                    return;
                }
                
                // Identify "Updates of the Day" (the most recent updates today)
                // Since our records are seeded with date = today, let's find the max date
                let maxDateStr = "";
                data.forEach(u => {
                    if (u.date > maxDateStr) maxDateStr = u.date;
                });
                
                const todayUpdates = data.filter(u => u.date === maxDateStr);
                if (todayUpdates.length > 0) {
                    updatesOfTheDaySection.classList.remove("hidden");
                    todayUpdates.slice(0, 3).forEach(update => {
                        const card = document.createElement("a");
                        card.href = update.article_url || "#";
                        card.target = "_blank";
                        card.rel = "noopener noreferrer";
                        card.className = "block bg-white rounded-xl shadow-md overflow-hidden border-2 border-indigo-100 transition duration-300 hover:shadow-lg hover:-translate-y-1 relative cursor-pointer";
                        
                        let statusColor = "bg-gray-100 text-gray-800";
                        if (update.status === "Resolved") statusColor = "bg-green-100 text-green-800";
                        else if (update.status === "In Progress") statusColor = "bg-yellow-100 text-yellow-800";
                        else if (update.status === "Reported") statusColor = "bg-red-100 text-red-800";

                        let sourceLabel = update.source ? `<span class="text-indigo-600 font-semibold text-xs bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">${update.source}</span>` : "";

                        card.innerHTML = `
                            <div class="h-44 overflow-hidden relative">
                                <img src="${update.image_url}" alt="Civic Update" class="w-full h-full object-cover transition duration-500 hover:scale-105" onerror="this.src='https://picsum.photos/400/300?random=${update.id}'">
                                <div class="absolute top-3 right-3 flex flex-col items-end gap-1">
                                    <span class="px-2.5 py-1 text-xs font-bold rounded-md ${statusColor} shadow-sm backdrop-blur-md bg-opacity-90">${update.status}</span>
                                </div>
                            </div>
                            <div class="p-5">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="text-xs text-gray-400 font-semibold">${update.date}</span>
                                    ${sourceLabel}
                                </div>
                                <h3 class="text-base font-bold text-gray-900 mb-2 line-clamp-1">${update.title}</h3>
                                <p class="text-sm text-gray-500 line-clamp-3">${update.description}</p>
                            </div>
                        `;
                        updatesOfTheDayGrid.appendChild(card);
                    });
                }
                
                // Populate regular feed
                data.forEach(update => {
                    const card = document.createElement("a");
                    card.href = update.article_url || "#";
                    card.target = "_blank";
                    card.rel = "noopener noreferrer";
                    card.className = "block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 transition duration-300 hover:shadow-md hover:-translate-y-1 cursor-pointer";
                    
                    let statusColor = "bg-gray-100 text-gray-800";
                    if (update.status === "Resolved") statusColor = "bg-green-100 text-green-800";
                    else if (update.status === "In Progress") statusColor = "bg-yellow-100 text-yellow-800";
                    else if (update.status === "Reported") statusColor = "bg-red-100 text-red-800";

                    let sourceLabel = update.source ? `<span class="text-indigo-600 font-semibold text-[10px] bg-indigo-50 px-2 py-0.5 rounded-full">${update.source}</span>` : "";

                    card.innerHTML = `
                        <div class="h-40 overflow-hidden relative">
                            <img src="${update.image_url}" alt="Civic Update" class="w-full h-full object-cover transition duration-500 hover:scale-105" onerror="this.src='https://picsum.photos/400/300?random=${update.id}'">
                            <div class="absolute top-3 right-3">
                                <span class="px-2.5 py-1 text-xs font-bold rounded-md ${statusColor} shadow-sm backdrop-blur-md bg-opacity-90">${update.status}</span>
                            </div>
                        </div>
                        <div class="p-4">
                            <div class="flex justify-between items-center mb-2">
                                <div class="flex items-center gap-1.5 text-xs text-gray-400 font-medium">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                    ${update.date}
                                </div>
                                ${sourceLabel}
                            </div>
                            <h3 class="text-base font-bold text-gray-900 mb-1 line-clamp-1">${update.title}</h3>
                            <p class="text-sm text-gray-500 line-clamp-2">${update.description}</p>
                        </div>
                    `;
                    updatesFeed.appendChild(card);
                });
            })
            .catch(err => console.error("Error loading updates feed:", err));
    }

    constituencySelect.addEventListener("change", loadData);
    monthSelect.addEventListener("change", () => {
        if (currentTab === "dashboard") {
            loadData();
        } else if (currentTab === "reports") {
            loadReports();
        }
    });

    // Navigation and Page Routing
    function switchTab(tab) {
        currentTab = tab;
        
        // Update tab styling
        [navDashboard, navReports, navTeams].forEach(el => {
            el.classList.remove("bg-indigo-800", "opacity-100");
            el.classList.add("opacity-75", "hover:bg-indigo-800");
        });

        // Hide all views
        dashboardContent.classList.add("hidden");
        emptyState.classList.add("hidden");
        reportsContent.classList.add("hidden");
        teamsContent.classList.add("hidden");

        // Header view default hides
        constituencySelect.classList.remove("hidden");
        monthSelect.classList.remove("hidden");
        downloadBtn.classList.add("hidden");

        if (tab === "dashboard") {
            navDashboard.classList.add("bg-indigo-800", "opacity-100");
            headerTitle.textContent = "Overview";
            loadData();
        } else if (tab === "reports") {
            navReports.classList.add("bg-indigo-800", "opacity-100");
            headerTitle.textContent = "Reports Center";
            constituencySelect.classList.add("hidden");
            reportsContent.classList.remove("hidden");
            loadReports();
        } else if (tab === "teams") {
            navTeams.classList.add("bg-indigo-800", "opacity-100");
            headerTitle.textContent = "Municipal Teams";
            constituencySelect.classList.add("hidden");
            monthSelect.classList.add("hidden");
            teamsContent.classList.remove("hidden");
            loadTeams();
        }
    }

    navDashboard.addEventListener("click", (e) => { e.preventDefault(); switchTab("dashboard"); });
    navReports.addEventListener("click", (e) => { e.preventDefault(); switchTab("reports"); });
    navTeams.addEventListener("click", (e) => { e.preventDefault(); switchTab("teams"); });

    // Reports Center logic
    function loadReports() {
        reportsGrid.innerHTML = `
            <div class="col-span-full flex justify-center py-12">
                <svg class="animate-spin h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>
        `;
        
        const monthVal = monthSelect.value;
        let url = "/api/all_stats";
        if (monthVal) url += `?month=${monthVal}`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                reportsGrid.innerHTML = "";
                if (data.length === 0) {
                    reportsGrid.innerHTML = "<p class='col-span-full text-center text-gray-500 py-8'>No constituencies found. Seed the database first.</p>";
                    return;
                }
                
                data.forEach(item => {
                    const card = document.createElement("div");
                    card.className = "bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between hover:shadow-md transition";
                    card.innerHTML = `
                        <div>
                            <h3 class="text-lg font-bold text-gray-900 mb-2">${item.name}</h3>
                            <div class="grid grid-cols-3 gap-2 text-center my-4">
                                <div class="bg-blue-50 p-2 rounded-lg">
                                    <span class="block text-xs font-semibold text-blue-700">Total</span>
                                    <span class="block text-lg font-bold text-blue-900">${item.total}</span>
                                </div>
                                <div class="bg-green-50 p-2 rounded-lg">
                                    <span class="block text-xs font-semibold text-green-700">Resolved</span>
                                    <span class="block text-lg font-bold text-green-900">${item.resolved}</span>
                                </div>
                                <div class="bg-red-50 p-2 rounded-lg">
                                    <span class="block text-xs font-semibold text-red-700">Open</span>
                                    <span class="block text-lg font-bold text-red-900">${item.reported + item.in_progress}</span>
                                </div>
                            </div>
                        </div>
                        <div class="mt-4 flex gap-2">
                            <button class="flex-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-50 border border-indigo-200 py-2 px-3 rounded-lg transition btn-view-dashboard" data-id="${item.id}">
                                Dashboard
                            </button>
                            <button class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold py-2 px-3 rounded-lg shadow-sm transition btn-download-pdf" data-id="${item.id}">
                                Export PDF
                            </button>
                        </div>
                    `;
                    reportsGrid.appendChild(card);
                });

                // Attach button actions
                document.querySelectorAll(".btn-view-dashboard").forEach(btn => {
                    btn.addEventListener("click", (e) => {
                        const id = e.currentTarget.getAttribute("data-id");
                        constituencySelect.value = id;
                        switchTab("dashboard");
                    });
                });

                document.querySelectorAll(".btn-download-pdf").forEach(btn => {
                    btn.addEventListener("click", (e) => {
                        const id = e.currentTarget.getAttribute("data-id");
                        let url = `/api/reports/${id}/download`;
                        if(monthVal) url += `?month=${monthVal}`;
                        window.location.href = url;
                    });
                });
            })
            .catch(err => {
                console.error("Error loading reports center:", err);
                reportsGrid.innerHTML = "<p class='col-span-full text-center text-red-500 py-8'>Failed to load constituency reports. Make sure database is seeded.</p>";
            });
    }

    // Teams Directory logic
    function loadTeams(filter = "") {
        teamsGrid.innerHTML = "";
        const query = filter.toLowerCase();
        
        const filteredTeams = teamsData.filter(member => 
            member.name.toLowerCase().includes(query) || 
            member.role.toLowerCase().includes(query) ||
            member.zones.toLowerCase().includes(query)
        );

        if (filteredTeams.length === 0) {
            teamsGrid.innerHTML = "<p class='col-span-full text-center text-gray-500 py-8'>No team members match your search.</p>";
            return;
        }

        filteredTeams.forEach(member => {
            const card = document.createElement("div");
            card.className = "bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between hover:shadow-md transition";
            
            let badgeColor = "bg-green-100 text-green-800";
            if (member.status === "In Field") badgeColor = "bg-yellow-100 text-yellow-800";
            else if (member.status === "On Leave") badgeColor = "bg-gray-100 text-gray-800";

            // Blank profile picture placeholder SVG
            const blankAvatarSvg = `
                <div class="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 border border-gray-200 flex-shrink-0 shadow-inner">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path>
                    </svg>
                </div>
            `;

            card.innerHTML = `
                <div>
                    <div class="flex items-start gap-4 mb-4">
                        ${blankAvatarSvg}
                        <div>
                            <h3 class="text-base font-bold text-gray-900">${member.name}</h3>
                            <p class="text-xs font-semibold text-indigo-600 mt-0.5">${member.role}</p>
                            <span class="inline-block mt-2 px-2 py-0.5 text-[10px] font-bold rounded-md ${badgeColor}">${member.status}</span>
                        </div>
                    </div>
                    <div class="space-y-2 text-xs text-gray-600 border-t border-gray-50 pt-3">
                        <div class="flex items-center gap-2">
                            <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                            <span>${member.email}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 001.07.747V21a2 2 0 01-2 2 17.25 17.25 0 01-14.75-14.75V5z"></path></svg>
                            <span>${member.phone}</span>
                        </div>
                        <div class="flex items-start gap-2 pt-1">
                            <svg class="w-3.5 h-3.5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                            <span class="line-clamp-2"><span class="font-medium text-gray-700">Assigned Areas:</span> ${member.zones}</span>
                        </div>
                    </div>
                </div>
                <div class="mt-5 pt-3 border-t border-gray-100 flex gap-2">
                    <button class="flex-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-50 border border-indigo-200 py-2 px-3 rounded-lg transition btn-view-member-zone" data-constituency-id="${member.constituencyId}">
                        View Area Updates
                    </button>
                    <a href="mailto:${member.email}" class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold text-center py-2 px-3 rounded-lg shadow-sm transition">
                        Contact Officer
                    </a>
                </div>
            `;
            teamsGrid.appendChild(card);
        });

        // Attach action for viewing area updates
        document.querySelectorAll(".btn-view-member-zone").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const constituencyId = e.currentTarget.getAttribute("data-constituency-id");
                constituencySelect.value = constituencyId;
                switchTab("dashboard");
            });
        });
    }

    teamSearch.addEventListener("input", (e) => {
        loadTeams(e.target.value);
    });

    const viewAllUpdates = document.getElementById("view-all-updates");
    if (viewAllUpdates) {
        viewAllUpdates.addEventListener("click", () => {
            switchTab("reports");
        });
    }

    // Chart.js helper
    function updateChart(resolved, inProgress, reported) {
        const ctx = document.getElementById('statusChart').getContext('2d');
        
        if (statusChartInstance) {
            statusChartInstance.destroy();
        }

        if(resolved === 0 && inProgress === 0 && reported === 0) {
             statusChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['No Data'],
                    datasets: [{
                        data: [1],
                        backgroundColor: ['#f3f4f6'],
                        borderWidth: 0
                    }]
                },
                options: {
                    cutout: '75%',
                    plugins: { tooltip: { enabled: false }, legend: { display: false } }
                }
            });
            return;
        }

        statusChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Resolved', 'In Progress', 'Reported'],
                datasets: [{
                    data: [resolved, inProgress, reported],
                    backgroundColor: [
                        '#10b981', // green-500
                        '#eab308', // yellow-500
                        '#ef4444'  // red-500
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: { family: "'Inter', sans-serif", size: 12 }
                        }
                    }
                },
                animation: { animateScale: true, animateRotate: true }
            }
        });
    }
});
