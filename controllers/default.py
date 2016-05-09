# -*- coding: utf-8 -*-
import re
import gluon
import datetime
import os
import subprocess
import weasyprint
from reportlab.platypus   import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4,letter
from reportlab.rl_config  import defaultPageSize
from reportlab.lib.units  import inch, mm
from reportlab.lib.enums  import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from gluon.tools   import Crud
from uuid import uuid4
from cgi  import escape
from usbutils import get_ldap_data, random_key
from cgi import escape

### required - do no delete
crud = Crud(db)

def has_admin(user_id):
    is_admin = False
    for ad in ['Asistente','Coordinador','Administrador','Administrador Dex']:
        if auth.has_membership(None, user_id,ad):
            is_admin = True
            break
    return is_admin

def representsInt(s):
    try:
        sint = int(s)
        return True if sint > 0 else False
    except ValueError:
        return False

class Actividad:
    def __init__(self,f_nombre,f_resumen,f_alumnos,f_requerimientos):
        self.f_nombre = f_nombre
        self.f_resumen = f_resumen
        self.f_alumnos = f_alumnos
        self.f_requerimientos = f_requerimientos

# auth = Auth(db,cas_provider = 'https://secure.ds
###

#def user():
#      http://.../[app]/default/user/register
#      http://.../[app]/default/user/login
#      http://.../[app]/default/user/logout
#      http://.../[app]/default/user/profile
#      http://.../[app]/default/user/change_password
#      http://.../[app]/default/user/verify_email
#      http://.../[app]/default/user/retrieve_username
#      http://.../[app]/default/user/request_reset_password
#      http://.../[app]/default/user/reset_password
#      http://.../[app]/default/user/impersonate
#      http://.../[app]/default/user/groups
#      http://.../[app]/default/user/not_authorized
#    form=auth()
#    return dict(form=form)

def verificar(form):
    return dict(form=form)

def download():
    return response.download(request,db)
def call(): return service()

### controlers
def index():
    if auth.is_logged_in():
        redirect(URL("home"))

    return dict(form=auth.login(), host=request.env.http_host)

def error():
    return dict()

#
# Inicio de sesion
########################
def logout():
    es_interno = db.auth_user(auth.user_id)['f_tipo'] != 'Externo'
    url = 'http://secure.dst.usb.ve/logout' if es_interno else URL('index')
    auth.logout(next=url)


def login_cas():
    print "im in    "
    if not request.vars.getfirst('ticket'):
        redirect(URL('error'))
    try:
        import ssl
        import urllib2
        #ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://secure.dst.usb.ve/validate?ticket="+\
              request.vars.getfirst('ticket') +\
              "&service=http%3A%2F%2F"+ request.env.http_host +"%2FSIGESCANTIGUO%2Fdefault%2Flogin_cas"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
	print the_page
    except Exception, e:
        print e
        redirect(URL('error'))
    print "pase"
    if the_page[0:2] == "no":
        print "no :("
        redirect(URL('index'))
    else:
        # session.casticket = request.vars.getfirst('ticket')
        data  = the_page.split()
        usbid = data[1]
        tablaUs  = db.t_universitario
        consulta = db(tablaUs.f_usbid==usbid)
        print(consulta)
        if consulta.isempty():

            clave   = random_key()
            us      = get_ldap_data(usbid)

            # print "insertando"
            a = db.auth_user.insert(
                first_name = us.get('first_name'),
                last_name  = us.get('last_name'),
                username   = usbid,
                password   = db.auth_user.password.validate(clave)[0],
                email      = us.get('email'),
                f_cedula     = us['cedula'],
                f_telefono   = us['phone'],
                f_tipo       = us['tipo'],
            )

            user = db(db.auth_user.username==usbid).select()[0]
            print us
            db.t_universitario.insert(
                f_usbid   = usbid,
                f_key     = clave,
                f_usuario = user.id
            )

            userUniv = db(db.t_universitario.f_usbid==usbid).select()[0]

            if (us['tipo'] == "Pregrado") or (us['tipo'] == "Postgrado"):
               # Si es estudiante insertar en su tabla
                db.t_estudiante.insert(
                    f_universitario = userUniv.id,
                    f_carrera       = us['carrera'],
                    f_sede          = "Sartenejas"
                )
            elif us['tipo'] == "Docente":
                # En caso de ser docente, agregar dpto.
                db.t_tutor_academico.insert(
                    f_universitario = userUniv.id,
                    f_departamento  = us['dpto'],
                    f_sede          = "Sartenejas"
                )

        else:
            userUniv = db(db.t_universitario.f_usbid==usbid).select()[0]
            clave    = userUniv.f_key


        # Al finalizar login o registro, redireccionamos a home
        auth.login_bare(usbid,clave)
        redirect('home')
    return None


# Contolador de redireccion de usuarios
@auth.requires_login()
def home():
    is_admin = has_admin(auth.user_id)
    usuario  = db.auth_user(auth.user_id)
    msj      = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    tipo = db.auth_user(auth.user_id)['f_tipo']

    return dict(is_admin=is_admin,tipo_usuario=tipo,bienvenida=msj, host=request.env.http_host)

# @ticket_in_session
def mostrar_credencial():
    return dict()


def registro():
    return dict(formulario=auth.register())

@auth.requires_login()
def perfil():
    if request.args(0) == 'search':
        if not has_admin(auth.user_id):
            redirect(URL('home'))
        user_id = request.args(1)
    else:
        user_id = auth.user_id


    if db.auth_user(auth.user_id)['f_foto']:
        picture = URL('default', 'download', args=db.auth_user(user_id)['f_foto'])
    else:
        picture = URL('static', 'img/user.png')

    sede,dpto,carrera = None,None,None
    univ = db.t_universitario(f_usuario=user_id)

    if db.auth_user(auth.user_id)['f_tipo'] == "Docente":
        sede = univ.t_tutor_academico.select()[0]['f_sede']
        dpto = univ.t_tutor_academico.select()[0]['f_departamento']
    elif db.auth_user(auth.user_id)['f_tipo'] in ["Pregrado","Postgrado"]:
        sede    = univ.t_estudiante.select()[0]['f_sede']
        carrera = univ.t_estudiante.select()[0]['f_carrera']
    user = db.auth_user(auth.user_id)
    return dict(form=user,picture=picture,dpto=dpto, sede=sede,carrera=carrera)

@auth.requires_login()
def editar_perfil():
    db.auth_user.username.writable=False
    db.auth_user.f_foto.writable  =True
    form = auth.profile()
    form.element('input', _type = 'submit')['_class'] = 'btn btn-primary'

    estudiante = None
    docente    = None
    if auth.user['f_tipo'] in ["Pregrado","Postgrado"]:
        estudiante = db.auth_user(auth.user_id)['t_universitario'].select()[0]['t_estudiante'].select()[0]
        form[0].insert(-1, TR(LABEL(T('Carrera:')),
                             INPUT(_id='carrera',
                                   _name='carrera',
                                   _value=estudiante['f_carrera']
                            )))
        form[0].insert(-1, TR(LABEL(T('Sede:')),
                             SELECT(estudiante['f_sede'],
                                OPTGROUP('Sartenejas','Litoral'),
                                _id='sede',
                                _name='sede'
                            )))
    elif auth.user['f_tipo']== "Docente":
        docente = db.auth_user(auth.user_id)['t_universitario'].select()[0]['t_tutor_academico'].select()[0]
        form[0].insert(-1, TR(LABEL(T('Departamento:')),
                             INPUT(_id='departamento',
                                   _name='departamento',
                                   _value=docente['f_departamento']
                            )))
        form[0].insert(-1, TR(LABEL(T('Sede:')),
                             SELECT(docente['f_sede'],
                                OPTGROUP('Sartenejas','Litoral'),
                                _id='sede',
                                _name='sede'
                            )))

    if form.accepts(request.vars, session, formname='form1'):
        response.flash = 'form accepted'

        if estudiante:
            f_univ = db.auth_user(auth.user_id)['t_universitario'].select()[0]
            db(db.t_estudiante.f_universitario == f_univ['id']).update(
                f_sede=form.vars['sede'],
                f_carrera=form.vars['carrera'])
        elif docente:
            f_univ = db.auth_user(auth.user_id)['t_universitario'].select()[0]
            db(db.t_tutor_academico.f_universitario == f_univ['id']).update(
                f_sede=form.vars['sede'],
                f_departamento=form.vars['departamento'])
    elif form.errors:
        response.flash = 'form has errors'


    return dict(form=form,contrasena=auth.change_password())

def proponenteProyecto():
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    idProponente = db(db.t_proponente.f_user==auth.user).select()
    return dict(proyectos = db(db.t_project.f_proponente==idProponente[0]).select(), bienvenida=msj)

def moderarProyectos():
    return dict(proyectos=db().select(db.t_cursa.ALL))

def estudiantes():
    form = SQLFORM(db.t_estudiante,formstyle='table3cols')
    if form.process().accepted:
        response.flash = '1'
    elif form.errors:
        response.flash = '0'
    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, est=db(db.t_usuario_universitario.f_rol == "Estudiante").select(),message=T(response.flash))

def usuarios():
    return dict(registrados=db(db.auth_user.id!=auth.user_id).select())

def usuarios_detalles():
    idUsuario=request.args(0)

    if db.auth_user(idUsuario)['f_foto']:
        picture = URL('default', 'download', args=db.auth_user(idUsuario)['f_foto'])
    else:
        picture = URL('static', 'img/user.png')

    sede,dpto,carrera = "","",""
    univ = db.t_universitario(f_usuario=idUsuario)

    if db.auth_user(idUsuario)['f_tipo'] == "Docente":
        sede = univ.t_tutor_academico.select()[0]['f_sede']
        dpto = univ.t_tutor_academico.select()[0]['f_departamento']
    elif db.auth_user(idUsuario)['f_tipo'] in ["Pregrado","Postgrado"]:
        sede    = univ.t_estudiante.select()[0]['f_sede']
        carrera = univ.t_estudiante.select()[0]['f_carrera']

    tabla= db(db.auth_user.id==idUsuario).select()[0]
    return dict(form=tabla,picture=picture,dpto=dpto, sede=sede,carrera=carrera)

def eliminar_usuario():
    idUsuario=request.args(0)
    db(db.auth_user.id==idUsuario).delete()
    redirect(URL('usuarios'))

def roles_usuarios():
    relaciones=db(db.auth_membership.user_id!=auth.user_id).select()
    return dict(registrados=relaciones)

def eliminar_rol():
    idrol=request.args(0)
    db(db.auth_membership.id==idrol).delete()
    redirect(URL('roles_usuarios'))

def agregar_rol():
    usuarios=db(db.auth_user.id!=auth.user_id).select()
    return dict(usuarios=usuarios)

def agregar_rol_usuario():
    idUsuario=request.args(0)
    rolesUsuario= db(db.auth_membership.user_id==idUsuario).select()
    roles= db().select(db.auth_group.ALL)
    nombreUsuario= db(db.auth_user.id==idUsuario).select()[0].username
    return dict(roles=roles,rolesUsuario=rolesUsuario,nombreUsuario=nombreUsuario,idUsuario=idUsuario)

