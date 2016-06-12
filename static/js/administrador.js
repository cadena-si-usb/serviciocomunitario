jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-admin').html(miniloader);
  ajax('home_admin', [], 'vista-admin');
  
  confirmarEliminar=function(idUsuario){ 
    confirmar=confirm("¿Seguro que desea eliminar este usuario?"); 
    if (confirmar)
        window.location="eliminar_usuario?id="+idUsuario;
  }; 

  mostrarDetallesUsuario=function(idUsuario){ 
    jQuery('#detalles-usuario').empty();
    jQuery('#detalles-usuario').html(miniloader);
    ajax('admin_usuarios_detalles?id='+idUsuario, [], 'detalles-usuario'); 
  }; 

  jQuery('#menu-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('home_admin', [], 'vista-admin'); 
      
  });

  jQuery('#usuarios-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('usuarios', [], 'vista-admin');
  });

  jQuery('#areas-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('areas_admin', [], 'vista-admin');
  });

  jQuery('#usuarios').on('click', function (e) {
 
  });

  jQuery('.load_content2').on('click', function (e) {

  });

});
  