document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const dropdownBtnSelect = document.getElementById("dropdown-btn-select");
    const dropdownSelectedText = document.getElementById("dropdown-selected-text");
    const dropdownOptionsMenu = document.getElementById("dropdown-options-menu");
    const checkboxSelectAll = document.getElementById("checkbox-select-all");
    const checkboxOptionsList = document.getElementById("checkbox-options-list");

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

    const mobileNavDashboard = document.getElementById("mobile-nav-dashboard");
    const mobileNavReports = document.getElementById("mobile-nav-reports");
    const mobileNavTeams = document.getElementById("mobile-nav-teams");

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
    let currentUpdatesData = [];
    let hasAttemptedFallback = false;

    // Clickable Cards & Sub-Dashboard
    const cardTotal = document.getElementById("card-total");
    const cardReported = document.getElementById("card-reported");
    const cardInProgress = document.getElementById("card-inprogress");
    const cardResolved = document.getElementById("card-resolved");

    const mainDashboardView = document.getElementById("main-dashboard-view");
    const subDashboardView = document.getElementById("sub-dashboard-view");
    const btnBackToDashboard = document.getElementById("btn-back-to-dashboard");
    const subDashboardTitle = document.getElementById("sub-dashboard-title");
    const subDashboardSubtitle = document.getElementById("sub-dashboard-subtitle");
    const subDashboardBadge = document.getElementById("sub-dashboard-badge");
    const subDashboardCategories = document.getElementById("sub-dashboard-categories");
    const subDashboardFeed = document.getElementById("sub-dashboard-feed");
    const subDashboardFeedTitle = document.getElementById("sub-dashboard-feed-title");


    // Mock Teams Data
    const teamsData = [
        {
            name: "Dr. K. Vijayakarthikeyan, IAS",
            role: "Zonal Commissioner (North)",
            email: "comm.north@chennaicorporation.gov.in",
            phone: "+91 44 2561 9301",
            zones: "Royapuram, Harbour, Egmore",
            constituencyId: 22, // Royapuram
            status: "On Duty"
        },
        {
            name: "Smt. M. Priyadarshini",
            role: "Assistant Executive Engineer (Roads)",
            email: "aee.roads@chennaicorporation.gov.in",
            phone: "+91 94451 90022",
            zones: "Anna Nagar, Kolathur, Villivakkam",
            constituencyId: 20, // Kolathur
            status: "In Field"
        },
        {
            name: "Shri. R. Balaji",
            role: "Superintending Engineer (SWD)",
            email: "se.swd@chennaicorporation.gov.in",
            phone: "+91 94451 90115",
            zones: "Velachery, Mylapore, Saidapet",
            constituencyId: 15, // Velachery
            status: "On Duty"
        },
        {
            name: "Dr. Sandeep Kumar, IRS",
            role: "Regional Deputy Commissioner (Central)",
            email: "rdc.central@chennaicorporation.gov.in",
            phone: "+91 44 2561 9305",
            zones: "Thousand Lights, Virugampakkam, T. Nagar",
            constituencyId: 27, // Thousand Lights
            status: "On Duty"
        },
        {
            name: "Smt. K. Latha",
            role: "Zonal Officer (Zone 13)",
            email: "zo13@chennaicorporation.gov.in",
            phone: "+91 94451 90013",
            zones: "Velachery, Mylapore, Saidapet",
            constituencyId: 14, // Mylapore
            status: "In Field"
        },
        {
            name: "Shri. G. Vignesh",
            role: "Assistant Engineer (Sanitation)",
            email: "ae.sanitation@chennaicorporation.gov.in",
            phone: "+91 94451 90289",
            zones: "Thiru-Vi-Ka-Nagar, Egmore",
            constituencyId: 21, // Thiru-Vi-Ka-Nagar
            status: "On Leave"
        },
        {
            name: "Shri. M. Prathap, IAS",
            role: "Corporation Commissioner (Coimbatore)",
            email: "commr.coimbatore@tn.gov.in",
            phone: "+91 422 230 2491",
            zones: "Coimbatore (South), Coimbatore (North), Singanallur",
            constituencyId: 122, // Coimbatore (South)
            status: "On Duty"
        },
        {
            name: "Dr. L. Madhubalan, IAS",
            role: "Corporation Commissioner (Madurai)",
            email: "commr.madurai@tn.gov.in",
            phone: "+91 452 253 9161",
            zones: "Madurai Central, Madurai East, Melur",
            constituencyId: 193, // Madurai Central
            status: "In Field"
        },
        {
            name: "Smt. R. Vaithinathan, IAS",
            role: "Corporation Commissioner (Trichy)",
            email: "commr.trichy@tn.gov.in",
            phone: "+91 431 241 5437",
            zones: "Tiruchirappalli (West), Tiruchirappalli (East)",
            constituencyId: 140, // Tiruchirappalli (West)
            status: "On Duty"
        },
        {
            name: "Shri. T. Christuraj, IAS",
            role: "Corporation Commissioner (Salem)",
            email: "commr.salem@tn.gov.in",
            phone: "+91 427 221 2100",
            zones: "Salem (North), Salem (West), Salem (South)",
            constituencyId: 89, // Salem (North)
            status: "On Duty"
        }
    ];

    // Toggle dropdown open/close
    if (dropdownBtnSelect) {
        dropdownBtnSelect.addEventListener("click", (e) => {
            e.stopPropagation();
            if (dropdownOptionsMenu) dropdownOptionsMenu.classList.toggle("hidden");
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
        const container = document.getElementById("constituency-dropdown-container");
        if (container && !container.contains(e.target)) {
            if (dropdownOptionsMenu) dropdownOptionsMenu.classList.add("hidden");
        }
    });

    let allConstituencies = [];
    let selectedConstituencyIds = [];

    // Update the visual selection summary text
    function updateSelectedText() {
        if (!dropdownSelectedText || !checkboxSelectAll) return;
        const checkedBoxes = document.querySelectorAll(".constituency-checkbox:checked");
        const totalCount = document.querySelectorAll(".constituency-checkbox").length;
        
        if (checkedBoxes.length === totalCount && totalCount > 0) {
            dropdownSelectedText.textContent = "All Tamil Nadu (All)";
            checkboxSelectAll.checked = true;
            selectedConstituencyIds = []; // Empty represents overall aggregate
        } else if (checkedBoxes.length === 0) {
            dropdownSelectedText.textContent = "No Constituency Selected";
            checkboxSelectAll.checked = false;
            selectedConstituencyIds = ["none"];
        } else {
            checkboxSelectAll.checked = false;
            selectedConstituencyIds = Array.from(checkedBoxes).map(cb => cb.value);
            
            // Check if exactly one district is fully selected
            const districtGroups = {};
            document.querySelectorAll(".constituency-checkbox").forEach(cb => {
                const dist = cb.getAttribute("data-district");
                if (!districtGroups[dist]) districtGroups[dist] = { total: 0, checked: 0 };
                districtGroups[dist].total++;
                if (cb.checked) districtGroups[dist].checked++;
            });
            
            const fullySelectedDistricts = Object.keys(districtGroups).filter(d => districtGroups[d].checked === districtGroups[d].total);
            const partiallySelectedDistricts = Object.keys(districtGroups).filter(d => districtGroups[d].checked > 0 && districtGroups[d].checked < districtGroups[d].total);
            
            if (fullySelectedDistricts.length === 1 && partiallySelectedDistricts.length === 0) {
                dropdownSelectedText.textContent = `${fullySelectedDistricts[0]} (All)`;
            } else if (checkedBoxes.length <= 2) {
                dropdownSelectedText.textContent = Array.from(checkedBoxes).map(cb => cb.getAttribute("data-name")).join(", ");
            } else {
                dropdownSelectedText.textContent = `${checkedBoxes.length} Selected`;
            }
        }
    }

    // Toggle All Checkboxes
    if (checkboxSelectAll) {
        checkboxSelectAll.addEventListener("change", () => {
            const isChecked = checkboxSelectAll.checked;
            document.querySelectorAll(".constituency-checkbox").forEach(cb => {
                cb.checked = isChecked;
            });
            document.querySelectorAll(".district-checkbox").forEach(cb => {
                cb.checked = isChecked;
            });
            updateSelectedText();
            loadData();
        });
    }

    // Dropdown Search Input
    const dropdownSearch = document.getElementById("dropdown-search");
    if (dropdownSearch) {
        dropdownSearch.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            const groupContainers = document.querySelectorAll(".district-group-container");
            
            groupContainers.forEach(container => {
                const districtName = container.getAttribute("data-district-name").toLowerCase();
                const items = container.querySelectorAll(".constituency-item");
                let hasVisibleItem = false;
                
                items.forEach(item => {
                    const cName = item.getAttribute("data-constituency-name").toLowerCase();
                    if (cName.includes(query) || districtName.includes(query)) {
                        item.style.display = "flex";
                        hasVisibleItem = true;
                    } else {
                        item.style.display = "none";
                    }
                });
                
                if (hasVisibleItem || districtName.includes(query)) {
                    container.style.display = "block";
                    // Automatically expand if typing search query
                    const listContainer = container.querySelector(".constituency-list-container");
                    const toggleIcon = container.querySelector(".toggle-icon");
                    if (query !== "" && listContainer && listContainer.classList.contains("hidden")) {
                        listContainer.classList.remove("hidden");
                        if (toggleIcon) toggleIcon.classList.add("rotate-90");
                    }
                } else {
                    container.style.display = "none";
                }
            });
        });
    }

    // Fetch constituencies for dropdown
    fetch("/api/constituencies")
        .then(response => response.json())
        .then(data => {
            allConstituencies = data;
            
            if (checkboxOptionsList) {
                checkboxOptionsList.innerHTML = "";
                
                // Group by district
                const grouped = {};
                data.forEach(c => {
                    const dist = c.district || "Other";
                    if (!grouped[dist]) grouped[dist] = [];
                    grouped[dist].push(c);
                });
                
                // Sort districts
                const sortedDistricts = Object.keys(grouped).sort();
                
                sortedDistricts.forEach(distName => {
                    const distGroup = document.createElement("div");
                    distGroup.className = "district-group-container border-b border-gray-100 pb-2 mb-2 last:border-b-0";
                    distGroup.setAttribute("data-district-name", distName);
                    
                    // District Header row
                    const headerRow = document.createElement("div");
                    headerRow.className = "flex items-center justify-between px-2 py-1 bg-gray-50 hover:bg-gray-100 rounded cursor-pointer select-none";
                    
                    const leftContainer = document.createElement("label");
                    leftContainer.className = "flex items-center gap-2 cursor-pointer flex-1 py-1";
                    leftContainer.innerHTML = `
                        <input type="checkbox" class="district-checkbox rounded text-indigo-600 focus:ring-indigo-500 border-gray-300" data-district="${distName}" checked>
                        <span class="text-xs font-bold text-gray-800">${distName}</span>
                    `;
                    
                    const toggleBtn = document.createElement("button");
                    toggleBtn.className = "p-1 hover:bg-gray-200 rounded text-gray-500 focus:outline-none flex items-center justify-center";
                    toggleBtn.innerHTML = `
                        <svg class="toggle-icon w-3 h-3 transform transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    `;
                    
                    headerRow.appendChild(leftContainer);
                    headerRow.appendChild(toggleBtn);
                    
                    // Constituency sub-list container (hidden by default to avoid huge lists scrolling forever)
                    // We can default expand the first few or expand when searched. Let's make them hidden by default for cleaner UI.
                    const listContainer = document.createElement("div");
                    listContainer.className = "constituency-list-container pl-6 pt-1 space-y-1 hidden";
                    
                    grouped[distName].forEach(c => {
                        const item = document.createElement("label");
                        item.className = "constituency-item flex items-center gap-2 px-2 py-1 hover:bg-indigo-50 rounded cursor-pointer text-xs font-medium text-gray-600";
                        item.setAttribute("data-constituency-name", c.name);
                        item.innerHTML = `
                            <input type="checkbox" class="constituency-checkbox rounded text-indigo-600 focus:ring-indigo-500 border-gray-300" value="${c.id}" data-district="${distName}" data-name="${c.name}" checked>
                            <span>${c.name}</span>
                        `;
                        listContainer.appendChild(item);
                    });
                    
                    distGroup.appendChild(headerRow);
                    distGroup.appendChild(listContainer);
                    checkboxOptionsList.appendChild(distGroup);
                    
                    // Bind collapse toggle
                    const toggleCollapse = (e) => {
                        if (e) e.stopPropagation();
                        listContainer.classList.toggle("hidden");
                        const icon = toggleBtn.querySelector(".toggle-icon");
                        if (icon) icon.classList.toggle("rotate-90");
                    };
                    
                    toggleBtn.addEventListener("click", toggleCollapse);
                    // Clicking the text label of header should expand too, but NOT clicking the checkbox
                    headerRow.addEventListener("click", (e) => {
                        if (e.target.tagName !== "INPUT" && !toggleBtn.contains(e.target)) {
                            toggleCollapse();
                        }
                    });
                });
                
                // Bind individual constituency checkbox changes
                document.querySelectorAll(".constituency-checkbox").forEach(cb => {
                    cb.addEventListener("change", () => {
                        const dist = cb.getAttribute("data-district");
                        const distCheckbox = document.querySelector(`.district-checkbox[data-district="${dist}"]`);
                        
                        // Check if all in district are checked
                        const siblings = document.querySelectorAll(`.constituency-checkbox[data-district="${dist}"]`);
                        const allChecked = Array.from(siblings).every(s => s.checked);
                        if (distCheckbox) distCheckbox.checked = allChecked;
                        
                        updateSelectedText();
                        loadData();
                    });
                });
                
                // Bind district checkbox changes
                document.querySelectorAll(".district-checkbox").forEach(db => {
                    db.addEventListener("change", () => {
                        const dist = db.getAttribute("data-district");
                        const siblings = document.querySelectorAll(`.constituency-checkbox[data-district="${dist}"]`);
                        siblings.forEach(s => s.checked = db.checked);
                        
                        updateSelectedText();
                        loadData();
                    });
                });
            }

            updateSelectedText();
            loadData();
        })
        .catch(err => {
            console.error("Error loading constituencies:", err);
            loadData();
        });

    // Dashboard Data Loading
    function loadData() {
        const monthVal = monthSelect.value;
        updatesFeed.innerHTML = "";
        updatesOfTheDayGrid.innerHTML = "";
        updatesOfTheDaySection.classList.add("hidden");
        
        emptyState.classList.add("hidden");
        dashboardContent.classList.remove("hidden");
        downloadBtn.classList.remove("hidden");
        
        let updatesUrl = `/api/updates/all`;
        if (monthVal) {
            updatesUrl += `?month=${monthVal}`;
        }

        // Configure Export button
        downloadBtn.onclick = () => {
            const checkedBoxes = document.querySelectorAll(".constituency-checkbox:checked");
            let url = `/api/reports/all_aggregate/download`;
            if (checkedBoxes.length === 1) {
                url = `/api/reports/${checkedBoxes[0].value}/download`;
            }
            if (monthVal) url += (url.includes("?") ? "&" : "?") + `month=${monthVal}`;
            window.location.href = url;
        };

        fetch(updatesUrl)
            .then(response => response.json())
            .then(fetchedData => {
                // Fallback to the latest month containing data if the current selection has no data on initial load
                if (fetchedData.length === 0 && !hasAttemptedFallback && monthVal) {
                    hasAttemptedFallback = true;
                    fetch(`/api/updates/all`)
                        .then(r => r.json())
                        .then(allData => {
                            if (allData && allData.length > 0) {
                                const latestDate = allData[0].date;
                                if (latestDate) {
                                    const parts = latestDate.split("-");
                                    monthSelect.value = `${parts[0]}-${parts[1]}`;
                                    loadData();
                                }
                            }
                        })
                        .catch(e => console.error("Fallback error:", e));
                    return;
                }

                let filteredData = fetchedData;
                if (checkboxSelectAll && !checkboxSelectAll.checked) {
                    if (selectedConstituencyIds.includes("none")) {
                        filteredData = [];
                    } else {
                        const stringIds = selectedConstituencyIds.map(String);
                        filteredData = fetchedData.filter(u => stringIds.includes(String(u.constituency_id)));
                    }
                }

                currentUpdatesData = filteredData;
                mainDashboardView.classList.remove("hidden");
                subDashboardView.classList.add("hidden");

                // Compute stats dynamically
                const total = filteredData.length;
                const resolved = filteredData.filter(u => u.status === "Resolved").length;
                const in_progress = filteredData.filter(u => u.status === "In Progress").length;
                const reported = filteredData.filter(u => u.status === "Reported").length;

                statTotal.textContent = total;
                statReported.textContent = reported;
                statInProgress.textContent = in_progress;
                statResolved.textContent = resolved;

                updateChart(resolved, in_progress, reported);

                const data = filteredData;

                if (data.length === 0) {
                    updatesFeed.innerHTML = "<p class='col-span-full text-gray-500 text-center py-8'>No updates available for the selection.</p>";
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
                                <img src="${update.image_url}" referrerpolicy="no-referrer" alt="Civic Update" class="w-full h-full object-cover transition duration-500 hover:scale-105" onerror="this.src='https://picsum.photos/400/300?random=${update.id}'">
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
                            <img src="${update.image_url}" referrerpolicy="no-referrer" alt="Civic Update" class="w-full h-full object-cover transition duration-500 hover:scale-105" onerror="this.src='https://picsum.photos/400/300?random=${update.id}'">
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

    const dropdownContainer = document.getElementById("constituency-dropdown-container");

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
        
        // Update desktop tab styling
        [navDashboard, navReports, navTeams].forEach(el => {
            el.classList.remove("bg-indigo-800", "opacity-100");
            el.classList.add("opacity-75", "hover:bg-indigo-800");
        });

        // Update mobile tab styling
        [mobileNavDashboard, mobileNavReports, mobileNavTeams].forEach(el => {
            if (el) {
                el.classList.remove("opacity-100");
                el.classList.add("opacity-60");
            }
        });

        // Hide all views
        dashboardContent.classList.add("hidden");
        emptyState.classList.add("hidden");
        reportsContent.classList.add("hidden");
        teamsContent.classList.add("hidden");

        // Header view default hides
        if (dropdownContainer) dropdownContainer.classList.remove("hidden");
        monthSelect.classList.remove("hidden");
        downloadBtn.classList.add("hidden");

        if (tab === "dashboard") {
            navDashboard.classList.add("bg-indigo-800", "opacity-100");
            if (mobileNavDashboard) mobileNavDashboard.classList.add("opacity-100");
            if (mobileNavDashboard) mobileNavDashboard.classList.remove("opacity-60");
            headerTitle.textContent = "Overview";
            loadData();
        } else if (tab === "reports") {
            navReports.classList.add("bg-indigo-800", "opacity-100");
            if (mobileNavReports) mobileNavReports.classList.add("opacity-100");
            if (mobileNavReports) mobileNavReports.classList.remove("opacity-60");
            headerTitle.textContent = "Reports Center";
            if (dropdownContainer) dropdownContainer.classList.add("hidden");
            reportsContent.classList.remove("hidden");
            loadReports();
        } else if (tab === "teams") {
            navTeams.classList.add("bg-indigo-800", "opacity-100");
            if (mobileNavTeams) mobileNavTeams.classList.add("opacity-100");
            if (mobileNavTeams) mobileNavTeams.classList.remove("opacity-60");
            headerTitle.textContent = "Municipal Teams";
            if (dropdownContainer) dropdownContainer.classList.add("hidden");
            monthSelect.classList.add("hidden");
            teamsContent.classList.remove("hidden");
            loadTeams();
        }
    }

    navDashboard.addEventListener("click", (e) => { e.preventDefault(); switchTab("dashboard"); });
    navReports.addEventListener("click", (e) => { e.preventDefault(); switchTab("reports"); });
    navTeams.addEventListener("click", (e) => { e.preventDefault(); switchTab("teams"); });

    if (mobileNavDashboard) mobileNavDashboard.addEventListener("click", (e) => { e.preventDefault(); switchTab("dashboard"); });
    if (mobileNavReports) mobileNavReports.addEventListener("click", (e) => { e.preventDefault(); switchTab("reports"); });
    if (mobileNavTeams) mobileNavTeams.addEventListener("click", (e) => { e.preventDefault(); switchTab("teams"); });

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
                        if (checkboxSelectAll) checkboxSelectAll.checked = false;
                        document.querySelectorAll(".constituency-checkbox").forEach(cb => {
                            cb.checked = (String(cb.value) === String(id));
                        });
                        updateSelectedText();
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
                if (checkboxSelectAll) checkboxSelectAll.checked = false;
                document.querySelectorAll(".constituency-checkbox").forEach(cb => {
                    cb.checked = (String(cb.value) === String(constituencyId));
                });
                updateSelectedText();
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

    // Dynamic Category Classifier
    function getCategory(title, description) {
        const text = (title + " " + description).toLowerCase();
        if (text.includes("drain") || text.includes("water") || text.includes("flood") || text.includes("sew") || text.includes("canal")) {
            return "Water & Drainage";
        }
        if (text.includes("road") || text.includes("pothole") || text.includes("pavement") || text.includes("bridge") || text.includes("street") || text.includes("flyover")) {
            return "Roads & Traffic";
        }
        if (text.includes("garbage") || text.includes("waste") || text.includes("trash") || text.includes("clean") || text.includes("dump") || text.includes("litter")) {
            return "Garbage & Sanitation";
        }
        if (text.includes("light") || text.includes("power") || text.includes("electr") || text.includes("dark") || text.includes("wire") || text.includes("cable")) {
            return "Electricity & Power";
        }
        return "General Civic Issues";
    }

    // Render Sub-Dashboard View
    function showSubDashboard(status) {
        mainDashboardView.classList.add("hidden");
        subDashboardView.classList.remove("hidden");

        const filtered = status === "Total" 
            ? currentUpdatesData 
            : currentUpdatesData.filter(u => u.status === status);

        // Update badge design
        let badgeColor = "bg-indigo-100 text-indigo-800";
        if (status === "Resolved") badgeColor = "bg-green-100 text-green-800";
        else if (status === "In Progress") badgeColor = "bg-yellow-100 text-yellow-800";
        else if (status === "Reported") badgeColor = "bg-red-100 text-red-800";

        subDashboardBadge.className = `inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm ${badgeColor}`;
        subDashboardBadge.textContent = status === "Total" ? "All Issues" : status;
        
        subDashboardTitle.textContent = status === "Total" 
            ? "Total Civic Issues Overview" 
            : `${status} Issues Overview`;

        subDashboardSubtitle.textContent = `Showing details for ${filtered.length} issues in the current selection.`;
        subDashboardFeedTitle.textContent = `${status} Issues Feed (${filtered.length})`;

        // 1. Calculate Category breakdown
        const categoriesCount = {
            "Water & Drainage": 0,
            "Roads & Traffic": 0,
            "Garbage & Sanitation": 0,
            "Electricity & Power": 0,
            "General Civic Issues": 0
        };

        filtered.forEach(u => {
            const cat = getCategory(u.title, u.description);
            categoriesCount[cat] = (categoriesCount[cat] || 0) + 1;
        });

        subDashboardCategories.innerHTML = "";
        Object.entries(categoriesCount).forEach(([catName, count]) => {
            const percentage = filtered.length > 0 ? (count / filtered.length) * 100 : 0;
            let barColor = "bg-indigo-600";
            if (status === "Resolved") barColor = "bg-green-500";
            else if (status === "In Progress") barColor = "bg-yellow-500";
            else if (status === "Reported") barColor = "bg-red-500";

            const row = document.createElement("div");
            row.innerHTML = `
                <div class="flex justify-between items-center text-xs font-medium text-gray-700 mb-1">
                    <span>${catName}</span>
                    <span class="font-bold">${count} (${Math.round(percentage)}%)</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-2">
                    <div class="${barColor} h-2 rounded-full" style="width: ${percentage}%"></div>
                </div>
            `;
            subDashboardCategories.appendChild(row);
        });

        // 2. Populate detailed list
        subDashboardFeed.innerHTML = "";
        if (filtered.length === 0) {
            subDashboardFeed.innerHTML = "<p class='col-span-full text-center text-gray-500 py-8'>No issues found under this status.</p>";
            return;
        }

        filtered.forEach(update => {
            const card = document.createElement("a");
            card.href = update.article_url || "#";
            card.target = "_blank";
            card.rel = "noopener noreferrer";
            card.className = "block bg-gray-50 hover:bg-indigo-50 border border-gray-100 rounded-xl overflow-hidden p-4 transition hover:shadow-sm";
            
            let statusBadgeColor = "bg-gray-100 text-gray-800";
            if (update.status === "Resolved") statusBadgeColor = "bg-green-100 text-green-800";
            else if (update.status === "In Progress") statusBadgeColor = "bg-yellow-100 text-yellow-800";
            else if (update.status === "Reported") statusBadgeColor = "bg-red-100 text-red-800";

            let sourceLabel = update.source ? `<span class="text-indigo-600 font-semibold text-[10px] bg-white px-2 py-0.5 rounded-full border border-indigo-100">${update.source}</span>` : "";

            card.innerHTML = `
                <div class="flex gap-4">
                    <div class="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200 border border-gray-100">
                        <img src="${update.image_url}" referrerpolicy="no-referrer" alt="Thumbnail" class="w-full h-full object-cover" onerror="this.src='https://picsum.photos/150/150?random=${update.id}'">
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between gap-2 mb-1.5">
                            <span class="text-[10px] text-gray-400 font-semibold">${update.date}</span>
                            <div class="flex items-center gap-1">
                                ${sourceLabel}
                                <span class="px-2 py-0.5 text-[9px] font-bold rounded-md ${statusBadgeColor}">${update.status}</span>
                            </div>
                        </div>
                        <h4 class="text-sm font-bold text-gray-900 line-clamp-1 mb-1">${update.title}</h4>
                        <p class="text-xs text-gray-500 line-clamp-2">${update.description}</p>
                    </div>
                </div>
            `;
            subDashboardFeed.appendChild(card);
        });
    }

    // Attach card listeners
    if (cardTotal) cardTotal.addEventListener("click", () => showSubDashboard("Total"));
    if (cardReported) cardReported.addEventListener("click", () => showSubDashboard("Reported"));
    if (cardInProgress) cardInProgress.addEventListener("click", () => showSubDashboard("In Progress"));
    if (cardResolved) cardResolved.addEventListener("click", () => showSubDashboard("Resolved"));

    if (btnBackToDashboard) {
        btnBackToDashboard.addEventListener("click", (e) => {
            e.preventDefault();
            subDashboardView.classList.add("hidden");
            mainDashboardView.classList.remove("hidden");
        });
    }
});
