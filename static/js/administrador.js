jQuery(document).ready(function(){

  var miniloader="<div class='miniloader'></div>";

  jQuery('#vista-admin').html(miniloader);
  ajax('home_admin', [], 'vista-admin');
  
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
            var table=$('#estuds').DataTable();
            table.row($("#"+idArea))
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

  enviarArea=function(idArea){
    $.ajax('nueva_area_admin_modificada?id='+idArea+"&nombre="+jQuery("#nombre-area").val()+"&codigo="+jQuery("#codigo-area").val()+"&descripcion=" +jQuery("#descripcion-area").val() + "&estado=" +jQuery("#estado-area").val()
    ).done(function(html) {

      if (html=='Exito'){
        $('#myModal2').modal('toggle');

        var table=$('#estuds').DataTable();
        
        table.row($("#"+idArea)).remove().draw();

        var rowNode = table
        .row.add([jQuery("#nombre-area").val(),jQuery("#codigo-area").val(),jQuery("#estado-area").val(),'<a class="enlace" onclick="mostrarDetallesArea(\''+idArea+'\')" data-toggle="modal" data-target="#myModal2"><i class="glyphicon glyphicon-search"></i></a>','<a class="enlace" onclick="confirmarEliminarArea(\''+idArea+'\')"><i class="glyphicon glyphicon-remove"></i></a>','<a class="enlace" onclick="editarArea(\''+idArea+'\')"><i class="glyphicon glyphicon-pencil" data-toggle="modal" data-target="#myModal2"></i></a>'])
        .draw()
        .node();
 
        $(rowNode).attr("id",idArea);
        $(rowNode).css('color','green').animate({ color: 'black' });

      }else{
        $('#target').html(html);
      };
      
    });
 
  };


});
  