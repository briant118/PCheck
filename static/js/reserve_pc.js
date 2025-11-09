// Wait for jQuery to be available
function initReservePC() {
  if (typeof jQuery === 'undefined' && typeof $ === 'undefined') {
    // jQuery not loaded yet, retry after a short delay
    setTimeout(initReservePC, 100);
    return;
  }
  
  var $ = jQuery || window.$;
  
  $(document).ready(function () {
    // Support both old .pc-button and new .pc-button-modern classes
    const $pcButton = $(".pc-button-modern, .pc-button");
    const $nextButton = $(".reserve-next-button");
    const $blockButton = $("#block-button");
    const $blockButtonNext = $("#block-button-next");
    const $pageNav = $("#page-nav");
    const $pcGroupButton = $(".pc-group-number");

  function cancelReservation(pcId) {
    $.ajax({
      url: "/ajax/cancel-reservation/",
      method: "POST",
      data: { pc_id: pcId },
      success: function (data) {
        console.log("Reservation cancelled");
      },
      error: function (xhr, status, error) {
        console.error("Error updating message status:", error);
      }
    });
  }

  // Note: PC selection is now handled by inline JavaScript in the template
  // This code is kept for backward compatibility with old templates
  $pcButton.click(function () {
    // Skip if already handled by template's selectPCForReservation function
    if ($(this).hasClass('pc-button-modern')) {
      return;
    }
    
    $(this).toggleClass("text-success");
    $("#pc_id").val($(this).data("pc-id"));

    const hasSelected = $pcButton.filter(".text-success").length > 0;

    // disable other buttons when one is selected, show/hide page nav
    $pcButton.not(this).prop("disabled", hasSelected);
    $pageNav.prop("hidden", hasSelected);

    // next visible when any selected; block hidden when any selected
    $nextButton.prop("hidden", !hasSelected);
    $blockButton.prop("hidden", hasSelected);
  });

  const reserveUrl = $("#generate-qr-button").data("reserve-url");

  // Show duration form on "Next"
  $nextButton.click(function () {
    $("#durationModal").modal("show");
  });

  // Plus and minus buttons
  $("#plusBtn").click(function () {
    let current = parseInt($("#durationInput").val()) || 0;
    $("#durationInput").val(current + 5); // increment by 5 mins
    if (current > 170) {
      $(this).prop("disabled", true);
    }
  });

  $("#minusBtn").click(function () {
    let current = parseInt($("#durationInput").val()) || 0;
    if (current > 1) {
      $("#durationInput").val(current - 5); // decrement by 5 mins
    }
    if (current < 185) {
      $("#plusBtn").prop("disabled", false);
    }
  });

  // Plus and minus fb buttons
  $("#fb-plusBtn").click(function () {
    let current = parseInt($("#customNumOfPc").val()) || 0;
    $("#customNumOfPc").val(current + 1); // increment by 1
    if (current > 15) {
      $(this).prop("disabled", true);
    }
  });

  $("#fb-minusBtn").click(function () {
    let current = parseInt($("#customNumOfPc").val()) || 0;
    if (current >= 1) {
      $("#customNumOfPc").val(current - 1); // decrement by 1
    }
    if (current < 15) {
      $("#fb-plusBtn").prop("disabled", false);
    }
  });

  // Plus button with max limit of 180 mins
  $("#plusBtn").click(function () {
    let current = parseInt($("#durationInput").val()) || 0;
    $("#durationInput").val(current + 5); // increment by 5 mins
    if (current > 170) {
      $(this).prop("disabled", true);
    }
  });

  $("#minusBtn").click(function () {
    let current = parseInt($("#durationInput").val()) || 0;
    if (current > 1) {
      $("#durationInput").val(current - 5); // decrement by 5 mins
    }
    if (current < 185) {
      $("#plusBtn").prop("disabled", false);
    }
  });

  let countdownInterval;

  $("#generate-qr-button").click(function () {
    let duration = $("#durationInput").val();
    let selected_pc = $("#pc_id").val();

    if (!duration || duration <= 0) {
      alert("Please enter a valid duration.");
      return;
    }

    // Validate PC status - check if selected PC is offline or in repair
    // Support both old and new button styles
    var selectedButton = $(".pc-button-modern.pc-selected, .pc-button-modern.selected, .pc-button.text-success").first();
    if (selectedButton.length > 0) {
      var pcStatus = selectedButton.attr('data-pc-status');
      var pcCondition = selectedButton.attr('data-pc-condition');
      var pcBookingStatus = selectedButton.attr('data-booking-status');
      var pcName = selectedButton.attr('data-pc-name');
      
      if (pcCondition === 'repair') {
        alert(`PC ${pcName} is currently in repair and cannot be reserved.\n\nPlease select a different PC.`);
        return;
      }
      
      if (pcStatus === 'disconnected') {
        alert(`PC ${pcName} is currently offline and cannot be reserved.\n\nPlease select a different PC.`);
        return;
      }
      
      if (pcBookingStatus === 'in_use' || pcBookingStatus === 'in_queue') {
        alert(`PC ${pcName} is currently ${pcBookingStatus.replace('_', ' ')} and cannot be reserved.\n\nPlease select a different PC.`);
        return;
      }
    }

    $.ajax({
      url: reserveUrl,
      type: "POST",
      data: {
        pc_id: selected_pc,
        duration: duration,
      },
      success: function (response) {
        $("#durationModal").modal("hide");

        // Show QR code in modal and enable re-open button
        var qrDataUrl = "data:image/png;base64," + response.qr_code;
        $("#qrImage").attr("src", qrDataUrl);
        $("#booking_id").text(response.booking_id);
        $("#qrModal").modal("show");
        // Persist last QR so user can re-open it after closing
        window.__lastQR__ = { img: qrDataUrl, bookingId: response.booking_id };
        $("#viewQRButtonContainer").show();

        // Countdown target = now + 10 minutes
        let endTime = new Date().getTime() + 10 * 60 * 1000;

        // Clear any old timer
        clearInterval(countdownInterval);

        // Start real-time countdown
        countdownInterval = setInterval(function () {
          let now = new Date().getTime();
          let diff = endTime - now;

          if (diff <= 0) {
            clearInterval(countdownInterval);
            $("#qrCountdown").text("00:00");
            $("#qrModal").modal("hide"); // auto-close
            // Hide View QR button because QR is no longer valid
            $("#viewQRButtonContainer").hide();
            cancelReservation(selected_pc);
            return;
          }

          let minutes = Math.floor(diff / 60000);
          let seconds = Math.floor((diff % 60000) / 1000);

          $("#qrCountdown").text(
            minutes.toString().padStart(2, "0") +
              ":" +
              seconds.toString().padStart(2, "0")
          );
        }, 1000);
      },
      error: function (xhr) {
        alert("Error: " + xhr.responseText);
      },
    });

    // Runs every 5 seconds until a request has been approved or denied
    function checkApproval(callback) {
      var bookingId = $("#booking_id").text();
      $.getJSON(`/ajax/waiting-approval/${bookingId}`)
        .done(function (data) {
          if (data.error) {
            console.log(data.error);
          } else {
            callback(data.status); // give status back via callback
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          console.error("Error fetching booking data:", errorThrown);
        });
    }

    // Run every 1 second
    let approvalChecker = setInterval(async function () {
      checkApproval(function (status) {
        if (status === "confirmed") {
          // alert("Your reservation has been confirmed!");
          $("#qrModal").fadeOut();
          $("#viewQRButtonContainer").hide();
          clearInterval(approvalChecker);
          // Clear the QR expiration countdown timer
          clearInterval(countdownInterval);
          console.log("Approval detected. QR expiration timer stopped.");
          let durationMinutes = parseInt($("#durationInput").val()); 
          let endTime = new Date().getTime() + durationMinutes * 60 * 1000;

          // Set booking ID for end session button
          var bookingId = $("#booking_id").text();
          var endSessionBtn = $("#end-session-early-btn");
          if (endSessionBtn.length && bookingId) {
            endSessionBtn.attr("data-booking-id", bookingId);
            console.log("Set booking_id on end-session-early-btn:", bookingId);
          }

          $("#timeRemainingModal").modal({
            backdrop: "static",  // prevent closing by clicking outside
            keyboard: false      // prevent closing with Esc key
          }).modal("show");

          // Start countdown timer
          let countdown = setInterval(function () {
            let now = new Date().getTime();
            let diff = endTime - now;

            if (diff <= 0) {
              clearInterval(countdown);
              $("#timeRemaining").text("Expired");
              return;
            }

            let minutes = Math.floor(diff / (1000 * 60));
            let seconds = Math.floor((diff % (1000 * 60)) / 1000);
            $("#timeRemaining").text(minutes + "m " + seconds + "s");
          }, 1000);
        } 
        else if (status === "cancelled"){
          $("#qrModal").fadeOut();
          clearInterval(approvalChecker);
          // Clear the QR expiration countdown timer
          clearInterval(countdownInterval);
          console.log("Reservation cancelled. QR expiration timer stopped.");
          alert("Your reservation has been declined!");
          window.location.href = "/pc-reservation/";
        } 
        else {
          console.log("Still waiting for approval...");
        }
      });
    }, 1000);
  });

  // Re-open last QR code if available
  $("#viewQRCodeBtn").on("click", function(){
    if (window.__lastQR__ && window.__lastQR__.img) {
      $("#qrImage").attr("src", window.__lastQR__.img);
      $("#booking_id").text(window.__lastQR__.bookingId || "");
      $("#qrModal").modal("show");
    }
  });

  $blockButton.on("click", function () {
    $("#students-booking").hide();
    $("#legend").hide();
    $("#faculty-booking-pc-group").prop("hidden", false);
    $(this).prop("hidden", true);
  });

  $pcGroupButton.click(function () {
    let qty = $(this).data("qty");
    $("#numOfPc").val(qty);
    $(this).toggleClass("bg-warning");
    const hasSelected = $pcGroupButton.filter(".bg-warning").length > 0;
    // disable other buttons when one is selected
    $pcGroupButton.not(this).prop("disabled", hasSelected);
    $blockButtonNext.prop("hidden", !hasSelected);
  });

  $blockButtonNext.click(function () {
    $("#legend-and-control").prop("hidden", true);
    $("#faculty-booking-pc-group").prop("hidden", true);
    $("#faculty-form-section").prop("hidden", false);
  });

  $(".next").click(function(){
    var nextStep = $(this).data("next");

    $(this).closest(".step").removeClass("active");
    $("#" + nextStep).addClass("active");
  });

  $("#emailList").on("input", function () {
    const input = $("#emailList").val();
    const emails = input.split(",").map(e => e.trim()).filter(e => e.length > 0);

    const validEmails = [];
    const invalidEmails = [];

    // Simple email validation regex
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    emails.forEach(email => {
      if (emailPattern.test(email)) {
        validEmails.push(email);
        if ($("#id_result").text() == 'None' && input != '') {
          $("#step3NextBtn").prop("hidden", false);
        }
      } else {
        invalidEmails.push(email);
      }
    });

    // Show result
    let resultHtml = ``;
    resultHtml += `<p><strong>Invalid emails:</strong> <span style="color:red;" id="id_result">${invalidEmails.join(", ") || 'None'}</span></p>`;

    $("#result").html(resultHtml);
  });
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initReservePC);
} else {
  initReservePC();
}