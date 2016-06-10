
$(document).ready(function() {
		$('#no_table_f_fechaini, #no_table_f_fechafin').datepicker({
        	format: "dd/mm/yyyy"
		});
		function init_plugins() {
			$('select[multiple]').multiselect({
			    columns: 1,
			    search: true,
			    placeholder: 'Seleccione uno o más tutores'
			});
		}

        function process(date){
            var parts = date.split("/");
            return new Date(parts[2], parts[1] - 1, parts[0]);
        }


		function enviarPropuesta(accion) {
			pag = parseInt($("#siguiente").data('pag'));

			datos = $("form").serializeObject();

			datos['actividades'] = actividades;
			datos['objetivos_especificos'] = objetivos;
			datos['plan_operativo'] = filas;
			
			if (pag == 3) {
				datos["f_tutores"] = $("#no_table_f_tutores").val();
				datos["f_tutores_comunitarios"] = $("#no_table_f_tutores_comunitarios").val();
			}
			var ajaxResult = false;
			
			// Borro los errores
			$('span.form-error').remove();
			$('.form-error').removeClass('form-error');

			$.ajax({
			  method: "POST",
			  url: "propuestasCrear.json?accion="+accion+"&pag="+pag,
			  data: datos,
           	  async: false,
           	  success: function(res, textStatus, jqXHR) {
           	  	ajaxResult = res;
           	  	errors_count = 0;
           	  	for (var p in res.errors) {
				  	for (var k in res.errors[p]) {
				  		errors_count++;
				  	}
				}
			  	if (errors_count) {
			  		$('html,body').animate({scrollTop:0},0);
			  		$("#fail").show();
			  	}
			  }
			})
			ajaxResult['errors_count'] = errors_count;
			return ajaxResult;
		}
		$('body').on("click", "#agregar_act", function(){
			actividad_tmp = $(".form-actividades").serializeObject();
			actividad = {};
			for (key in actividad_tmp) {
				k = key.replace("_act","");
				k = "f_" + k;
				actividad[k] = actividad_tmp[key];
			}
			if (actividad.f_nombre) {

				actividades.push(actividad);
				nro_actividad = actividades.length-1;
				$('.tbl_actividades tbody').append(
					"<tr><td><span>"+actividad.f_nombre+"</span>"+
					"<a href='#' class='act_remove glyphicon glyphicon-remove pull-right' data-id='"+nro_actividad+"'></a>"+
					"<a href='#' class='act_edit glyphicon glyphicon-pencil pull-right' data-id='"+nro_actividad+"'></a></td></tr>");
				$(".form-actividades").each(function(i,e) {
					$(this).val("");
				})
			}
		})
		$('body').on('click', '.tbl_actividades .act_remove', function(e) {
			e.preventDefault();
			nro_act = $(this).data('id');
			fila = $(this).parent().parent();
			actividades.splice(nro_act, 1);
			$('.tbl_actividades .act_remove').each(function(i,e) {
				curId = $(e).data('id');
				if (curId >= nro_act) {
					$(e).data('id',curId-1);
				}
			}) 
			fila.remove();
		})

		$('body').on("click", "#agregar_obj", function(){
			objetivo_tmp = $(".form-objetivos").serializeObject();
			objetivo = {};
			for (key in objetivo_tmp) {
				k = key.replace("_obj","");
				k = "f_" + k;
				objetivo[k] = objetivo_tmp[key];
			}
			if (objetivo.f_objetivo) {

				objetivos.push(objetivo);
				nro_objetivo = objetivos.length-1;
				$('.tbl_objetivos tbody').append(
					"<tr><td><span>"+objetivo.f_objetivo+"</span>"+
					"<a href='#' class='act_remove glyphicon glyphicon-remove pull-right' data-id='"+nro_objetivo+"'></a>"+
					"<a href='#' class='act_edit glyphicon glyphicon-pencil pull-right' data-id='"+nro_objetivo+"'></a></td></tr>");
				$(".form-objetivos").each(function(i,e) {
					$(this).val("");
				})
			}
		})
		$('body').on('click', '.tbl_objetivos .act_remove', function(e) {
			e.preventDefault();
			nro_act = $(this).data('id');
			fila = $(this).parent().parent();
			console.log(fila, objetivos[nro_act]);
			objetivos.splice(nro_act, 1);
			$('.tbl_objetivos .act_remove').each(function(i,e) {
				curId = $(e).data('id');
				if (curId >= nro_act) {
					$(e).data('id',curId-1);
				}
			}) 
			fila.remove();
		})
		editing = false;
		$('body').on('click', '.act_edit', function(e) {
			
		})

		$('body').on("click", "#agregar_plan", function(){
			fila = $(".form-plan").serializeObject();
			actividad = $("select[name='f_actividad'] option[value='"+fila.f_actividad+"']").html();
			obj = $("select[name='f_objetivo'] option[value='"+fila.f_objetivo+"']").html();
			if (fila.f_actividad && fila.f_objetivo) {

				filas.push(fila);
				nro_fila = filas.length-1;
				$('.tbl_filas tbody').append(
					"<tr><td><span>"+actividad+"</span></td>"+
					"<td><span>"+obj+"</span>"+
					"<a href='#' class='act_remove glyphicon glyphicon-remove pull-right' data-id='"+nro_fila+"'></a>"+
					"<a href='#' class='act_edit glyphicon glyphicon-pencil pull-right' data-id='"+nro_fila+"'></a></td></tr>");
				$(".form-plan").each(function(i,e) {
					$(this).val("");
				})
			}
		})
		$('body').on('click', '.tbl_filas .act_remove', function(e) {
			e.preventDefault();
			nro_act = $(this).data('id');
			fila = $(this).parent().parent();
			filas.splice(nro_act, 1);
			$('.tbl_filas .act_remove').each(function(i,e) {
				curId = $(e).data('id');
				if (curId >= nro_act) {
					$(e).data('id',curId-1);
				}
			}) 
			fila.remove();
		})

		$('body').on("click", "#guardar", function(e) {
			e.preventDefault();
            function process(date){
   var parts = date.split("/");
   return new Date(parts[2], parts[1] - 1, parts[0]);
}
            var ini = process($('#no_table_f_fechaini').val());
            var fin = process($('#no_table_f_fechafin').val());
            var duracion = fin - ini;
            var duracionEnAnios = duracion/(1000*60*60*24*365);
            console.log("INI");
            console.log(ini);
            console.log("FIN");
            console.log(fin);
            console.log("DURACION");
            console.log(duracion);
            console.log("DURACION EN ANIOS");
            console.log(duracionEnAnios);
            
			if ($('#no_table_f_nombre').val() == ''){
                alert("El nombre del proyecto no puede estar vacio");
                return false;
            }
            else if (duracion < 0){
                alert("La fecha de inicio no puede ser posterior a la de finalizacion");
                return false;
            }
            else if (duracionEnAnios > 2){
                alert("El proyecto no puede durar mas de 2 años");
                return false;
            }
            else {
                ajaxResult = enviarPropuesta('guardar');
                
            for (var p in ajaxResult.errors) {
                if (Object.keys(ajaxResult.errors[p]).length) {
                    $(".btn-pag[data-pag='"+p+"']").css("color","red");
                }
                else {
                    $(".btn-pag[data-pag='"+p+"']").css("color","green");
                }
                for (var k in ajaxResult.errors[p]) {
                    // Obtener nuevo contenido del tooltip 
                    cur_title = $(".btn-pag[data-pag='"+p+"']").attr("data-original-title");
                    new_title = cur_title ? cur_title + "\n\n" + k + ": " + ajaxResult.errors[p][k] : k + ": " + ajaxResult.errors[p][k];
                    // set new tooltip
                    $('.btn-pag[data-pag="'+p+'"]').attr('data-original-title', new_title).tooltip('fixTitle');
                    $("#no_table_"+k).addClass('form-error');
                    $("#no_table_"+k).parent().append('<span class="form-error red">*'+ajaxResult.errors[p][k]+'</span>')
                }
            }
                if (ajaxResult.proyecto_id) {
                    $("[name='proyecto_id'],[name='f_proyecto']").val(ajaxResult.proyecto_id);
                    console.log(ajaxResult);
                    if (ajaxResult.errors_count == 0) {
                        alert("La propuesta ha sido guardada exitosamente. Puede seguir llenándola cuando le plazca");
                    }
                }
            }

		})


		$('body').on("click", "#siguiente", function(e) {
			e.preventDefault();
			pag = parseInt($("#siguiente").data('pag'));
			if (pag == 6)
				accion = "registrar"
			else
				accion = "guardar"
			
			ajaxResult = enviarPropuesta(accion);
			console.log(ajaxResult.es_adm);
       	  	for (var p in ajaxResult.errors) {
       	  		if (Object.keys(ajaxResult.errors[p]).length) {
       	  			$(".btn-pag[data-pag='"+p+"']").css("color","red");
       	  		}
       	  		else {
       	  			$(".btn-pag[data-pag='"+p+"']").css("color","green");
       	  		}
			  	for (var k in ajaxResult.errors[p]) {
			  		// Obtener nuevo contenido del tooltip 
			  		cur_title = $(".btn-pag[data-pag='"+p+"']").attr("data-original-title");
			  		new_title = cur_title ? cur_title + "\n\n" + k + ": " + ajaxResult.errors[p][k] : k + ": " + ajaxResult.errors[p][k];
			  		// set new tooltip
			  		$('.btn-pag[data-pag="'+p+'"]').attr('data-original-title', new_title).tooltip('fixTitle');
			  		$("#no_table_"+k).addClass('form-error');
			  		$("#no_table_"+k).parent().append('<span class="form-error red">*'+ajaxResult.errors[p][k]+'</span>')
			  	}
			}
		  	if (ajaxResult.errors_count) {
		  		$('html,body').animate({scrollTop:0},0);
		  		$("#fail").show();
		  	}
			if (ajaxResult.proyecto_id != 0 && ajaxResult.errors_count == 0) { 
           	  	nextPag = pag+1;
           	  	if (nextPag < 7) {
           	  		window.location = "propuestasCrear?proyecto_id="+ajaxResult.proyecto_id+"&pag="+nextPag;
           	  	}
		  		else if (ajaxResult.estado_propuesta == 'En espera del aval' && !ajaxResult.es_adm) {
		  			window.location = "generarPlanillaAval/"+ajaxResult.proyecto_id;
		  		}
		  		else {
		  			window.location = "propuestas";
		  		}
			}
		})
		// Validaciones numericas
		$('body').on("keydown", "[name='f_tiempo'],[name='f_incorporacion_estudiantes'],[name='f_incorporacion_empleados'],[name='f_incorporacion_obreros'],[name='alumnos_act'],[name='costo_act'],[name='monto_total_act']", function (e) {
	        // Allow: backspace, delete, tab, escape, enter and .
	        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
	             // Allow: Ctrl+A, Command+A
	            (e.keyCode == 65 && ( e.ctrlKey === true || e.metaKey === true ) ) || 
	             // Allow: home, end, left, right, down, up
	            (e.keyCode >= 35 && e.keyCode <= 40)) {
	                 // let it happen, don't do anything
	                 return;
	        }
	        // Ensure that it is a number and stop the keypress
	        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
	            e.preventDefault();
	        }
		})
		init_plugins();
})