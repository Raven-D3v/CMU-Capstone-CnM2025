document.addEventListener("DOMContentLoaded", () => {
    const ul = document.getElementById("notif-list");

    function refreshNotifications() {
        fetch(window.NOTIFICATIONS_JSON_URL)
            .then(res => res.json())
            .then(data => {
                // Update badge
                let badge = document.querySelector("[x-ref='badge']");
                if (data.unread_count > 0) {
                    if (!badge) {
                        badge = document.createElement("span");
                        badge.setAttribute("x-ref", "badge");
                        badge.className = "absolute -top-1 -right-2 bg-red-600 text-white text-xs font-bold px-1.5 py-0.5 rounded-full";
                        document.querySelector("button.relative").appendChild(badge);
                    }
                    badge.innerText = data.unread_count;
                } else if (badge) {
                    badge.remove();
                }

                // Update notification list
                ul.innerHTML = "";
                if (data.notifications.length > 0) {
                    data.notifications.forEach(note => {
                        const li = document.createElement("li");
                        li.id = `note-${note.id}`;
                        li.className = "p-3 " + (note.is_read ? "" : "bg-gray-100 font-semibold");
                        li.innerHTML = `
                            <a href="${note.url}" class="notif-link block" data-id="${note.id}">
                                <div>${note.message}</div>
                                <small class="text-gray-500">${note.created_at}</small>
                            </a>`;
                        ul.appendChild(li);
                    });
                } else {
                    ul.innerHTML = '<li class="p-3 text-gray-500">No notifications</li>';
                }

                attachClickHandlers();
            });
    }

    function attachClickHandlers() {
        document.querySelectorAll(".notif-link").forEach(link => {
            link.addEventListener("click", e => {
                e.preventDefault();
                const noteId = link.dataset.id;

                fetch(`/notifications/mark/${noteId}/`, { 
                    headers: { 'X-Requested-With': 'XMLHttpRequest' } 
                })
                .then(() => {
                    // Update badge
                    const badge = document.querySelector("[x-ref='badge']");
                    if (badge) {
                        let count = parseInt(badge.innerText);
                        if (count > 0) badge.innerText = count - 1;
                        if (count - 1 === 0) badge.remove();
                    }

                    // Remove highlight
                    const li = document.getElementById(`note-${noteId}`);
                    if (li) li.classList.remove('bg-gray-100','font-semibold');

                    // Redirect
                    window.location.href = link.href;
                });
            });
        });
    }

    // Initial run
    refreshNotifications();

    // Refresh every 10 seconds
    setInterval(refreshNotifications, 10000);
});
