
/*
 * LoanGuard AI
 * Dynamic Application Wizard
 *
 * Applicant-specific flow:
 *
 * Student:
 * Personal → Student → Employment & Income → Credit → Loan → Assets
 *
 * Startup:
 * Personal → Startup → Employment & Income → Credit → Loan → Assets
 *
 * Investor:
 * Personal → Investor → Employment & Income → Credit → Loan → Assets
 *
 * Individual:
 * Personal → Individual → Employment & Income → Credit → Loan → Assets
 */

const FLOWS = {

  student: [
    { key: "personal", label: "Personal" },
    { key: "student", label: "Student Details" },
    { key: "employment", label: "Income & Financial Support" },
    { key: "credit", label: "Credit Profile" },
    { key: "loan", label: "Loan Details" },
    { key: "assets", label: "Assets & Liabilities" }
  ],

  startup: [
    { key: "personal", label: "Personal" },
    { key: "startup", label: "Startup Details" },
    { key: "employment", label: "Income & Financial Details" },
    { key: "credit", label: "Credit Profile" },
    { key: "loan", label: "Loan Details" },
    { key: "assets", label: "Assets & Liabilities" }
  ],

  investor: [
    { key: "personal", label: "Personal" },
    { key: "investor", label: "Investor Details" },
    { key: "employment", label: "Income & Financial Details" },
    { key: "credit", label: "Credit Profile" },
    { key: "loan", label: "Loan Details" },
    { key: "assets", label: "Assets & Liabilities" }
  ],

  individual: [
    { key: "personal", label: "Personal" },
    { key: "individual", label: "Individual Details" },
    { key: "employment", label: "Employment & Income" },
    { key: "credit", label: "Credit Profile" },
    { key: "loan", label: "Loan Details" },
    { key: "assets", label: "Assets & Liabilities" }
  ]

};


/* =========================================================
   PAGE VALIDATION FIELDS
========================================================= */

const PAGE_FIELDS = {

  personal: [
    "applicant_type",
    "full_name",
    "age",
    "gender",
    "marital_status",
    "education"
  ],

  student: [
    "student_institution_name",
    "student_course",
    "student_year_of_study",
    "student_expected_graduation",
    "student_education_loan_requirement"
  ],

  startup: [
    "startup_name",
    "startup_business_stage",
    "startup_business_age_years",
    "startup_annual_revenue",
    "startup_funding_required"
  ],

  investor: [
    "investor_investment_experience",
    "investor_annual_investment_income",
    "investor_investment_portfolio_value",
    "investor_investment_purpose"
  ],

  individual: [
    "occupation",
    "residential_status"
  ],

  credit: [
    "credit_score",
    "credit_history_years"
  ],

  loan: [
    "loan_purpose",
    "loan_amount",
    "loan_tenure_months"
  ],

  assets: []

};


let currentFlow = [];
let currentPage = 0;


/* =========================================================
   GET APPLICANT TYPE
========================================================= */

function getApplicantType() {

  const input = document.getElementById("applicant_type");

  if (!input) {
    return "";
  }

  return input.value.trim().toLowerCase();

}


/* =========================================================
   GET CURRENT APPLICANT FLOW
========================================================= */

function setFlow() {

  const applicantType = getApplicantType();

  currentFlow = FLOWS[applicantType] || [
    { key: "personal", label: "Personal" }
  ];

}


/* =========================================================
   ADD NOT APPLICABLE OPTION
========================================================= */

function addNotApplicableOption() {

  const employmentType =
    document.getElementById("employment_type");

  if (!employmentType) {
    return;
  }

  const exists = Array.from(
    employmentType.options
  ).some(option => option.value === "Not Applicable");

  if (!exists) {

    const option = document.createElement("option");

    option.value = "Not Applicable";
    option.textContent = "Not Applicable";

    employmentType.insertBefore(
      option,
      employmentType.options[1] || null
    );

  }

}


/* =========================================================
   CONFIGURE INCOME PAGE BY APPLICANT TYPE
========================================================= */

