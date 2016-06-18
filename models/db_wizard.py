# -*- coding: utf-8 -*-
### we prepend t_ to tablenames and f_ to fieldnames for disambiguity

########################################
# Rupdev
#

# USUARIOS UNIVERSITARIOS
# Usuarios internos de la universidad, solo poseen carnet
# Relaciona auth_user con la comunidad universitaria
db.define_table('t_universitario',
    Field('f_usbid', type='string', notnull=True, unique=True,
          label=T('Usbid'), writable=True,),
    Field('f_key', type='string', notnull=True, readable=False,
          label=T('Key'), writable=False,), # Clave generada al azar
    Field('f_usuario', type='reference auth_user', notnull=True,
          label=T('Usuario')),
    format='%(f_usuario)s carnet: %(f_usbid)s')

# ESTUDIANTES
# Estudiantes, deben encontrarse en t_universitario
db.define_table('t_estudiante',
    Field('f_universitario', 'reference t_universitario',
          unique=True, notnull=True,
          requires=IS_IN_DB(db,db.t_universitario,'%(f_usbid)s'),
          label=T('Usuario univesitario'),
          writable=False),
    Field('f_carrera',type='string',
          notnull=True,
          label=T('Carrera')),
    Field('f_sede',
          requires=IS_IN_SET(['Sartenejas','Litoral']),
          notnull=True,
          label=T('Sede')),
    Field('f_informe','upload',label=T('Informe'), notnull=False),
    format='%(f_universitario)s',
    migrate=settings.migrate)


# TUTORES ACADÉMICOS
db.define_table('t_tutor_academico',
    Field('f_universitario', 'reference t_universitario',
          unique=True, notnull=True,
          requires=IS_IN_DB(db,db.t_universitario,'%(f_usbid)s'),
          label=T('Usuario univesitario'),
          writable=False),
    Field('f_departamento',type='string',
          notnull=True,
          label=T('Departamento')),
    Field('f_sede',
          requires=IS_IN_SET(['Sartenejas','Litoral']),
          notnull=True,
          label=T('Sede')),
    format='%(f_universitario)s',
    migrate=settings.migrate)


db.define_table('t_estado',
    Field('f_nombre', type='string', notnull=True,
          label=T('Nombre')),
    format='%(f_nombre)s',
    migrate=settings.migrate)
db.define_table('t_estado_archive',db.t_estado,Field('current_record','reference t_estado',readable=False,writable=False))


db.define_table('t_comunidad',
    Field('f_nombre', type='string', notnull=True,
          label=T('Nombre')),
    Field('f_descripcion', type='text', notnull=True,
          label=T('Descripcion')),
    Field('f_cantidadbeneficiados', type='integer', notnull=True,
          label=T('Cantidadbeneficiados')),
    Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
          label=T('Estado'), default='Activo'), # Dos grupos tienen el campo con nombre dif
    auth.signature,
    format='%(f_nombre)s',
    migrate=settings.migrate)

db.define_table('t_comunidad_archive',db.t_comunidad,Field('current_record','reference t_comunidad',readable=False,writable=False))


db.define_table('t_area',
    Field('f_nombre', type='string', notnull=True,
          label=T('Nombre')),
    Field('f_descripcion', type='string', notnull=False,
          label=T('Descripcíon')),
    Field('f_codigo', type='string', notnull=True,
          label=T('Código')),
    Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
          label=T('Estado'), default='Activo'),
    auth.signature,
    format='%(f_nombre)s',
    migrate=settings.migrate)
db.define_table('t_area_archive',db.t_area,Field('current_record','reference t_area',readable=False,writable=False))


db.define_table('t_area_carrera',
    Field('f_nombre', type='string', notnull=True,
          label=T('Nombre')),
    auth.signature,
    format='%(f_nombre)s',
    migrate=settings.migrate)
db.define_table('t_area_carrera_archive',db.t_area_carrera,Field('current_record','reference t_area_carrera',readable=False,writable=False))


