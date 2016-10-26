jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-reportes').html(miniloader);
  
  // Home Reportes
  ajax('home_reportes', [], 'vista-reportes');

  // Buscar por Proyectos
  jQuery('#generar-proyectos').on('click', function (e) {
    jQuery('#vista-reportes').empty();
    jQuery('#vista-reportes').html(miniloader);
    ajax('buscar_proyectos_reportes?fecha_inicial='+jQuery('#proyectos-init').val()
      +"&fecha_final="+jQuery('#proyectos-final').val()
      +"&codigo="+jQuery('#proyectos-codigo').val()
      +"&tipo="+jQuery('#proyectos-tipo').val()
      +"&culminado="+jQuery('#proyectos-culminado').val()
      +"&evaluado="+jQuery('#proyectos-evaluado').val()
      +"&organizacion="+jQuery('#proyectos-organizacion').val()
      +"&idComunidad="+jQuery('#proyectos-comunidad').val()
      +"&idArea="+jQuery('#proyectos-area').val()
      +"&estado="+jQuery('#proyectos-estado').val()
      , [], 'vista-reportes');
  });
  
 
});
  