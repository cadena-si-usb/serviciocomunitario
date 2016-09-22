jQuery(document).ready(function(){

  var debeTener=/^[a-z0-9A-Z@.\-_#$+*]+$/;
  var letrasMinusculas=/[a-z]/;
  var numeros=/[0-9]/;
  var letrasMayusculas=/[A-Z]/
  var caracteresEspeciales=/[@.#\-_$+*]/;

  var acceptPassword=function(clave){

      if ((clave.match(debeTener)!==null) && (clave.search(numeros)!==-1) 
        && (clave.search(letrasMayusculas)!==-1) && (clave.search(letrasMinusculas)!==-1) 
        && (clave.search(caracteresEspeciales)!==-1) && (clave.length>=8)){
        return true;
      }else{
        return false;
      }

  };

  enviarDatos=function(clave,idUsuario){
    var path=window.location.pathname
    var path=path.substring(0,path.indexOf("cambiarClave"))
   $.ajax(path+'claveCambiada?input='+encodeURI(clave)+"&idUsuario="+idUsuario).done(function(respuesta) {
      if (respuesta=="Si"){
        var path=window.location.pathname.replace("cambiarClave", "claveCambiadaExitosamente");
        window.location.pathname=path;
        //alert("si");
      }
    });
  }; 

  jQuery('#enviar-clave').on('click', function (e) {
    var inputClave=jQuery("#auth_user_password").val();
    var idUsuario=jQuery("#enviar-clave").attr("idUsuario");
    if (inputClave!==""){
      var Okclave = acceptPassword(inputClave);
      if (Okclave){
        enviarDatos(inputClave,idUsuario);
      }else{
        jQuery("#errorFormClave").css("display","block");
      }
    }
  });

});