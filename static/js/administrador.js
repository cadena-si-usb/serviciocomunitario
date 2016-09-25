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

  mostrarDetallesUsuario=function(idUsuario){ 
    jQuery('#detalles-usuario').empty();
    jQuery('#detalles-usuario').html(miniloader);
    ajax('admin_usuarios_detalles?id='+idUsuario, [], 'detalles-usuario'); 
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

  jQuery('#roles-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html(miniloader);
    ajax('roles_admin', [], 'vista-admin');
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

  agregarRol=function(idUsuario){
    //console.log("rol agregado..")
    jQuery('#detalles-usuario').empty();
    jQuery('#detalles-usuario').html(miniloader);
    ajax('agregar_rol_admin?id='+idUsuario, [], 'detalles-usuario'); 
    //$( "input[value='Hot Fuzz']" )
    //var allListElements = $( "li" );
    //$( "li.item-ii" ).find( allListElements );
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

});
  