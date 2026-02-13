// ========================================
// LEAD DETAIL PAGE - CONSOLIDATED JAVASCRIPT
// ========================================

// ========================================
// 1. GLOBAL STATE & VARIABLES
// ========================================
let selectedOutcome = null;
let isEditingClient = false;
let originalClientData = {};
let flatpickrInstances = {}; // Store flatpickr instances

// ========================================
// 2. UTILITY FUNCTIONS
// ========================================

/**
 * Toast Notification System
 */
function showToast(title, message, type = "info", duration = 3000) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icons = {
    success:
      '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><path d="M22 4L12 14.01l-3-3"></path>',
    error:
      '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>',
    warning:
      '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>',
    info: '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>',
  };

  toast.innerHTML = `
    <div class="toast-icon">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        ${icons[type]}
      </svg>
    </div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <div class="toast-close" onclick="closeToast(this)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </div>
    <div class="toast-progress"></div>
  `;

  container.appendChild(toast);
  setTimeout(() => removeToast(toast), duration);
}

function closeToast(button) {
  const toast = button.closest(".toast");
  removeToast(toast);
}

function removeToast(toast) {
  toast.classList.add("removing");
  setTimeout(() => toast.remove(), 300);
}

// ========================================
// 3. FLATPICKR DATE PICKER INITIALIZATION - ENHANCED
// ========================================

/**
 * Initialize flatpickr on all date fields
 * Auto-fills "Progress Updated Date" fields with today's date
 */
function initializeDatePickers() {
  console.log('Initializing flatpickr on all date fields...');
  
  // Find ALL date fields on the page (not just specific IDs)
  const dateFields = document.querySelectorAll('input[type="date"]');
  console.log(`Found ${dateFields.length} date fields on the page`);
  
  // Track which fields we auto-filled
  let autoFilledCount = 0;
  const today = new Date().toISOString().split('T')[0];
  let flatpickrCount = 0;
  
  dateFields.forEach((field, index) => {
    const fieldId = field.id || `date-field-${index}`;
    const fieldName = field.name || 'unnamed';
    const originalValue = field.value;
    
    console.log(`Processing date field #${index + 1}:`, {
      id: fieldId,
      name: fieldName,
      value: originalValue,
      placeholder: field.placeholder
    });
    
    // Special handling for actual_call_date field
    if (fieldName === 'actual_call_date' || field.id === 'actual_call_date') {
      if (!originalValue) {
        field.value = today;
        autoFilledCount++;
        console.log(`✓ Actual Call Date auto-filled: ${today}`);
      }
      
      // Initialize flatpickr with enhanced options for actual_call_date
      try {
        const fpInstance = flatpickr(field, {
          dateFormat: "Y-m-d",
          defaultDate: today,
          allowInput: true,
          clickOpens: true,
          disableMobile: false,
          maxDate: "today",
          locale: {
            firstDayOfWeek: 1
          },
          onReady: function(selectedDates, dateStr, instance) {
            // Ensure the input has the flatpickr class
            field.classList.add('flatpickr-input');
            instance.calendarContainer.classList.add('flatpickr-blue-theme');
            console.log('✓ Actual Call Date flatpickr ready');
          },
          onChange: function(selectedDates, dateStr, instance) {
            console.log('📅 Actual Call Date changed to:', dateStr);
            showToast('success', 'Date Updated', `Actual call date set to ${dateStr}`, 2000);
          }
        });
        
        flatpickrInstances[fieldId] = fpInstance;
        flatpickrCount++;
        console.log(`✓ flatpickr initialized for actual_call_date`);
      } catch (error) {
        console.error(`✗ Failed to initialize flatpickr for actual_call_date:`, error);
      }
      return; // Skip further processing for this field
    }
    
    // Auto-fill empty date fields with today's date (except actual_call_date)
    if (!originalValue) {
      field.value = today;
      autoFilledCount++;
      console.log(`Auto-filled ${fieldName} with today's date: ${today}`);
    }
    
    // Initialize flatpickr with enhanced options for other date fields
    try {
      flatpickrInstances[fieldId] = flatpickr(field, {
        dateFormat: "Y-m-d", // Django compatible format
        allowInput: true, // Allow manual typing
        clickOpens: true,
        disableMobile: false, // Enable mobile support
        locale: {
          firstDayOfWeek: 1 // Monday
        },
        onReady: function(selectedDates, dateStr, instance) {
          // Ensure the input has the flatpickr class
          field.classList.add('flatpickr-input');
          instance.calendarContainer.classList.add('flatpickr-blue-theme');
        },
        onChange: function(selectedDates, dateStr, instance) {
          console.log(`Date changed for ${fieldName}: ${dateStr}`);
        }
      });
      
      flatpickrCount++;
      console.log(`✓ flatpickr initialized for ${fieldName}`);
    } catch (error) {
      console.error(`✗ Failed to initialize flatpickr for ${fieldName}:`, error);
    }
  });
  
  console.log(`Flatpickr initialized on ${flatpickrCount} date fields`);
  console.log(`Auto-filled ${autoFilledCount} date fields with today's date`);
  
  // Debug: List all date fields that were processed
  if (dateFields.length > 0) {
    console.log('All date fields processed:');
    dateFields.forEach((field, index) => {
      console.log(`${index + 1}. ${field.name || field.id || 'unnamed'}: ${field.value}`);
    });
  }
}