function configureEmploymentPage() {

  const applicantType = getApplicantType();

  const employmentType =
    document.getElementById("employment_type");

  const employmentYears =
    document.getElementById("employment_years");

  const monthlyIncome =
    document.getElementById("monthly_income");

  const otherIncome =
    document.getElementById("other_monthly_income");

  const employmentTitle =
    document.querySelector('[data-page="employment"] h2');

  const employmentHint =
    document.querySelector('[data-page="employment"] .step-hint');

  const monthlyIncomeLabel =
    document.querySelector('label[for="monthly_income"]');

  const otherIncomeLabel =
    document.querySelector('label[for="other_monthly_income"]');

  if (!employmentType || !monthlyIncome) {
    return;
  }

  addNotApplicableOption();

  // Allow zero income where applicable.
  monthlyIncome.min = "0";
  monthlyIncome.required = false;

  if (otherIncome) {
    otherIncome.min = "0";
    otherIncome.required = false;
  }

  if (applicantType === "student") {

    if (employmentTitle) {
      employmentTitle.textContent =
        "Income & Financial Support";
    }

    if (employmentHint) {
      employmentHint.textContent =
        "Provide your stipend, part-time income and any regular financial support received from family or guardians.";
    }

    if (monthlyIncomeLabel) {
      monthlyIncomeLabel.textContent =
        "Monthly stipend / part-time income (₹)";
    }

    if (otherIncomeLabel) {
      otherIncomeLabel.textContent =
        "Monthly family / guardian support (₹)";
    }

    employmentType.value = "Not Applicable";

    if (employmentYears) {
      employmentYears.value = "0";
      employmentYears.required = false;
    }

    monthlyIncome.placeholder = "Enter 0 if unemployed";

    if (otherIncome) {
      otherIncome.placeholder =
        "Enter regular monthly support";
    }

  }

  else if (applicantType === "startup") {

    if (employmentTitle) {
      employmentTitle.textContent =
        "Startup Income & Financial Details";
    }

    if (employmentHint) {
      employmentHint.textContent =
        "Your startup revenue is collected separately. Provide any additional personal or other monthly income here.";
    }

    if (monthlyIncomeLabel) {
      monthlyIncomeLabel.textContent =
        "Other personal monthly income (₹)";
    }

    if (otherIncomeLabel) {
      otherIncomeLabel.textContent =
        "Additional monthly income (₹)";
    }

    employmentType.value = "Not Applicable";

    if (employmentYears) {
      employmentYears.value = "0";
      employmentYears.required = false;
    }

    monthlyIncome.placeholder =
      "Optional personal income";

    if (otherIncome) {
      otherIncome.placeholder =
        "Optional additional income";
    }

  }

  else if (applicantType === "investor") {

    if (employmentTitle) {
      employmentTitle.textContent =
        "Investment Income & Financial Details";
    }

    if (employmentHint) {
      employmentHint.textContent =
        "Your annual investment income is collected separately. Provide any additional monthly income here.";
    }

    if (monthlyIncomeLabel) {
      monthlyIncomeLabel.textContent =
        "Other personal monthly income (₹)";
    }

    if (otherIncomeLabel) {
      otherIncomeLabel.textContent =
        "Additional monthly income (₹)";
    }

    employmentType.value = "Not Applicable";

    if (employmentYears) {
      employmentYears.value = "0";
      employmentYears.required = false;
    }

    monthlyIncome.placeholder =
      "Optional personal income";

    if (otherIncome) {
      otherIncome.placeholder =
        "Optional additional income";
    }

  }

  else if (applicantType === "individual") {

    if (employmentTitle) {
      employmentTitle.textContent =
        "Employment & Income";
    }

    if (employmentHint) {
      employmentHint.textContent =
        "Provide your employment details and actual monthly income.";
    }

    if (monthlyIncomeLabel) {
      monthlyIncomeLabel.textContent =
        "Monthly income (₹)";
    }

    if (otherIncomeLabel) {
      otherIncomeLabel.textContent =
        "Co-applicant / other income (₹)";
    }

    employmentType.required = true;

    if (employmentYears) {
      employmentYears.required = true;
    }

    monthlyIncome.required = true;
    monthlyIncome.min = "1";

    monthlyIncome.placeholder =
      "Enter your monthly income";

  }

}