db.define_table('t_proyecto',
   Field('f_nombre', type='string', notnull=False,
          label=T('Nombre'),default = ''),
    Field('f_continuacion', type='boolean', notnull=False,
          label=T('Nuevo o continuación'), default=False),
    Field('f_resumen', type='text', notnull=False,
          label=T('Resumen')),
    Field('f_relacion_planes', type='text', notnull=False,
          label=T('Relación con planes nacionales')),
    Field('f_antecedentes', type='text', notnull=False,
          label=T('Antecedentes')),
    Field('f_obj_generales', type='text', notnull=False,
          label=T('Objetivos Generales')),
    Field('f_poblacion_beneficiaria', type='text', notnull=False,
          label=T('Población beneficiaria')),
    Field('f_justificacion', type='text', notnull=False,
          label=T('Justificación')),
    Field('f_logros_sociales', type='text', notnull=False,
      label=T('Justificación')),
    Field('f_impacto_social', type='text', notnull=False,
      label=T('Justificación')),
    Field('f_evaluacion', type='text', notnull=False,
          label=T('Evaluación')),
    Field('f_difusion_resultados', type='text', notnull=False,
          label=T('Difusión de resultados')),
    Field('f_aplicacion_dir_ley', type='text', notnull=False,
          label=T('Aplicación de las directrices y valores expuestos en la ley')),
    Field('f_obj_aprendizaje', type='text', notnull=False,
          label=T('Objetivos de aprendizaje')),
    Field('f_num_requeridos', type='integer', notnull=False,
          label=T('Número de estudiantes requeridos')),
    Field('f_relevancia', type='text', notnull=False,
          label=T('Relevancia')),
    Field('f_originalidad', type='text', notnull=False,
          label=T('Originalidad')),
    Field('f_capacidad_ejecutora', type='text', notnull=False,
          label=T('Capacidad ejecutora')),
    Field('f_asoc_externa', type='text', notnull=False,
          label=T('Asociatividad externa')),
    Field('f_asoc_interna', type='text', notnull=False,
          label=T('Asociatividad interna')),
    Field('f_incorporacion_estudiantes', type='integer', notnull=False,
          label=T('Incorporación estudiantes')),
    Field('f_incorporacion_profesores', type='integer', notnull=False,
          label=T('Incorporación profesores')),
    Field('f_incorporacion_empleados', type='integer', notnull=False,
          label=T('Incorporación empleados')),
    Field('f_incorporacion_obreros', type='integer', notnull=False,
          label=T('Incorporación obreros')),
    Field('f_area', type='reference t_area', requires=IS_EMPTY_OR(IS_IN_DB(db, 't_area.id', '%(f_nombre)s')), notnull=False,
          label=T('Área de atención social')),
    Field('f_area_carrera', type='reference t_area_carrera', requires=IS_EMPTY_OR(IS_IN_DB(db, 't_area_carrera.id', '%(f_nombre)s')), notnull=False,
          label=T('Área de competencia por carrera')),
    Field('f_estado', type='reference t_estado', requires=IS_EMPTY_OR(IS_IN_DB(db, 't_estado.id', '%(f_nombre)s')), notnull=False,
          label=T('Estado')),
    Field('f_fechaini', type='date', requires= IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))), notnull=False,
          label=T('Fechaini')),
    Field('f_fechafin', type='date', requires= IS_EMPTY_OR(IS_DATE(format=('%d/%m/%Y'))),notnull=False,
          label=T('Fechafin')),
    Field('f_comunidad', type='string', notnull=False,
          label=T('Comunidad')),
    Field('f_sede', requires=IS_EMPTY_OR(IS_IN_SET(['Sartenejas','Litoral'])),notnull=False,label=T('Sede')),
    migrate=settings.migrate)
db.define_table('t_proyecto_archive',db.t_proyecto,Field('current_record','reference t_proyecto',readable=False,writable=False))


db.define_table('t_objetivo',
    Field('f_proyecto', type='reference t_proyecto', notnull=True),
    Field('f_objetivo', type='text', notnull=True),
    format='%(f_objetivo)s'
)
db.define_table('t_objetivo_archive',db.t_objetivo,Field('current_record','reference t_objetivo',readable=False,writable=False))


db.define_table('t_proyecto_tutor',
    Field('f_proyecto', type='reference t_proyecto'),
    Field('f_tutor', type='reference auth_user'))
db.define_table('t_proyecto_tutor_archive',db.t_proyecto_tutor,Field('current_record','reference t_proyecto_tutor',readable=False,writable=False))


db.define_table('t_proyecto_tutor_comunitario',
    Field('f_proyecto', type= 'reference t_proyecto'),
    Field('f_tutor', type='reference auth_user'))
db.define_table('t_proyecto_tutor_comunitario_archive',db.t_proyecto_tutor_comunitario,Field('current_record','reference t_proyecto_tutor_comunitario',readable=False,writable=False))


