// Wait for jQuery to be available
function initReservePC() {
  if (typeof jQuery === 'undefined' && typeof $ === 'undefined') {
    // jQuery not loaded yet, retry after a short delay
    setTimeout(initReservePC, 100);
    return;
  }
  
  var $ = jQuery || window.$;
  // Helper to work with Bootstrap 5 modals without jQuery plugins
  function getBsModal(selector, options) {
    var el = document.querySelector(selector);
    if (!el || !window.bootstrap || !bootstrap.Modal) return null;
    var inst = bootstrap.Modal.getInstance(el);
    if (!inst) {
      inst = new bootstrap.Modal(el, options || {});
    }
    return inst;
  }
  
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
  // Use event delegation to handle clicks even if button is dynamically added/changed
  $(document).on('click', '.reserve-next-button:not(:disabled)', function (e) {
    e.preventDefault();
    e.stopPropagation();
    
    var $btn = $(this);
    
    // Check if a PC is selected
    var selectedPc = $("#pc_id").val();
    if (!selectedPc) {
      console.log('No PC selected');
      alert('Please select a PC first');
      return false;
    }
    
    console.log('Next button clicked, showing duration modal');
    var modal = getBsModal("#durationModal");
    if (modal) {
      modal.show();
    } else {
      console.error('Duration modal not found');
      alert('Error: Duration modal not found');
    }
    
    return false;
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
  let approvalChecker;

  // Check if current user has an active booking before showing View QR button
  // Only show View QR button if user has an active booking
  function checkAndShowViewQRButton() {
    // First check if user has an active booking
    $.ajax({
      url: '/ajax/get-my-active-booking/',
      method: 'GET',
      success: function(data) {
        console.log('Active booking check result:', data);
        
        // Only show View QR button if user has an active booking
        // Also check if booking is not finished/expired/cancelled/confirmed
        // View QR button should only show for pending bookings (waiting for approval)
        var isBookingActive = data.has_booking === true && 
                              data.booking_id && 
                              data.booking_status !== 'cancelled' &&
                              data.booking_status !== 'confirmed' &&
                              data.time_remaining !== 'Expired';
        
        // Allow showing only if booking is waiting for approval (not confirmed)
        if ((isBookingActive && data.booking_status !== 'confirmed') || 
            (data.booking_id && data.time_remaining === 'Waiting for approval' && data.booking_status !== 'confirmed')) {
          // User has an active booking, check if we have QR code data
          var hasQRData = false;
          
          if (window.__lastQR__ && window.__lastQR__.img) {
            // Verify the booking ID matches
            if (window.__lastQR__.bookingId == data.booking_id) {
              hasQRData = true;
              console.log('Found matching QR code for active booking');
            }
          } else {
            // Try to load from localStorage
            try {
              var storedQR = localStorage.getItem('qrCodeData');
              var storedBookingId = localStorage.getItem('qrBookingId');
              var storedTimestamp = localStorage.getItem('qrCodeTimestamp');
              
              if (storedQR && storedBookingId == data.booking_id) {
                // Check if QR code is still valid (10 minutes = 600000ms)
                var timestamp = storedTimestamp ? parseInt(storedTimestamp) : 0;
                var now = Date.now();
                var tenMinutes = 10 * 60 * 1000;
                
                if (timestamp && (now - timestamp) < tenMinutes) {
                  console.log('Found valid QR code in localStorage for active booking');
                  // Get end time from localStorage
                  var storedEndTime = localStorage.getItem('qrCodeEndTime');
                  var endTime = storedEndTime ? parseInt(storedEndTime) : null;
                  
                  // Restore to window.__lastQR__
                  window.__lastQR__ = {
                    img: storedQR,
                    bookingId: storedBookingId || '',
                    endTime: endTime
                  };
                  hasQRData = true;
                  
                  // Restart countdown if end time is available and valid
                  if (endTime) {
                    var now = Date.now();
                    if (endTime > now) {
                      restartCountdown(endTime);
                    }
                  }
                } else {
                  // QR code expired, clear it
                  console.log('QR code in localStorage expired, clearing');
                  localStorage.removeItem('qrCodeData');
                  localStorage.removeItem('qrBookingId');
                  localStorage.removeItem('qrCodeTimestamp');
                  localStorage.removeItem('qrCodeEndTime');
                }
              }
            } catch (e) {
              console.error('Error loading QR code from localStorage:', e);
            }
          }
          
          // Only show View QR button if we have QR data for this booking
          if (hasQRData) {
            $("#viewQRButtonContainer").show();
            $("#viewQRCodeButtonNext").show();
          } else {
            // Hide View QR button if no QR data for this booking
            $("#viewQRButtonContainer").hide();
            $("#viewQRCodeButtonNext").hide();
          }
        } else {
          // User has no active booking, hide View QR button and clear QR data
          console.log('User has no active booking, hiding View QR button');
          $("#viewQRButtonContainer").hide();
          $("#viewQRCodeButtonNext").hide();
          
          // Clear QR data if user has no active booking
          if (window.__lastQR__) {
            window.__lastQR__ = null;
          }
          try {
            localStorage.removeItem('qrCodeData');
            localStorage.removeItem('qrBookingId');
            localStorage.removeItem('qrCodeTimestamp');
            localStorage.removeItem('qrCodeEndTime');
          } catch (e) {
            console.error('Error clearing localStorage:', e);
          }
        }
      },
      error: function(xhr, status, error) {
        console.error('Error checking active booking:', error);
        // On error, hide View QR button to be safe
        $("#viewQRButtonContainer").hide();
        $("#viewQRCodeButtonNext").hide();
      }
    });
  }

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
        var durationModal = getBsModal("#durationModal");
        if (durationModal) durationModal.hide();

        // Show QR code in modal and enable re-open button
        var qrDataUrl = "data:image/png;base64," + response.qr_code;
        $("#qrImage").attr("src", qrDataUrl);
        $("#booking_id").text(response.booking_id);
        var qrModal = getBsModal("#qrModal");
        if (qrModal) qrModal.show();
        // Countdown target = now + 10 minutes
        let endTime = new Date().getTime() + 10 * 60 * 1000;
        
        // Persist last QR so user can re-open it after closing
        window.__lastQR__ = { 
          img: qrDataUrl, 
          bookingId: response.booking_id,
          endTime: endTime  // Store end time for countdown
        };
        
        // Save to localStorage so it persists after page refresh
        try {
          localStorage.setItem('qrCodeData', qrDataUrl);
          localStorage.setItem('qrBookingId', response.booking_id);
          localStorage.setItem('qrCodeTimestamp', Date.now().toString());
          localStorage.setItem('qrCodeEndTime', endTime.toString());
        } catch (e) {
          console.error('Error saving QR code to localStorage:', e);
        }
        
        // Show View QR button so user can view QR again after closing modal
        // Only show if user has an active booking (will be verified by checkAndShowViewQRButton)
        checkAndShowViewQRButton();
        
        // Immediately refresh PC status to show updated status to all users
        if (typeof window.refreshPCStatusForReservation === 'function') {
          // Refresh multiple times to ensure status is updated
          setTimeout(function() {
            window.refreshPCStatusForReservation();
          }, 500);
          setTimeout(function() {
            window.refreshPCStatusForReservation();
          }, 1500);
          setTimeout(function() {
            window.refreshPCStatusForReservation();
          }, 3000);
        }

        // Clear any old timer
        clearInterval(countdownInterval);

        // Start real-time countdown
        countdownInterval = setInterval(function () {
          let now = new Date().getTime();
          let diff = endTime - now;

          if (diff <= 0) {
            clearInterval(countdownInterval);
            $("#qrCountdown").text("00:00");
            var qrModalAuto = getBsModal("#qrModal");
            if (qrModalAuto) qrModalAuto.hide(); // auto-close
            // Hide View QR button because QR is no longer valid
            $("#viewQRButtonContainer").hide();
            $("#viewQRCodeButtonNext").hide();
            // Clear localStorage
            try {
              localStorage.removeItem('qrCodeData');
              localStorage.removeItem('qrBookingId');
              localStorage.removeItem('qrCodeTimestamp');
              localStorage.removeItem('qrCodeEndTime');
            } catch (e) {
              console.error('Error clearing localStorage:', e);
            }
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
    approvalChecker = setInterval(async function () {
      checkApproval(function (status) {
        if (status === "confirmed") {
          // alert("Your reservation has been confirmed!");
          $("#qrModal").fadeOut();
          $("#viewQRButtonContainer").hide();
          $("#viewQRCodeButtonNext").hide();
          // Clear localStorage when booking is confirmed (finished)
          try {
            localStorage.removeItem('qrCodeData');
            localStorage.removeItem('qrBookingId');
            localStorage.removeItem('qrCodeTimestamp');
            localStorage.removeItem('qrCodeEndTime');
          } catch (e) {
            console.error('Error clearing localStorage:', e);
          }
          // Clear QR data from memory when booking is confirmed/finished
          if (window.__lastQR__) {
            window.__lastQR__ = null;
          }
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

          var trModal = getBsModal("#timeRemainingModal", {
            backdrop: "static",
            keyboard: false
          });
          if (trModal) trModal.show();

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
          var qrModalCancelled = getBsModal("#qrModal");
          if (qrModalCancelled) qrModalCancelled.hide();
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
  // Use event delegation to handle clicks on dynamically added buttons
  $(document).on('click', '#viewQRCodeBtn', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('View QR Code button clicked');
    
    // Check if we have stored QR data
    if (window.__lastQR__ && window.__lastQR__.img) {
      console.log('Loading stored QR code');
      $("#qrImage").attr("src", window.__lastQR__.img);
      $("#booking_id").text(window.__lastQR__.bookingId || "");
      
      var qrModal = getBsModal("#qrModal");
      if (qrModal) {
        qrModal.show();
        // Restore countdown if available
        var countdownEl = $("#qrCountdown");
        if (countdownEl.length) {
          if (countdownInterval) {
            // Countdown is still running, it will update automatically
            // Just show the modal
          } else if (window.__lastQR__ && window.__lastQR__.endTime) {
            // Restart countdown based on stored end time
            var storedEndTime = window.__lastQR__.endTime;
            restartCountdown(storedEndTime);
          } else {
            // Try to get end time from localStorage
            try {
              var storedEndTime = localStorage.getItem('qrCodeEndTime');
              if (storedEndTime) {
                var endTime = parseInt(storedEndTime);
                var now = new Date().getTime();
                if (endTime > now) {
                  restartCountdown(endTime);
                } else {
                  countdownEl.text("00:00");
                }
              } else {
                countdownEl.text("Viewing saved QR");
              }
            } catch (e) {
              countdownEl.text("Viewing saved QR");
            }
          }
        }
      }
    } else {
      // Try to load from localStorage as fallback
      try {
        var storedQR = localStorage.getItem('qrCodeData');
        var storedBookingId = localStorage.getItem('qrBookingId');
        var storedEndTime = localStorage.getItem('qrCodeEndTime');
        if (storedQR) {
          console.log('Loading QR code from localStorage');
          $("#qrImage").attr("src", storedQR);
          if (storedBookingId) {
            $("#booking_id").text(storedBookingId);
          }
          var qrModal = getBsModal("#qrModal");
          if (qrModal) {
            qrModal.show();
            // Restart countdown if end time is available
            if (storedEndTime) {
              var endTime = parseInt(storedEndTime);
              var now = new Date().getTime();
              if (endTime > now) {
                restartCountdown(endTime);
              } else {
                $("#qrCountdown").text("00:00");
              }
            }
          }
        } else {
          alert('No QR code found. Please generate a QR code first.');
        }
      } catch (e) {
        console.error('Error loading QR code from localStorage:', e);
        alert('No QR code found. Please generate a QR code first.');
      }
    }
    
    return false;
  });

  // Cancel booking button handler - use event delegation for dynamically added buttons
  $(document).on('click', '#cancelBookingBtn', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Confirm cancellation
    if (!confirm('Are you sure you want to cancel this booking?')) {
      return false;
    }
    
    // Get booking ID and PC ID
    var bookingId = $("#booking_id").text().trim();
    var selectedPc = $("#pc_id").val();
    
    // Try to get PC ID from hidden field if available
    var pcIdInput = $("#qr_booking_pc_id");
    if (pcIdInput.length > 0) {
      selectedPc = pcIdInput.val() || selectedPc;
    }
    
    console.log('Cancel button clicked. Booking ID:', bookingId, 'PC ID:', selectedPc);
    
    // Validate that we have at least one identifier
    if (!bookingId && !selectedPc) {
      alert('Error: No booking information found. Please refresh the page and try again.');
      return false;
    }
    
    // Disable button to prevent multiple clicks
    var $btn = $(this);
    var originalHtml = $btn.html();
    $btn.prop('disabled', true);
    $btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Cancelling...');
    
    // Clear intervals
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
    if (approvalChecker) {
      clearInterval(approvalChecker);
      approvalChecker = null;
    }
    
    // Get CSRF token
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    
    var csrftoken = $('[name=csrfmiddlewaretoken]').val() || getCookie('csrftoken');
    
    // Send cancel request
    $.ajax({
      url: '/ajax/cancel-reservation/',
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken || ''
      },
      data: {
        booking_id: bookingId,
        pc_id: selectedPc
      },
      success: function(response) {
        console.log('Cancel booking response:', response);
        
        // Close QR modal
        var qrModal = getBsModal("#qrModal");
        if (qrModal) {
          qrModal.hide();
        }
        
        // After booking is cancelled, user no longer has active booking
        // So don't show View QR button - hide it instead
        $("#viewQRButtonContainer").hide();
        $("#viewQRCodeButtonNext").hide();
        
        // Clear QR data when booking is cancelled
        if (window.__lastQR__) {
          window.__lastQR__ = null;
        }
        try {
          localStorage.removeItem('qrCodeData');
          localStorage.removeItem('qrBookingId');
          localStorage.removeItem('qrCodeTimestamp');
          localStorage.removeItem('qrCodeEndTime');
        } catch (e) {
          console.error('Error clearing localStorage:', e);
        }
        
        // Show success message
        var message = 'Booking cancelled successfully';
        if (response && response.message) {
          message = response.message;
        }
        alert(message);
        
        // Don't reload page - keep the View QR button visible
        // User can still view the QR code if needed
      },
      error: function(xhr, status, error) {
        console.error('Cancel booking error:', xhr, status, error);
        
        // Extract error message from response
        var errorMsg = 'Failed to cancel booking';
        try {
          if (xhr.responseJSON && xhr.responseJSON.error) {
            errorMsg = xhr.responseJSON.error;
          } else if (xhr.responseText) {
            var jsonResponse = JSON.parse(xhr.responseText);
            if (jsonResponse.error) {
              errorMsg = jsonResponse.error;
            }
          }
        } catch (e) {
          console.error('Error parsing response:', e);
        }
        
        alert('Error: ' + errorMsg);
        
        // Re-enable button on failure
        $btn.prop('disabled', false);
        $btn.html(originalHtml);
      }
    });
    
    return false;
  });

  // Handle QR modal close event - refresh page when closed
  var qrModalElement = document.getElementById('qrModal');
  if (qrModalElement) {
    qrModalElement.addEventListener('hidden.bs.modal', function() {
      console.log('QR modal closed - refreshing page');
      
      // Refresh the page when modal is closed
      location.reload();
    });
  }

  // View QR Code button handler (under Next button)
  $(document).on('click', '#viewQRCodeBtnNext', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('View QR Code button (next) clicked');
    
    // Use the same handler as the other View QR buttons
    if (window.__lastQR__ && window.__lastQR__.img) {
      console.log('Loading stored QR code');
      $("#qrImage").attr("src", window.__lastQR__.img);
      $("#booking_id").text(window.__lastQR__.bookingId || "");
      
      var qrModal = getBsModal("#qrModal");
      if (qrModal) {
        qrModal.show();
        // Restore countdown if available
        var countdownEl = $("#qrCountdown");
        if (countdownEl.length) {
          if (countdownInterval) {
            // Countdown is still running, it will update automatically
            // Just show the modal
          } else if (window.__lastQR__ && window.__lastQR__.endTime) {
            // Restart countdown based on stored end time
            var storedEndTime = window.__lastQR__.endTime;
            restartCountdown(storedEndTime);
          } else {
            // Try to get end time from localStorage
            try {
              var storedEndTime = localStorage.getItem('qrCodeEndTime');
              if (storedEndTime) {
                var endTime = parseInt(storedEndTime);
                var now = new Date().getTime();
                if (endTime > now) {
                  restartCountdown(endTime);
                } else {
                  countdownEl.text("00:00");
                }
              } else {
                countdownEl.text("Viewing saved QR");
              }
            } catch (e) {
              countdownEl.text("Viewing saved QR");
            }
          }
        }
      }
    } else {
      // Try to load from localStorage as fallback
      try {
        var storedQR = localStorage.getItem('qrCodeData');
        var storedBookingId = localStorage.getItem('qrBookingId');
        var storedEndTime = localStorage.getItem('qrCodeEndTime');
        if (storedQR) {
          console.log('Loading QR code from localStorage');
          $("#qrImage").attr("src", storedQR);
          if (storedBookingId) {
            $("#booking_id").text(storedBookingId);
          }
          var qrModal = getBsModal("#qrModal");
          if (qrModal) {
            qrModal.show();
            // Restart countdown if end time is available
            if (storedEndTime) {
              var endTime = parseInt(storedEndTime);
              var now = new Date().getTime();
              if (endTime > now) {
                restartCountdown(endTime);
              } else {
                $("#qrCountdown").text("00:00");
              }
            }
          }
        } else {
          alert('No QR code found. Please generate a QR code first.');
        }
      } catch (e) {
        console.error('Error loading QR code from localStorage:', e);
        alert('No QR code found. Please generate a QR code first.');
      }
    }
    
    return false;
  });
  
  // Function to restart countdown timer
  function restartCountdown(endTime) {
    // Clear any existing countdown
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    
    // Start countdown timer
    countdownInterval = setInterval(function () {
      let now = new Date().getTime();
      let diff = endTime - now;

      if (diff <= 0) {
        clearInterval(countdownInterval);
        countdownInterval = null;
        $("#qrCountdown").text("00:00");
        var qrModalAuto = getBsModal("#qrModal");
        if (qrModalAuto) qrModalAuto.hide(); // auto-close
        // Hide View QR button because QR is no longer valid
        $("#viewQRButtonContainer").hide();
        $("#viewQRCodeButtonNext").hide();
        // Clear localStorage
        try {
          localStorage.removeItem('qrCodeData');
          localStorage.removeItem('qrBookingId');
          localStorage.removeItem('qrCodeTimestamp');
          localStorage.removeItem('qrCodeEndTime');
        } catch (e) {
          console.error('Error clearing localStorage:', e);
        }
        // Clear QR data from memory
        if (window.__lastQR__) {
          window.__lastQR__ = null;
        }
        // Verify booking is finished by checking with server
        checkAndShowViewQRButton();
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
  }
  
  // Periodically check if booking is still active and hide View QR button if finished
  // This ensures the button is hidden when booking finishes
  setInterval(function() {
    // Only check if View QR button is visible
    if ($("#viewQRCodeButtonNext").is(':visible') || $("#viewQRButtonContainer").is(':visible')) {
      checkAndShowViewQRButton();
    }
  }, 30000); // Check every 30 seconds

  // End Session button handler for QR modal
  $(document).on('click', '#endQRSessionBtn', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    var bookingId = $("#booking_id").text().trim();
    if (!bookingId) {
      // Show styled error alert
      showStyledAlert('Error', 'No booking ID found. Please refresh the page and try again.', 'danger');
      return false;
    }
    
    // Show custom confirmation modal
    var confirmModal = getBsModal("#confirmEndSessionModal");
    if (confirmModal) {
      confirmModal.show();
    }
    
    // Store booking ID for confirmation
    $("#confirmEndSessionBtn").data('booking-id', bookingId);
    
    return false;
  });
  
  // Confirm End Session button handler
  $(document).on('click', '#confirmEndSessionBtn', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    var bookingId = $(this).data('booking-id');
    if (!bookingId) {
      showStyledAlert('Error', 'No booking ID found. Please refresh the page and try again.', 'danger');
      var confirmModal = getBsModal("#confirmEndSessionModal");
      if (confirmModal) {
        confirmModal.hide();
      }
      return false;
    }
    
    var $btn = $(this);
    var originalHtml = $btn.html();
    $btn.prop('disabled', true);
    $btn.html('<i class="fa-solid fa-spinner fa-spin me-1"></i>Ending...');
    
    // Clear timers
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
    if (approvalChecker) {
      clearInterval(approvalChecker);
      approvalChecker = null;
    }
    
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    
    var csrftoken = $('[name=csrfmiddlewaretoken]').val() || getCookie('csrftoken');
    
    $.ajax({
      url: '/ajax/end-session/' + bookingId + '/',
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken || ''
      },
      success: function(response) {
        console.log('End session response:', response);
        
        // Close confirmation modal
        var confirmModal = getBsModal("#confirmEndSessionModal");
        if (confirmModal) {
          confirmModal.hide();
        }
        
        // Close QR modal
        var qrModal = getBsModal("#qrModal");
        if (qrModal) {
          qrModal.hide();
        }
        
        // Hide View QR button
        $("#viewQRButtonContainer").hide();
        $("#viewQRCodeButtonNext").hide();
        
        // Clear QR data
        if (window.__lastQR__) {
          window.__lastQR__ = null;
        }
        try {
          localStorage.removeItem('qrCodeData');
          localStorage.removeItem('qrBookingId');
          localStorage.removeItem('qrCodeTimestamp');
          localStorage.removeItem('qrCodeEndTime');
        } catch (e) {
          console.error('Error clearing localStorage:', e);
        }
        
        // Reload page immediately after session ends
        location.reload();
      },
      error: function(xhr, status, error) {
        console.error('Error ending session:', error);
        $btn.prop('disabled', false);
        $btn.html(originalHtml);
        
        var errorMsg = 'Failed to end session';
        if (xhr.responseJSON && xhr.responseJSON.error) {
          errorMsg = xhr.responseJSON.error;
        } else if (xhr.status === 403) {
          errorMsg = 'Permission denied. You can only end your own session.';
        } else if (xhr.status === 404) {
          errorMsg = 'Booking not found. It may have already been cancelled.';
        }
        
        // Show error alert
        showStyledAlert('Error', errorMsg, 'danger');
      }
    });
    
    return false;
  });
  
  // Function to show green success notification at top of available PC section
  function showSuccessNotification(message) {
    // Remove existing notification if any
    $('#successNotificationBanner').remove();
    
    // Find the students-booking container
    var studentsBooking = $('#students-booking');
    if (studentsBooking.length === 0) {
      console.error('students-booking container not found');
      return;
    }
    
    // Create notification banner
    var notificationHtml = `
      <div id="successNotificationBanner" class="alert alert-success alert-dismissible fade show" role="alert" style="
        position: relative;
        z-index: 1000;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(25, 135, 84, 0.2);
        animation: slideDown 0.3s ease-out;
      ">
        <i class="fa-solid fa-circle-check me-2"></i>
        <strong style="color: #198754;">${message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
    
    // Add CSS animation if not already added
    if (!$('#successNotificationStyle').length) {
      $('head').append(`
        <style id="successNotificationStyle">
          @keyframes slideDown {
            from {
              opacity: 0;
              transform: translateY(-20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          @keyframes fadeOut {
            from {
              opacity: 1;
            }
            to {
              opacity: 0;
            }
          }
        </style>
      `);
    }
    
    // Insert notification at the top of students-booking container
    studentsBooking.prepend(notificationHtml);
    
    // Auto-dismiss after 10 seconds
    setTimeout(function() {
      var notification = $('#successNotificationBanner');
      if (notification.length) {
        notification.css('animation', 'fadeOut 0.5s ease-out');
        setTimeout(function() {
          notification.alert('close');
        }, 500);
      }
    }, 10000);
  }
  
  // Function to show styled alert modal
  function showStyledAlert(title, message, type, callback) {
    // Remove existing alert modal if any
    $('#styledAlertModal').remove();
    
    var iconClass = 'fa-circle-check';
    var bgClass = 'bg-success';
    if (type === 'danger') {
      iconClass = 'fa-circle-exclamation';
      bgClass = 'bg-danger';
    } else if (type === 'warning') {
      iconClass = 'fa-triangle-exclamation';
      bgClass = 'bg-warning text-dark';
    } else if (type === 'info') {
      iconClass = 'fa-circle-info';
      bgClass = 'bg-info';
    }
    
    var alertHtml = `
      <div class="modal fade" id="styledAlertModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg">
            <div class="modal-header ${bgClass} text-white border-0">
              <h5 class="modal-title">
                <i class="fa-solid ${iconClass} me-2"></i>${title}
              </h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-center py-4">
              <p class="mb-0">${message}</p>
            </div>
            <div class="modal-footer border-0 justify-content-center pb-4">
              <button type="button" class="btn btn-primary" data-bs-dismiss="modal">OK</button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    $('body').append(alertHtml);
    
    var alertModal = getBsModal("#styledAlertModal");
    if (alertModal) {
      alertModal.show();
      
      // Handle callback when modal is closed
      if (callback && typeof callback === 'function') {
        $('#styledAlertModal').on('hidden.bs.modal', function() {
          callback();
          $(this).remove();
        });
        
        // Auto-close after 5 seconds if user doesn't close it manually
        setTimeout(function() {
          var modal = getBsModal("#styledAlertModal");
          if (modal) {
            modal.hide();
          }
        }, 5000);
      } else {
        $('#styledAlertModal').on('hidden.bs.modal', function() {
          $(this).remove();
        });
      }
    }
  }

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
  
  // Check on page load if user has active booking and show View QR button
  checkAndShowViewQRButton();
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initReservePC);
} else {
  initReservePC();
}