/* =========================================================
   RENDER WIZARD STEPS
========================================================= */

function renderSteps() {

  const el = document.getElementById("wizardSteps");

  if (!el) {
    return;
  }

  el.innerHTML = currentFlow.map((step, index) => {

    const state =
      index < currentPage
        ? "done"
        : index === currentPage
          ? "current"
          : "";

    const dot =
      index < currentPage
        ? "✓"
        : index + 1;

    return `
      <div class="wizard-step ${state}">
        <span class="dot">${dot}</span>
        <span class="label">${step.label}</span>
      </div>
    `;

  }).join("");

}


/* =========================================================
   SHOW WIZARD PAGE
========================================================= */

function showPage(index) {

  if (!currentFlow.length) {
    return;
  }

  index = Math.max(
    0,
    Math.min(index, currentFlow.length - 1)
  );

  currentPage = index;

  const currentStep = currentFlow[currentPage];

  document.querySelectorAll(".wizard-page").forEach(page => {

    page.hidden =
      page.dataset.page !== currentStep.key;

  });

  if (currentStep.key === "employment") {
    configureEmploymentPage();
  }

  renderSteps();

  const backBtn =
    document.getElementById("backBtn");

  if (backBtn) {

    backBtn.style.visibility =
      currentPage === 0
        ? "hidden"
        : "visible";

  }

  const nextBtn =
    document.getElementById("nextBtn");

  if (nextBtn) {

    nextBtn.textContent =
      currentPage === currentFlow.length - 1
        ? "Submit application"
        : "Continue";

  }

  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });

}


/* =========================================================
   VALIDATE CURRENT PAGE
========================================================= */

function validatePage(index) {

  if (!currentFlow[index]) {
    return false;
  }

  const pageKey = currentFlow[index].key;

  let fields = PAGE_FIELDS[pageKey] || [];

  // Employment validation depends on applicant category.
  if (pageKey === "employment") {

    const applicantType = getApplicantType();

    if (applicantType === "individual") {

      fields = [
        "employment_type",
        "employment_years",
        "monthly_income"
      ];

    } else {

      fields = [
        "employment_type",
        "employment_years"
      ];

    }

  }

  let valid = true;

  fields.forEach(id => {

    const input = document.getElementById(id);

    if (!input) {
      return;
    }

    input.classList.remove("invalid");

    const value = String(input.value).trim();

    if (!value || !input.checkValidity()) {

      input.classList.add("invalid");

      valid = false;

    }

  });

  return valid;

}


/* =========================================================
   SAFE VALUE HELPERS
========================================================= */

function getValue(id, fallback = "") {

  const input = document.getElementById(id);

  if (!input) {
    return fallback;
  }

  return input.value;

}


function getNumber(id, fallback = 0) {

  const input = document.getElementById(id);

  if (!input || input.value === "") {
    return fallback;
  }

  const number = Number(input.value);

  return Number.isFinite(number)
    ? number
    : fallback;

}


/*
 * Returns null when an optional numeric field is empty.
 * This distinguishes missing information from an actual zero.
 */

function getOptionalNumber(id) {

  const input = document.getElementById(id);

  if (!input || input.value.trim() === "") {
    return null;
  }

  const number = Number(input.value);

  return Number.isFinite(number)
    ? number
    : null;

}


// Converts Yes / No select values into true / false.
// An empty selection is sent as null.

function getBoolean(id) {

  const input = document.getElementById(id);

  if (!input || input.value === "") {
    return null;
  }

  return input.value === "true";

}


/* =========================================================
   FORMAT API ERRORS
========================================================= */