db.define_table('t_actividad',
    Field('f_proyecto', type='reference t_proyecto', notnull=True, writable=False, readable=True,
          label=T('Proyecto')),
    Field('f_nombre', type='string', notnull=True, default='',
          label=T('Nombre')),
    Field('f_resumen', type='text', default='',
          label=T('Resumen')),
    Field('f_alumnos', type='integer', default=1,
          label=T('Alumnos requeridos')),
    Field('f_requerimientos', type='text', default='',
          label=T('Requerimientos')),
    Field('f_recursos', type='text', default='',
          label=T('Recursos')),
    Field('f_costo', type='float',
          label=T('Costo')),
    Field('f_recursos_propios', type='text', default='',
          label=T('Recursos propios')),
    Field('f_aportes_otros', type='text', default='',
          label=T('Aportes de otros donantes')),
    Field('f_aportes_dex', type='text', default='',
          label=T('Aportes solicitados a DEx')),
    Field('f_monto_total', type='float', default='',
          label=T('Monto total')),
    auth.signature,
    format='%(f_nombre)s',
    migrate=settings.migrate                 
)   
db.define_table('t_actividad_archive',db.t_actividad,Field('current_record','reference t_actividad',readable=False,writable=False))

########################################


########################################
# DUPLICADO
# db.define_table('t_carrera',
#     Field('f_codigo', type='string', notnull=True,
#           label=T('Codigo')),
#     Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
#           label=T('Estado'), default='Activo'),
#     auth.signature,
#     format='%(f_codigo)s',
#     migrate=settings.migrate)

# db.define_table('t_carrera_archive',db.t_carrera,Field('current_record','reference t_carrera',readable=False,writable=False))
db.define_table('t_carrera',
    Field('f_codigo', type='string', notnull=True,
          label=T('Codigo')),
    Field('f_nombre', type='string', notnull=True, default='',
          label=T('Nombre')),
    auth.signature,
    format='%(f_codigo)s',
    migrate=settings.migrate)

db.define_table('t_carrera_archive',db.t_carrera,Field('current_record','reference t_carrera',readable=False,writable=False))



########################################
db.define_table('t_cursa',
    Field('f_estudiante', type='reference t_estudiante', notnull=True,
          label=T('Estudiante')),
    Field('f_proyecto', type='reference t_proyecto', notnull=True,
          label=T('Proyecto')),
    Field('f_estado', 
          requires=IS_IN_SET(['Aprobado',
                              'Retirado',
                              'Culminado',
                              'Pendiente']), notnull=True, label=T('Estado'), default='Aprobado'),
    Field('f_valido', requires=IS_IN_SET(['Valido', 'Invalido','']), notnull=True, label=T('Valido'), default='Valido'),
    Field('f_fecha', type='date', requires = IS_DATE(format=('%d/%m/%Y')), notnull=False,
          label=T('Fecha')),#fecha en que retira o culmina el SC
    auth.signature,
    format='%(id)s',
    migrate=settings.migrate)

db.define_table('t_cursa_archive',db.t_cursa,Field('current_record','reference t_cursa',readable=False,writable=False))

###################################
#actividad de la bitacora
db.define_table('t_actividad_estudiante',
    Field('f_cursa', type='reference t_cursa', notnull=True,
        label=T('Cursa')),
    Field('f_actividad', type='reference t_actividad', notnull=True,
        label=T('Actividad')),
    Field('f_horas', requires=IS_INT_IN_RANGE(0,121), notnull=True,
        label=T('Horas a realizar'), default=0),
    Field('f_realizada', type='boolean',      # el estudiante dice que hizo la actividad
        notnull=True, default=False, writable=False,
        label=T('Actividad realizada')),
    Field('f_confirmada', type='boolean',     # el tutor comunitario confirma que se hizo la actividad
        notnull=True, default=False, writable=False,
        label=T('Actividad confirmada')),
    format='%(f_cursa)s',
    migrate=settings.migrate)
db.define_table('t_actividad_estudiante_archive',db.t_actividad_estudiante,Field('current_record','reference t_actividad_estudiante',readable=False,writable=False))

