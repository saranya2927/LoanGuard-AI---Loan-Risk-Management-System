const NAV_ICONS = {
  dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>',
  apply: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14"/></svg>',
  history: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 3v5h5"/><path d="M3.05 13a9 9 0 1 0 2.13-7.36L3 8"/><path d="M12 7v5l3 3"/></svg>',
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9.5a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V10"/></svg>',
};

/**
 * Builds the sidebar for a logged-in user and mounts it, wrapping existing
 * <main data-app-content> into the app-shell layout.
 * navKey: "dashboard" | "apply" | "history"
 */
function mountAppShell(user, navKey) {
  const links = {
    applicant: [
      { key: "apply", href: "/apply.html", label: "New Application" },
      { key: "history", href: "/history.html", label: "My Applications" },
    ],
    officer: [
      { key: "dashboard", href: "/dashboard.html", label: "Dashboard" },
      { key: "apply", href: "/apply.html", label: "New Application" },
      { key: "history", href: "/history.html", label: "Application History" },
    ],
    admin: [
      { key: "dashboard", href: "/dashboard.html", label: "Dashboard" },
      { key: "apply", href: "/apply.html", label: "New Application" },
      { key: "history", href: "/history.html", label: "Application History" },
    ],
  };

  const navLinks = links[user.role] || links.applicant;
  const initials = user.full_name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const sidebar = document.createElement("aside");
  sidebar.className = "sidebar";
  sidebar.innerHTML = `
    <a href="/index.html" class="sidebar-logo">
      <span class="mark">LG</span>
      <span class="word">LoanGuard AI</span>
    </a>
    <nav class="sidebar-nav">
      ${navLinks
        .map(
          (l) => `<a href="${l.href}" class="${l.key === navKey ? "active" : ""}">${
            NAV_ICONS[l.key] || ""
          }${l.label}</a>`
        )
        .join("")}
    </nav>
    <div class="sidebar-foot">
      <div class="sidebar-user">
        <span class="avatar">${initials}</span>
        <span class="who">
          <div class="name">${user.full_name}</div>
          <div class="role">${user.role}</div>
        </span>
      </div>
      <span class="sidebar-logout" id="logoutBtn">Log out</span>
    </div>
  `;

  document.body.classList.add("app-shell");
  document.body.prepend(sidebar);

  document.getElementById("logoutBtn").addEventListener("click", async () => {
    await API.logout();
    window.location.href = "/index.html";
  });
}
