jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-admin').html(miniloader);
  
  // Home Administrador
  ajax('home_admin', [], 'vista-admin');
  
  jQuery('#menu-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('home_admin', [], 'vista-admin'); 
  });

  // Gestionar Usuarios
  jQuery('#usuarios-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('usuarios', [], 'vista-admin');
  });

  confirmarEliminar=function(idUsuario){ 
    confirmar=confirm("¿Seguro que desea eliminar este usuario?"); 
    if (confirmar){
      $.ajax('eliminar_usuario?id='+idUsuario).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds').DataTable();
            table.row($("#"+idUsuario))
            .remove()
            .draw();
          }
      });
    }

  }; 

  mostrarDetallesUsuario=function(idUsuario){ 
    jQuery('#detalles-usuario').empty();
    jQuery('#detalles-usuario').html(miniloader);
    ajax('admin_usuarios_detalles?id='+idUsuario, [], 'detalles-usuario'); 
  }; 

  // Gestionar Areas de Proyectos
  editarArea=function(idArea){
    jQuery('#detalles-areas').empty();
    jQuery('#detalles-areas').html(miniloader);
    ajax('admin_modificar_area?id='+idArea, [], 'detalles-areas');
  }; 

  confirmarEliminarArea=function(idArea){ 
    confirmar=confirm("¿Seguro que desea eliminar esta area de proyecto?"); 
    if (confirmar){
      $.ajax('eliminar_area?id='+idArea).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds-areas').DataTable();
            table.row($("#"+idArea))
            .remove()
            .draw();
          }
      }); 
    }

  }; 

  mostrarDetallesArea=function(idArea){ 
    jQuery('#detalles-areas').empty();
    jQuery('#detalles-areas').html(miniloader);
    ajax('admin_areas_detalles?id='+idArea, [], 'detalles-areas'); 
  }; 

  jQuery('#areas-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('areas_admin', [], 'vista-admin');
  });

  enviarArea=function(idArea){
    $.ajax('nueva_area_admin_modificada?id='+idArea+"&nombre="+jQuery("#nombre-area").val()+"&codigo="+jQuery("#codigo-area").val()+"&descripcion=" +jQuery("#descripcion-area").val() + "&estado=" +jQuery("#estado-area").val()
    ).done(function(html) {

      if (html=='Exito'){
        $('#myModal2').css('display','none');
        var table=$("#estuds-areas").DataTable();
        
        table.row($("#"+idArea)).remove().draw();

        var rowNode = table
        .row.add([jQuery("#nombre-area").val(),jQuery("#codigo-area").val(),jQuery("#estado-area").val(),'<a class="enlace" onclick="mostrarDetallesArea(\''+idArea+'\')" data-toggle="modal" data-target="#myModal2"><i class="glyphicon glyphicon-search"></i></a>','<a class="enlace" onclick="confirmarEliminarArea(\''+idArea+'\')"><i class="glyphicon glyphicon-remove"></i></a>','<a class="enlace" onclick="editarArea(\''+idArea+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idArea);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha modificado el Area exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  nuevaArea=function(){

    $.ajax('nueva_area_admin?nombre='+jQuery("#nombre-area").val()+"&codigo="+jQuery("#codigo-area").val()+"&descripcion=" +jQuery("#descripcion-area").val() + "&estado=" +jQuery("#estado-area").val()
    ).done(function(html) {
      console.log();
      
      if (!(isNaN(html))){
        var idArea=html;
        $('#myModal2').css('display','none');

        var table=$("#estuds-areas").DataTable();

        var rowNode = table
        .row.add([jQuery("#nombre-area").val(),jQuery("#codigo-area").val(),jQuery("#estado-area").val(),'<a class="enlace" onclick="mostrarDetallesArea(\''+idArea+'\')" data-toggle="modal" data-target="#myModal2"><i class="glyphicon glyphicon-search"></i></a>','<a class="enlace" onclick="confirmarEliminarArea(\''+idArea+'\')"><i class="glyphicon glyphicon-remove"></i></a>','<a class="enlace" onclick="editarArea(\''+idArea+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idArea);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha creado el Area exitosamente.');
        
      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  // Gestionar Roles de Usuarios
  jQuery('#roles-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('roles_admin', [], 'vista-admin');
  });

  agregarRol=function(idUsuario){
    jQuery('#detalles-usuario').empty();
    jQuery('#detalles-usuario').html(miniloader);
    ajax('agregar_rol_admin?id='+idUsuario, [], 'detalles-usuario'); 
  };

  enviarRol=function(idUsuario){
    var idRol=jQuery("#id-Rol").val();
    var rolName=jQuery("#id-Rol option[value=\'"+idRol+"\']").text();
    $.ajax('agregar_rol_admin_listo?idUsuario='+idUsuario+"&idRol="+idRol).done(function(html) {
      if (!(isNaN(html))){
        var idRelacion=html;
        $('#myModal2').css('display','none');
        var elementoNinguno=$("li[idRelacion='ninguno']");
        var ulRoles=$("tr[idUsuario=\'"+idUsuario+"\'] td ul");
        if (ulRoles.find(elementoNinguno).length>0){
          ulRoles.empty();
        }
        var liRelacion="<li style='color:green' idRelacion=\'"+idRelacion+"\'>"+rolName
                      +"<a style='cursor:pointer' onclick='confirmarEliminarRol("+idUsuario+","+idRelacion+")'><i class='glyphicon glyphicon-remove'></i></a>"
                      +"</li>";

        ulRoles.append(liRelacion);              
        alert('Se ha agregado el rol exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
  };

  confirmarEliminarRol=function(idUsuario,idRelacion){ 
    confirmar=confirm("¿Seguro que desea eliminar este Rol al Usuario?"); 
    if (confirmar){
      $.ajax('eliminar_rol_admin?idRelacion='+idRelacion).done(function(html) {
        if (html=="Si"){
          $("li[idRelacion=\'"+idRelacion+"\']").remove();
          var ulRoles=$("tr[idUsuario=\'"+idUsuario+"\'] td ul");
          if (ulRoles.find($("li")).length==0){
            var elementoNinguno="<li idRelacion='ninguno' style='color:green'> Ninguno</li>";
            ulRoles.append(elementoNinguno);
          }
        }
      }); 
    }

  };

  // Gestionar Sedes
  jQuery('#sedes-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('sedes_admin', [], 'vista-admin');
  });  

  nuevaSede=function(){
    $.ajax('nueva_sede_admin?nombre='+jQuery("#nombre-sede").val()+ "&estado=" +jQuery("#estado-sede").val()
    ).done(function(html) {
      console.log("entro");
      if (!(isNaN(html))){
        var idSede=html;
        $('#myModal2').css('display','none');

        var table=$("#estuds-sedes").DataTable();

        var rowNode = table
        .row.add([jQuery("#nombre-sede").val(),jQuery("#estado-sede").val(),'<a class="enlace" onclick="editarSede(\''+idSede+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarSede(\''+idSede+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idSede);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha creado la Sede exitosamente.');
        
      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  editarSede=function(idSede){
    jQuery('#detalles-sedes').empty();
    jQuery('#detalles-sedes').html(miniloader);
    ajax('admin_modificar_sede?id='+idSede, [], 'detalles-sedes');
  }; 

  enviarSede=function(idSede){
    $.ajax('nueva_sede_admin_modificada?id='+idSede+"&nombre="+jQuery("#nombre-sede").val()+"&estado=" +jQuery("#estado-sede").val()
    ).done(function(html) {

      if (html=='Exito'){
        $('#myModal2').css('display','none');
        var table=$("#estuds-sedes").DataTable();
        
        table.row($("#"+idSede)).remove().draw();

        var rowNode = table
        .row.add([jQuery("#nombre-sede").val(),jQuery("#estado-sede").val(),'<a class="enlace" onclick="editarSede(\''+idSede+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarSede(\''+idSede+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idSede);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha modificado la Sede exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  confirmarEliminarSede=function(idSede){ 
    confirmar=confirm("¿Seguro que desea eliminar esta sede?"); 
    if (confirmar){
      $.ajax('eliminar_sede?id='+idSede).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds-sedes').DataTable();
            table.row($("#"+idSede))
            .remove()
            .draw();
          }
      }); 
    }

  }; 

  // Gestionar Carreras
  jQuery('#carreras-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('carreras_admin', [], 'vista-admin');
  });

  enviarCarrera=function(idCarrera){
    $.ajax('nueva_carrera_admin_modificada?id='+idCarrera+"&nombre="+jQuery("#nombre-carrera").val()+ "&codigo=" +jQuery("#codigo-carrera").val()+ "&area=" +jQuery("#area-carrera").val()+ "&estado=" +jQuery("#estado-carrera").val()
    ).done(function(html) {

      if (html=='Exito'){
        $('#myModal2').css('display','none');
        var table=$("#estuds-carreras").DataTable();
        
        table.row($("#"+idCarrera)).remove().draw();

        var areaCarreraName=jQuery("#area-carrera option[value=\'"+jQuery("#area-carrera").val()+"\']").text();
        var rowNode = table
        .row.add([jQuery("#codigo-carrera").val(),jQuery("#nombre-carrera").val(),areaCarreraName,jQuery("#estado-carrera").val(),'<a class="enlace" onclick="editarCarrera(\''+idCarrera+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarCarrera(\''+idCarrera+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idCarrera);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha modificado la carrera exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  editarCarrera=function(idCarrera){
    jQuery('#detalles-carreras').empty();
    jQuery('#detalles-carreras').html(miniloader);
    ajax('admin_modificar_carrera?id='+idCarrera, [], 'detalles-carreras');
  };   

  nuevaCarrera=function(){
    $.ajax('nueva_carrera_admin?nombre='+jQuery("#nombre-carrera").val()+ "&codigo=" +jQuery("#codigo-carrera").val()+ "&area=" +jQuery("#area-carrera").val()+ "&estado=" +jQuery("#estado-carrera").val()
    ).done(function(html) {
      if (!(isNaN(html))){
        var idCarrera=html;
        $('#myModal2').css('display','none');

        var table=$("#estuds-carreras").DataTable();
        var areaCarreraName=jQuery("#area-carrera option[value=\'"+jQuery("#area-carrera").val()+"\']").text();
        var rowNode = table
        .row.add([jQuery("#codigo-carrera").val(),jQuery("#nombre-carrera").val(),areaCarreraName,jQuery("#estado-carrera").val(),'<a class="enlace" onclick="editarCarrera(\''+idCarrera+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarCarrera(\''+idCarrera+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idCarrera);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha creado la Carrera exitosamente.');
        
      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  confirmarEliminarCarrera=function(idCarrera){ 
    confirmar=confirm("¿Seguro que desea eliminar esta carrera?"); 
    if (confirmar){
      $.ajax('eliminar_carrera?id='+idCarrera).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds-carreras').DataTable();
            table.row($("#"+idCarrera))
            .remove()
            .draw();
          }
      }); 
    }

  }; 

  // Gestionar Proyectos
  jQuery('#proyectos-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('proyectos_admin', [], 'vista-admin');
  });

  detallesProyecto=function(idProyectoAprobado){ 
    jQuery('#detalles-proyectos').empty();
    jQuery('#detalles-proyectos').html(miniloader);
    ajax('admin_proyectos_detalles?id='+idProyectoAprobado, [], 'detalles-proyectos'); 
  }; 

  confirmarEliminarProyecto=function(idProyectoAprobado){ 
    confirmar=confirm("¿Seguro que desea eliminar este proyecto?"); 
    if (confirmar){
      $.ajax('eliminar_proyecto_aprobado?id='+idProyectoAprobado).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds-proyectos').DataTable();
            table.row($("#"+idProyectoAprobado))
            .remove()
            .draw();
          }
      }); 
    }

  };

  editarProyecto=function(idProyectoAprobado){
    jQuery('#detalles-proyectos').empty();
    jQuery('#detalles-proyectos').html(miniloader);
    ajax('admin_modificar_proyecto_aprobado?id='+idProyectoAprobado, [], 'detalles-proyectos');
  };    

  enviarProyecto=function(idProyectoAprobado){
    $.ajax('admin_proyecto_modificado?id='+idProyectoAprobado+ "&codigo=" +jQuery("#codigo-proyecto").val()+"&estado=" +jQuery("#estado-proyecto").val()
    ).done(function(html) {

      if (html=='Exito'){
        $('#myModal2').css('display','none');
        var table=$("#estuds-proyectos").DataTable();
        
        table.row($("#"+idProyectoAprobado)).remove().draw();
        var rowNode = table
        .row.add([jQuery("#codigo-proyecto").val(),jQuery("#nombre-proyecto").text(),jQuery("#estado-proyecto").val(),'<a class="enlace" onclick="detallesProyecto(\''+idProyectoAprobado+'\')"><i class="glyphicon glyphicon-search" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="editarProyecto(\''+idProyectoAprobado+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarProyecto(\''+idProyectoAprobado+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idProyectoAprobado);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha modificado el proyecto exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  // Gestionar Areas de Carreras
  jQuery('#areas-carreras-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('areas_carreras_admin', [], 'vista-admin');
  });  

  nuevaAreaCarrera=function(){
    $.ajax('nueva_area_carrera_admin?nombre='+jQuery("#nombre-area-carrera").val()+ "&estado=" +jQuery("#estado-area-carrera").val()
    ).done(function(html) {
      if (!(isNaN(html))){
        var idArea=html;
        $('#myModal2').css('display','none');

        var table=$("#estuds-areas-carreras").DataTable();

        var rowNode = table
        .row.add([jQuery("#nombre-area-carrera").val(),jQuery("#estado-area-carrera").val(),'<a class="enlace" onclick="editarAreaCarrera(\''+idArea+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarAreaCarrera(\''+idArea+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idArea);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha creado la area de carrera exitosamente.');
        
      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  editarAreaCarrera=function(idArea){
    jQuery('#detalles-areas-carreras').empty();
    jQuery('#detalles-areas-carreras').html(miniloader);
    ajax('admin_modificar_area_carrera?id='+idArea, [], 'detalles-areas-carreras');
  }; 

  enviarAreaCarrera=function(idArea){
    $.ajax('nueva_area_carrera_admin_modificada?id='+idArea+"&nombre="+jQuery("#nombre-area-carrera").val()+"&estado=" +jQuery("#estado-area-carrera").val()
    ).done(function(html) {
      if (html=='Exito'){
        $('#myModal2').css('display','none');
        var table=$("#estuds-areas-carreras").DataTable();
        
        table.row($("#"+idArea)).remove().draw();

        var rowNode = table
        .row.add([jQuery("#nombre-area-carrera").val(),jQuery("#estado-area-carrera").val(),'<a class="enlace" onclick="editarAreaCarrera(\''+idArea+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarAreaCarrera(\''+idArea+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idArea);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha modificado la area de carrera exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  confirmarEliminarAreaCarrera=function(idArea){ 
    confirmar=confirm("¿Seguro que desea eliminar esta area de carrera?"); 
    if (confirmar){
      $.ajax('eliminar_area_carrera?id='+idArea).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds-areas-carreras').DataTable();
            table.row($("#"+idArea))
            .remove()
            .draw();
          }
      }); 
    }

  }; 

 // Gestionar Comunidades
  jQuery('#comunidades-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('comunidades_admin', [], 'vista-admin');
  });  

  nuevaComunidad=function(){
    $.ajax('nueva_comunidad_admin?nombre='+jQuery("#nombre-comunidad").val()+ "&estado=" +jQuery("#estado-comunidad").val()
    ).done(function(html) {
      if (!(isNaN(html))){
        var idComunidad=html;
        $('#myModal2').css('display','none');

        var table=$("#estuds-comunidades").DataTable();

        var rowNode = table
        .row.add([jQuery("#nombre-comunidad").val(),jQuery("#estado-comunidad").val(),'<a class="enlace" onclick="editarComunidad(\''+idComunidad+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarComunidad(\''+idComunidad+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idComunidad);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha creado la comunidad exitosamente.');
        
      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  editarComunidad=function(idComunidad){
    jQuery('#detalles-comunidades').empty();
    jQuery('#detalles-comunidades').html(miniloader);
    ajax('admin_modificar_comunidad?id='+idComunidad, [], 'detalles-comunidades');
  }; 

  enviarComunidad=function(idComunidad){
    $.ajax('nueva_comunidad_admin_modificada?id='+idComunidad+"&nombre="+jQuery("#nombre-comunidad").val()+"&estado=" +jQuery("#estado-comunidad").val()
    ).done(function(html) {
      if (html=='Exito'){
        $('#myModal2').css('display','none');
        var table=$("#estuds-comunidades").DataTable();
        
        table.row($("#"+idComunidad)).remove().draw();

        var rowNode = table
        .row.add([jQuery("#nombre-comunidad").val(),jQuery("#estado-comunidad").val(),'<a class="enlace" onclick="editarComunidad(\''+idComunidad+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>','<a class="enlace" onclick="confirmarEliminarComunidad(\''+idComunidad+'\')"><i class="glyphicon glyphicon-remove"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idComunidad);
        $(rowNode).css('color','green').animate({ color: 'black' });
        alert('Se ha modificado la comunidad exitosamente.');

      }else{
        $('#target').html(html);
      };
      
    });
 
  };

  confirmarEliminarComunidad=function(idComunidad){ 
    confirmar=confirm("¿Seguro que desea eliminar esta comunidad?"); 
    if (confirmar){
      $.ajax('eliminar_comunidad?id='+idComunidad).done(function(html) {
          if (html=="Si"){
            var table=$('#estuds-comunidades').DataTable();
            table.row($("#"+idComunidad))
            .remove()
            .draw();
          }
      }); 
    }

  }; 
  
});
  