function formatApiError(error) {

  function formatDetail(detail) {

    if (Array.isArray(detail)) {

      return detail.map(item => {

        if (typeof item === "string") {
          return item;
        }

        if (item && typeof item === "object") {

          const location = Array.isArray(item.loc)
            ? item.loc.filter(Boolean).join(" → ")
            : "";

          const message =
            item.msg ||
            item.message ||
            item.error ||
            "";

          if (location && message) {
            return `${location}: ${message}`;
          }

          if (message) {
            return message;
          }

          return JSON.stringify(item);

        }

        return String(item);

      }).join("\n");

    }

    if (typeof detail === "string") {
      return detail;
    }

    if (detail && typeof detail === "object") {

      return (
        detail.message ||
        detail.msg ||
        detail.error ||
        JSON.stringify(detail)
      );

    }

    return "";

  }

  if (!error) {
    return "Something went wrong. Please try again.";
  }

  if (error.detail !== undefined) {

    const message = formatDetail(error.detail);

    if (message) {
      return message;
    }

  }

  if (error.response?.data?.detail !== undefined) {

    const message = formatDetail(
      error.response.data.detail
    );

    if (message) {
      return message;
    }

  }

  if (error.data?.detail !== undefined) {

    const message = formatDetail(error.data.detail);

    if (message) {
      return message;
    }

  }

  if (
    typeof error.message === "string" &&
    error.message.trim()
  ) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  try {

    return JSON.stringify(error, null, 2);

  } catch {

    return "Unable to submit application. Please try again.";

  }

}


/* =========================================================
   DISPLAY SUBMISSION ERROR
========================================================= */

function showSubmissionError(error) {

  const alertBox =
    document.getElementById("alertBox");

  const message = formatApiError(error);

  console.error(
    "LoanGuard application submission error:",
    error
  );

  if (!alertBox) {

    window.alert(message);

    return;

  }

  alertBox.replaceChildren();

  const errorDiv = document.createElement("div");

  errorDiv.className = "alert alert-error";

  errorDiv.textContent = message;

  errorDiv.style.whiteSpace = "pre-line";

  alertBox.appendChild(errorDiv);

  alertBox.scrollIntoView({
    behavior: "smooth",
    block: "center"
  });

}


/* =========================================================
   COLLECT APPLICATION PAYLOAD
========================================================= */

function collectPayload() {

  return {

    applicant_type:
      getValue("applicant_type"),

    // Personal information
    full_name:
      getValue("full_name"),

    age:
      getNumber("age"),

    gender:
      getValue("gender"),

    marital_status:
      getValue("marital_status"),

    education:
      getValue("education"),


    // Student academic information
    student_institution_name:
      getValue("student_institution_name") || null,

    student_course:
      getValue("student_course") || null,

    student_year_of_study:
      getValue("student_year_of_study") === ""
        ? null
        : getNumber("student_year_of_study"),

    student_expected_graduation:
      getValue("student_expected_graduation") === ""
        ? null
        : getNumber("student_expected_graduation"),

    student_education_loan_requirement:
      getValue("student_education_loan_requirement") || null,


    // Student financial support information
    student_support_source:
      getValue("student_support_source") || null,

    student_guardian_relationship:
      getValue("student_guardian_relationship") || null,

    student_guardian_occupation:
      getValue("student_guardian_occupation") || null,

    student_guardian_monthly_income:
      getOptionalNumber("student_guardian_monthly_income"),

    student_scholarship_amount:
      getOptionalNumber("student_scholarship_amount"),

    student_co_applicant_available:
      getBoolean("student_co_applicant_available"),

    student_co_applicant_relationship:
      getValue("student_co_applicant_relationship") || null,


    // Startup information
    startup_name:
      getValue("startup_name") || null,

    startup_business_stage:
      getValue("startup_business_stage") || null,

    startup_business_age_years:
      getNumber("startup_business_age_years"),

    startup_annual_revenue:
      getNumber("startup_annual_revenue"),

    startup_funding_required:
      getNumber("startup_funding_required"),

    startup_existing_funding:
      getOptionalNumber("startup_existing_funding"),


    // Investor information
    investor_investment_experience:
      getValue("investor_investment_experience") || null,

    investor_annual_investment_income:
      getNumber("investor_annual_investment_income"),

    investor_investment_portfolio_value:
      getNumber("investor_investment_portfolio_value"),

    investor_investment_purpose:
      getValue("investor_investment_purpose") || null,


    // Individual information
    occupation:
      getValue("occupation") || null,

    residential_status:
      getValue("residential_status") || null,


    // Employment and income
    employment_type:
      getValue("employment_type", "Not Applicable"),

    employment_years:
      getNumber("employment_years"),

    monthly_income:
      getNumber("monthly_income"),

    other_monthly_income:
      getNumber("other_monthly_income"),


    // Credit profile
    credit_score:
      getNumber("credit_score"),

    credit_history_years:
      getNumber("credit_history_years"),

    credit_accounts:
      getNumber("credit_accounts"),

    credit_utilization_percent:
      getNumber("credit_utilization_percent"),

    previous_loans:
      getNumber("previous_loans"),

    late_payments:
      getNumber("late_payments"),

    previous_defaults:
      getNumber("previous_defaults"),


    // Loan information
    loan_purpose:
      getValue("loan_purpose"),

    loan_amount:
      getNumber("loan_amount"),

    loan_tenure_months:
      getNumber("loan_tenure_months"),

    existing_emi:
      getNumber("existing_emi"),


    // Assets and liabilities
    assets:
      getNumber("assets"),

    liabilities:
      getNumber("liabilities"),

    bank_balance:
      getNumber("bank_balance")

  };

}


