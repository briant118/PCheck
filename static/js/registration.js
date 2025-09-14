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
    // Combine prefix + domain into hidden field
    var prefix = $("#email_prefix").val().trim();
    var domain = "@psu.palawan.edu.ph";

    if (!regex.test(prefix)) {
      alert("Email prefix must only contain letters and numbers (no @ or .).");
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
