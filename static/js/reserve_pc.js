$(document).ready(function () {
  const $pcButton = $(".pc-button");
  const $nextButton = $(".reserve-next-button");
  const $blockButton = $("#block-button");
  const $blockButtonNext = $("#block-button-next");
  const $pageNav = $("#page-nav");
  const $pcGroupButton = $(".pc-group-number");

  $pcButton.click(function () {
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
    let current = parseInt($("#numOfPc").val()) || 0;
    $("#numOfPc").val(current + 1); // increment by 1
    if (current > 15) {
      $(this).prop("disabled", true);
    }
  });

  $("#fb-minusBtn").click(function () {
    let current = parseInt($("#numOfPc").val()) || 0;
    if (current >= 1) {
      $("#numOfPc").val(current - 1); // decrement by 1
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

  $blockButton.on("click", function () {
    $("#students-booking").hide();
    $("#legend").hide();
    $("#faculty-booking-pc-group").prop("hidden", false);
    $(this).prop("hidden", true);
  });

  $pcGroupButton.click(function () {
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

  $("#facultyFormSubmit").click(function () {
    $("#step3").prop("hidden", true);
    $("#step4").prop("hidden", false);
    $("#step4").addClass("active");
  });
});