# db.define_table('t_actividad_estudiante',
#     Field('f_cursa', type='reference t_cursa', notnull=True,
#         label=T('Cursa')),
#     Field('f_actividad', type='reference t_actividad', notnull=True,
#         label=T('Actividad')),
#     Field('f_horas', requires=IS_INT_IN_RANGE(0,121), notnull=True,
#           label=T('horas a realizar'), default=0),
#     Field('f_realizada', type='boolean',      # el estudiante dice que hizo la actividad
#         notnull=True, default=False, writable=False,
#         label=T('Actividad realizada')),
#     Field('f_confirmada', type='boolean',     # el tutor comunitario confirma que se hizo la actividad
#         notnull=True, default=False, writable=False,
#         label=T('Actividad confirmada')),
#     format='%(f_cursa)s',
#     migrate=settings.migrate)

# db.define_table('t_actividad_estudiante_archive',db.t_relacionestproy,Field('current_record','reference t_actividad_estudiante',readable=False,writable=False))


########################################
db.define_table('t_tipoprop',
    Field('f_tipo', type='string', notnull=True,
          label=T('Tipo')),
    Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
          label=T('Estado'), default='Activo'),
    auth.signature,
    format='%(f_tipo)s',
    migrate=settings.migrate)

db.define_table('t_tipoprop_archive',db.t_tipoprop,Field('current_record','reference t_tipoprop',readable=False,writable=False))


########################################
#db.define_table('t_proyecto',
#    Field('f_codigo', type='string', notnull=True,
#          label=T('Codigo')),
#    auth.signature,
#    format='%(f_codigo)s',
#    migrate=settings.migrate)

#db.define_table('t_proyecto_archive',db.t_proyecto,Field('current_record','reference t_proyecto',readable=False,writable=False))

########################################



########################################
db.define_table('t_condicion',
    Field('f_tipo', type='string', notnull=True,
          label=T('Tipo')),
    Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
          label=T('Estado'), default='Activo'),
    auth.signature,
    format='%(f_tipo)s',
    migrate=settings.migrate)

db.define_table('t_condicion_archive',db.t_condicion,Field('current_record','reference t_condicion',readable=False,writable=False))


db.define_table('t_propuesta',
    Field('f_proyecto', type='reference t_proyecto', notnull=True,
          label=T('ID del proyecto'), writable=False, readable=True),
    Field('f_estado_propuesta', requires=IS_EMPTY_OR(IS_IN_SET(['Incompleta', 'En espera de revision', 'Aprobado', 'Rechazado con observaciones'])),
          label=T('Estado'), default='Incompleta', notnull=False),
    Field('f_observaciones', type='text', default='',
          label=T('Observaciones')),
    Field('f_proponente', type='reference auth_user', default=auth.user_id, notnull=False,
          label=T('Proponente')),
    auth.signature,
    format='%(f_proyecto)s',
    #primarykey=['f_version','f_codigo'],
    migrate=settings.migrate)
db.define_table('t_propuesta_archive',db.t_propuesta,Field('current_record','reference t_propuesta',readable=False,writable=False))


db.define_table('t_proyecto_aprobado',
    Field('f_proyecto', type='reference t_proyecto', notnull=True,
          label=T('ID del proyecto'), writable=False, readable=True),
    Field('f_codigo', type='string', notnull=True, unique = True,
          label=T('Código')),
    Field('f_estado_proyecto', requires=IS_IN_SET(['Activo', 'Inactivo']),
          label=T('Estado'), default='Activo', notnull=True),
    auth.signature,
    format='%(f_codigo)s',
    #primarykey=['f_version','f_codigo'],
    migrate=settings.migrate)
db.define_table('t_proyecto_aprobado_archive',db.t_proyecto_aprobado,Field('current_record','reference t_proyecto_aprobado',readable=False,writable=False))


db.define_table('t_plan_operativo',
    Field('f_proyecto', type='reference t_proyecto', notnull=True,
          label=T('Proyecto')),
    Field('f_actividad', type='reference t_actividad', notnull=True,
          label=T('Actividad')),
    Field('f_objetivo', type='reference t_objetivo', notnull=True,
          label=T('Objetivo')),
    Field('f_meta', type='text', notnull=True,
          label=T('Meta')),
    Field('f_tiempo', type='integer', notnull=True,
          label=T('Tiempo de ejecución')),
    Field('f_recursos', type='text', notnull=True,
          label=T('Recursos humanos y materiales')),
    Field('f_resultados_esperados', type='text', notnull=True,
          label=T('Resultados esperados')),
    Field('f_responsable', type='string', notnull=True, requires=IS_EMPTY_OR(IS_IN_SET(['Estudiante','Tutor académico','Tutor comunitario'])),
          label=T('Responsable')))