def insertar_rol():
    idUsuario=request.args(0)
    idGrupo=request.args(1)
    auth.add_membership(idGrupo, idUsuario)
    redirect(URL(r=request,f='agregar_rol_usuario',args=idUsuario))

def vista_proponente():
    def my_form_processing(form):
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'

    msj= 'Bienvenid@ %s %s' % (session.user.f_nombres,session.user.f_apellidos)
    return dict(bienvenida=msj)

def proponenteProyecto():
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    idProponente = db(db.t_proponente.f_user==auth.user).select()
    return dict(proyectos = db(db.t_project.f_proponente==idProponente[0]).select(), bienvenida=msj)

def moderarProyectos():
    return dict(proyectos=db().select(db.t_cursa.ALL))

@auth.requires_login()
def estado_manage():
    form = SQLFORM.smartgrid(db.t_estado,onupdate=auth.archive)
    return dict(form=form)

# @auth.requires_membership(['Administrador','Coordinador'])
@auth.requires_login()
def areas():
    def my_form_processing(form):
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    form = SQLFORM(db.t_area,onupdate=auth.archive)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'

    elif form.errors:
        response.flash = '0'

    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, areas=db(db.t_area.f_estado=="Activo").select(),message=T(response.flash))

@auth.requires_membership('Administrador')
def proyectos():
    def my_form_processing(form):
        if not re.match('\d{4}', form.vars.f_codigo):
            form.errors.f_codigo = 'El formato válido del código son 4 dígitos'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_descripcion):
            form.errors.f_descripcion = 'Sólo puede contener letras'
        if not re.match('\d+', form.vars.f_version):
            form.errors.f_version = 'El formato válido de la versión son 2 dígitos'
        if form.vars.f_fechaini > form.vars.f_fechafin:
            form.errors.f_fechaini = 'La fecha final del proyecto es menor que la inicial'
            form.errors.f_fechafin = 'La fecha final del proyecto es menor que la inicial'
    form = SQLFORM(db.t_proyecto,onupdate=auth.archive)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'

    elif form.errors:
        response.flash = '0'

    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, proyectos=db(db.t_proyecto.f_estado_del=="Activo").select(),message=T(response.flash))


# @auth.requires_membership('Estudiantes')
@auth.requires_login()
def proyectosEstudiante():
    f_tutores = []
    def my_form_processing(form):
        f_tutores += form.vars.f_tutores
        del form.vars.f_tutores
        if not re.match('\d{4}', form.vars.f_codigo):
            form.errors.f_codigo = 'El formato válido del código son 4 dígitos'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_descripcion):
            form.errors.f_descripcion = 'Sólo puede contener letras'
        if not re.match('\d+', form.vars.f_version):
            form.errors.f_version = 'El formato válido de la versión son 2 dígitos'
        if form.vars.f_fechaini > form.vars.f_fechafin:
            form.errors.f_fechaini = 'La fecha final del proyecto es menor que la inicial'
            form.errors.f_fechafin = 'La fecha final del proyecto es menor que la inicial'
    form = SQLFORM(db.t_proyecto,onupdate=auth.archive)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'
    elif form.errors:
        response.flash = '0'
    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, proyectos=db(db.t_proyecto.f_estado_del=="Activo").select(),message=T(response.flash))


@auth.requires_membership('Administrador')
def comunidades():
    def my_form_processing(form):
        if not re.match('\d', form.vars.f_cantidadbeneficiados):
            form.errors.f_cantidadbeneficiados = 'Debe ser un número'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    form = SQLFORM(db.t_comunidad,onupdate=auth.archive)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'

    elif form.errors:
        response.flash = '0'

    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, comunidades=db(db.t_comunidad.f_estado_del=="Activo").select(),message=T(response.flash))

@auth.requires_membership('Administrador')
def validarProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_state="2",f_valido="Valido")
    return dict(proyecto=idProyecto)

def validacionProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_valido="Activo")
    return dict(proyecto=idProyecto)

def solicitarValidacion():
    idProyecto = long(request.args[0])
    return dict(proyecto=idProyecto)

def solicitarValidacionEstudiante():
    idProyecto = long(request.args[0])
    return dict(proyecto=idProyecto)

def rechazarProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_state="3")
    return dict(proyecto=idProyecto)

def registrarProyectoEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    proyectoInscrito = db(db.t_cursa.f_estudiante==idEstudiante).select()
    if not proyectoInscrito:
        db.t_cursa.insert(f_estudiante=idEstudiante,f_project=idProyecto,f_estado="Pendiente")
        mensaje = "Registro de proyecto exitoso. Volver a proyectos"
    else:
        mensaje = "Usted ya tiene un proyecto inscrito. Volver a proyectos"

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje)

def registrarProyectoComoEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    proyectoInscrito = db(db.t_cursa.f_estudiante==idEstudiante).select()
    if not proyectoInscrito:
        db.t_cursa.insert(f_estudiante=idEstudiante,f_project=idProyecto,f_state="2")
        mensaje = "Registro de proyecto exitoso. Volver a proyectos"
    else:
        mensaje = "Usted ya tiene un proyecto inscrito. Volver a proyectos"

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje)

@auth.requires_membership('Administrador')
def comunidad_manage():
    form = SQLFORM.smartgrid(db.t_comunidad,onupdate=auth.archive)
    return locals()

@auth.requires_membership('Administrador')
def area_manage():
    form = SQLFORM.smartgrid(db.t_area,onupdate=auth.archive)
    return locals()

def estudiante_manage():
    form = SQLFORM.smartgrid(db.t_estudiante.id==request.args(0))
    if form.process().accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return locals()

def proponente_manage():
    form = SQLFORM.smartgrid(db.t_proponente,onupdate=auth.archive)
    return locals()

def tutor_manage():
    form = SQLFORM.smartgrid(db.t_tutor,onupdate=auth.archive)
    return locals()

def proyecto_manage():
    form = SQLFORM.smartgrid(db.t_proyecto,onupdate=auth.archive)
    return locals()

def condicion_manage():
    form = SQLFORM.smartgrid(db.t_condicion,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def caracterisicas_manage():
    form = SQLFORM.smartgrid(db.t_caracterisicas,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def cursa_manage():
    form = SQLFORM.smartgrid(db.t_cursa,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def carrera_manage():
    form = SQLFORM.smartgrid(db.t_carrera,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def tipoprop_manage():
    form = SQLFORM.smartgrid(db.t_tipoprop,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def relacionestproy_manage():
    form = SQLFORM.smartgrid(db.t_relacionestproy,onupdate=auth.archive)
    return locals()

def sedesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_sede.id==x).select())


def estudianteProyectos():
    x = long (request.args[0])
    return dict(rows = db(db.t_estudiante.id==x).select(),proyectos=db().select(db.t_proyecto.ALL),estudianteID=x)

def estudianteInscribeProyectos():
    x = long (request.args[0])
    return dict(rows = db(db.t_estudiante.id==x).select(),proyectos=db().select(db.t_proyecto.ALL),estudianteID=x)


def estudiantesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_estudiante.id==x).select(),estudianteId=x)

def tutoresDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_tutor.id==x).select())

def proyectosDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_proyecto.id==x).select())

def proyectosDetallesEstudiantes():
    x = long (request.args[0])
    return dict(rows = db(db.t_proyecto.id==x).select())

def proponentesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_proponente.id==x).select())

def areasDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_area.id==x).select())

def comunidadesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_comunidad.id==x).select())

