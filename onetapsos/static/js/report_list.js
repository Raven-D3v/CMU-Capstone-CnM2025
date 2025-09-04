function fetchReports() {
    const q = document.querySelector('input[name="q"]')?.value || "";
    const date_filter = document.querySelector('input[name="date_filter"]')?.value || "";
    const location_filter = document.querySelector('select[name="location_filter"]')?.value || "";
    const crime_category_filter = document.querySelector('select[name="crime_category_filter"]')?.value || "";
    const status_filter = document.querySelector('select[name="status_filter"]')?.value || "";

    let url = `${window.REPORT_LIST_URL}?q=${encodeURIComponent(q)}&date_filter=${encodeURIComponent(date_filter)}&location_filter=${encodeURIComponent(location_filter)}&crime_category_filter=${encodeURIComponent(crime_category_filter)}`;
    if (status_filter) url += `&status_filter=${encodeURIComponent(status_filter)}`;

    fetch(url, { credentials: "include" })
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("reportTableBody");
            const cardBody = document.getElementById("reportCardBody");
            tableBody.innerHTML = "";
            cardBody.innerHTML = "";

            let colspan = 4; // ID, Date, Location, Sender
            if (window.PAGE_CONTEXT.show_unclassified) colspan += 1; // Message
            else colspan += 2; // Crime Category + Status
            if (window.PAGE_CONTEXT.show_resolved) colspan += 3; // Responded, Officers, Resolved
            if (window.PAGE_CONTEXT.show_rejected) colspan += 3; // Rejected On, Message, Days Remaining
            colspan += 2; // Actions

            if (!data.reports || data.reports.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="${colspan}" class="p-3 border-b text-center">No reports found.</td></tr>`;
                cardBody.innerHTML = `<p class="text-center text-gray-500">No reports found.</p>`;
                return;
            }

            data.reports.forEach(r => {
                let officers = r.officers_responded && r.officers_responded.length > 0 
                    ? r.officers_responded.join(", ")
                    : "--";

                const viewUrl = window.PAGE_CONTEXT.show_unclassified 
                    ? `${window.UNCLASSIFIED_VIEW_BASE}${r.report_id}/` 
                    : `/reports/view/${r.report_id}/`;
                const editUrl = `/reports/edit/${r.report_id}/`;

                // --- DESKTOP TABLE ROW ---
                let row = `<tr>
                    <td class="p-3 border-b">${r.report_id}</td>
                    <td class="p-3 border-b">${r.date_time_reported}</td>
                    <td class="p-3 border-b">${r.location}</td>
                    <td class="p-3 border-b">${r.sender}</td>`;

                if (window.PAGE_CONTEXT.show_unclassified) {
                    row += `<td class="p-3 border-b">${r.message || "--"}</td>`;
                } else {
                    row += `<td class="p-3 border-b">${r.crime_category || "Unknown"}</td>
                            <td class="p-3 border-b">${r.status}</td>`;
                }

                if (window.PAGE_CONTEXT.show_resolved) {
                    row += `<td class="p-3 border-b">${r.date_time_responded || "--"}</td>
                            <td class="p-3 border-b">${officers}</td>
                            <td class="p-3 border-b">${r.date_time_resolved || "--"}</td>`;
                }

                if (window.PAGE_CONTEXT.show_rejected) {
                    row += `<td class="p-3 border-b">${r.date_time_rejected || "--"}</td>
                            <td class="p-3 border-b">${r.message || "--"}</td>
                            <td class="p-3 border-b">${r.days_remaining !== null ? r.days_remaining + " day" + (r.days_remaining !== 1 ? "s" : "") : "--"}</td>`;
                }

                // --- ACTIONS ---
                row += `<td class="p-3 border-b text-center">
                            <a href="${viewUrl}">
                                <button class="px-2 py-1 bg-[#4B7289] text-white rounded hover:bg-[#6B7280]">VIEW</button>
                            </a>
                        </td>`;

                // Only show EDIT button if NOT unclassified page
                if (!window.PAGE_CONTEXT.show_unclassified) {
                    row += `<td class="p-3 border-b text-center">
                                <a href="${editUrl}">
                                    <button class="px-2 py-1 bg-[#4B7289] text-white rounded hover:bg-[#6B7280]">EDIT</button>
                                </a>
                            </td>`;
                }

                row += `</tr>`;
                tableBody.innerHTML += row;

                // --- MOBILE CARD ---
                let card = `<div class="bg-white shadow-md rounded-lg p-4 border">
                    <p><strong>ID:</strong> ${r.report_id}</p>
                    <p><strong>Date:</strong> ${r.date_time_reported}</p>
                    <p><strong>Location:</strong> ${r.location}</p>
                    <p><strong>Sender:</strong> ${r.sender}</p>`;

                if (window.PAGE_CONTEXT.show_unclassified) {
                    card += `<p><strong>Message:</strong> ${r.message || "--"}</p>`;
                } else {
                    card += `<p><strong>Category:</strong> ${r.crime_category || "Unknown"}</p>
                            <p><strong>Status:</strong> ${r.status}</p>`;
                }

                if (window.PAGE_CONTEXT.show_resolved) {
                    card += `<p><strong>Responded:</strong> ${r.date_time_responded || "--"}</p>
                            <p><strong>Officers:</strong> ${officers}</p>
                            <p><strong>Resolved:</strong> ${r.date_time_resolved || "--"}</p>`;
                }

                if (window.PAGE_CONTEXT.show_rejected) {
                    card += `<p><strong>Rejected On:</strong> ${r.date_time_rejected || "--"}</p>
                            <p><strong>Message:</strong> ${r.message || "--"}</p>
                            <p><strong>Days Remaining:</strong> ${r.days_remaining !== null ? r.days_remaining + " day" + (r.days_remaining !== 1 ? "s" : "") : "--"}</p>`;
                }

                // ACTION buttons
                card += `<div class="mt-3 flex space-x-2">
                            <a href="${viewUrl}" class="flex-1">
                                <button class="w-full px-2 py-1 bg-[#4B7289] text-white rounded hover:bg-[#6B7280]">VIEW</button>
                            </a>`;

                if (!window.PAGE_CONTEXT.show_unclassified) {
                    card += `<a href="${editUrl}" class="flex-1">
                                <button class="w-full px-2 py-1 bg-[#4B7289] text-white rounded hover:bg-[#6B7280]">EDIT</button>
                            </a>`;
                }

                card += `</div></div>`;
                cardBody.innerHTML += card;
            });
        })
        .catch(err => console.error("Error fetching reports:", err));
}

setInterval(fetchReports, 5000);
fetchReports();

const filterForm = document.querySelector('.filters form');
if (filterForm) {
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        fetchReports();
    });
}
