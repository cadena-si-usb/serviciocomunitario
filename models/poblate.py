# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
if len(db().select(db.auth_group.ALL)) == 0:
    db.auth_group.insert(
        role='Asistente',
        description='Asistentes de coordinación. Permisos de administrador',
    )
    db.auth_group.insert(
        role='Coordinador',
        description='Coordinador. Permisos de administrador',
    )
    db.auth_group.insert(
        role='Administrador Dex',
        description='Administrador Dex. Permisos de administrador',
    )
    db.auth_group.insert(
        role='Administrador',
        description='Administrador',
    )
    db.auth_group.insert(
        role='Permiso Tutor',
        description='Permiso que le otorga el Coordinador a cualquier usuario para ser Tutor Academico.',
    )

if len(db().select(db.t_sede.ALL)) == 0:
    db.t_sede.insert(
        f_nombre='Sartenejas',
        f_estado='Activo',
    )
    db.t_sede.insert(
        f_nombre='Litoral',
        f_estado='Activo',
    )

if len(db().select(db.t_area.ALL)) == 0:
    db.t_area.insert(
        f_nombre='Ambiental',
        f_codigo='AB'
    )
    db.t_area.insert(
        f_codigo='SC',
        f_nombre='Socio-comunitaria',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='TE',
        f_nombre='Tecnológica',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='LS',
        f_nombre='Laboral y Socio-productiva',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='ED',
        f_nombre='Educativa',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='IF',
        f_nombre='Infraestructura, Habitat y Vivienda',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='SR',
        f_nombre='Seguridad y Riesgo',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='SA',
        f_nombre='Salud, Higiene y Alimentación',
        f_descripcion='lorem'
    )
    db.t_area.insert(
        f_codigo='DR',
        f_nombre='Deportes, Recreación y Cultura',
        f_descripcion='lorem'
    )

areas_carrera = [
    'Ingeniería',
    'Ciencias Básicas',
    'Ciencias Sociales y Administrativas',
    'Área Industrial',
    'Área Administrativa'
]

estados = ['Amazonas','Anzoategui','Apure','Aragua','Barinas','Bolivar','Carabobo','Cojedes','Delta Amacuro','Distrito Capital','Falcon','Guarico','Lara','Merida','Miranda','Monagas','Nueva Esparta','Portuguesa','Sucre','Tachira','Trujillo','Vargas','Yaracuy','Zulia']
# Llenar tabla de carreras, por codigo y nombre.
carreras={'0800':'Ingeniería de la Computación'}

if len(db().select(db.t_area_carrera.ALL)) == 0:
    for area in areas_carrera:
        db.t_area_carrera.insert(f_nombre=area)

if len(db().select(db.t_estado.ALL)) == 0:
    for estado in estados:
        db.t_estado.insert(f_nombre=estado)

if len(db().select(db.t_carrera.ALL)) == 0:
    for codigo,carrera in carreras.items():
        db.t_carrera.insert(
            f_codigo=codigo,
            f_area_carrera=db(db.t_area_carrera.f_nombre=='Ingeniería').select()[0].id,
            f_nombre=carrera
        )

if len(db().select(db.t_fechas_tope.ALL)) == 0:
    ahora=datetime.today()
    db.t_fechas_tope.insert(
        f_tipo='Inscripción',
        f_fecha_inicial=ahora -timedelta(days=24),
        f_fecha_final=ahora +timedelta(days=300),
    )
    db.t_fechas_tope.insert(
        f_tipo='Inscripción Extemporánea',
        f_fecha_inicial=ahora -timedelta(days=24),
        f_fecha_final=ahora +timedelta(days=300),
    )
    db.t_fechas_tope.insert(
        f_tipo='Enero-Marzo',
        f_fecha_inicial=ahora -timedelta(days=24),
        f_fecha_final=ahora +timedelta(days=300),
    )
    db.t_fechas_tope.insert(
        f_tipo='Abril-Julio',
        f_fecha_inicial=ahora -timedelta(days=24),
        f_fecha_final=ahora +timedelta(days=300),
    )
    db.t_fechas_tope.insert(
        f_tipo='Septiembre-Diciembre',
        f_fecha_inicial=ahora -timedelta(days=24),
        f_fecha_final=ahora +timedelta(days=300),
    )
    db.t_fechas_tope.insert(
        f_tipo='Verano (Julio-Agosto)',
        f_fecha_inicial=ahora -timedelta(days=24),
        f_fecha_final=ahora +timedelta(days=300),
    )
if len(db().select(db.t_comunidad.ALL)) == 0:
    db.t_comunidad.insert(
        f_nombre='Comunidad I'
    )