def estudiantesEditar():
    def my_form_processing(form):
        if not re.match('\d{2}-\d{5}$', form.vars.f_usbid):
            form.errors.f_usbid = 'El formato válido de carnet es: 00-00000'
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    record = db.t_estudiante(request.args[0])
    form = SQLFORM(db.t_estudiante, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def estudiantesEditarPerfil():
    def my_form_processing(form):
        if not re.match('\d{2}-\d{5}$', form.vars.f_usbid):
            form.errors.f_usbid = 'El formato válido de carnet es: 00-00000'
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_estudiante(request.args[0])
    form = SQLFORM(db.t_estudiante, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def areasEditar():
    def my_form_processing(form):
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    x = long (request.args[0])
    record = db.t_area(request.args[0])
    form = SQLFORM(db.t_area, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def sedesEditar():
    def my_form_processing(form):
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    x = long (request.args[0])
    record = db.t_sede(request.args[0])
    form = SQLFORM(db.t_sede, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

# def vista_admin():
#     msj= 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)

#     if auth.has_membership('Proponentes'):
#         redirect(URL('vista_proponente'))

def proponentesEditar():
    def my_form_processing(form):
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_proponente(request.args[0])
    form = SQLFORM(db.t_proponente, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def tutoresEditar():
    def my_form_processing(form):
        if form.vars.f_usbid:
            if not re.match('\d{2}-\d{5}$', form.vars.f_usbid) and not re.match('[a-zA-Z0-9_.+-]+', form.vars.f_usbid):
                form.errors.f_usbid = 'usbid invalido'
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_tutor(request.args[0])
    form = SQLFORM(db.t_tutor, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('El tutor ha sido eliminado')
    return dict(form = form)


def proyectosEditar():
    def my_form_processing(form):
        if not re.match('\d{4}', form.vars.f_codigo):
            form.errors.f_codigo = 'El formato válido del código son 4 dígitos'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_descripcion):
            form.errors.f_descripcion = 'Sólo puede contener letras'
        if not re.match('\d+', form.vars.f_version):
            form.errors.f_version = 'El formato válido de la versión son 2 dígitos'
        if form.vars.f_fechaini > form.vars.f_fechafin:
            form.errors.f_fechaini = 'La fecha final del proyecto es menor que la inicial'
            form.errors.f_fechafin = 'La fecha final del proyecto es menor que la inicial'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_proyecto(request.args[0])
    form = SQLFORM(db.t_proyecto, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('El proyecto ha sido eliminada')
    return dict(form = form)

def comunidadesEditar():
    def my_form_processing(form):
        if not re.match('\d', form.vars.f_cantidadbeneficiados):
            form.errors.f_cantidadbeneficiados = 'Debe ser un número'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_comunidad(request.args[0])
    form = SQLFORM(db.t_comunidad, record, deletable = True)
    if form.process(nvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La comunidad ha sido eliminada')
    return dict(form = form)

########################################################################################
################## syscorp
########################################################################################
def proyectos_tutor_comunitario():
    tutor     = db.auth_user(auth.user_id)
    msj       = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    proyectos = db(db.t_proyecto_tutor_comunitario.f_tutor==tutor).select()
    return dict(bienvenida=msj,proyectos=proyectos)

def proyecto_tutor_comunitario():
    tutor       = db.auth_user(auth.user_id)
    id_proy     = request.vars.proy
    proyecto    = db(db.t_proyecto.id==id_proy).select().first()
    msj         = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    estudiantes = db(db.t_estudiante.id==db.t_cursa.f_estudiante)(db.t_cursa.f_proyecto==id_proy).select()
    return dict(estudiantes=estudiantes,bienvenida=msj,proyecto=proyecto)

#AJAX confirmacion de actividad
def confirmar_actividad():
    actividad = db(db.t_actividad_estudiante.id==request.vars.id).update(f_confirmada=True)
    return ""

def bitacora_de_estudiante():
    tutor      = db.auth_user(auth.user_id)
    msj        = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    id_est     = request.vars.est
    proyecto   = db(db.t_cursa.f_estudiante==id_est and db.t_cursa.f_proyecto==request.vars.proy).select().first()
    estudiante = db(db.t_estudiante.id==id_est).select().first()
    bitacora   = db(db.t_actividad_estudiante.f_cursa==proyecto)(db.t_actividad_estudiante.f_realizada==True).select()
    return dict(bienvenida=msj,bitacora=bitacora,estudiante=estudiante,proyecto=proyecto)

#AJAX completar actividad
def completar_actividad():
    actividad = db(db.t_actividad_estudiante.id==request.vars.id).update(f_realizada=True)
    return ""

#@auth.requires_membership('Estudiantes')
def estado_estudiante():
    usuario    = db.auth_user(auth.user_id)
    msj        = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt = db(db.t_universitario.f_usuario==usuario).select().first()
    estudiante = db(db.t_estudiante.f_universitario==estt).select().first()
    #Proyecto
    try:
        proyectos = db(db.t_cursa.f_estudiante==estudiante.id).select()
        proyectos = proyectos[0]
        proyecto = proyectos
        proy = proyectos.f_proyecto
    except:
        proyecto = None
        proy = None

    #Tutores
    tutor_comunitario = []
    for obj in db(db.t_proyecto_tutor_comunitario.f_proyecto==proy).select():
        tutor_comunitario.append(obj.f_tutor.first_name + " " + obj.f_tutor.last_name)

    tutor = []
    for obj in db(db.t_proyecto_tutor.f_proyecto==proy).select():
        tutor.append(obj.f_tutor.first_name + " " + obj.f_tutor.last_name)

    #Actividades
    actividades = db(db.t_actividad_estudiante.f_cursa==proyectos.id).select()

    #PlanesOperativosPorActividad
    planoperativo = []
    horas_realizadas = 0

    for row in actividades:
        planoperativo.append(db(db.t_plan_operativo.f_actividad==row.f_actividad).select())
        if row.f_realizada:
            horas_realizadas += int(row.f_horas)

    if request.env.request_method =='POST':
        if form.process(onvalidation=my_form_processing, keepvalues=True).accepted:
            response.flash = 'form accepted'
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill out the form'
    return dict(rows=usuario, bienvenida=msj,estudianteId=estudiante.id, tutor=", ".join(tutor),
                proyecto=proyecto, actividades=actividades, planoperativo=planoperativo,
                horas_realizadas=horas_realizadas, tutor_comunitario=", ".join(tutor_comunitario),)

def vista_estudiante():
    usuario    = db.auth_user(auth.user_id)
    msj        = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt       = db(db.t_universitario.f_usuario==usuario).select().first()
    estudiante = db(db.t_estudiante.f_universitario==estt).select().first()

    try:
        cursa = db(db.t_cursa.f_estudiante==estudiante.id, db.t_cursa.f_valido=="Invalido").select()
        cursa = cursa[0]
        if not cursa:
            cursa = db(db.t_cursa.f_estudiante==estudiante.id, db.t_cursa.f_valido=="Valido").select()
            cursa = cursa[0]
        proyecto = cursa.f_proyecto
    except:
        proyecto = None
        cursa = None

    print cursa

    # Buscamos todas las actividades de todos los proyectos que alguna vez realizó el estudiante.
    horas_realizadas = 0
    todos_los_proyectos = db(db.t_cursa.f_estudiante==estudiante).select()
    for proy in todos_los_proyectos:
        todas_actividades = db(db.t_actividad_estudiante.f_cursa==proy).select()
        for acti in todas_actividades:
            if acti.f_realizada:
                horas_realizadas += int(acti.f_horas)
    pInscrito = 'vacio'
    pActividad = 'no'
    tutor = None
    proyectoInscrito = db(db.t_cursa.f_estudiante==estudiante).select().first()
    #cursa = db(db.t_cursa.f_estudiante==estudiante).select()
    actividad = None
    if proyecto:
        actividad = db(db.t_actividad_estudiante.f_cursa==proyectoInscrito).select()
    if actividad:
        pActividad = 'si'
    if proyectoInscrito:
        pInscrito = 'proyecto inscrito'
        tutor = db(db.t_inscripcion.f_estudiante==estudiante).select().first()
        aprob_tutor = tutor.f_estado
        aprob_coord = cursa.f_valido
    else:
        aprob_tutor = 'tutorVacio'
        aprob_coord = 'coordVacio'

    estudianteId = estudiante.id
    return dict(usuario,estudianteId=estudianteId,horas=horas_realizadas,estudiante=estudiante,
                bienvenida=msj,proyecto=proyecto,pInscrito=pInscrito,pActividad=pActividad,
                aprob_tutor=aprob_tutor,aprob_coord=aprob_coord,cursa=cursa,tutor=tutor)

def retirar_proyecto():
    x = long (request.args[0])
    usuario = db.auth_user(auth.user_id)
    msj     = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt    = db(db.t_universitario.f_usuario==usuario).select().first()
    usuario = db(db.t_estudiante.f_universitario==estt).select().first()
    proyecto  = db(db.t_cursa.f_estudiante==usuario)(db.t_cursa.f_proyecto==x).select().first()
    horas = 0
    todas_actividades = db(db.t_actividad_estudiante.f_cursa==proyecto).select()
    for acti in todas_actividades:
        if acti.f_realizada:
            horas += int(acti.f_horas)
    return dict(estudiante=usuario, bienvenida=msj,proyecto=proyecto,horas=horas)

def retiro():
    retiro = db(db.t_cursa.f_estudiante==request.vars.id and db.t_cursa.f_estado=='Aprobado').update(f_estado='Retirado',f_fecha=datetime.datetime.today())
    return ""

def culminar_proyecto():
    x = long (request.args[0])
    usuario  = db.auth_user(auth.user_id)
    msj      = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt = db(db.t_universitario.f_usuario==usuario).select().first()
    usuario = db(db.t_estudiante.f_universitario==estt).select().first()
    proyecto = db(db.t_cursa.f_estudiante==usuario)(db.t_cursa.f_proyecto==x).select().first()
    error = None

    form = SQLFORM.factory(Field('f_informe','upload',uploadfolder=request.folder+'static/pdfs',label=T('Informe'),requires = [IS_LENGTH(maxsize=2097152),IS_UPLOAD_FILENAME(extension='pdf')]))
    if form.process(session=None, formname='test').accepted:
        if form.vars.f_informe:
            db(db.t_estudiante.f_universitario==auth.user.id).update(f_informe=form.vars.f_informe)
            db(db.t_cursa.f_estudiante==usuario).update(f_estado="Culminado",f_fecha=datetime.datetime.today())
            return redirect(URL('culminar_proyecto',args=[x]))
        print('form accepted')
    elif form.errors:
        error = "El informe debe estar en formato pdf y no ser mayor a 2Mb"
        print('form has errors')
    else:
        print('please fill the form')

    # Buscamos todas las actividades de todos los proyectos que alguna vez realizó el estudiante.
    horas_realizadas = 0
    todos_los_proyectos = db(db.t_cursa.f_estudiante==usuario).select()
    for proy in todos_los_proyectos:
        todas_actividades = db(db.t_actividad_estudiante.f_cursa==proy).select()
        for acti in todas_actividades:
            if acti.f_realizada:
                horas_realizadas += int(acti.f_horas)
    return dict(horas=horas_realizadas,error=error, estudiante=usuario, bienvenida=msj,proyecto=proyecto)

############# PDF
def encabezado(canvas,doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/img/DEX.png')
    canvas.drawImage(logo, 68, A4[1]-104, 120, 74)
    canvas.drawString(inch, A4[1]-114, "COORDINACIÓN DE  EXTENSIÓN SEDE LITORAL")
    canvas.drawString(inch, A4[1]-124, "PROGRAMA ACCIÓN SOCIAL Y SERVICIO COMUNITARIO")
    canvas.drawString(inch, A4[1]-128, '_'*100)
    canvas.restoreState()

def pie(canvas,doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.86 * inch, '_'*100)
    canvas.drawString(inch, 0.72 * inch, "Valle de Camurí Grande. Edf. Laboratorios Pesados. Piso 2. Ofic LPD 208l. Telf.: 0212-9069170.")
    canvas.drawString(inch, 0.60 * inch, "Web: http://www.cfgc.dex.usb.ve | E-mail: psc-sl@usb.ve")
    canvas.restoreState()

def generarPdfConstanciaRetiro():
    x = long (request.args[0])
    y = long (request.args[1])
    est   = db(db.t_estudiante.id==x).select().first()
    proy  = db(db.t_proyecto.id==y).select().first()
    tutor = db(db.t_proyecto_tutor.f_proyecto==proy).select().first()
    tutor = tutor.f_tutor

    USBID     = est.f_universitario.f_usbid
    Nombre    = est.f_universitario.f_usuario.first_name
    Apellido  = est.f_universitario.f_usuario.last_name
    Carrera   = est.f_carrera
    codigo_pr = proy.id
    nombre_pr = proy.f_nombre
    descripcion_pr = proy.f_resumen
    horas = 0
    todas_actividades = db(db.t_actividad_estudiante.f_cursa==proy).select()
    for acti in todas_actividades:
        if acti.f_realizada:
            horas += int(acti.f_horas)

    comunidad_pr  = proy.f_comunidad

    title = "CERTIFICACION DE RETIRO DE SERVICIO COMUNITARIO"

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='test',fontName='Times-Roman',spaceBefore=5,spaceAfter=2,alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='titulo',fontName='Times-Bold',spaceBefore=20,fontSize=12,spaceAfter=16,alignment=TA_CENTER))
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))

    story = []
    story.append(NextPageTemplate('Culminacion'))
    story.append(Paragraph(escape(title),styles["titulo"]))
    story.append(Paragraph(escape('APELLIDO Y NOMBRE DEL ESTUDIANTE: ' + str(Apellido) +', '+ str(Nombre)),styles["test"]))
    story.append(Paragraph(escape('CARNET: ' + str(USBID)),styles["test"]))
    story.append(Paragraph(escape('CARRERA: ' + str(Carrera)),styles["test"]))
    story.append(Paragraph(escape('TITULO DEL PROYECTO DE SERVICIO COMUNITARIO: ' + str(nombre_pr)),styles["test"]))
    story.append(Paragraph(escape('CÓDIGO: ' + str(codigo_pr)),styles["test"]))
    story.append(Paragraph(escape('COMUNIDAD BENEFICIADA: ' +str(comunidad_pr)),styles["test"]))
    story.append(Paragraph(escape('APELLIDO Y NOMBRE DEL TUTOR ACADÉMICO: '+str(tutor.first_name)+', '+str(tutor.last_name)),styles["test"]))
    story.append(Paragraph(escape('CÉDULA DE IDENTIDAD DEL TUTOR ACADÉMICO: '+str(tutor.f_cedula)),styles["test"]))
    story.append(Paragraph(escape('CERTIFICO QUE EL ESTUDIANTE CUMPLIÓ CON LOS OBJETIVOS PLANTEADOS DURANTE EL \
        DESARROLLO DEL PROYECTO DE SERVICIO COMUNITARIO POR UN LAPSO DE '+ str(horas)+' HORAS, COMO LO ESTABLECE EL \
        REGLAMENTO DE FORMACIÓN COMPLEMENTARIA PROFESIONAL EN SU SECCIÓN 2 DEL SERVICIO COMUNITARIO EN SU ARTÍCULO 24 \
        PARÁGRAFO EVALUACIÓN.'),styles["test"]))
    story.append(Paragraph(escape('CONFORME:'),styles["test"]))
    story.append(Spacer(0,0.6*inch))
    t = Table([
        ['_'*30,'_'*30],
        ['Firma del Tutor ACADÉMICO\n(Firma y Sello del Dpto. Adscripción)', 'Validación de CFGC o COORDEXT\n(Firma y Sello )']
        ], colWidths=160, rowHeights=16)
    t2 = Table([
        ['FECHA DE LA CERTIFICACIÓN:  '+'_'*42],
        ['OBSERVACIONES:  '+'_'*54],
        ['_'*72],
        ['_'*72]
        ], rowHeights=22)
    t.setStyle(TableStyle([
                        ('VALIGN',(0,0),(-1,-1),'TOP'),
                        ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                        ('FONTNAME',(0,0),(-1,-1),'Times-Roman'),
                        ]))
    t2.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Times-Roman')]))
    story.append(t)
    story.append(Spacer(0,0.4*inch))
    story.append(t2)

    frameN = Frame(inch, inch, 451, 630, id='normal')
    PTCulminacion = PageTemplate(id='Culminacion', frames=frameN, onPage=encabezado, onPageEnd=pie)
    doc = BaseDocTemplate(tmpfilename, pageTemplates=[PTCulminacion])
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data

def generarPdfConstanciaCulminacion():
    x = long (request.args[0])
    y = long (request.args[1])
    est   = db(db.t_estudiante.id==x).select().first()
    proy  = db(db.t_proyecto.id==y).select().first()
    tutor = db(db.t_proyecto_tutor.f_proyecto==proy).select().first()
    tutor = tutor.f_tutor

    USBID     = est.f_universitario.f_usbid
    Nombre    = est.f_universitario.f_usuario.first_name
    Apellido  = est.f_universitario.f_usuario.last_name
    Carrera   = est.f_carrera
    codigo_pr = proy.id
    nombre_pr = proy.f_nombre
    descripcion_pr = proy.f_resumen
    horas = 0
    todas_actividades = db(db.t_actividad_estudiante.f_cursa==proy).select()
    for acti in todas_actividades:
        if acti.f_realizada:
            horas += int(acti.f_horas)

    comunidad_pr  = proy.f_comunidad

    title = "CERTIFICACION DE CUMPLIMIENTO DE SERVICIO COMUNITARIO"

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='test',fontName='Times-Roman',spaceBefore=5,spaceAfter=2,alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='titulo',fontName='Times-Bold',spaceBefore=20,fontSize=12,spaceAfter=16,alignment=TA_CENTER))
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))

    story = []
    story.append(NextPageTemplate('Culminacion'))
    story.append(Paragraph(escape(title),styles["titulo"]))
    story.append(Paragraph(escape('APELLIDO Y NOMBRE DEL ESTUDIANTE: ' + str(Apellido) +', '+ str(Nombre)),styles["test"]))
    story.append(Paragraph(escape('CARNET: ' + str(USBID)),styles["test"]))
    story.append(Paragraph(escape('CARRERA: ' + str(Carrera)),styles["test"]))
    story.append(Paragraph(escape('TITULO DEL PROYECTO DE SERVICIO COMUNITARIO: ' + str(nombre_pr)),styles["test"]))
    story.append(Paragraph(escape('CÓDIGO: ' + str(codigo_pr)),styles["test"]))
    story.append(Paragraph(escape('COMUNIDAD BENEFICIADA: ' +str(comunidad_pr)),styles["test"]))
    story.append(Paragraph(escape('APELLIDO Y NOMBRE DEL TUTOR ACADÉMICO: '+str(tutor.first_name)+', '+str(tutor.last_name)),styles["test"]))
    story.append(Paragraph(escape('CÉDULA DE IDENTIDAD DEL TUTOR ACADÉMICO: '+str(tutor.f_cedula)),styles["test"]))
    story.append(Paragraph(escape('CERTIFICO QUE EL ESTUDIANTE CUMPLIÓ CON LOS OBJETIVOS PLANTEADOS DURANTE EL \
        DESARROLLO DEL PROYECTO DE SERVICIO COMUNITARIO POR UN LAPSO DE '+ str(horas)+' HORAS, COMO LO ESTABLECE EL \
        REGLAMENTO DE FORMACIÓN COMPLEMENTARIA PROFESIONAL EN SU SECCIÓN 2 DEL SERVICIO COMUNITARIO EN SU ARTÍCULO 24 \
        PARÁGRAFO EVALUACIÓN.'),styles["test"]))
    story.append(Paragraph(escape('CONFORME:'),styles["test"]))
    story.append(Spacer(0,0.6*inch))
    t = Table([
        ['_'*30,'_'*30],
        ['Firma del Tutor ACADÉMICO\n(Firma y Sello del Dpto. Adscripción)', 'Validación de CFGC o COORDEXT\n(Firma y Sello )']
        ], colWidths=160, rowHeights=16)
    t2 = Table([
        ['FECHA DE LA CERTIFICACIÓN:  '+'_'*42],
        ['OBSERVACIONES:  '+'_'*54],
        ['_'*72],
        ['_'*72]
        ], rowHeights=22)
    t.setStyle(TableStyle([
                        ('VALIGN',(0,0),(-1,-1),'TOP'),
                        ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                        ('FONTNAME',(0,0),(-1,-1),'Times-Roman'),
                        ]))
    t2.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Times-Roman')]))
    story.append(t)
    story.append(Spacer(0,0.4*inch))
    story.append(t2)

    frameN = Frame(inch, inch, 451, 630, id='normal')
    PTCulminacion = PageTemplate(id='Culminacion', frames=frameN, onPage=encabezado, onPageEnd=pie)
    doc = BaseDocTemplate(tmpfilename, pageTemplates=[PTCulminacion])
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data

