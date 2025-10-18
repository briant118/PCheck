$(document).ready(function () {
  const $pcButton = $(".pc-button");
  const $nextButton = $(".reserve-next-button");
  const $pageNav = $("#page-nav");

  // Bootstrap 5 modal instances
  const durationModal = new bootstrap.Modal(document.getElementById('durationModal'));
  const qrModal = new bootstrap.Modal(document.getElementById('qrModal'));
  
  // Auto-refresh PC status every 2 seconds for real-time updates
  setInterval(function() {
    refreshPCStatus();
  }, 2000);
  
  // Manual refresh button
  $('#manual-refresh').click(function() {
    refreshPCStatus();
  });
  
  // Function to refresh PC status
  function refreshPCStatus() {
    // Show loading indicator
    $('#last-updated').html('<i class="fa fa-sync-alt fa-spin text-primary"></i> Updating...');
    
    $.ajax({
      url: '/ajax/get-pc-status/',
      type: 'GET',
      success: function(data) {
        if (data.success) {
          console.log('PC Status Update:', data.pc_status);
          console.log('Debug Info:', data.debug_info);
          updatePCButtons(data.pc_status);
          updateLastRefreshTime();
        }
      },
      error: function() {
        console.log('Failed to refresh PC status');
        $('#last-updated').html('<i class="fa fa-exclamation-triangle text-warning"></i> Connection error');
      }
    });
  }
  
  // Function to update last refresh time
  function updateLastRefreshTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    $('#last-updated').html(`<i class="fa fa-check text-success"></i> Last updated: ${timeString}`);
  }
  
  // Function to update PC button states
  function updatePCButtons(pcStatus) {
    console.log('Updating PC buttons with status:', pcStatus);
    
    $('.pc-button').each(function() {
      const pcId = $(this).data('pc-id');
      const status = pcStatus[pcId];
      
      if (status) {
        console.log(`PC ${pcId} (${status.name}): ${status.booking_status} (${status.system_condition})`);
        
        // Update button appearance based on status
        $(this).removeClass('text-success text-warning text-danger text-secondary');
        $(this).removeAttr('disabled');
        
        if (status.system_condition === 'repair') {
          $(this).addClass('text-secondary').prop('disabled', true);
          $(this).attr('title', `PC ${status.name} - Status: Under Repair`);
          $(this).find('.pc-time-display').hide();
        } else if (status.booking_status === 'available') {
          $(this).addClass('text-success');
          $(this).attr('title', `PC ${status.name} - Status: Available`);
          $(this).find('.pc-time-display').hide();
        } else if (status.booking_status === 'in_queue') {
          $(this).addClass('text-warning').prop('disabled', true);
          $(this).attr('title', `PC ${status.name} - Status: In Queue`);
          $(this).find('.pc-time-display').hide();
        } else if (status.booking_status === 'in_use') {
          $(this).addClass('text-danger').prop('disabled', true);
          let title = `PC ${status.name} - Status: In Use`;
          const timeDisplay = $(this).find('.pc-time-display');
          
          if (status.remaining_time && status.remaining_time > 0) {
            const minutes = Math.floor(status.remaining_time / 60);
            const seconds = status.remaining_time % 60;
            const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            title += `\nTime remaining: ${timeString}`;
            
            // Show time on the button
            timeDisplay.text(timeString).show();
          } else {
            timeDisplay.hide();
          }
          $(this).attr('title', title);
        } else {
          $(this).addClass('text-secondary').prop('disabled', true);
          $(this).attr('title', `PC ${status.name} - Status: Offline`);
          $(this).find('.pc-time-display').hide();
        }
      } else {
        console.log(`No status found for PC ${pcId}`);
      }
    });
  }

  $pcButton.click(function () {
    // Only allow clicking on available PCs
    if ($(this).prop('disabled')) {
      const pcName = $(this).data("pc-name");
      const title = $(this).attr('title');
      const status = title.split('Status: ')[1].split('\n')[0];
      
      if (status === 'In Use') {
        // Show remaining time for PCs in use
        const timeRemaining = title.includes('Time remaining:') ? 
          '\n' + title.split('Time remaining:')[1] : '';
        alert(`PC ${pcName} is currently in use and cannot be selected.${timeRemaining}`);
      } else {
        alert(`PC ${pcName} is ${status} and cannot be selected.`);
      }
      return;
    }
    
    $(this).toggleClass("text-success");
    $("#pc_id").val($(this).data("pc-id"));
    console.log("PC ID:", $("#pc_id").val());
    $pcButton.not(this).prop("disabled", true); // Disable other buttons
    $pageNav.attr("hidden", true); // Hide pag navigation
    $nextButton.prop("hidden", !$pcButton.filter(".text-success").length); // Enable next button if any selected
    if (!$(this).hasClass("text-success")) {
      $pcButton.prop("disabled", false); // Re-enable all buttons if none selected
      $nextButton.prop("hidden", true); // Disable next button
      $pageNav.prop("hidden", false);
    }
  });

  const reserveUrl = $("#generate-qr-button").data("reserve-url");

  // Show duration form on "Next"
  $nextButton.click(function () {
    durationModal.show();
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

  let countdownInterval;

  $("#generate-qr-button").click(function () {
    let duration = $("#durationInput").val();
    let selected_pc = $("#pc_id").val();

    if (!duration || duration <= 0) {
      alert("Please enter a valid duration.");
      return;
    }

    $.ajax({
      url: reserveUrl,
      type: "POST",
      data: {
        pc_id: selected_pc,
        duration: duration,
      },
      success: function (response) {
        durationModal.hide();
        
        // Check if the reservation was successful
        if (!response.success) {
          alert(response.message || "Reservation failed. Please try again.");
          return;
        }

        // Show QR code in modal
        $("#qrImage").attr("src", "data:image/png;base64," + response.qr_code);
        $("#booking_id").text(response.booking_id);
        qrModal.show();
        
        // Immediately refresh PC status to show the booked PC as "In Queue"
        refreshPCStatus();

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
            qrModal.hide(); // auto-close
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
          alert("Your reservation has been confirmed!");
          $("#qrModal").fadeOut();
          clearInterval(approvalChecker);
          console.log("Approval detected. Script stopped.");
          let durationMinutes = parseInt($("#durationInput").val()); 
          let endTime = new Date().getTime() + durationMinutes * 60 * 1000;

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
          console.log("Approval detected. Script stopped.");
          alert("Your reservation has been declined!");
          window.location.href = "/pc-reservation/";
        } 
        else {
          console.log("Still waiting for approval...");
        }
      });
    }, 1000);
  });
});
