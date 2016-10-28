jQuery(document).ready(function(){
  $('#errorBox').hide();

  jQuery('#login').on('click', function (e) {
    $('#registro').hide();
    //console.log(jQuery("#user").val());
    if ((jQuery("#user").val()!=="") &&(jQuery("#pasword").val()!=="")){
      var expUser=/^[a-z\d_]{3,15}$/i;  
      var expRif=/^[JGVEP][-][0-9]{8}[-][0-9]{1}$/;

      var OK = expUser.exec(jQuery("#user").val()) ||(jQuery("#user").val().length >=3); 

      if (OK){

        $.ajax('login_sin_usbid?user='+jQuery("#user").val()+"&pasword="+jQuery("#pasword").val()
        ).done(function(html) {
          if (html=="Si"){
            var path=window.location.pathname.replace("index", "home");
            window.location.pathname=path;
          }else{
            //$('#errorLogin').empty();
            $('#errorLogin').html("Usuario, RIF o clave incorrectos.");
            $('#errorLogin').show();
            $('#errorBox').show();
          }
        });
      }else{
        $('#errorLogin').html("*Usuario o RIF incorrectos.");  
        $('#errorLogin').show();
        $('#errorBox').show();
      }


    }else{
        $('#errorLogin').html("*El Usuario RIF o clave no pueden estar vacíos.");  
        $('#errorLogin').show();
        $('#errorBox').show();
    }
  });


});