########################################################################################
################## final syscorp
########################################################################################

def genPDF(base_url='applications/SIGESC/templates_pdf/planillaAval/', template_html='template.html',template_css='template.css', output="out.pdf",variables=dict()):
    template = open(base_url+template_html).read()
    contenido = template.format(**variables)
    weasyprint.HTML(string=contenido,base_url=base_url).render(stylesheets=[base_url+template_css]).write_pdf(output)
    pdf = open(output).read()
    os.remove(output)
    return pdf

def proponenteProyecto():
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    idProponente = db(db.t_proponente.f_user==auth.user).select()
    return dict(proyectos = db(db.t_project.f_proponente==idProponente[0]).select(), bienvenida=msj)


def solicitudes_tutor():
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    idTutor = db(db.t_universitario.f_usuario == auth.user).select().first()
    idTutorAcademico = db(db.t_tutor_academico.f_universitario == idTutor).select().first()
    listaProyectosTutores = db(db.t_proyecto_tutor.f_tutor == idTutorAcademico).select()
    listaInscripcion = []
    listaEnviados = []
    for proy in listaProyectosTutores:
        listaInscripcion += db(db.t_inscripcion.f_proyecto == proy.f_proyecto).select()
    for ins in listaInscripcion:
        act = []
        cursa = db(db.t_cursa.f_estudiante==ins.f_estudiante).select().first()
        act += db(db.t_actividad_estudiante.f_cursa==cursa.id).select()
        if act:
            listaEnviados += [ins]
    return dict(proyectos = listaProyectosTutores, bienvenida=msj,listaInscripcion=listaInscripcion,enviados=listaEnviados)


def solicitud_constancia_coordinacion():
    estudianteCursa = db(db.t_cursa).select()
    print '----> ', estudianteCursa
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)

    return dict(bienvenida=msj,estudianteCursa=estudianteCursa)

def solicitud_plan_de_trabajo():
    idEstudiante = request.args[1]
    idProyecto = request.args[0]
    proyecto = db(db.t_proyecto.id==idProyecto).select()
    estudiante = db(db.t_estudiante.id==idEstudiante).select()
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    idTutor = db(db.t_universitario.f_usuario == auth.user).select().first()
    idTutorAcademico = db(db.t_tutor_academico.f_universitario == idTutor).select().first()
    listaProyectosTutores = db(db.t_proyecto_tutor.f_tutor == idTutorAcademico).select()
    listaInscripcion = []
    for proy in listaProyectosTutores:
        listaInscripcion += db(db.t_inscripcion.f_proyecto == proy.f_proyecto).select()

    listaActividades = db(db.t_actividad.f_proyecto==idProyecto).select()
    inscripcion = db(db.t_inscripcion.f_estudiante == idEstudiante).select()

    listaStringActividades = ''
    for celda in listaActividades:
        listaStringActividades += (str((celda.id))) + '/'

    return dict(proyectos = listaProyectosTutores,bienvenida=msj,listaInscripcion=listaInscripcion,
                estudiante=estudiante[0],proyecto=proyecto[0],listaActividades=listaActividades,
                inscripcion=inscripcion[0],idProyecto=idProyecto,estudianteID=idEstudiante,
                listaStringActividades=listaStringActividades)

def enviarPlanTrabajo():
    idProyecto = request.args[0]
    idEstudiante = request.args[1]
    lista = []
    listaHoras = []
    tope = (len(request.args)-3)/3
    for i in range(tope):
        if request.args[i+2+tope+1] == "1":
            lista.append(request.args[i+2])
            listaHoras.append(request.args[i+2+1+tope*2])
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    mensaje = 'Plan de Trabajo enviado'

    idCursa = db(db.t_cursa.f_estudiante==idEstudiante).select()
    for j in range(len(lista)):
        #idActividad = db(db.t_actividad.id==j).select()
        db.t_actividad_estudiante.insert(f_cursa=idCursa[0],f_actividad=lista[j],f_horas=listaHoras[j])

    return dict(idProyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje,bienvenida=msj,lista=lista)

@auth.requires_membership('Administrador')
def moderarProyectos():
    return dict(proyectos=db().select(db.t_cursa.ALL))


@auth.requires_membership('Administrador')
def proponentes():
    def my_form_processing(form):
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'

    form = SQLFORM(db.t_proponente)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'

    elif form.errors:
        response.flash = '0'

    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, proponentes=db(db.t_proponente.f_estado=="Activo").select(),message=T(response.flash))


@auth.requires_login()
def estado_manage():
    form = SQLFORM.smartgrid(db.t_estado,onupdate=auth.archive)
    return dict(form=form)