db.define_table('t_plan_operativo_archive',db.t_plan_operativo,Field('current_record','reference t_plan_operativo',readable=False,writable=False))

########################################
# db.define_table('t_carrera',
#     Field('f_codigo', type='string', notnull=True,
#           label=T('Codigo')),
#     Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
#           label=T('Estado'), default='Activo'),
#     auth.signature,
#     format='%(f_codigo)s',
#     migrate=settings.migrate)

# db.define_table('t_carrera_archive',db.t_carrera,Field('current_record','reference t_carrera',readable=False,writable=False))

#######################################
# db.define_table('t_estudiante',
#     Field('f_usbid', type='string', notnull=True,
#           label=T('Usbid'), writable=False),
#     Field('f_nombre', type='string', notnull=True,
#           label=T('Nombre')),
#     Field('f_apellido', type='string', notnull=True,
#           label=T('Apellido')),
#     Field('f_cedula', type='string', notnull=True,
#           label=T('Cedula')),
#     Field('f_carrera', type='reference t_carrera', notnull=True,
#           label=T('Carrera')),
#     Field('f_sede', type='reference t_sede', notnull=True,
#           label=T('Sede')),
#     Field('f_email', type='string', notnull=True,
#           label=T('Email')),
#     Field('f_sexo', type='reference t_sexo', notnull=True,
#           label=T('Sexo')),
#     Field('f_telefono', type='string', notnull=True,
#           label=T('Telefono')),
#     Field('f_user', type='reference auth_user', notnull=False,
#           label=T('Nombre de usuario')),
#     Field('f_direccion', type='text', notnull=True,
#           label=T('Direccion')),
#     Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
#           label=T('Estado'), default='Activo'),
#     auth.signature,
#     format='%(f_usbid)s',
#     migrate=settings.migrate)

# db.define_table('t_estudiante_archive',db.t_estudiante,Field('current_record','reference t_estudiante',readable=False,writable=False))

########################################
# db.define_table('t_relacionestproy',
#     Field('f_tipo', type='string', notnull=True,
#           label=T('Tipo')),

#     auth.signature,
#     format='%(f_tipo)s',
#     migrate=settings.migrate)

# db.define_table('t_relacionestproy_archive',db.t_relacionestproy,Field('current_record','reference t_relacionestproy',readable=False,writable=False))

########################################
# db.define_table('t_cursa',
#     Field('f_estudiante', type='reference t_estudiante', notnull=True,
#           label=T('Estudiante')),
#     Field('f_proyecto', type='reference t_proyecto', notnull=True,
#           label=T('Proyecto')),
#     Field('f_state', type='reference t_relacionestproy', notnull=True,
#           label=T('State')),
#     Field('f_valido', type='string', notnull=True, label=T('Valido'), default='Invalido'),
#     auth.signature,
#     format='%(f_estudiante)s',
#     migrate=settings.migrate)

# db.define_table('t_cursa_archive',db.t_cursa,Field('current_record','reference t_cursa',readable=False,writable=False))
### we prepend t_ to tablenames and f_ to fieldnames for disambiguity

# GESTION DE PROYECTO
########################################
db.define_table('t_sede',
    Field('f_nombre', type='string', notnull=True,
          label=T('Nombre')),
    Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
          label=T('Estado'), default='Activo'),

    auth.signature,
    format='%(f_nombre)s',
    migrate=settings.migrate)

db.define_table('t_sede_archive',db.t_sede,Field('current_record','reference t_sede',readable=False,writable=False))

########################################

########################################

########################################

########################################

########################################
# db.define_table('t_tutor',
#     Field('f_usbid', type='string', notnull=False,
#           label=T('Usbid')),
#     Field('f_cedula', type='string', notnull=True,
#           label=T('Cedula')),
#     Field('f_nombre', type='string', notnull=True,
#           label=T('Nombre')),
#     Field('f_apellido', type='string', notnull=True,
#           label=T('Apellido')),
#     Field('f_sede', type='reference t_sede', notnull=True,
#           label=T('Sede')),
#     Field('f_email', type='string', notnull=True,
#           label=T('Email')),
#     Field('f_sexo', type='reference t_sexo', notnull=True,
#           label=T('Sexo')),
#     Field('f_telefono', type='string', notnull=True,
#           label=T('Telefono')),
#     Field('f_direccion', type='text', notnull=True,
#           label=T('Direccion')),
#     Field('f_user', type='reference auth_user', notnull=False,
#           label=T('Nombre de usuario')),
#     Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
#           label=T('Estado'), default='Activo'),
#     auth.signature,
#     format='%(f_usbid)s',
#     migrate=settings.migrate)

