$(document).ready(function () {
  const $pcButton = $(".pc-button");
  const $nextButton = $(".reserve-next-button");
  const $pageNav = $("#page-nav");

  $pcButton.click(function () {
    $(this).toggleClass("text-success");
    $("#pc_id").val($(this).data("pc-id"));
    console.log("PC ID:", $("#pc_id").val());
    $pcButton.not(this).prop("disabled", true); // Disable other buttons
    $pageNav.prop("hidden", true); // Hide pag navigation
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
        $("#durationModal").modal("hide");

        // Show QR code in modal
        $("#qrImage").attr("src", "data:image/png;base64," + response.qr_code);
        $("#booking_id").text(response.booking_id);
        $("#qrModal").modal("show");

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

    // Run every 5 seconds
    let approvalChecker = setInterval(function () {
      checkApproval(function (status) {
        if (status === "confirmed" || status === "cancelled") {
          $("#qrModal").fadeOut();
          clearInterval(approvalChecker);
          console.log("Approval detected. Script stopped.");
          alert("Your reservation has been " + status + "!");
          window.location.href = "/reserve-pc/";
        } else {
          console.log("Still waiting for approval...");
        }
      });
    }, 5000);
  });
});