@auth.requires_membership('Administrador')
def proyectos():
    def my_form_processing(form):
        if not re.match('\d{4}', form.vars.f_codigo):
            form.errors.f_codigo = 'El formato válido del código son 4 dígitos'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_descripcion):
            form.errors.f_descripcion = 'Sólo puede contener letras'
        if not re.match('\d+', form.vars.f_version):
            form.errors.f_version = 'El formato válido de la versión son 2 dígitos'
        if form.vars.f_fechaini > form.vars.f_fechafin:
            form.errors.f_fechaini = 'La fecha final del proyecto es menor que la inicial'
            form.errors.f_fechafin = 'La fecha final del proyecto es menor que la inicial'
    form = SQLFORM(db.t_project,onupdate=auth.archive)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'

    elif form.errors:
        response.flash = '0'

    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, proyectos=db(db.t_project.f_estado_del=="Activo").select(),message=T(response.flash))

#@auth.requires(auth.has_membership(role='Administrador') or auth.has_membership(role='Proponentes'))
def propuestas():

    es_adm = 'Administrador' in auth.user_groups.values()
    es_adm = es_adm or 'Coordinador' in auth.user_groups.values() 

    if es_adm:
        propuestas = [
            {
                'id': p.f_proyecto,
                'nombre': db.t_proyecto(p.f_proyecto).f_nombre,
                'estado': p.f_estado_propuesta
            } for p in db(db.t_propuesta).select()
        ]
    else:
        propuestas = [
            {
                'id': p.f_proyecto,
                'nombre': db.t_proyecto(p.f_proyecto).f_nombre,
                'estado': p.f_estado_propuesta
            } for p in db(db.t_propuesta.f_proponente==auth.user.id).select()
        ]
    return dict(
        es_adm = es_adm,
        propuestas=propuestas,
        message=T(response.flash)
    )

def fixJSON(json,arrayNames):
    for arrayName in arrayNames:
        pattern = r"{}\[(\d+)\]\[(.*)\]".format(arrayName)
        tmp = {}
        tam_array = -1
        array = []

        for key in json:
            if arrayName+"[" in key:
                match = re.search(pattern,key)
                i = match.group(1)
                tam_array = max(tam_array, int(i))
                tmp[key] = json[key]

        if tam_array >= 0:
            array += [{} for i in range(tam_array+1)]

            for key in tmp:
                match = re.search(pattern,key)
                i = int(match.group(1))
                k = match.group(2)
                array[i][k] = tmp[key]

        json[arrayName] = array

    simpleArrayKeys = []
    for key in json:
        if '[]' in key:
            simpleArrayKeys += [key]
    for key in simpleArrayKeys:
        json[key.replace('[]','')] = json[key]
        del json[key]

    return json


def propuestasDetalles():
    proyecto_id = long (request.args[0])
    propuesta = db(db.t_propuesta.f_proyecto ==proyecto_id).select().first()
    proyecto =  db(db.t_proyecto.id == propuesta.f_proyecto).select().first()
    actividades = db(db.t_actividad.f_proyecto == proyecto_id).select()
    objetivos = db(db.t_objetivo.f_proyecto == proyecto_id).select()
    plan_operativo = db(db.t_plan_operativo.f_proyecto == proyecto_id).select()
    tutores = db(
        db.t_proyecto_tutor.f_proyecto == proyecto_id and
        db.auth_user.id==db.t_proyecto_tutor.f_tutor
    ).select()

    tutores_comunitarios = db(
        db.t_proyecto_tutor_comunitario.f_proyecto == proyecto_id and
        db.auth_user.id==db.t_proyecto_tutor_comunitario.f_tutor
    ).select()


    return dict(
        propuesta = propuesta,
        proyecto = proyecto,
        actividades = actividades,
        objetivos = objetivos,
        plan_operativo = plan_operativo,
        tutores = tutores,
        tutores_comunitarios = tutores_comunitarios
    )


def propuestasEditar():
    proyecto_id = long(request.args[0])
    redirect(URL('propuestasCrear',vars=dict(proyecto_id=proyecto_id)))

def propuestaPredecesor():

    proyectos = db(
        db.t_proyecto.id==db.t_proyecto_aprobado.f_proyecto
    ).select()

    if not proyectos:
        redirect(URL('propuestasCrear'))

    idViejo = request.vars.proyectoPredecesor

    if idViejo:
        proyectoViejo = db.t_proyecto(idViejo)
        proyecto_fields = proyectoViejo.as_dict()
        del proyecto_fields['id']
        proyecto_fields['f_continuacion'] = True
        proyecto_id = db.t_proyecto.insert(**proyecto_fields)
        db.t_propuesta.insert(f_proyecto=proyecto_id)
        redirect(URL('propuestasCrear',vars=dict(proyecto_id=proyecto_id)))

    return dict(
        proyectos=proyectos
    )


