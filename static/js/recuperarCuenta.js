jQuery(document).ready(function(){

  var errorUsuario="El usuario: debe tener al menos 4 caracteres, comenzar con una letra minuscula o mayuscula. </br>Puede poseer numeros y los siguientes caracteres especiales: (@.#$-_+*). </br> El Rif: Ejemplo: J-21232343-1.";
  var errorEmail='Formato de correo no reconocido, Ejemplo: example@example.com';
  var errorUsuarioNoEncontrado="Usuarío no encontrado en la base de datos del sistema.";
  var errorEmailNoEncontrado="Email no encontrado en la base de datos del sistema.";

  enviarDatos=function(accion,input){ 
   $.ajax('buscarCuenta?input='+input+"&accion="+accion).done(function(respuesta) {
        if (respuesta=="Si"){
          var path=window.location.pathname.replace("recuperarCuenta", "correoRecuperarCuenta");
          window.location.pathname=path;
          //alert("si");
        }else{
          jQuery("#errorFormUser").empty();
          jQuery("#errorFormEmail").empty();
          if (accion==="usuario"){
            jQuery("#errorFormUser").html(errorUsuarioNoEncontrado);
          }else{
            jQuery("#errorFormEmail").html(errorEmailNoEncontrado);
          }
        }
    });
  }; 

  jQuery('#enviar-usuario').on('click', function (e) {
    var debeTener=/^[a-z0-9A-Z@.\-_#$+*]+$/;
    var letrasMinusculas=/[a-z]/;
    var letrasMayusculas=/[A-Z]/  
    var inputUser=jQuery("#auth_user_username").val();
    if (inputUser!==""){
      var Okuser = inputUser.length >=4 && inputUser.match(debeTener)!=null && ((inputUser.search(letrasMinusculas)==0) || (inputUser.search(letrasMayusculas)==0)); 
      var expRif=/^[JGVEP][-][0-9]{8}[-][0-9]{1}$/;
      var OKrif = expRif.exec(jQuery("#rif input").val()); 

      if (Okuser || OKrif){
        enviarDatos("usuario",inputUser);
      }else{
        jQuery("#errorFormEmail").empty();
        jQuery("#errorFormUser").html(errorUsuario);
      }
    }
  });

  jQuery('#enviar-email').on('click', function (e) {
    var correo=/^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$/
    var inputEmail=jQuery("#auth_user_email").val();
    if (inputEmail!==""){
      var Okemail=inputEmail.match(correo)!=null;
      if (Okemail){
        enviarDatos("email",inputEmail);
      }else{
        jQuery("#errorFormUser").empty();
        jQuery("#errorFormEmail").html(errorEmail); 
      }
      
    } 
  });

});
  