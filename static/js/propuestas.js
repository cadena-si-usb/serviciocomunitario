$(document).ready(function (e) {
    $('.imprimir').on('click', function() {
        var str = '<!DOCTYPE html><html lang="en" xmlns="http://www.w3.org/1999/xhtml">';
        str += $('html').html();
        str += '</html>';
        $('.contenido-pagina').val(str);
        $('.formulario-pagina').submit();
    })
    $('[data-toggle="tooltip"]').tooltip(); 

})