def propuestasCrear():
    response.generic_patterns = ['json']
    es_adm = 'Coordinador' in auth.user_groups.values()
    es_adm = es_adm or 'Administrador' in auth.user_groups.values()
    es_adm = es_adm or 'Administrador Dex' in auth.user_groups.values()
    es_adm = es_adm or 'Asistente' in auth.user_groups.values()

    # Obtener página actual
    pag = int(request.vars.pag) if 'pag' in request.vars else 1

    form_paginas = {
        1: [
            'f_nombre',
            'f_continuacion',
            'f_resumen',
            'f_area',
            'f_area_carrera',
            'f_relacion_planes',
            'f_estado',
            'f_fechaini',
            'f_fechafin',
            'f_sede',
            'f_proponente'
        ],
        2: [
            'f_antecedentes',
            'f_comunidad',
            'f_obj_generales',
            'f_poblacion_beneficiaria',
            'f_justificacion',
            'f_logros_sociales',
            'f_impacto_social',
            'f_evaluacion',
            'f_difusion_resultados',
            'objetivos_especificos'
        ],
        3: [
            'f_aplicacion_dir_ley',
            'f_obj_aprendizaje',
            'f_num_requeridos',
            'f_tutores',
            'f_tutores_comunitarios'
        ],
        4: [
            'f_relevancia',
            'f_originalidad',
            'f_capacidad_ejecutora',
            'f_asoc_externa',
            'f_asoc_interna',
            'f_incorporacion_estudiantes',
            'f_incorporacion_profesores',
            'f_incorporacion_empleados',
            'f_incorporacion_obreros'
        ],
        5: ['actividades'],
        6: ['plan_operativo',
            'f_observaciones',
            'f_estado_propuesta'
        ]
    }


    def propuestasGuardar(proyecto_id):
        tutores, tutores_comunitarios = [], []

        k_del = []

        for k in form.vars:
            if k not in form_paginas[pag]:
                k_del += [k]

        for k in k_del:
            del form.vars[k]


        if not form.vars.f_proponente:
            form.vars.f_proponente = auth.user.id
        if not form.vars.f_estado_propuesta:
            form.vars.f_estado_propuesta = "Incompleta"
        if not form.vars.f_nombre and proyecto_id:
            form.vars.f_nombre = db.t_proyecto(proyecto_id).f_nombre
        if not form.vars.f_observaciones and proyecto_id:
            form.vars.f_observaciones = db(db.t_propuesta.f_proyecto==proyecto_id).select().first().f_observaciones

        proyecto_fields = db.t_proyecto._filter_fields(form.vars)

        if proyecto_fields:
            if not proyecto_id:
                print("Nuevo proyecto")
                proyecto_id = db.t_proyecto.insert(**proyecto_fields)
            else:
                print("Actualizar proyecto {}".format(proyecto_id))
                print(proyecto_fields)
                db(db.t_proyecto.id==proyecto_id).update(
                    **proyecto_fields)

        form.vars.f_proyecto = proyecto_id

        propuesta = db(db.t_propuesta.f_proyecto==proyecto_id).select()
        if propuesta:
            propuesta_id = propuesta[0].id
            db(db.t_propuesta.id==propuesta_id).update(
                **db.t_propuesta._filter_fields(form.vars))
        else:
            propuesta_id = db.t_propuesta.insert(
                **db.t_propuesta._filter_fields(form.vars))

        propuesta = db.t_propuesta(propuesta_id)

        print("Proyecto",proyecto_id,"Propuesta",propuesta_id)
        tutores = form.vars.f_tutores
        tutores_comunitarios = form.vars.f_tutores_comunitarios
        print("Tutores",tutores,tutores_comunitarios)
        if propuesta_id and proyecto_id:
            if tutores:
                db(db.t_proyecto_tutor.f_proyecto==proyecto_id).delete()
                if isinstance(tutores,str):
                    tutores = [tutores]
                for tutor_id in tutores:
                    print("tutor id", tutor_id)
                    db.t_proyecto_tutor.insert(
                        f_proyecto=proyecto_id,
                        f_tutor=tutor_id
                    )

            if tutores_comunitarios:
                db(db.t_proyecto_tutor_comunitario.f_proyecto==proyecto_id).delete()
                if isinstance(tutores_comunitarios,str):
                    tutores_comunitarios = [tutores_comunitarios]
                for tutor_id in tutores_comunitarios:
                    print("tutor com id", tutor_id)
                    db.t_proyecto_tutor_comunitario.insert(
                        f_proyecto=proyecto_id,
                        f_tutor=tutor_id
                    )
            # Insertar actividades
            if request.post_vars.actividades:
                db(db.t_actividad.f_proyecto==proyecto_id).delete()
                for actividad in request.post_vars.actividades:
                    actividad['f_proyecto'] = proyecto_id
                    actividad_id = db.t_actividad.insert(**actividad)
                    print("Actividad", actividad_id)
            if request.post_vars.objetivos_especificos:
                db(db.t_objetivo.f_proyecto==proyecto_id).delete()
                for objetivo in request.post_vars.objetivos_especificos:
                    objetivo['f_proyecto'] = proyecto_id
                    objetivo_id = db.t_objetivo.insert(**objetivo)
                    print("Objetivo", objetivo_id)
            if request.post_vars.plan_operativo:
                db(db.t_plan_operativo.f_proyecto==proyecto_id).delete()
                for fila in request.post_vars.plan_operativo:
                    fila['f_proyecto'] = proyecto_id
                    fila = db.t_plan_operativo._filter_fields(fila)
                    obj = db.t_objetivo(fila['f_objetivo'])
                    act = db.t_actividad(fila['f_actividad'])
                    if obj and act:
                        fila_id = db.t_plan_operativo.insert(**fila)
                        print("Fila PO", fila_id)

        # Chequear si el proyecto fue validado
        if propuesta.f_estado_propuesta in ['Aprobado', 'Aprobado con observaciones']:
            print("Aprobando")
            codigo_area = db.t_area(db.t_proyecto(proyecto_id).f_area).f_codigo
            codigo = "{area}{proyecto_id}{ano}".format(area=codigo_area, proyecto_id=proyecto_id, ano=datetime.datetime.now().year%2000)
            db.t_proyecto_aprobado.update_or_insert(db.t_proyecto_aprobado.f_proyecto==proyecto_id,
                f_proyecto=proyecto_id,
                f_codigo=codigo,
                f_estado_proyecto='Activo'
            )
        else:
            r = db(db.t_proyecto_aprobado.f_proyecto==proyecto_id).select()
            print(r)
            if r:
                print("Desaprobando proyecto")
                db(db.t_proyecto_aprobado.f_proyecto==proyecto_id).delete()
        return dict(
            form=form,
            tutores=tutores,
            tutores_comunitarios=tutores_comunitarios,
            proyecto_id = proyecto_id,
            propuesta_id = propuesta_id,
        )

    #fix arrays
    request.post_vars = fixJSON(request.post_vars,["plan_operativo","actividades","objetivos_especificos"])
    accion = request.vars.accion
    proyecto_id = int(request.vars.proyecto_id) if 'proyecto_id' in request.vars else 0
    propuesta_id = db(db.t_propuesta.f_proyecto==proyecto_id).select().first().id if proyecto_id else 0

    actividades = request.post_vars.actividades
    obj_especificos = request.post_vars.objetivos_especificos
    plan_operativo = request.post_vars.plan_operativo

    actividades_db = db(db.t_actividad.f_proyecto==proyecto_id).select()
    obj_especificos_db = db(db.t_objetivo.f_proyecto==proyecto_id).select()
    plan_operativo_db = db(db.t_plan_operativo.f_proyecto==proyecto_id).select()

    if accion not in ['guardar','registrar']:
        if proyecto_id:
            actividades = actividades_db
            obj_especificos = obj_especificos_db
            plan_operativo = plan_operativo_db

    if pag == 6:
        # Las actividades y objetivos del plan operativo deben pertenecer al proyecto:
        db.t_plan_operativo.f_actividad.requires = IS_EMPTY_OR(IS_IN_SET([(a.id,a.f_nombre) for a in actividades_db]))
        db.t_plan_operativo.f_objetivo.requires = IS_EMPTY_OR(IS_IN_SET([(o.id,o.f_objetivo) for o in obj_especificos_db]))


    # Obtener lista de todos los tutores
    lista_tutores = [(tutor.id, '{} {}'.format(tutor.first_name,tutor.last_name)) for tutor in db(db.auth_user.f_tipo == 'Docente').select()]
    lista_tutores_comunitarios = [(tutor.id, '{} {}'.format(tutor.first_name,tutor.last_name)) for tutor in db(db.auth_user).select()]

    # Crear form
    if pag < 6:
        db.t_propuesta.f_proponente.notnull = False
        db.t_propuesta.f_proponente.requires = None

        form = SQLFORM.factory(
            db.t_proyecto,
            db.t_propuesta,
            Field(
                'f_tutores',
                requires=IS_IN_SET(lista_tutores, multiple=True)
            ),
            Field(
                'f_tutores_comunitarios',
                requires=IS_IN_SET(lista_tutores_comunitarios, multiple=True)
            ), _class="form-horizontal"
        )

        # Agregar clases de bootstrap a los input
        for inp in form.elements('input, textarea, select'):
            inp['_class'] = 'form-control'

    else:
        db.t_propuesta.f_proponente.requires = None
        db.t_plan_operativo.f_meta.requires = None
        db.t_plan_operativo.f_recursos.requires = None
        db.t_plan_operativo.f_resultados_esperados.requires = None
        db.t_plan_operativo.f_tiempo.requires = None

        form = SQLFORM.factory(db.t_plan_operativo, db.t_propuesta)
        # Agregar clases de bootstrap a los input y js
        for inp in form.elements('input, textarea, select'):
            inp['_class'] = 'form-plan form-control'

    if proyecto_id:
        print("form tutores",request.vars.f_tutores,request.vars.f_tutores_comunitarios)
        if not form.vars.f_tutores:
            tutores_proyecto = [str(t.f_tutor)
                for t in db(
                    db.t_proyecto_tutor.f_proyecto == proyecto_id
                ).select()
            ]
        else:
            tutores_proyecto = form.vars.f_tutores
        select_tutor = form.element('select', _name="f_tutores")
        if select_tutor:
            tutor_opts = select_tutor.elements('option')
            for opt in tutor_opts:
                opt['_selected'] = opt['_value'] in tutores_proyecto

        if not form.vars.f_tutores_comunitarios:
            tutores_proyecto = [str(t.f_tutor)
                for t in db(
                    db.t_proyecto_tutor_comunitario.f_proyecto == proyecto_id
                ).select()
            ]
        else:
            tutores_proyecto = form.vars.f_tutores_comunitarios
        print("Tutores com",tutores_proyecto)
        select_tutor = form.element('select',_name='f_tutores_comunitarios')
        if select_tutor:
            tutor_opts = select_tutor.elements('option')
            for opt in tutor_opts:
                opt['_selected'] = opt['_value'] in tutores_proyecto

    print("form.vars tutores", [k for k in form.vars])
    res = dict(
        form=form,
        pag= pag,
        es_adm= es_adm,
        message=T(response.flash),
        actividades=actividades,
        obj_especificos=obj_especificos,
        plan_operativo=plan_operativo,
        tutores=[],
        tutores_comunitarios=[],
        proyecto_id=proyecto_id,
        propuesta_id=propuesta_id,
        actividades_js = "[]",
        obj_especificos_js = "[]",
        plan_operativo_js = "[]",
        estado_propuesta = ""
    )
    def soft_validation(form):
        print("Validación suave")
        print(form.vars.f_nombre,proyecto_id)
        if not form.vars.f_nombre and pag == 1:
            form.errors.f_nombre = "Este campo no puede estar vacío"

        return form

    def hard_validation(form):
        print("Validación fuerte")
        proyecto = db.t_proyecto(form.vars.f_proyecto)
        propuesta = db(db.t_propuesta.f_proyecto==proyecto.id).select()[0]
        actividades = db(db.t_actividad.f_proyecto==proyecto_id).select()
        obj_especificos = db(db.t_objetivo.f_proyecto==proyecto_id).select()
        # Esta validación ocurre con el plan que se envia
        plan_operativo = request.post_vars.plan_operativo

        for f in db.t_proyecto:
            f = str(f).replace('t_proyecto.','')
            if f != 'f_continuacion' and not proyecto[f]:
                form.errors[f] = "Este campo no puede estar vacío"
        for f in db.t_propuesta:
            f = str(f).replace('t_propuesta.','')
            if not propuesta[f] and f != 'f_observaciones':
                form.errors[f] = "Este campo no puede estar vacío"
        for actividad in actividades:
            for f in db.t_actividad:
                f = str(f).replace('t_actividad.','')
                if not actividad[f] and f != 'f_requerimientos':
                    form.errors[f] = "Este campo no puede estar vacío"
        for objetivo in obj_especificos:
            for f in db.t_objetivo:
                f = str(f).replace('t_objetivo.','')
                if not objetivo[f]:
                    form.errors[f] = "Este campo no puede estar vacío"

        if not actividades:
            form.errors['actividades'] = 'No ha registrado ninguna actividad'
        if not obj_especificos:
            form.errors['objetivos'] = 'No ha registrado ningun objetivo específico'
        if not plan_operativo:
            form.errors['plan_operativo'] = 'No ha registrado el plan operativo'

        print(form.errors)
        return form

    if accion == "registrar":
        def form_validation(form):
            form = hard_validation(form)
    elif accion == "guardar":
        def form_validation(form):
            form = soft_validation(form)
    else:
        # Set form values to project record
        if proyecto_id:
            form.vars = db.t_proyecto(proyecto_id)
            if form.vars.f_fechaini:
                form.vars.f_fechaini = form.vars.f_fechaini.strftime('%d/%m/%Y')
            if form.vars.f_fechafin:
                form.vars.f_fechafin = form.vars.f_fechafin.strftime('%d/%m/%Y')
        def form_validation(form):
            form = form # función de mentira


    if form.process(onvalidation=form_validation, keepvalues=True).accepted:
        print("Paso la validacion")
        if accion == "guardar":
            res.update(propuestasGuardar(proyecto_id))
            response.flash = '1'
        elif accion == "registrar":
            res.update(propuestasGuardar(proyecto_id))
            propuesta = db.t_propuesta(res['propuesta_id'])
            print(propuesta)
            if propuesta.f_estado_propuesta == 'Incompleta':
                db(db.t_propuesta.id==res['propuesta_id']).update(
                    f_estado_propuesta = 'En espera del aval'
                )
                res['estado_propuesta'] = 'En espera del aval'
            else:
                res['estado_propuesta'] = propuesta.f_estado_propuesta 
            response.flash = '1'
    else:
        print("Fallo la validacion", form.errors)
        response.flash = '0'

    # Pasarle los datos como json para tenerlo en js
    if isinstance(actividades, gluon.dal.Rows):
        res['actividades_js'] = actividades.as_json()

    if isinstance(obj_especificos, gluon.dal.Rows):
        res['obj_especificos_js'] = obj_especificos.as_json()

    if isinstance(plan_operativo, gluon.dal.Rows):
        res['plan_operativo_js'] = plan_operativo.as_json()

    # Clasificar errores por pagina
    errors_pag = {1:{},2:{},3:{},4:{},5:{},6:{}}
    for field in form.errors:
        p = 1
        for pag in form_paginas:
            if field in form_paginas[pag]:
                p = pag
                break
        label = db.t_proyecto[field].label if field in db.t_proyecto else field
        if field in db.t_propuesta:
            label = db.t_propuesta[field].label
        if field == 'objetivos':
            label = 'Objetivos específicos'
        elif field == 'actividades':
            label = 'Actividades'
        elif field == 'plan_operativo':
            label = 'Plan Operativo'

        errors_pag[p][str(label)] = form.errors[field]

    print(errors_pag)

    res['errors'] = errors_pag
    return res

def generarPlanillaAval():
    proyecto_id = long(request.args(0))
    proyecto = db.t_proyecto(proyecto_id)
    propuesta = db(db.t_propuesta.f_proyecto==proyecto_id).select().first()
    proponente = db.auth_user(propuesta.f_proponente)
    print (proponente)
    response.headers['Content-Type'] = 'application/pdf; charset=UTF-8'
    pdf = genPDF(
        variables=dict(
            nombre='{} {}'.format(proponente.first_name,proponente.last_name),
            telefono="",
            dependencia='Coordinación de carrera'
        )
    )
    return pdf


def propuestaPDF():
    base_url='applications/SIGESC/templates_pdf/propuesta/'
    template_css='template.css'
    output="out.pdf"
    if request.post_vars:
        response.headers['Content-Type'] = 'application/pdf; charset=UTF-8'
        pdf = weasyprint.HTML(string=request.post_vars.html).render(stylesheets=[base_url+template_css]).write_pdf()
        return pdf
        
@auth.requires_membership('Administrador')
def comunidades():
    def my_form_processing(form):
        if not re.match('\d', form.vars.f_cantidadbeneficiados):
            form.errors.f_cantidadbeneficiados = 'Debe ser un número'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    form = SQLFORM(db.t_comunidad,onupdate=auth.archive)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = '1'

    elif form.errors:
        response.flash = '0'

    else:
        response.flash = 'Llene el formulario'
    return dict(form=form, comunidades=db(db.t_comunidad.f_estado_del=="Activo").select(),message=T(response.flash))


def estudianteCursa():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    form = SQLFORM(db.t_cursa,fields = ['f_estudiante','f_proyecto'])
    form.vars.f_estudiante = idEstudiante
    form.vars.f_proyecto = idProyecto

    if form.process(keepvalues=True).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    #formulario = FORM('Tu nombre:', INPUT(_name='nombre'), INPUT(_type='submit'))

    #db.define_table('kldhbvjgfe',
    #    Field('edad', requires=IS_IN_SET(['0', '1', '2'])))

    #formulario = SQLFORM(db.kldhbvjgfe)

    return dict(proyectos=db(db.t_proyecto_aprobado.id==idProyecto).select(),estudianteId=idEstudiante,idProyecto=idProyecto)

