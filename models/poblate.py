# -*- coding: utf-8 -*-
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

if len(db().select(db.t_area.ALL)) == 0:
    db.t_area.insert(
        f_codigo='AB',
        f_nombre='Ambiental'
    )
    db.t_area.insert(
        f_codigo='SC',
        f_nombre='Socio-comunitaria'
    )
    db.t_area.insert(
        f_codigo='TE',
        f_nombre='Tecnológica'
    )
    db.t_area.insert(
        f_codigo='LS',
        f_nombre='Laboral y Socio-productiva'
    )
    db.t_area.insert(
        f_codigo='ED',
        f_nombre='Educativa'
    )
    db.t_area.insert(
        f_codigo='IF',
        f_nombre='Infraestructura, Habitat y Vivienda'
    )
    db.t_area.insert(
        f_codigo='SR',
        f_nombre='Seguridad y Riesgo'
    )
    db.t_area.insert(
        f_codigo='SA',
        f_nombre='Salud, Higiene y Alimentación'
    )
    db.t_area.insert(
        f_codigo='DR',
        f_nombre='Deportes, Recreación y Cultura'
    )

areas_carrera = [
	'Ciencias Básicas',
	'Ciencias Sociales y Humanidades',
	'Ingeniería y Ciencias Aplicadas',
	'Industrial',
	'Administración'
]

estados = ['Amazonas','Anzoategui','Apure','Aragua','Barinas','Bolivar','Carabobo','Cojedes','Delta Amacuro','Distrito Capital','Falcon','Guarico','Lara','Merida','Miranda','Monagas','Nueva Esparta','Portuguesa','Sucre','Tachira','Trujillo','Vargas','Yaracuy','Zulia']

if len(db().select(db.t_area_carrera.ALL)) == 0:
    for area in areas_carrera:
    	db.t_area_carrera.insert(f_nombre=area)

if len(db().select(db.t_estado.ALL)) == 0:
    for estado in estados:
    	db.t_estado.insert(f_nombre=estado)