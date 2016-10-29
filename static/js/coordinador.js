jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-coord').html(miniloader);
  
  // Home Coordinador
  ajax('home_coord', [], 'vista-coord');
  
  jQuery('#menu-coord').on('click', function (e) {
    jQuery('#vista-coord').empty();
    jQuery('#vista-coord').html(miniloader);
    ajax('home_coord', [], 'vista-coord'); 
  });


  // Inscripciones de Estudiantes
  jQuery('#inscripciones-coord').on('click', function (e) {
    jQuery('#vista-coord').empty();
    jQuery('#vista-coord').html(miniloader);
    ajax('coord_solicitud_inscripcion', [], 'vista-coord');
  });

  aprobarSolicitudEstudiante=function(idCursa){
    confirmar=confirm("¿Seguro que desea aprobar la solicitud de inscripcion de este estudiante?"); 
    if (confirmar){
      $.ajax('coord_aprobar_solicitud_estudiante?idCursa='+idCursa).done(function(html) {
          if (html=="Si"){
            var table=$('#coord-inscripcion').DataTable();
            table.row($("#"+idCursa))
            .remove()
            .draw();
            alert('Se ha aprobado la solicitud de inscripcion del estudiante exitosamente.');
          }
      });
    }

  };

  // Retiros de Estudiantes
  jQuery('#retiros-coord').on('click', function (e) {
    jQuery('#vista-coord').empty();
    jQuery('#vista-coord').html(miniloader);
    ajax('coord_retiros_estudiantes', [], 'vista-coord');
  });

  aprobarRetiroEstudiante=function(idCursa){
    confirmar=confirm("¿Seguro que desea aprobar la solicitud de retiro de este estudiante?"); 
    if (confirmar){
      $.ajax('coord_aprobar_retiro_estudiante?idCursa='+idCursa).done(function(html) {
          if (html=="Si"){
            var table=$('#coord-retiros').DataTable();
            table.row($("#"+idCursa))
            .remove()
            .draw();
            alert('Se ha aprobado la solicitud de retiro del estudiante exitosamente.');
          }
      });
    }

  };

  // Culminaciones de Estudiantes
  jQuery('#culminaciones-coord').on('click', function (e) {
    jQuery('#vista-coord').empty();
    jQuery('#vista-coord').html(miniloader);
    ajax('coord_culminaciones_estudiantes', [], 'vista-coord');
  });

  aprobarCulminacionEstudiante=function(idCursa){
    confirmar=confirm("¿Seguro que desea aprobar la solicitud de culminacion de este estudiante?"); 
    if (confirmar){
      $.ajax('coord_aprobar_culminacion_estudiante?idCursa='+idCursa).done(function(html) {
          if (html=="Si"){
            var table=$('#coord-culminaciones').DataTable();
            table.row($("#"+idCursa))
            .remove()
            .draw();
            alert('Se ha aprobado la solicitud de culminacion del estudiante exitosamente.');
          }
      });
    }

  };

  // Fechas topoe
  jQuery('#fechas-tope-coord').on('click', function (e) {
    jQuery('#vista-coord').empty();
    jQuery('#vista-coord').html(miniloader);
    ajax('actualizar_fechas_tope', [], 'vista-coord');
  });

  actualizarFecha=function(idFecha){
    var fecha_inicial=jQuery("#fecha_inicial"+idFecha).val();
    var fecha_final=jQuery("#fecha_final"+idFecha).val();
    $.ajax('cambiar_fecha_tope?id='+idFecha+"&fecha_inicial="+fecha_inicial+"&fecha_final="+fecha_final).done(function(html) {
        if (html=="Si"){
          alert('Se ha cambiado la fecha exitosamente.');
        }
    });
  }

});
  