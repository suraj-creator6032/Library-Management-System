const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("sidebar-overlay");
const toggleButton = document.getElementById("sidebar-toggle");

function openSidebar() {
    sidebar.classList.remove("-translate-x-full");
    overlay.classList.remove("hidden");
}

function closeSidebar() {
    sidebar.classList.add("-translate-x-full");
    overlay.classList.add("hidden");
}

if (toggleButton && sidebar && overlay) {
    toggleButton.addEventListener("click", openSidebar);
    overlay.addEventListener("click", closeSidebar);
}