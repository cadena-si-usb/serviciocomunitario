jQuery(document).ready(function(){

  jQuery('#vista-admin').html("<div class='miniloader'></div>");
  ajax('home_admin', [], 'vista-admin');
  
  confirmarEliminar=function(idUsuario){ 
    confirmar=confirm("¿Seguro que desea eliminar este usuario?"); 
    if (confirmar)
        window.location="eliminar_usuario?id="+idUsuario;
  }; 

  jQuery('#menu-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html("<div class='miniloader'></div>");
    ajax('home_admin', [], 'vista-admin'); 
      
  });

  jQuery('#usuarios-admin').on('click', function (e) {
    jQuery('#vista-admin').empty();
    jQuery('#vista-admin').html("<div class='miniloader'></div>");
    ajax('usuarios', [], 'vista-admin');
  });

    jQuery('#usuarios').on('click', function (e) {
     //   elem = $(this); // elem = $(e.target)
      //  url = elem.attr("data-url");
       // target = elem.attr("data-target");
        //web2py_ajax_page("GET", url, "", target);
       // $.ajax('{{=URL('default', 'user')}}', ['body'],target)
        //return false; // e.preventDefault()
      ajax('{{=URL("default", "user")}}', [], 'vista-admin');
      //$("#ajax_container").html('{{=LOAD('default', 'user.load', ajax=True, target='ajax_container')}}');  
      
  });

  jQuery('.load_content2').on('click', function (e) {
     //   elem = $(this); // elem = $(e.target)
      //  url = elem.attr("data-url");
       // target = elem.attr("data-target");
        //web2py_ajax_page("GET", url, "", target);
       // $.ajax('{{=URL('default', 'user')}}', ['body'],target)
        //return false; // e.preventDefault()
      ajax('{{=URL("default", "aja")}}', [], 'vista-admin');
      //$("#ajax_container").html('{{=LOAD('default', 'user.load', ajax=True, target='ajax_container')}}');  
      
  });

    jQuery('#usuarios').on('click', function (e) {
     //   elem = $(this); // elem = $(e.target)
      //  url = elem.attr("data-url");
       // target = elem.attr("data-target");
        //web2py_ajax_page("GET", url, "", target);
       // $.ajax('{{=URL('default', 'user')}}', ['body'],target)
        //return false; // e.preventDefault()
      ajax('{{=URL("default", "user")}}', [], 'vista-admin');
      //$("#ajax_container").html('{{=LOAD('default', 'user.load', ajax=True, target='ajax_container')}}');  
      
  });

  jQuery('.load_content2').on('click', function (e) {
     //   elem = $(this); // elem = $(e.target)
      //  url = elem.attr("data-url");
       // target = elem.attr("data-target");
        //web2py_ajax_page("GET", url, "", target);
       // $.ajax('{{=URL('default', 'user')}}', ['body'],target)
        //return false; // e.preventDefault()
      ajax('{{=URL("default", "aja")}}', [], 'vista-admin');
      //$("#ajax_container").html('{{=LOAD('default', 'user.load', ajax=True, target='ajax_container')}}');  
      
  });

});
  