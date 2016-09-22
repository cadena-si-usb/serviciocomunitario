jQuery(document).ready(function(){


  jQuery('#login').on('click', function (e) {
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
            $('#errorLogin').html("*El usuario o RIF o contraseña son incorrectos.");
          }
        });
      }else{
        $('#errorLogin').html("*Usuario o RIF incorrectos.");  
      }


    }
  });


});



