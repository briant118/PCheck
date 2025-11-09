console.log("pc_management.js is loading...");
console.log("jQuery available:", typeof $ !== 'undefined');

$(document).ready(function () {
  console.log("pc_management.js: Document ready, jQuery version:", $.fn.jquery);
  
  // Try both approaches
  var $addPCbutton1 = $("#addPCbutton");
  var $addPCbutton2 = jQuery("#addPCbutton");
  
  console.log("Add PC button (with $):", $addPCbutton1.length);
  console.log("Add PC button (with jQuery):", $addPCbutton2.length);
  console.log("All buttons with ID:", $("button[id='addPCbutton']").length);
  
  const $ip_address = $("#id_ip_address");
  const $connectButton = $("#connectButton");
  const $statusIndicator = $("#status_indicator");
  const $addPCbutton = $addPCbutton1.length > 0 ? $addPCbutton1 : $("button").filter(function() { return $(this).text().includes("Add PC"); });
  const $PCformDiv = $("#PCformDiv");
  const $status = $("#id_status");
  const $name = $("#id_name");
  const $nameError = $("#name-error");
  const $ip_addressError = $("#ip-address-error");
  const $cancelButton = $("#cancel-button");
  const $repairButton = $("#repair-button");

  console.log("Add PC button found:", $addPCbutton.length > 0);

  // Validate PC name duplication
  $name.on("change", function () {
    $.getJSON(`/ajax/verify-pc-name/?name=${$name.val()}`)
      .done(function (data) {
        if (data.error) {
          console.log(data.error);
        } else {
          if (data.result) {
            $nameError.text("PC with this name already exists.");
          } else {
            $nameError.text("");
          }
        }
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Error fetching name data:", errorThrown);
      });
  });

  // Validate IP address duplication
  $ip_address.on("change", function () {
    $.getJSON(`/ajax/verify-pc-ip-address/?ip_address=${$ip_address.val()}`)
      .done(function (data) {
        if (data.error) {
          console.log(data.error);
        } else {
          if (data.result) {
            $ip_addressError.text("PC with this IP address already exists.");
          } else {
            $ip_addressError.text("");
          }
        }
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Error fetching name data:", errorThrown);
      });
  });

  // Trigger ping IP address
  $connectButton.on("click", function (e) {
    e.preventDefault();
    const ipAddress = $ip_address.val();

    // Spinner
    if (
      $.trim($statusIndicator.text()) != "reachable" ||
      $.trim($statusIndicator.text()) != "unreachable"
    ) {
      $("#spinner").show();
    } else {
      $("#spinner").hide();
    }

    $(document).on("contentLoaded", function () {
      $("#spinner").hide();
    });

    if (ipAddress) {
      $.getJSON(`/ajax/get-ping-data/?ip_address=${ipAddress}`)
        .done(function (data) {
          if (data.error) {
            console.log(data.error);
          } else {
            console.log("result:", data);
            $statusIndicator.text(data.result ? "Reachable" : "Unreachable");
            if (data.result) {
              $statusIndicator
                .removeClass("text-danger")
                .addClass("text-success");
              $status.val("connected");
            } else {
              $statusIndicator
                .removeClass("text-success")
                .addClass("text-danger");
              $status.val("disconnected");
            }
            $("#spinner").hide();
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching ping data:", errorThrown);
        });
    } else {
      alert("Please enter an IP address.");
    }
  });

  // Function to show Add PC modal
  function showAddPcModal() {
    console.log("Showing Add PC Modal");
    
    // Clear form fields
    $("#add-pc_id").val("");
    $("#add-id_name").val("");
    $("#add-id_ip_address").val("");
    $("#add-id_status").val("connected");
    $("#add-id_system_condition").val("active");
    $("#add-status_indicator").text("");
    
    // Clear error messages
    $("#add-name-error").text("");
    $("#add-ip-address-error").text("");
    
    // Show modal using Bootstrap 5
    var modalElement = document.getElementById("addPcModal");
    if (modalElement) {
      var existingModal = bootstrap.Modal.getInstance(modalElement);
      if (existingModal) {
        existingModal.show();
      } else {
        var modal = new bootstrap.Modal(modalElement, {
          backdrop: true,
          keyboard: true,
          focus: true
        });
        modal.show();
      }
    } else {
      console.error("Add PC modal element not found!");
    }
  }

  // Add PC button handler
  console.log("Attaching Add PC button handler...");
  $addPCbutton.on("click", function (e) {
    console.log("Add PC button clicked!");
    e.preventDefault();
    showAddPcModal();
  });

  // Function to show PC information modal
  function showPCInfoModal(id, name, ip, status, health) {
    console.log("Showing PC Info Modal:", { id, name, ip, status, health });
    
    // Set modal content
    $("#modal-pc-name").text(name || "-");
    $("#modal-pc-ip").text(ip || "-");
    
    // Set status badge
    var statusBadge = $("#modal-status-badge");
    statusBadge.removeClass("bg-success bg-danger bg-warning");
    if (status === "connected") {
      statusBadge.text("Connected").addClass("bg-success");
    } else {
      statusBadge.text("Disconnected").addClass("bg-danger");
    }
    
    // Set health badge
    var healthBadge = $("#modal-health-badge");
    healthBadge.removeClass("bg-success bg-danger bg-warning");
    if (health === "active") {
      healthBadge.text("Active").addClass("bg-success");
    } else if (health === "repair") {
      healthBadge.text("Repair").addClass("bg-danger");
    } else {
      healthBadge.text(health || "-");
    }
    
    // Set edit button to show edit modal
    $("#modal-edit-btn").off("click").on("click", function() {
      // Close info modal
      var modalElement = document.getElementById("pcInfoModal");
      var modal = bootstrap.Modal.getInstance(modalElement);
      if (modal) {
        modal.hide();
      }
      // Show edit modal
      showEditPcModal(id, name, ip, status, health);
    });
    
    // Show modal using Bootstrap 5
    var modalElement = document.getElementById("pcInfoModal");
    if (modalElement) {
      // Check if modal instance already exists
      var existingModal = bootstrap.Modal.getInstance(modalElement);
      if (existingModal) {
        existingModal.show();
      } else {
        var modal = new bootstrap.Modal(modalElement, {
          backdrop: true,
          keyboard: true,
          focus: true
        });
        modal.show();
      }
    } else {
      console.error("Modal element not found!");
    }
  }

  // Function to show Edit PC modal
  function showEditPcModal(id, name, ip, status, health) {
    console.log("Showing Edit PC Modal:", { id, name, ip, status, health });
    
    // Fill edit modal form fields
    $("#edit-pc_id").val(id || "");
    $("#edit-id_name").val(name || "");
    $("#edit-id_ip_address").val(ip || "");
    $("#edit-id_status").val(status || "connected");
    $("#edit-id_system_condition").val(health || "active");
    $("#edit-status_indicator").text("");
    
    // Clear error messages
    $("#edit-name-error").text("");
    $("#edit-ip-address-error").text("");
    
    // Show modal using Bootstrap 5
    var modalElement = document.getElementById("editPcModal");
    if (modalElement) {
      var existingModal = bootstrap.Modal.getInstance(modalElement);
      if (existingModal) {
        existingModal.show();
      } else {
        var modal = new bootstrap.Modal(modalElement, {
          backdrop: true,
          keyboard: true,
          focus: true
        });
        modal.show();
      }
    } else {
      console.error("Edit modal element not found!");
    }
  }

  // Function to fill PC form - kept for backward compatibility, now shows modal
  function fillPCForm(id, name, ip, status, health) {
    showEditPcModal(id, name, ip, status, health);
  }

  // Make edit-row clickable - use event delegation to handle dynamically added rows
  $(document).on("click", ".edit-row", function (e) {
    // Don't trigger if clicking on delete button
    if ($(e.target).closest(".delete-pc-link").length > 0) {
      console.log("Delete link clicked, ignoring row click");
      return;
    }
    
    e.preventDefault();
    e.stopPropagation();
    
    let id = $(this).data("pc-id");
    let name = $(this).data("name");
    let ip = $(this).data("ip");
    let status = $(this).data("status");
    let health = $(this).data("health");
    
    console.log("Edit row clicked:", id, name);
    
    // Show edit modal
    showEditPcModal(id, name, ip, status, health);
  });

  // Handle form submission  
  $("#pc-form").on("submit", function(e) {
    console.log("Form is being submitted");
    
    // Check if form has required fields
    var name = $(this).find('input[name="name"]').val();
    var ipAddress = $(this).find('input[name="ip_address"]').val();
    
    if (!name || name.trim() === '') {
      alert("Please enter a PC name");
      e.preventDefault();
      return false;
    }
    if (!ipAddress || ipAddress.trim() === '') {
      alert("Please enter an IP address");
      e.preventDefault();
      return false;
    }
    
    console.log("Form validation passed, submitting...");
    // Don't prevent default - let form submit normally
    return true;
  });

  $cancelButton.click(function () {
    // Clear form
    $("#pc_id").val("");
    $("#id_name").val("");
    $("#id_ip_address").val("");
    $("#id_status").val("connected");
    $("#id_system_condition").val("active");
    $("#status_indicator").text("");
    $("#form-title").text("Add a PC");
    $PCformDiv.attr("hidden", true);
    $addPCbutton.removeClass("bg-warning");
    $("#cancel-button").hide();
  });

  let currentUrl = new URL(window.location.href);
  let repairBtn = $("#repair-button");
  let allPcBtn = $("#all-pc-button");

  // Set initial Filter button state based on URL
  if (currentUrl.searchParams.get("filter") === "repair") {
    repairBtn.addClass("bg-warning");
    allPcBtn.removeClass("bg-warning");
  } else {
    allPcBtn.addClass("bg-warning");
    repairBtn.removeClass("bg-warning");
  }

  // Handle All PC button click
  allPcBtn.on("click", function (e) {
    e.preventDefault();
    currentUrl.searchParams.delete("filter");
    window.location.href = currentUrl.pathname;
  });

  // Handle Repair button click
  repairBtn.on("click", function (e) {
    e.preventDefault();
    currentUrl.searchParams.set("filter", "repair");
    window.location.href = currentUrl.toString();
  });

  // Handle PC list button clicks - use event delegation
  $(document).on("click", ".pc-list-button", function (e) {
    // Don't trigger if clicking on delete button
    if ($(e.target).closest(".delete-pc-btn").length > 0) {
      console.log("Delete button clicked, ignoring button click");
      return;
    }
    
    e.preventDefault();
    e.stopPropagation();
    
    let id = $(this).data("pc-id");
    let name = $(this).data("pc-name");
    let ip = $(this).data("pc-ip");
    let status = $(this).data("pc-status");
    let health = $(this).data("pc-health");
    
    console.log("PC list button clicked:", id, name);
    
    // Show edit modal
    showEditPcModal(id, name, ip, status, health);
    
    // Highlight selected button
    $(".pc-list-button").removeClass("selected-pc");
    $(this).addClass("selected-pc");
  });

  // Add PC modal handlers
  // Test connection button in add modal
  $("#add-connectButton").on("click", function(e) {
    e.preventDefault();
    const ipAddress = $("#add-id_ip_address").val();
    const $statusIndicator = $("#add-status_indicator");
    const $spinner = $("#add-spinner");
    const $status = $("#add-id_status");

    if ($spinner.length) {
      $spinner.show();
    }

    if (ipAddress) {
      $.getJSON(`/ajax/get-ping-data/?ip_address=${ipAddress}`)
        .done(function (data) {
          if ($spinner.length) {
            $spinner.hide();
          }
          if (data.error) {
            console.log(data.error);
          } else {
            console.log("result:", data);
            if (data.result) {
              $statusIndicator.text("Reachable")
                .removeClass("text-danger")
                .addClass("text-success");
              $status.val("connected");
            } else {
              $statusIndicator.text("Unreachable")
                .removeClass("text-success")
                .addClass("text-danger");
              $status.val("disconnected");
            }
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching ping data:", errorThrown);
          if ($spinner.length) {
            $spinner.hide();
          }
        });
    } else {
      alert("Please enter an IP address.");
      if ($spinner.length) {
        $spinner.hide();
      }
    }
  });

  // Name validation in add modal
  $("#add-id_name").on("change", function () {
    const name = $(this).val();
    if (name) {
      $.getJSON(`/ajax/verify-pc-name/?name=${name}`)
        .done(function (data) {
          if (data.error) {
            console.log(data.error);
          } else {
            if (data.result) {
              $("#add-name-error").text("PC with this name already exists.");
            } else {
              $("#add-name-error").text("");
            }
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching name data:", errorThrown);
        });
    }
  });

  // IP validation in add modal
  $("#add-id_ip_address").on("change", function () {
    const ip = $(this).val();
    if (ip) {
      $.getJSON(`/ajax/verify-pc-ip-address/?ip_address=${ip}`)
        .done(function (data) {
          if (data.error) {
            console.log(data.error);
          } else {
            if (data.result) {
              $("#add-ip-address-error").text("PC with this IP address already exists.");
            } else {
              $("#add-ip-address-error").text("");
            }
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching IP data:", errorThrown);
        });
    }
  });

  // Add form submission
  $("#add-pc-form").on("submit", function(e) {
    console.log("Add form is being submitted");
    
    const name = $("#add-id_name").val();
    const ipAddress = $("#add-id_ip_address").val();
    
    if (!name || name.trim() === '') {
      alert("Please enter a PC name");
      e.preventDefault();
      return false;
    }
    if (!ipAddress || ipAddress.trim() === '') {
      alert("Please enter an IP address");
      e.preventDefault();
      return false;
    }
    
    console.log("Add form validation passed, submitting...");
    return true;
  });

  // Edit modal handlers
  // Test connection button in edit modal
  $("#edit-connectButton").on("click", function(e) {
    e.preventDefault();
    const ipAddress = $("#edit-id_ip_address").val();
    const $statusIndicator = $("#edit-status_indicator");
    const $spinner = $("#edit-spinner");
    const $status = $("#edit-id_status");

    if ($spinner.length) {
      $spinner.show();
    }

    if (ipAddress) {
      $.getJSON(`/ajax/get-ping-data/?ip_address=${ipAddress}`)
        .done(function (data) {
          if ($spinner.length) {
            $spinner.hide();
          }
          if (data.error) {
            console.log(data.error);
          } else {
            console.log("result:", data);
            if (data.result) {
              $statusIndicator.text("Reachable")
                .removeClass("text-danger")
                .addClass("text-success");
              $status.val("connected");
            } else {
              $statusIndicator.text("Unreachable")
                .removeClass("text-success")
                .addClass("text-danger");
              $status.val("disconnected");
            }
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching ping data:", errorThrown);
          if ($spinner.length) {
            $spinner.hide();
          }
        });
    } else {
      alert("Please enter an IP address.");
      if ($spinner.length) {
        $spinner.hide();
      }
    }
  });

  // Name validation in edit modal
  $("#edit-id_name").on("change", function () {
    const name = $(this).val();
    const pcId = $("#edit-pc_id").val();
    if (name) {
      $.getJSON(`/ajax/verify-pc-name/?name=${name}&exclude_id=${pcId}`)
        .done(function (data) {
          if (data.error) {
            console.log(data.error);
          } else {
            if (data.result) {
              $("#edit-name-error").text("PC with this name already exists.");
            } else {
              $("#edit-name-error").text("");
            }
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching name data:", errorThrown);
        });
    }
  });

  // IP validation in edit modal
  $("#edit-id_ip_address").on("change", function () {
    const ip = $(this).val();
    const pcId = $("#edit-pc_id").val();
    if (ip) {
      $.getJSON(`/ajax/verify-pc-ip-address/?ip_address=${ip}&exclude_id=${pcId}`)
        .done(function (data) {
          if (data.error) {
            console.log(data.error);
          } else {
            if (data.result) {
              $("#edit-ip-address-error").text("PC with this IP address already exists.");
            } else {
              $("#edit-ip-address-error").text("");
            }
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching IP data:", errorThrown);
        });
    }
  });

  // Edit form submission
  $("#edit-pc-form").on("submit", function(e) {
    console.log("Edit form is being submitted");
    
    const name = $("#edit-id_name").val();
    const ipAddress = $("#edit-id_ip_address").val();
    
    if (!name || name.trim() === '') {
      alert("Please enter a PC name");
      e.preventDefault();
      return false;
    }
    if (!ipAddress || ipAddress.trim() === '') {
      alert("Please enter an IP address");
      e.preventDefault();
      return false;
    }
    
    console.log("Edit form validation passed, submitting...");
    return true;
  });

});
