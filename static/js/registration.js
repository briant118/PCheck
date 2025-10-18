$(document).ready(function () {
  // Registration script
  // Handle next button clicks
  $(".next").click(function(){
    var nextStep = $(this).data("next");

    // if role button clicked, set role value
    if($(this).data("role")){
      $("#role").val($(this).data("role"));
    }

    $(this).closest(".step").removeClass("active");
    $("#" + nextStep).addClass("active");
  });

  // Handle form submit
  $("#registrationForm").on("submit", function(e) {
    console.log("registration submit handler triggered");
    // Optional: quick visual confirmation
    // alert("Submitting...");
    // Validate role selected
    var role = $("#role").val();
    if (!role) {
      alert("Please select your role.");
      e.preventDefault();
      return false;
    }

    // Combine prefix + domain into hidden field
    var prefix = $("#email_prefix").val().trim();
    var domain = "@psu.palawan.edu.ph";
    var regex = /^[A-Za-z0-9]+$/;

    if (!regex.test(prefix)) {
      alert("Email prefix must only contain letters and numbers (no @ or .).");
      e.preventDefault();
      return false;
    }

    $("#email_full").val(prefix + domain);

    // Validate names
    var firstName = $("input[name='first_name']").val().trim();
    var lastName = $("input[name='last_name']").val().trim();
    if (!firstName || !lastName) {
      alert("Please enter your first and last name.");
      e.preventDefault();
      return false;
    }

    // Validate college, course, year, block
    var college = $("select[name='college']").val();
    var course = $("input[name='course']").val().trim();
    var year = $("input[name='year']").val().trim();
    var block = $("input[name='block']").val().trim();
    if (!college || !course || !year || !block) {
      alert("Please complete your college details.");
      e.preventDefault();
      return false;
    }

    // Validate passwords
    var password = $("input[name='password']").val();
    var password2 = $("input[name='password2']").val();
    if (!password || !password2) {
      alert("Please enter and confirm your password.");
      e.preventDefault();
      return false;
    }
    if (password !== password2) {
      alert("Passwords do not match.");
      e.preventDefault();
      return false;
    }
  });

  $("#code4").on("input", function() {
    var codes = [];
    var code_str = ""
    for (var i = 1; i < 5; i++){
      code_str = "#code"+i
      codes.push($(code_str).val());
    }
    $("#code").val(codes.join(''));
    // console.log("codes", codes.join(''));
  });
  
  $("#code1").on("input", function() {
    $("#code2").focus();
  });
  
  $("#code2").on("input", function() {
    $("#code3").focus();
  });
  
  $("#code3").on("input", function() {
    $("#code4").focus();
  });

});