/* =========================================================
   INITIALIZE WIZARD
========================================================= */

async function init() {

  const user = await requireAuth([
    "applicant",
    "officer",
    "admin"
  ]);

  if (!user) {
    return;
  }

  mountAppShell(user, "apply");

  currentFlow = [
    { key: "personal", label: "Personal" }
  ];

  currentPage = 0;

  showPage(0);


  /* =======================================================
     APPLICANT TYPE CHANGE
  ======================================================= */

  const applicantType =
    document.getElementById("applicant_type");

  if (applicantType) {

    applicantType.addEventListener("change", () => {

      setFlow();

      configureEmploymentPage();

      currentPage = 0;

      showPage(0);

    });

  }


  /* =======================================================
     BACK BUTTON
  ======================================================= */

  const backBtn =
    document.getElementById("backBtn");

  if (backBtn) {

    backBtn.addEventListener("click", () => {

      if (currentPage > 0) {
        showPage(currentPage - 1);
      }

    });

  }


  /* =======================================================
     CONTINUE / SUBMIT BUTTON
  ======================================================= */

  const nextBtn =
    document.getElementById("nextBtn");

  if (!nextBtn) {

    console.error(
      "LoanGuard: nextBtn element not found."
    );

    return;

  }

  nextBtn.addEventListener("click", async () => {

    if (!validatePage(currentPage)) {
      return;
    }

    // Build the correct flow after personal details.
    if (
      currentPage === 0 &&
      getApplicantType() &&
      currentFlow.length === 1
    ) {

      setFlow();

      showPage(0);

      return;

    }

    // Move to the next page.
    if (currentPage < currentFlow.length - 1) {

      showPage(currentPage + 1);

      return;

    }


    /* ===================================================
       FINAL APPLICATION SUBMISSION
    =================================================== */

    nextBtn.disabled = true;

    nextBtn.textContent = "Scoring application…";

    const alertBox =
      document.getElementById("alertBox");

    if (alertBox) {
      alertBox.replaceChildren();
    }

    try {

      const payload = collectPayload();

      console.log(
        "Submitting LoanGuard application:",
        payload
      );

      const result =
        await API.submitApplication(payload);

      if (!result || !result.id) {

        throw new Error(
          "The server response did not contain an application ID. Please check the backend response."
        );

      }

      sessionStorage.setItem(
        "lastResultId",
        result.id
      );

      window.location.href =
        `/result.html?id=${encodeURIComponent(result.id)}`;

    } catch (err) {

      showSubmissionError(err);

      nextBtn.disabled = false;

      nextBtn.textContent =
        "Submit application";

    }

  });

}


/* =========================================================
   START WIZARD
========================================================= */

init();