// ========================================
// 4. OUTCOME SELECTION - UPDATED
// ========================================

function selectOutcome(outcome, button) {
  // Remove selected from all buttons
  document.querySelectorAll(".outcome-btn").forEach((btn) => {
    btn.classList.remove("selected");
  });

  // Hide all containers and disable their required fields
  document.querySelectorAll(".outcome-container").forEach((container) => {
    container.classList.remove("show");
    
    // Remove required attribute from all fields in hidden containers
    container.querySelectorAll('[required]').forEach(field => {
      field.removeAttribute('required');
      // Store that this field was required
      field.setAttribute('data-was-required', 'true');
    });
  });

  // Add selected to clicked button
  button.classList.add("selected");
  selectedOutcome = outcome;
  document.getElementById("outcomeField").value = outcome;

  // Show corresponding container
  const containerId = "container-" + outcome;
  const container = document.getElementById(containerId);
  if (container) {
    container.classList.add("show");
    
    // Add required attribute back to fields in visible container
    container.querySelectorAll('[data-was-required]').forEach(field => {
      field.setAttribute('required', 'required');
    });
    
    setTimeout(() => {
      container.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }
}

// ========================================
// 5. TANK MANAGEMENT
// ========================================

function addTank() {
  const tankList = document.getElementById("tank-list");
  const tankItem = document.createElement("div");
  tankItem.className = "tank-item";
  tankItem.innerHTML = `
    <select name="tank_type[]" required>
      <option value="">Tank Type</option>
      <option value="Zincallum">Zincallum</option>
      <option value="SecureStore">SecureStore</option>
      <option value="FM Approved">FM Approved</option>
      <option value="GFS Tank">GFS Tank</option>
    </select>
    <input type="text" name="tank_capacity[]" placeholder="Capacity (e.g., 1000 KL)" required>
    <input type="number" name="tank_quantity[]" placeholder="Quantity" min="1" required>
    <button type="button" class="remove-btn" onclick="removeTank(this)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  `;
  tankList.appendChild(tankItem);
  updateRemoveButtons();
}

function removeTank(button) {
  button.closest(".tank-item").remove();
  updateRemoveButtons();
}

function updateRemoveButtons() {
  const tanks = document.querySelectorAll(".tank-item");
  tanks.forEach((tank) => {
    const removeBtn = tank.querySelector(".remove-btn");
    if (removeBtn) {
      removeBtn.style.display = tanks.length > 1 ? "flex" : "none";
    }
  });
}

// ========================================
// 6. CLIENT TYPE HANDLERS (REQUIREMENT YES)
// ========================================

function handleClientTypeChange(clientType) {
  // Hide all sub-options
  const sections = [
    "consultant-options",
    "consultant-other",
    "contractor-options",
    "contractor-other",
    "endclient-options",
    "endclient-other",
  ];
  sections.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
  });

  // Reset fields
  const fields = [
    "consultant_type",
    "consultant_other_text",
    "contractor_type",
    "contractor_other_text",
    "endclient_category",
    "endclient_other_text",
  ];
  fields.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.value = "";
      el.required = false;
    }
  });

  // Show relevant section
  if (clientType === "CONSULTANT") {
    const section = document.getElementById("consultant-options");
    const field = document.getElementById("consultant_type");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  } else if (clientType === "CONTRACTOR") {
    const section = document.getElementById("contractor-options");
    const field = document.getElementById("contractor_type");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  } else if (clientType === "END_CLIENT") {
    const section = document.getElementById("endclient-options");
    const field = document.getElementById("endclient_category");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }
}

