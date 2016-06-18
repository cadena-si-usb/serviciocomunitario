jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-admin').html(miniloader);
  ajax('home_admin', [], 'vista-admin');
  
  confirmarEliminar=function(idUsuario){ 
    confirmar=confirm("¿Seguro que desea eliminar este usuario?"); 
    if (confirmar){
      ajax('eliminar_usuario?id='+idUsuario, [], ''); 
      jQuery('#vista-admin').empty();
      jQuery('#vista-admin').html(miniloader);
      ajax('usuarios', [], 'vista-admin');
    }

  }; 

  editarArea=function(idArea){
    jQuery('#detalles-areas').empty();
    jQuery('#detalles-areas').html(miniloader);
    ajax('admin_modificar_area?id='+idArea, [], 'detalles-areas');
  }; 

  confirmarEliminarArea=function(idArea){ 
    confirmar=confirm("¿Seguro que desea eliminar esta area de proyecto?"); 
    if (confirmar){
      ajax('eliminar_area?id='+idArea, [], '');
      jQuery('#vista-admin').empty();
      jQuery('#vista-admin').html(miniloader);
      ajax('areas_admin', [], 'vista-admin'); 
    }

  }; 

  mostrarDetallesUsuario=function(idUsuario){ 
    jQuery('#detalles-usuario').empty();
    jQuery('#detalles-usuario').html(miniloader);
    ajax('admin_usuarios_detalles?id='+idUsuario, [], 'detalles-usuario'); 
  }; 

  mostrarDetallesArea=function(idArea){ 
    jQuery('#detalles-areas').empty();
    jQuery('#detalles-areas').html(miniloader);
    ajax('admin_areas_detalles?id='+idArea, [], 'detalles-areas'); 
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
  