def cursa():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    estado = db(db.t_relacionestproy).select().first()
    form = SQLFORM(db.t_cursa,fields = ['f_estudiante','f_project','f_estado'])
    form.vars.f_estudiante = idEstudiante
    form.vars.f_project = idProyecto
    form.vars.f_state = estado

    if form.process(keepvalues=True).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(proyectos=db(db.t_project.id==idProyecto).select(),estudianteID=idEstudiante,idProyecto=idProyecto)

@auth.requires_membership('Administrador')
def validarProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_state="2",f_valido="Valido")
    return dict(proyecto=idProyecto)

def validacionProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_valido="Activo")
    return dict(proyecto=idProyecto)

def solicitarValidacion():
    idProyecto = long(request.args[0])
    return dict(proyecto=idProyecto)

def validacionConstanciaInicioEstudiante():
    x = long (request.args[0])
    y = long (request.args[1])
    hola="hola"

    est = db(db.t_inscripcion.f_estudiante==x).select()
    proyInscr = db(db.t_cursa.f_estudiante==x).select()
    if not proyInscr:
        mensaje=("No tiene inscrito ningún proyecto.")
    elif est[0].f_aprobacion=="Pendiente":
        mensaje=("Falta aprobación del Tutor y de la Coordinación.")
    else:
        mensaje=("Falta aprobación de la Coordinación")
    return dict(bienvenida=hola, mensaje=mensaje)

def solicitarValidacionEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    validacionRealizada = db(db.t_inscripcion.f_estudiante==idEstudiante).select()
    inscProyRealizado = db(db.t_cursa.f_estudiante==idEstudiante).select()
    if inscProyRealizado:
        if not validacionRealizada:
            db.t_inscripcion.insert(f_estudiante=idEstudiante,f_project=idProyecto,f_state="2")
            mensaje = "Solicitud de validación procesada exitosamente. Volver al Menú"
        else:
            mensaje = "Solicitud ya realizada. Volver al Menú"
    else:
        mensaje = "No tiene algun proyecto inscrito. Volver al Menú"
    return dict(proyecto=idProyecto, mensaje=mensaje)

def estudiante_plan_trabajo():
    #idProyecto = long(request.args[0])
    idEstudiante = long(request.args[0])
    listaActividades = []
    cursa = db(db.t_cursa.f_estudiante==idEstudiante).select()
    listaActividades = db(db.t_actividad_estudiante.f_cursa==cursa[0].id).select()
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    return dict(listaActividades=listaActividades,bienvenida=msj,idEstudiante=idEstudiante)

def rechazar_solicitud_tutor():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    estudiante = db(db.t_estudiante.id==idEstudiante).select().first()
    print '>>>>>> ', estudiante.f_universitario.f_usuario.first_name
    return dict(proyecto=db(db.t_proyecto.id==idProyecto).select()[0], estudiante=estudiante)

def aprobar_solicitud_coordinacion():
    #idProyecto = long(request.args[0])
    idEstudiante = long(request.args[0])
    db(db.t_cursa.f_estudiante==idEstudiante).update(f_valido='Valido')
    db(db.t_cursa.f_estudiante==idEstudiante).update(f_estado='Aprobado')
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    return dict(bienvenida=msj)

def eliminar_inscripcion():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    db(db.t_cursa.f_estudiante==idEstudiante).delete()
    db(db.t_inscripcion.f_estudiante==idEstudiante).delete()
    mensaje="Solicitud rechazada. Volver a solicitudes."

    return dict(proyecto=idProyecto, mensaje=mensaje)

def aceptarPlanTrabajo():
    estado = request.args[0]
    idEstudiante = long(request.args[1])
    if estado == 'aceptado':
        mensaje="Plan de trabajo aceptado con éxito. Volver."
        db(db.t_inscripcion.f_estudiante==idEstudiante).update(f_estado='Aprobado')
        db(db.t_cursa.f_estudiante==idEstudiante).update(f_valido='Pendiente')
    else:
        mensaje="Se ha rechazado el plan de trabajo. Volver."
        cursa = db(db.t_cursa.f_estudiante==idEstudiante).select()
        db(db.t_actividad_estudiante.f_cursa==cursa[0].id).delete()

    return dict( mensaje=mensaje,estado=estado)

def rechazarProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_state="3")
    return dict(proyecto=idProyecto)

def registrarProyectoEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    proyectoInscrito = db(db.t_cursa.f_estudiante==idEstudiante).select()
    if not proyectoInscrito:
        db.t_cursa.insert(f_estudiante=idEstudiante,f_project=idProyecto,f_state="2")
        mensaje = "Registro de proyecto exitoso. Volver al Menú"
    else:
        mensaje = "Usted ya tiene un proyecto inscrito. Volver al Menú"

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje)

def registrarProyectoComoEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    dropdown = request.args[2]
    proyectoInscrito = db(db.t_cursa.f_estudiante==idEstudiante).select()
    if not proyectoInscrito:
        db.t_cursa.insert(f_estudiante=idEstudiante,f_proyecto=idProyecto,f_estado="Pendiente")
        mensaje = "Registro de proyecto exitoso. Volver al Menú"
        db.t_inscripcion.insert(f_estudiante=idEstudiante,f_proyecto=idProyecto,f_estado="Pendiente",f_horas = dropdown)
    else:
        mensaje = "Usted ya tiene un proyecto inscrito. Volver al Menú"

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje,dropdown=dropdown)

@auth.requires_membership('Administrador')
def sede_manage():
    form = SQLFORM.smartgrid(db.t_sede,onupdate=auth.archive)
    return locals()

@auth.requires_membership('Administrador')
def comunidad_manage():
    form = SQLFORM.smartgrid(db.t_comunidad,onupdate=auth.archive)
    return locals()

@auth.requires_membership('Administrador')
def area_manage():
    form = SQLFORM.smartgrid(db.t_area,onupdate=auth.archive)
    return locals()

@auth.requires_membership('Administrador')
def sexo_manage():
    form = SQLFORM.smartgrid(db.t_sexo,onupdate=auth.archive)
    return locals()


def estudiante_manage():
    form = SQLFORM.smartgrid(db.t_estudiante.id==request.args(0))
    if form.process().accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return locals()

def proponente_manage():
    form = SQLFORM.smartgrid(db.t_proponente,onupdate=auth.archive)
    return locals()

def tutor_manage():
    form = SQLFORM.smartgrid(db.t_tutor,onupdate=auth.archive)
    return locals()

def proyecto_manage():
    form = SQLFORM.smartgrid(db.t_proyecto,onupdate=auth.archive)
    return locals()

def condicion_manage():
    form = SQLFORM.smartgrid(db.t_condicion,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def caracterisicas_manage():
    form = SQLFORM.smartgrid(db.t_caracterisicas,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def cursa_manage():
    form = SQLFORM.smartgrid(db.t_cursa,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def carrera_manage():
    form = SQLFORM.smartgrid(db.t_carrera,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def tipoprop_manage():
    form = SQLFORM.smartgrid(db.t_tipoprop,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def relacionestproy_manage():
    form = SQLFORM.smartgrid(db.t_relacionestproy,onupdate=auth.archive)
    return locals()

def sedesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_sede.id==x).select())


def estudianteProyectos():
    x = long (request.args[0])
    #return dict(rows = db(db.t_estudiante.id==x).select())
    return dict(rows = db(db.t_estudiante.id==x).select(),proyectos=db().select(db.t_project.ALL),estudianteID=x)

def estudianteInscribeProyectos():
    x = long (request.args[0])
    usuario    = db.auth_user(auth.user_id)
    msj        = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    #return dict(rows = db(db.t_estudiante.id==x).select())
    mensaje="Registro de proyecto exitoso. Volver al Menú"
    return dict(proyectos=db().select(db.t_proyecto_aprobado.ALL),estudianteId=x, mensaje=mensaje,bienvenida=msj)


def estudiantesDetalles():
    x = long (request.args[0])
    #return dict(rows = db(db.t_estudiante.id==x).select())
    return dict(rows = db(db.t_estudiante.id==x).select(),estudianteId=x)

def tutoresDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_tutor.id==x).select())


def proyectosDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_project.id==x).select())

def proyectosDetallesEstudiantes():
    x = long (request.args[0])
    return dict(rows = db(db.t_project.id==x).select())

def proponentesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_proponente.id==x).select())

def areasDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_area.id==x).select())

def comunidadesDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_comunidad.id==x).select())

def estudiantesEditar():
    def my_form_processing(form):
        if not re.match('\d{2}-\d{5}$', form.vars.f_usbid):
            form.errors.f_usbid = 'El formato válido de carnet es: 00-00000'
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_estudiante(request.args[0])
    form = SQLFORM(db.t_estudiante, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)


def estudiantesEditarPerfil():
    def my_form_processing(form):
        if not re.match('\d{2}-\d{5}$', form.vars.f_usbid):
            form.errors.f_usbid = 'El formato válido de carnet es: 00-00000'
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_estudiante(request.args[0])
    form = SQLFORM(db.t_estudiante, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)