function handleConsultantChange(value) {
  const otherField = document.getElementById("consultant-other");
  const otherInput = document.getElementById("consultant_other_text");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleContractorChange(value) {
  const otherField = document.getElementById("contractor-other");
  const otherInput = document.getElementById("contractor_other_text");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleEndClientChange(value) {
  const otherField = document.getElementById("endclient-other");
  const otherInput = document.getElementById("endclient_other_text");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

// ========================================
// 7. CLIENT TYPE HANDLERS (REGRET OFFER)
// ========================================

function handleClientTypeChangeRegret(clientType) {
  const sections = [
    "consultant-options-regret",
    "consultant-other-regret",
    "contractor-options-regret",
    "contractor-other-regret",
    "endclient-options-regret",
    "endclient-other-regret",
  ];
  sections.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
  });

  const fields = [
    "consultant_type_regret",
    "consultant_other_text_regret",
    "contractor_type_regret",
    "contractor_other_text_regret",
    "endclient_category_regret",
    "endclient_other_text_regret",
  ];
  fields.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.value = "";
      el.required = false;
    }
  });

  if (clientType === "CONSULTANT") {
    const section = document.getElementById("consultant-options-regret");
    const field = document.getElementById("consultant_type_regret");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      if (section) section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  } else if (clientType === "CONTRACTOR") {
    const section = document.getElementById("contractor-options-regret");
    const field = document.getElementById("contractor_type_regret");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      if (section) section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  } else if (clientType === "END_CLIENT") {
    const section = document.getElementById("endclient-options-regret");
    const field = document.getElementById("endclient_category_regret");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      if (section) section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }
}

