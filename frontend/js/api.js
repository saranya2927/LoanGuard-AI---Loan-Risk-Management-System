
/* =========================================================
   LOANGUARD AI - API HANDLER
========================================================= */


/* =========================================================
   UNIVERSAL ERROR MESSAGE FORMATTER
========================================================= */

function formatApiError(value) {

  if (value === null || value === undefined) {
    return "Something went wrong. Please try again.";
  }

  // Already a string
  if (typeof value === "string") {
    return value.trim() || "Something went wrong. Please try again.";
  }

  // Number or boolean
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  // Array of validation errors
  if (Array.isArray(value)) {

    const messages = value.map((item) => {

      if (typeof item === "string") {
        return item;
      }

      if (item && typeof item === "object") {

        const location = Array.isArray(item.loc)
          ? item.loc.filter(part => part !== "body").join(" → ")
          : "";

        const message =
          item.msg ||
          item.message ||
          item.error ||
          item.detail;

        const formattedMessage = message
          ? formatApiError(message)
          : "";

        if (location && formattedMessage) {
          return `${location}: ${formattedMessage}`;
        }

        if (formattedMessage) {
          return formattedMessage;
        }

        return JSON.stringify(item);

      }

      return String(item);

    }).filter(Boolean);

    return messages.length
      ? messages.join("\n")
      : "Invalid input. Please check your application details.";

  }

  // Object response
  if (typeof value === "object") {

    // Common FastAPI response structures
    const possibleKeys = [
      "detail",
      "message",
      "msg",
      "error",
      "errors",
      "description"
    ];

    for (const key of possibleKeys) {

      if (
        value[key] !== undefined &&
        value[key] !== null &&
        value[key] !== value
      ) {

        const result = formatApiError(value[key]);

        if (result) {
          return result;
        }

      }

    }

    // Handle nested response data
    if (value.response?.data) {
      return formatApiError(value.response.data);
    }

    if (value.data) {
      return formatApiError(value.data);
    }

    // Last attempt: extract readable object values
    const readableValues = Object.values(value)
      .filter(item =>
        typeof item === "string" ||
        typeof item === "number"
      );

    if (readableValues.length) {
      return readableValues.join("\n");
    }

    return JSON.stringify(value, null, 2);

  }

  return "Something went wrong. Please try again.";

}


/* =========================================================
   API OBJECT
========================================================= */

const API = {

  base: "/api",


  /* =======================================================
     COMMON REQUEST HANDLER
  ======================================================= */

  async request(path, options = {}) {

    let response;

    try {

      const headers = {
        ...(options.headers || {})
      };

      if (options.body) {
        headers["Content-Type"] = "application/json";
      }

      response = await fetch(this.base + path, {

        credentials: "include",

        ...options,

        headers

      });

    } catch (networkError) {

      console.error("LoanGuard network error:", networkError);

      throw new Error(
        "Unable to connect to the server. Please check whether the LoanGuard backend is running."
      );

    }


    /* =====================================================
       READ RESPONSE
    ===================================================== */

    let data = null;

    const contentType =
      response.headers.get("content-type") || "";

    try {

      if (contentType.includes("application/json")) {

        data = await response.json();

      } else {

        const text = await response.text();

        data = text || null;

      }

    } catch (parseError) {

      console.error("Response parsing error:", parseError);

      data = null;

    }


    /* =====================================================
       HANDLE API ERRORS
    ===================================================== */

    if (!response.ok) {

      console.error("LoanGuard backend response:", {
        status: response.status,
        statusText: response.statusText,
        data: data
      });

      let message = "";

      if (data !== null) {
        message = formatApiError(data);
      }

      if (!message || message === "{}" || message === "[]") {

        message =
          `Server error (${response.status}). ${response.statusText || "Please try again."}`;

      }

      const error = new Error(message);

      error.status = response.status;

      error.response = {
        status: response.status,
        data: data
      };

      throw error;

    }


    /* =====================================================
       HANDLE EMPTY RESPONSE
    ===================================================== */

    if (response.status === 204) {
      return null;
    }


    return data;

  },


  /* =======================================================
     GET REQUEST
  ======================================================= */

  get(path) {

    return this.request(path, {
      method: "GET"
    });

  },


  /* =======================================================
     POST REQUEST
  ======================================================= */

  post(path, body) {

    return this.request(path, {

      method: "POST",

      body: JSON.stringify(body)

    });

  },


  /* =======================================================
     AUTHENTICATION
  ======================================================= */

  me() {

    return this.request("/auth/me")
      .catch(() => null);

  },


  login(email, password) {

    return this.post("/auth/login", {
      email,
      password
    });

  },


  register(full_name, email, password) {

    return this.post("/auth/register", {
      full_name,
      email,
      password
    });

  },


  logout() {

    return this.post("/auth/logout", {});

  },


  /* =======================================================
     LOAN APPLICATIONS
  ======================================================= */

  submitApplication(payload) {

    return this.post("/applications", payload);

  },


  myApplications() {

    return this.get("/applications/mine");

  },


  application(id) {

    return this.get(`/applications/${id}`);

  },


  applications(params = {}) {

    const qs = new URLSearchParams(

      Object.fromEntries(

        Object.entries(params).filter(
          ([, value]) => value !== "" && value != null
        )

      )

    ).toString();

    return this.get(
      `/applications${qs ? "?" + qs : ""}`
    );

  },


  /* =======================================================
     DASHBOARD
  ======================================================= */

  dashboardSummary() {

    return this.get("/dashboard/summary");

  }

};


/* =========================================================
   FORMAT CURRENCY
========================================================= */

function fmtCurrency(n) {

  if (n == null || n === "") {
    return "\u2014";
  }

  const number = Number(n);

  if (!Number.isFinite(number)) {
    return "\u2014";
  }

  return "\u20B9" + Math.round(number).toLocaleString("en-IN");

}


/* =========================================================
   FORMAT DATE
========================================================= */

function fmtDate(iso) {

  if (!iso) {
    return "\u2014";
  }

  const d = new Date(iso);

  if (Number.isNaN(d.getTime())) {
    return "\u2014";
  }

  return d.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric"
  });

}


/* =========================================================
   RISK BADGE CLASS
========================================================= */

function riskBadgeClass(level) {

  return {

    Low: "badge-low",

    Medium: "badge-medium",

    High: "badge-high"

  }[level] || "badge-neutral";

}


/* =========================================================
   DECISION BADGE CLASS
========================================================= */

function decisionBadgeClass(decision) {

  return {

    Approve: "badge-low",

    "Manual Review": "badge-medium",

    Reject: "badge-high"

  }[decision] || "badge-neutral";

}


/* =========================================================
   TOAST NOTIFICATION
========================================================= */

function toast(message) {

  let stack = document.querySelector(".toast-stack");

  if (!stack) {

    stack = document.createElement("div");

    stack.className = "toast-stack";

    document.body.appendChild(stack);

  }

  const el = document.createElement("div");

  el.className = "toast";

  el.textContent = formatApiError(message);

  stack.appendChild(el);

  setTimeout(() => el.remove(), 3200);

}


/* =========================================================
   AUTHENTICATION CHECK
   Redirect if user is not authenticated
========================================================= */

async function requireAuth(allowedRoles) {

  const user = await API.me();

  if (!user) {

    window.location.href = "/login.html";

    return null;

  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {

    window.location.href =
      user.role === "applicant"
        ? "/apply.html"
        : "/dashboard.html";

    return null;

  }

  return user;

}