# db.define_table('t_tutor_archive',db.t_tutor,Field('current_record','reference t_tutor',readable=False,writable=False))


########################################
#db.define_table('t_proyecto',
#    Field('f_codigo', type='string', notnull=True,
#          label=T('Codigo')),
#    auth.signature,
#    format='%(f_codigo)s',
#    migrate=settings.migrate)

#db.define_table('t_proyecto_archive',db.t_proyecto,Field('current_record','reference t_proyecto',readable=False,writable=False))



########################################

########################################
# TODOS SON PROPONENTES, AUTH_USER
# db.define_table('t_proponente',
#     Field('f_tipoprop', type='reference t_tipoprop', notnull=True,
#           label=T('Tipoprop')),
#     Field('f_cedula', type='string', notnull=True,
#           label=T('Cedula')),
#     Field('f_nombre', type='string', notnull=True,
#           label=T('Nombre')),
#     Field('f_apellido', type='string', notnull=True,
#           label=T('Apellido')),
#     Field('f_email', type='string', notnull=True,
#           label=T('Email')),
#     Field('f_user', type='reference auth_user', notnull=False,
#           label=T('Nombre de usuario')),
#     Field('f_sexo', type='reference t_sexo', notnull=True,
#           label=T('Sexo')),
#     Field('f_telefono', type='string', notnull=True,
#           label=T('Telefono')),
#     Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
#           label=T('Estado'), default='Activo'),
#     auth.signature,
#     format='%(f_tipoprop)s',
#     migrate=settings.migrate)

# db.define_table('t_proponente_archive',db.t_proponente,Field('current_record','reference t_proponente',readable=False,writable=False))

########################################




########################################

########################################
# auth_user, t_universitario y t_estudiante la incluyen
# db.define_table('t_estudiante',
#     Field('f_usbid', type='string', notnull=True,
#           label=T('Usbid'), writable=False),
#     Field('f_nombre', type='string', notnull=True,
#           label=T('Nombre')),
#     Field('f_apellido', type='string', notnull=True,
#           label=T('Apellido')),
#     Field('f_cedula', type='string', notnull=True,
#           label=T('Cedula')),
#     Field('f_carrera', type='reference t_carrera', notnull=True,
#           label=T('Carrera')),
#     Field('f_sede', type='reference t_sede', notnull=True,
#           label=T('Sede')),
#     Field('f_email', type='string', notnull=True,
#           label=T('Email')),
#     Field('f_sexo', type='reference t_sexo', notnull=True,
#           label=T('Sexo')),
#     Field('f_telefono', type='string', notnull=True,
#           label=T('Telefono')),
#     Field('f_user', type='reference auth_user', notnull=False,
#           label=T('Nombre de usuario')),
#     Field('f_direccion', type='text', notnull=True,
#           label=T('Direccion')),
#     Field('f_estado', requires=IS_IN_SET(['Activo', 'Inactivo']), notnull=True,
#           label=T('Estado'), default='Activo'),
#     auth.signature,
#     format='%(f_usbid)s',
#     migrate=settings.migrate)

# db.define_table('t_estudiante_archive',db.t_estudiante,Field('current_record','reference t_estudiante',readable=False,writable=False))

########################################

#actividad de la bitacora

########################################
db.define_table('t_inscripcion',
    Field('f_estudiante', type='reference t_estudiante', notnull=True,
          label=T('Estudiante')),
    Field('f_proyecto', type='reference t_proyecto', notnull=True,
          label=T('Proyecto')),
    Field('f_estado',
          requires=IS_IN_SET(['Aprobado',
                              'Pendiente'
                              ]), notnull=True, label=T('Estado'), default='Pendiente'),
    Field('f_horas', requires=IS_INT_IN_RANGE(0,121), notnull=True,
          label=T('horas'), default=30),
    auth.signature,
    format='%(f_estudiante)s',
    migrate=settings.migrate)

db.define_table('t_inscripcion_archive',db.t_inscripcion,Field('current_record','reference t_inscripcion',readable=False,writable=False))