function handleConsultantChangeRegret(value) {
  const otherField = document.getElementById("consultant-other-regret");
  const otherInput = document.getElementById("consultant_other_text_regret");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleContractorChangeRegret(value) {
  const otherField = document.getElementById("contractor-other-regret");
  const otherInput = document.getElementById("contractor_other_text_regret");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleEndClientChangeRegret(value) {
  const otherField = document.getElementById("endclient-other-regret");
  const otherInput = document.getElementById("endclient_other_text_regret");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleTankTypeChangeRegret() {
  const tankType = document.getElementById("tank_type_regret");
  const otherField = document.getElementById("tank-type-other-regret");
  const otherInput = document.getElementById("tank_type_other_text_regret");

  if (!tankType) return;

  if (tankType.value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

// ========================================
// 8. CLIENT TYPE HANDLERS (FUTURE REQUIREMENT)
// ========================================

function handleClientTypeChangeFuture(clientType) {
  const sections = [
    "consultant-options-future",
    "consultant-other-future",
    "contractor-options-future",
    "contractor-other-future",
    "endclient-options-future",
    "endclient-other-future",
  ];
  sections.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
  });

  const fields = [
    "consultant_type_future",
    "consultant_other_text_future",
    "contractor_type_future",
    "contractor_other_text_future",
    "endclient_category_future",
    "endclient_other_text_future",
  ];
  fields.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.value = "";
      el.required = false;
    }
  });

  if (clientType === "CONSULTANT") {
    const section = document.getElementById("consultant-options-future");
    const field = document.getElementById("consultant_type_future");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      if (section) section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  } else if (clientType === "CONTRACTOR") {
    const section = document.getElementById("contractor-options-future");
    const field = document.getElementById("contractor_type_future");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      if (section) section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  } else if (clientType === "END_CLIENT") {
    const section = document.getElementById("endclient-options-future");
    const field = document.getElementById("endclient_category_future");
    if (section) section.style.display = "grid";
    if (field) field.required = true;
    setTimeout(() => {
      if (section) section.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }
}

function handleConsultantChangeFuture(value) {
  const otherField = document.getElementById("consultant-other-future");
  const otherInput = document.getElementById("consultant_other_text_future");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleContractorChangeFuture(value) {
  const otherField = document.getElementById("contractor-other-future");
  const otherInput = document.getElementById("contractor_other_text_future");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

function handleEndClientChangeFuture(value) {
  const otherField = document.getElementById("endclient-other-future");
  const otherInput = document.getElementById("endclient_other_text_future");

  if (value === "Other") {
    if (otherField) otherField.style.display = "grid";
    if (otherInput) otherInput.required = true;
    setTimeout(() => {
      if (otherField) otherField.scrollIntoView({ behavior: "smooth", block: "nearest" });
      if (otherInput) otherInput.focus();
    }, 100);
  } else {
    if (otherField) otherField.style.display = "none";
    if (otherInput) {
      otherInput.required = false;
      otherInput.value = "";
    }
  }
}

// ========================================
// 9. VALIDATION FUNCTIONS
// ========================================

function validateRequirementYes() {
  const clientTypeMain = document.getElementById("client_type_main");
  const tankApplication = document.getElementById("tank_application");
  const assignedSales = document.getElementById("assigned_sales_person");
  const remark = document.getElementById("remark_yes");

  if (!clientTypeMain || !tankApplication || !assignedSales || !remark) {
    showToast("Validation Error", "Missing required fields", "error");
    return false;
  }

  // Validate main client type
  if (!clientTypeMain.value) {
    showToast("Validation Error", "Please select Type of Client", "error");
    clientTypeMain.focus();
    clientTypeMain.scrollIntoView({ behavior: "smooth", block: "center" });
    return false;
  }

  // Validate sub-options based on client type
  if (clientTypeMain.value === "CONSULTANT") {
    const consultantType = document.getElementById("consultant_type");
    if (!consultantType || !consultantType.value) {
      showToast("Validation Error", "Please select Consultant Type", "error");
      if (consultantType) consultantType.focus();
      return false;
    }
    if (
      consultantType.value === "Other"
    ) {
      const otherText = document.getElementById("consultant_other_text");
      if (!otherText || !otherText.value.trim()) {
        showToast("Validation Error", "Please specify Consultant Type", "error");
        if (otherText) otherText.focus();
        return false;
      }
    }
  } else if (clientTypeMain.value === "CONTRACTOR") {
    const contractorType = document.getElementById("contractor_type");
    if (!contractorType || !contractorType.value) {
      showToast("Validation Error", "Please select Contractor Type", "error");
      if (contractorType) contractorType.focus();
      return false;
    }
    if (contractorType.value === "Other") {
      const otherText = document.getElementById("contractor_other_text");
      if (!otherText || !otherText.value.trim()) {
        showToast("Validation Error", "Please specify Contractor Type", "error");
        if (otherText) otherText.focus();
        return false;
      }
    }
  } else if (clientTypeMain.value === "END_CLIENT") {
    const endClientCategory = document.getElementById("endclient_category");
    if (!endClientCategory || !endClientCategory.value) {
      showToast(
        "Validation Error",
        "Please select End Client Category",
        "error"
      );
      if (endClientCategory) endClientCategory.focus();
      return false;
    }
    if (endClientCategory.value === "Other") {
      const otherText = document.getElementById("endclient_other_text");
      if (!otherText || !otherText.value.trim()) {
        showToast(
          "Validation Error",
          "Please specify End Client Category",
          "error"
        );
        if (otherText) otherText.focus();
        return false;
      }
    }
  }

  // Validate tank application
  if (!tankApplication.value.trim()) {
    showToast("Validation Error", "Please enter Tank Application", "error");
    tankApplication.focus();
    return false;
  }

  // Validate at least one complete tank
  const tanks = document.querySelectorAll("#tank-list .tank-item");
  let validTank = false;

  tanks.forEach((tank) => {
    const type = tank.querySelector('select[name="tank_type[]"]');
    const capacity = tank.querySelector('input[name="tank_capacity[]"]');
    const qty = tank.querySelector('input[name="tank_quantity[]"]');

    if (type && capacity && qty && type.value && capacity.value.trim() && qty.value) {
      validTank = true;
    }
  });

  if (!validTank) {
    showToast(
      "Validation Error",
      "Please add at least one complete tank detail",
      "error"
    );
    return false;
  }

  // Validate assigned sales person
  if (!assignedSales.value) {
    showToast(
      "Validation Error",
      "Please select Assigned Sales Person",
      "error"
    );
    assignedSales.focus();
    return false;
  }

  // Validate remark
  if (!remark.value.trim()) {
    showToast("Validation Error", "Please enter Remark", "error");
    remark.focus();
    return false;
  }

  return true;
}

// ========================================
// 10. CLIENT CONTACT INFORMATION EDITING
// ========================================

function toggleClientEdit() {
  isEditingClient = !isEditingClient;

  const editBtn = document.getElementById("client-edit-btn");
  const actionsDiv = document.getElementById("client-actions");
  const addPhoneBtn = document.getElementById("add-phone-btn");
  const addEmailBtn = document.getElementById("add-email-btn");

  const nameDisplay = document.getElementById("client-name-display");
  const nameInput = document.getElementById("client-name-input");

  if (isEditingClient) {
    originalClientData = {
      name: nameDisplay.textContent,
      phones: [],
      emails: [],
    };

    editBtn.style.display = "none";
    if (actionsDiv) actionsDiv.style.display = "flex";
    if (addPhoneBtn) addPhoneBtn.style.display = "inline-flex";
    if (addEmailBtn) addEmailBtn.style.display = "inline-flex";

    nameDisplay.style.display = "none";
    nameInput.style.display = "block";

    enableContactEditing();
    showToast("Edit Mode", "You can now edit client information", "info");
  } else {
    cancelClientEdit();
  }
}

function enableContactEditing() {
  document.querySelectorAll(".contact-item").forEach((item) => {
    const display = item.querySelector(".contact-display");
    const input = item.querySelector(".contact-input");
    const actions = item.querySelector(".contact-actions");

    if (display && input) {
      const value = display.querySelector(".contact-value").textContent;
      if (item.dataset.type === "phone") {
        originalClientData.phones.push(value);
      } else {
        originalClientData.emails.push(value);
      }

      display.style.display = "none";
      input.style.display = "block";
      input.value = value;
    }

    if (actions) {
      const isPrimary = item.dataset.primary === "true";
      const list = item.closest(".contact-list");
      const itemCount = list.querySelectorAll(".contact-item").length;

      if (!isPrimary || itemCount > 1) {
        actions.style.display = "flex";
      }
    }
  });
}

function disableContactEditing() {
  document.querySelectorAll(".contact-item").forEach((item) => {
    const display = item.querySelector(".contact-display");
    const input = item.querySelector(".contact-input");
    const actions = item.querySelector(".contact-actions");

    if (display && input) {
      const value = input.value.trim();
      display.querySelector(".contact-value").textContent =
        value || "Not available";
      display.style.display = "flex";
      input.style.display = "none";
    }

    if (actions) {
      actions.style.display = "none";
    }
  });
}

function saveClientInfo() {
  const nameInput = document.getElementById("client-name-input");
  const nameDisplay = document.getElementById("client-name-display");
  const newName = nameInput.value.trim();

  if (!newName) {
    showToast(
      "Validation Error",
      "Please enter a contact person name",
      "error"
    );
    return;
  }

  nameDisplay.textContent = newName;

  const clientData = {
    name: newName,
    phones: [],
    emails: [],
  };

  document
    .querySelectorAll("#client-phone-list .contact-item")
    .forEach((item) => {
      const input = item.querySelector(".contact-input");
      const value = input.value.trim();
      if (value) {
        clientData.phones.push({
          value: value,
          primary: item.dataset.primary === "true",
        });
      }
    });

  document
    .querySelectorAll("#client-email-list .contact-item")
    .forEach((item) => {
      const input = item.querySelector(".contact-input");
      const value = input.value.trim();
      if (value) {
        clientData.emails.push({
          value: value,
          primary: item.dataset.primary === "true",
        });
      }
    });

  if (clientData.phones.length === 0) {
    showToast(
      "Validation Error",
      "Please add at least one phone number",
      "error"
    );
    return;
  }

  if (clientData.emails.length === 0) {
    showToast(
      "Validation Error",
      "Please add at least one email address",
      "error"
    );
    return;
  }

  console.log("Saving client data:", clientData);
  // TODO: Send to backend via AJAX

  isEditingClient = false;
  document.getElementById("client-edit-btn").style.display = "inline-flex";
  const actionsDiv = document.getElementById("client-actions");
  if (actionsDiv) actionsDiv.style.display = "none";
  const addPhoneBtn = document.getElementById("add-phone-btn");
  if (addPhoneBtn) addPhoneBtn.style.display = "none";
  const addEmailBtn = document.getElementById("add-email-btn");
  if (addEmailBtn) addEmailBtn.style.display = "none";

  nameDisplay.style.display = "block";
  nameInput.style.display = "none";

  disableContactEditing();
  showToast("Success", "Client information updated successfully!", "success");
}

function cancelClientEdit() {
  const nameDisplay = document.getElementById("client-name-display");
  const nameInput = document.getElementById("client-name-input");

  nameDisplay.textContent = originalClientData.name || "Not specified";
  nameDisplay.style.display = "block";
  nameInput.style.display = "none";

  const phoneList = document.getElementById("client-phone-list");
  const emailList = document.getElementById("client-email-list");

  if (phoneList) {
    phoneList.innerHTML = "";
    (originalClientData.phones || []).forEach((phone, index) => {
      const item = createContactItem("phone", phone, index === 0);
      phoneList.appendChild(item);
    });
  }

  if (emailList) {
    emailList.innerHTML = "";
    (originalClientData.emails || []).forEach((email, index) => {
      const item = createContactItem("email", email, index === 0);
      emailList.appendChild(item);
    });
  }

  isEditingClient = false;
  document.getElementById("client-edit-btn").style.display = "inline-flex";
  const actionsDiv = document.getElementById("client-actions");
  if (actionsDiv) actionsDiv.style.display = "none";
  const addPhoneBtn = document.getElementById("add-phone-btn");
  if (addPhoneBtn) addPhoneBtn.style.display = "none";
  const addEmailBtn = document.getElementById("add-email-btn");
  if (addEmailBtn) addEmailBtn.style.display = "none";

  disableContactEditing();
  originalClientData = {};
  showToast("Cancelled", "Changes have been discarded", "warning");
}

function addClientContact(type) {
  const listId = type === "phone" ? "client-phone-list" : "client-email-list";
  const list = document.getElementById(listId);

  const newItem = createContactItem(type, "", false);
  list.appendChild(newItem);

  const input = newItem.querySelector(".contact-input");
  const display = newItem.querySelector(".contact-display");
  const actions = newItem.querySelector(".contact-actions");

  display.style.display = "none";
  input.style.display = "block";
  if (actions) actions.style.display = "flex";
  if (input) input.focus();

  const contactType = type === "phone" ? "Phone number" : "Email address";
  showToast(
    "Contact Added",
    `New ${contactType.toLowerCase()} field added`,
    "info"
  );
}

function createContactItem(type, value, isPrimary) {
  const item = document.createElement("div");
  item.className = "contact-item";
  item.dataset.type = type;
  item.dataset.primary = isPrimary.toString();

  const icon =
    type === "phone"
      ? `<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>`
      : `<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
       <polyline points="22,6 12,13 2,6"></polyline>`;

  const iconClass = type === "phone" ? "phone-icon" : "email-icon";
  const inputType = type === "phone" ? "tel" : "email";
  const placeholder = type === "phone" ? "+91 XXXXXXXXXX" : "email@example.com";

  item.innerHTML = `
    <div class="contact-item-content">
      <div class="contact-icon ${iconClass}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          ${icon}
        </svg>
      </div>
      <div class="contact-details">
        <div class="contact-display">
          <span class="contact-value">${value || "Not available"}</span>
          ${isPrimary ? '<span class="primary-badge">Primary</span>' : ""}
        </div>
        <input type="${inputType}" class="contact-input" value="${value}" placeholder="${placeholder}" style="display: none;">
      </div>
    </div>
    <div class="contact-actions" style="display: none;">
      <button class="action-btn delete-btn" onclick="removeClientContact(this)" title="Remove">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  `;

  return item;
}

function removeClientContact(button) {
  const item = button.closest(".contact-item");
  const list = item.closest(".contact-list");
  const itemCount = list.querySelectorAll(".contact-item").length;

  if (itemCount <= 1) {
    showToast("Cannot Remove", "You must have at least one contact", "warning");
    return;
  }

  const type = item.dataset.type === "phone" ? "phone number" : "email address";
  item.remove();
  showToast("Contact Removed", `The ${type} has been removed`, "info");
}

// ========================================
// 11. FORM VALIDATION & SUBMISSION - UPDATED
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  console.log('DOM fully loaded and parsed');
  
  // ========================================
  // INITIALIZATION
  // ========================================
  
  // Initialize date pickers (auto-fills all empty date fields)
  setTimeout(() => {
    initializeDatePickers();
  }, 100);
  
  // Initialize all required fields with data-was-required attribute
  const containers = ['container-yes', 'container-regret', 'container-reconnect', 'container-future'];
  containers.forEach(containerId => {
    const container = document.getElementById(containerId);
    if (container) {
      container.querySelectorAll('[required]').forEach(field => {
        field.setAttribute('data-was-required', 'true');
        field.removeAttribute('required');
      });
    }
  });

  // Auto-fill expected call date (2 days after creation)
  const expectedField = document.getElementById("expected_call_date");
  if (expectedField && !expectedField.value) {
    // Get lead creation date from data attribute
    const leadDataEl = document.getElementById("lead-data");
    if (leadDataEl && leadDataEl.dataset.createdAt) {
      const createdDate = new Date(leadDataEl.dataset.createdAt);

      // Add 2 days to creation date
      const expectedDate = new Date(createdDate);
      expectedDate.setDate(createdDate.getDate() + 2);

      // Format as YYYY-MM-DD for input[type=date]
      const year = expectedDate.getFullYear();
      const month = String(expectedDate.getMonth() + 1).padStart(2, "0");
      const day = String(expectedDate.getDate()).padStart(2, "0");
      
      // Set value and update flatpickr if it exists
      expectedField.value = `${year}-${month}-${day}`;
      if (flatpickrInstances['expected_call_date']) {
        flatpickrInstances['expected_call_date'].setDate(expectedDate);
      }
    }
  }

  // Attach tank type change handler for regret
  const tankTypeRegret = document.getElementById("tank_type_regret");
  if (tankTypeRegret) {
    tankTypeRegret.addEventListener("change", handleTankTypeChangeRegret);
  }

  // Initialize remove buttons
  updateRemoveButtons();

  // ========================================
  // FORM SUBMISSION HANDLER
  // ========================================
  
  const form = document.getElementById("marketingForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault(); // Prevent default first
      
      const outcome = document.getElementById("outcomeField").value;
      const actualDate = document.getElementById("actual_call_date").value;

      if (!outcome) {
        showToast("Validation Error", "Please select an outcome", "error");
        return false;
      }

      if (!actualDate) {
        showToast(
          "Validation Error",
          "Please enter the actual call date",
          "error"
        );
        document.getElementById("actual_call_date").focus();
        return false;
      }

      let isValid = true;
      
      // Validate based on outcome
      if (outcome === "yes") {
        isValid = validateRequirementYes();
      } else if (outcome === "regret") {
        const clientType = document.getElementById("client_type_regret");
        const followup = document.getElementById("followup_date_regret");
        const tankType = document.getElementById("tank_type_regret");
        const remark = document.getElementById("remark_regret");

        if (!clientType || !clientType.value) {
          showToast("Validation Error", "Please select Type of Client", "error");
          if (clientType) clientType.focus();
          isValid = false;
        }

        // Validate sub-options
        if (clientType && clientType.value === "CONSULTANT") {
          const consultantType = document.getElementById("consultant_type_regret");
          if (!consultantType || !consultantType.value) {
            showToast("Validation Error", "Please select Consultant Type", "error");
            if (consultantType) consultantType.focus();
            isValid = false;
          }
          if (consultantType && consultantType.value === "Other") {
            const otherText = document.getElementById("consultant_other_text_regret");
            if (!otherText || !otherText.value.trim()) {
              showToast("Validation Error", "Please specify Consultant Type", "error");
              if (otherText) otherText.focus();
              isValid = false;
            }
          }
        } else if (clientType && clientType.value === "CONTRACTOR") {
          const contractorType = document.getElementById("contractor_type_regret");
          if (!contractorType || !contractorType.value) {
            showToast("Validation Error", "Please select Contractor Type", "error");
            if (contractorType) contractorType.focus();
            isValid = false;
          }
          if (contractorType && contractorType.value === "Other") {
            const otherText = document.getElementById("contractor_other_text_regret");
            if (!otherText || !otherText.value.trim()) {
              showToast("Validation Error", "Please specify Contractor Type", "error");
              if (otherText) otherText.focus();
              isValid = false;
            }
          }
        } else if (clientType && clientType.value === "END_CLIENT") {
          const endClientCategory = document.getElementById("endclient_category_regret");
          if (!endClientCategory || !endClientCategory.value) {
            showToast("Validation Error", "Please select End Client Category", "error");
            if (endClientCategory) endClientCategory.focus();
            isValid = false;
          }
          if (endClientCategory && endClientCategory.value === "Other") {
            const otherText = document.getElementById("endclient_other_text_regret");
            if (!otherText || !otherText.value.trim()) {
              showToast("Validation Error", "Please specify End Client Category", "error");
              if (otherText) otherText.focus();
              isValid = false;
            }
          }
        }

        if (!followup || !followup.value) {
          showToast("Validation Error", "Please enter Follow-up Date", "error");
          if (followup) followup.focus();
          isValid = false;
        }

        if (!tankType || !tankType.value) {
          showToast("Validation Error", "Please select Tank Type", "error");
          if (tankType) tankType.focus();
          isValid = false;
        }

        if (tankType && tankType.value === "Other") {
          const otherText = document.getElementById("tank_type_other_text_regret");
          if (!otherText || !otherText.value.trim()) {
            showToast("Validation Error", "Please specify Tank Type", "error");
            if (otherText) otherText.focus();
            isValid = false;
          }
        }

        if (!remark || !remark.value.trim()) {
          showToast("Validation Error", "Please enter Remark", "error");
          if (remark) remark.focus();
          isValid = false;
        }
      } else if (outcome === "reconnect") {
        const followup = document.getElementById("followup_date_reconnect");
        const remark = document.getElementById("remark_reconnect");

        if (!followup || !followup.value) {
          showToast("Validation Error", "Please enter Follow-up Date", "error");
          if (followup) followup.focus();
          isValid = false;
        }

        if (!remark || !remark.value.trim()) {
          showToast("Validation Error", "Please enter Remark", "error");
          if (remark) remark.focus();
          isValid = false;
        }
      } else if (outcome === "future") {
        const clientType = document.getElementById("client_type_future");
        const followup = document.getElementById("followup_date_future");
        const remark = document.getElementById("remark_future");

        if (!clientType || !clientType.value) {
          showToast("Validation Error", "Please select Type of Client", "error");
          if (clientType) clientType.focus();
          isValid = false;
        }

        // Validate sub-options
        if (clientType && clientType.value === "CONSULTANT") {
          const consultantType = document.getElementById("consultant_type_future");
          if (!consultantType || !consultantType.value) {
            showToast("Validation Error", "Please select Consultant Type", "error");
            if (consultantType) consultantType.focus();
            isValid = false;
          }
          if (consultantType && consultantType.value === "Other") {
            const otherText = document.getElementById("consultant_other_text_future");
            if (!otherText || !otherText.value.trim()) {
              showToast("Validation Error", "Please specify Consultant Type", "error");
              if (otherText) otherText.focus();
              isValid = false;
            }
          }
        } else if (clientType && clientType.value === "CONTRACTOR") {
          const contractorType = document.getElementById("contractor_type_future");
          if (!contractorType || !contractorType.value) {
            showToast("Validation Error", "Please select Contractor Type", "error");
            if (contractorType) contractorType.focus();
            isValid = false;
          }
          if (contractorType && contractorType.value === "Other") {
            const otherText = document.getElementById("contractor_other_text_future");
            if (!otherText || !otherText.value.trim()) {
              showToast("Validation Error", "Please specify Contractor Type", "error");
              if (otherText) otherText.focus();
              isValid = false;
            }
          }
        } else if (clientType && clientType.value === "END_CLIENT") {
          const endClientCategory = document.getElementById("endclient_category_future");
          if (!endClientCategory || !endClientCategory.value) {
            showToast("Validation Error", "Please select End Client Category", "error");
            if (endClientCategory) endClientCategory.focus();
            isValid = false;
          }
          if (endClientCategory && endClientCategory.value === "Other") {
            const otherText = document.getElementById("endclient_other_text_future");
            if (!otherText || !otherText.value.trim()) {
              showToast("Validation Error", "Please specify End Client Category", "error");
              if (otherText) otherText.focus();
              isValid = false;
            }
          }
        }

        if (!followup || !followup.value) {
          showToast("Validation Error", "Please enter Follow-up Date", "error");
          if (followup) followup.focus();
          isValid = false;
        }

        if (!remark || !remark.value.trim()) {
          showToast("Validation Error", "Please enter Remark", "error");
          if (remark) remark.focus();
          isValid = false;
        }
      }

      if (isValid) {
        showToast(
          "Submitting",
          "Marketing call information is being saved...",
          "info"
        );
        // Re-enable all required fields before submission
        const selectedContainer = document.getElementById(`container-${outcome}`);
        if (selectedContainer) {
          selectedContainer.querySelectorAll('[data-was-required]').forEach(field => {
            field.setAttribute('required', 'required');
          });
        }
        
        // Submit the form
        form.submit();
      }
    });
  }
});

// ========================================
// CLEANUP ON PAGE UNLOAD
// ========================================

window.addEventListener('beforeunload', function() {
  // Clean up flatpickr instances to prevent memory leaks
  Object.values(flatpickrInstances).forEach(instance => {
    if (instance && instance.destroy) {
      instance.destroy();
    }
  });
});

// Add a simple test function to check what's happening
function testDateAutoFill() {
  console.log('Testing date auto-fill...');
  const dateFields = document.querySelectorAll('input[type="date"]');
  console.log(`Found ${dateFields.length} date fields:`);
  
  dateFields.forEach((field, index) => {
    console.log(`${index + 1}. ${field.name || field.id || 'unnamed'}: ${field.value}`);
  });
  
  // Try to auto-fill one manually
  const today = new Date().toISOString().split('T')[0];
  const actualCallDate = document.getElementById('actual_call_date');
  if (actualCallDate) {
    console.log(`Actual Call Date field found. Current value: ${actualCallDate.value}`);
    if (!actualCallDate.value) {
      actualCallDate.value = today;
      console.log(`Manually set to: ${today}`);
    }
  }
}