def areasEditar():
    def my_form_processing(form):
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_area(request.args[0])
    form = SQLFORM(db.t_area, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def sedesEditar():
    def my_form_processing(form):
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_sede(request.args[0])
    form = SQLFORM(db.t_sede, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def proponentesEditar():
    def my_form_processing(form):
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_proponente(request.args[0])
    form = SQLFORM(db.t_proponente, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La sede ha sido eliminada')
    return dict(form = form)

def tutoresEditar():
    def my_form_processing(form):
        if form.vars.f_usbid:
            if not re.match('\d{2}-\d{5}$', form.vars.f_usbid) and not re.match('[a-zA-Z0-9_.+-]+', form.vars.f_usbid):
                form.errors.f_usbid = 'usbid invalido'
        if not re.match('[1-9][0-9]{0,8}$', form.vars.f_cedula):
            form.errors.f_cedula = 'El formato válido de cédula es: 1232382'
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', form.vars.f_email):
            form.errors.f_email = 'El formato válido de email es example@example.com'
        if not re.match('\d{7,13}', form.vars.f_telefono):
            form.errors.f_telefono = 'El formato válido de telefono es 08002023223'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_tutor(request.args[0])
    form = SQLFORM(db.t_tutor, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('El tutor ha sido eliminado')
    return dict(form = form)

# TODO: vista
@auth.requires(auth.has_membership(role='Administrador') or auth.has_membership(role='Coordinador'))
def propuestasEliminar():
    propuesta_id = long (request.args[0])
    record = db(db.t_propuesta.id==propuesta_id and db.t_propuesta.f_proponente==auth.user.id)
    record.delete()

def proyectosEditar():
    def my_form_processing(form):
        if not re.match('\d{4}', form.vars.f_codigo):
            form.errors.f_codigo = 'El formato válido del código son 4 dígitos'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_descripcion):
            form.errors.f_descripcion = 'Sólo puede contener letras'
        if not re.match('\d+', form.vars.f_version):
            form.errors.f_version = 'El formato válido de la versión son 2 dígitos'
        if form.vars.f_fechaini > form.vars.f_fechafin:
            form.errors.f_fechaini = 'La fecha final del proyecto es menor que la inicial'
            form.errors.f_fechafin = 'La fecha final del proyecto es menor que la inicial'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_project(request.args[0])
    form = SQLFORM(db.t_project, record, deletable = True)
    if form.process(onvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('El proyecto ha sido eliminada')
    return dict(form = form)

def comunidadesEditar():
    def my_form_processing(form):
        if not re.match('\d', form.vars.f_cantidadbeneficiados):
            form.errors.f_cantidadbeneficiados = 'Debe ser un número'
        if not re.match('[A-ZÁÉÍÓÚÑ]|[A-ZÁÉÍÓÚÑa]|[a-zñáéíóúäëïöü]*$', form.vars.f_nombre):
            form.errors.f_nombre = 'Sólo puede contener letras'
    x = long (request.args[0])
    #return dict(rows = db(db.t_sede.id==x).select())
    record = db.t_comunidad(request.args[0])
    form = SQLFORM(db.t_comunidad, record, deletable = True)
    if form.process(nvalidation=my_form_processing).accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    elif not record:
        return dict('La comunidad ha sido eliminada')
    return dict(form = form)

def generarPdfConstanciaInicio():
    x = long (request.args[0])
    y = long (request.args[1])

    #est = db(db.t_estudiante.id==x).select()
    carr = 'Ing. de Computación'
    # sed = db(est[0].f_sede==db.t_sede.id).select()
    # genero = db(est[0].f_sexo==db.t_sexo.id).select()
    #
    # proy = db(db.t_proyecto.id==y).select()
    # tut = db(proy[0].f_tutor==db.t_tutor.id).select()
    # comu = db(proy[0].f_comunidad==db.t_comunidad.id).select()

    USBID = '09-11086'
    Nombre = 'Luis Edgardo'
    Apellido = 'Colorado Sánchez'
    Cedula = '21203424'
    tlf = '0424-3218265'
    direccion = 'Maracay'

    Carrera = 'Ing. de la Computación'

    Sede = 'Sartenejas'

    Sexo = 'Masculino'

    codigo_pr = 'PS1115'
    nombre_pr = 'Soñar Despierto'
    descripcion_pr = 'Descrpción de Servicio Comunitario'
    area_pr = 'Salud y Ambiente'
    estado_pr = 'Activo'
    fecha_ini = '12/01/2016'
    fecha_fin = '26/08/2016'
    #version_pr = proy[0].f_version
    proponente_pr = 'Nombre proponente'

    tutor_pr_nombre = 'Nombres Tutor'
    tutor_pr_apellido = 'Apellidos Tutor'

    comunidad_pr = 'Santa Fe'
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
    u = inch/10.0

    inscProyRealizado = db(db.t_cursa.f_estudiante==x).select()

    if inscProyRealizado and inscProyRealizado[0].f_valido=="Valido":

        title = '<font size=10><b><u>__CONSTANCIA DE INICIO DE SERVICIO COMUNITARIO__</u></b></font>'
        heading = "Datos del estudiante:"


        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='titles', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='logos', alignment=TA_LEFT))
        tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
        doc = SimpleDocTemplate(tmpfilename,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=2,bottomMargin=18)
        logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/img/logo_dex.png')
        salto = '<br />\n'
        #linea = '__________________________________________________________________________________'

        story = []
        im = Image(logo,width=90, height=60)
        im.hAlign = 'LEFT'
        story.append(im)
        story.append(Paragraph(salto,styles["Normal"]))
        story.append(Paragraph(title,styles["titles"]))
        #story.append(Paragraph(linea,styles["Normal"]))
        story.append(Spacer(1,2*u))
        story.append(Paragraph(escape('Perído:___________________________________ Año: ______________'),styles["Normal"]))
        story.append(Paragraph(escape(heading),styles["Heading2"]))
        story.append(Paragraph(escape('Carné: ' + str(USBID)),styles["Normal"]))
        story.append(Paragraph(escape('Carrera: ' + str(Carrera)),styles["Normal"]))
        story.append(Paragraph(escape('Nombres: ' + str(Nombre)),styles["Normal"]))
        story.append(Paragraph(escape('Apellidos: ' + str(Apellido)),styles["Normal"]))
        story.append(Paragraph(escape('Cédula: ' + str(Cedula)),styles["Normal"]))
        story.append(Paragraph(escape('Teléfono: ' + str(tlf)),styles["Normal"]))
        story.append(Paragraph(escape('Dirección: ' + str(direccion)),styles["Normal"]))
        story.append(Paragraph(escape('Sede: ' + str(Sede)),styles["Normal"]))
        story.append(Paragraph(escape('Sexo: ' + str(Sexo)),styles["Normal"]))

        story.append(Paragraph(salto,styles["Normal"]))
        story.append(Paragraph(escape('Información del proyecto: '),styles["Heading2"]))
        story.append(Paragraph(escape('Nombre del proyecto: ' + str(nombre_pr)),styles["Normal"]))
        story.append(Paragraph(escape('Código del proyecto: ' + str(codigo_pr)),styles["Normal"]))
        story.append(Paragraph(escape('Tutor académico: ' +str(tutor_pr_nombre) + ' ' + str(tutor_pr_apellido)),styles["Normal"]))
        story.append(Paragraph(escape('Comunidad: ' + str(comunidad_pr)),styles["Normal"]))


        story.append(Spacer(1,2*inch))
        doc.build(story)
        data = open(tmpfilename,"rb").read()
        os.unlink(tmpfilename)
        response.headers['Content-Type']='application/pdf'
        return data
    else:
        redirect(URL(f='validacionConstanciaInicioEstudiante', args=[x,y]))
        return mensaje

def myFirstPage(canvas, doc):
 canvas.saveState()
 canvas.setFont('Times-Bold',16)
 #canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, "EJEMPLO")
 canvas.setFont('Times-Roman',9)
 canvas.drawString(inch, 0.75 * inch, "Página / %s" % "info")
 canvas.restoreState()

def myLaterPages(canvas, doc):
 canvas.saveState()
 canvas.setFont('Times-Roman',9)
 canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
 canvas.restoreState()

def generarPdfConstanciaInscripcion():
    x = long (request.args[0])
    y = long (request.args[1])

    est = db(db.t_estudiante.id==x).select()
    #carr = db(est[0].f_carrera==db.t_carrera.id).select()
    sed = db(est[0].f_sede==db.t_sede.id).select()
    genero = db(est[0].f_sexo==db.t_sexo.id).select()

    proy = db(db.t_project.id==y).select()
    tut = db(proy[0].f_tutor==db.t_tutor.id).select()
    comu = db(proy[0].f_comunidad==db.t_comunidad.id).select()

    USBID = est[0].f_usbid
    Nombre = est[0].f_nombre
    Apellido = est[0].f_apellido
    Cedula = est[0].f_cedula
    tlf = est[0].f_telefono
    direccion = est[0].f_direccion

    Carrera = carr[0].f_codigo

    Sede = sed[0].f_nombre

    Sexo = genero[0].f_tipo

    codigo_pr = proy[0].f_codigo
    nombre_pr = proy[0].f_nombre
    descripcion_pr = proy[0].f_descripcion
    area_pr = proy[0].f_area
    estado_pr = proy[0].f_estado
    fecha_ini = proy[0].f_fechaini
    fecha_fin = proy[0].f_fechafin
    version_pr = proy[0].f_version
    proponente_pr = proy[0].f_proponente

    tutor_pr_nombre = tut[0].f_nombre
    tutor_pr_apellido = tut[0].f_apellido

    comunidad_pr = comu[0].f_nombre

    # Rutas para la creación del PDF
    template_html='template_inscripcion_PDF/template.html'
    template_css='template_inscripcion_PDF/template.css'
    output="template_inscripcion_PDF/out1.pdf"
    # Datos del usuario a insertar en la constancia
    periodo = 'Enero-marzo'
    anio = '2016'
    usbid = USBID
    carrera = Carrera
    nombre = Nombre
    apellido = Apellido
    ci = Cedula
    telf_fijo = '0243-272 39 62'
    telf_movil = est[0].f_telefono
    email = est[0].f_email
    direccion = direccion

    nombreProyecto = nombre_pr
    codigo = codigo_pr
    ciudadBenef = proy[0].f_comunidad
    repComunidad = 'Padre Juan'
    ciRepComuni = '9.987.552'

    direccionRepComunidad= 'Santa Fe Valle Arriba'
    telfOficRepComunidad= '0212-555 55 55'
    celRepComunidad= '0416-555 55 55'
    emailRepComunidad= 'juan@gmail.com'
    tutorAca = tut[0].f_nombre
    ciTutorAca = tut[0].f_cedula
    dependencia = 'CFCG'
    telfOficTutorAca = tut[0].f_telefono
    celTutorAca = '555 55 55'
    emailTutorAca = tut[0].f_email
    direccionOrgDesSoc = 'Santa Fe Valle Arriba'
    telfOficOrgDesSoc = '0000 555 55 55'
    celOrgDesSoc = '555 55 55'
    emailOrgDesSoc = 'comunidad@yahoo.com'

    listaActividad = db(db.t_actividad_estudiante.id==x).select()

    # Diccionario con los valores que se insertaran en la vista
    variables={'periodo':periodo,'anio':anio,'usbid':usbid,'carrera':carrera,'nombre':nombre,'apellido':apellido,
					'ci':ci,'telf_fijo':telf_fijo,'telf_movil':telf_movil,'email':email,'direccion':direccion,
					'nombreProyecto':nombreProyecto,'codigo':codigo,'ciudadBenef':ciudadBenef,'repComunidad':repComunidad,
					'ciRepComuni':ciRepComuni, 'direccionRepComunidad':direccionRepComunidad,'telfOficRepComunidad':telfOficRepComunidad,
					'celRepComunidad':celRepComunidad,'emailRepComunidad':emailRepComunidad,'tutorAca':tutorAca,
					'ciTutorAca':ciTutorAca,'dependencia':dependencia,'telfOficTutorAca':telfOficTutorAca,'celTutorAca':celTutorAca,
					'emailTutorAca':emailTutorAca,'direccionOrgDesSoc':direccionOrgDesSoc,'telfOficOrgDesSoc':telfOficOrgDesSoc,
					'celOrgDesSoc':celOrgDesSoc,'emailOrgDesSoc':emailOrgDesSoc}
    # Construye el PDF en un archivo temporal
    html_template = open(template_html)
    html_content = html_template.read().format(**variables)
    open('tmp.html','w').write(html_content)
    # Crea el PDF y elimina el temporal
    subprocess.Popen(["weasyprint","tmp.html",output,"-s",template_css]).wait()
    os.remove("tmp.html")
    # Se abre el PDF creado y se muestra en la URL para que pueda descargarlo el usuario
    data = open(output,"rb").read()
    # Se elimina el PDF creado para que no ocupe espacio
    os.unlink(output)
    response.headers['Content-Type']='application/pdf'
    # Muestra el PDF en la URL
    return data


