jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-reportes').html(miniloader);

  function process(date){
        var parts = date.split("/");
        return new Date(parts[2], parts[1] - 1, parts[0]);
  }
  
  // Home Reportes
  ajax('home_reportes', [], 'vista-reportes');

  // Buscar por Proyectos
  jQuery('#generar-proyectos').on('click', function (e) {
    var ini = process($('#proyectos-init').val());
    var fin = process($('#proyectos-final').val());
    var duracion = fin - ini;
    if ((ini=="Invalid Date")|(fin=="Invalid Date")){
      alert("Alguna de las fechas esta vacia."); 
      return;
    };
    if (duracion < 0){
      alert("La fecha de inicio no puede ser posterior a la de finalizacion.");
      return;
    }
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

  // Buscar por Estudiantes
  jQuery('#generar-estudiantes').on('click', function (e) {
    var ini = process($('#estudiantes-init').val());
    var fin = process($('#estudiantes-final').val());
    var duracion = fin - ini;
    if ((ini=="Invalid Date")|(fin=="Invalid Date")){
      alert("Alguna de las fechas esta vacia."); 
      return;
    };
    if (duracion < 0){
      alert("La fecha de inicio no puede ser posterior a la de finalizacion.");
      return;
    }

    jQuery('#vista-reportes').empty();
    jQuery('#vista-reportes').html(miniloader);
    ajax('buscar_estudiantes_reportes?fecha_inicial='+jQuery('#estudiantes-init').val()
      +"&fecha_final="+jQuery('#estudiantes-final').val()
      +"&operacion="+jQuery('#estudiantes-operaciones').val()
      +"&carnet="+jQuery('#estudiantes-carnet').val()
      +"&idCarrera="+jQuery('#estudiantes-carrera').val()
      +"&sexo="+jQuery('#estudiantes-sexo').val()
      , [], 'vista-reportes');
  });

  mostrarDetallesUsuario=function(idUsuario){ 
    jQuery('#detalles-estudiantes').empty();
    jQuery('#detalles-estudiantes').html(miniloader);
    ajax('admin_usuarios_detalles?id='+idUsuario, [], 'detalles-estudiantes'); 
  }; 
  
  // Buscar por Tutores
  //var docentes={{=XML(docentes)}};
  console.log(docentes);

  jQuery('#generar-tutores').on('click', function (e) {
    jQuery('#vista-reportes').empty();
    jQuery('#vista-reportes').html(miniloader);
    ajax('buscar_tutores_reportes?username='+jQuery("#tags").val()
      +"&departamento=All"
      , [], 'vista-reportes');
  });

  detallesProyecto=function(idProyectoAprobado){ 
    jQuery('#detalles-estudiantes').empty();
    jQuery('#detalles-estudiantes').html(miniloader);
    ajax('admin_proyectos_detalles?id='+idProyectoAprobado, [], 'detalles-estudiantes'); 
  }; 

  var aux=[]
  for (var i in docentes){
    aux.push(docentes[i]["usbid"]);
  }

  $( "#tags" ).autocomplete({
    source: aux
  });

});
  