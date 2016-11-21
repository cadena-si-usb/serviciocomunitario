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
from reportlab.pdfgen import canvas
from gluon.tools   import Crud
from uuid import uuid4
from cgi  import escape
from usbutils import get_ldap_data, random_key
from cgi import escape 
import time
from gluon.tools import web2py_uuid

### required - do no delete
crud = Crud(db)

# Actualizar el correo de envio de correos del sistema.
correoEnvio=db().select(db.t_correo_envios.ALL)[0]
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = correoEnvio.f_email
mail.settings.login = correoEnvio.f_email+":"+correoEnvio.f_clave

def representsInt(s):
    try:
        sint = int(s)
        return True if sint > 0 else False
    except ValueError:
        return False
'''
class Actividad:
    def __init__(self,f_nombre,f_resumen,f_alumnos,f_requerimientos):
        self.f_nombre = f_nombre
        self.f_resumen = f_resumen
        self.f_alumnos = f_alumnos
        self.f_requerimientos = f_requerimientos
'''
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

def index():
    if auth.is_logged_in():
        redirect(URL("home"))

    return dict(host=request.env.http_host,rolesUsuario=[])

def verificarCorreo():
    registration_key = request.args(0)
    print registration_key
    usuario = db(db.auth_user.registration_key==registration_key).select().first()
    print usuario
    if not usuario:
        redirect(URL('default', 'index'))

    db(db.auth_user.id == usuario.id).update(registration_key="",f_confirmado=True)

    return dict(picture=pictureUsuario(),msj="Se ha verificado su correo exitosamente.",bienvenida='Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name))


def verifiqueCorreo():
    usuario = db.auth_user(auth.user_id)
    return dict(picture=pictureUsuario(),bienvenida='Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name),msj="Se le ha enviado un correo para verificar su registro.")

def recuperarCuenta():
    return dict()

def buscarCuenta():
    inputText=request.vars.input
    accion=request.vars.accion

    if accion=="usuario":
        usuario=db(db.auth_user.username==inputText).select().first()     
    else:
        usuario=db(db.auth_user.email==inputText).select().first()
    
    if not(usuario):
        return "No"

    registration_key = web2py_uuid()
    db(db.auth_user.id == usuario.id).update(reset_password_key=registration_key)

    mail.send(to=usuario.email, subject='Cambiar contraseña', \
    message='Hola %s,\n\n' %usuario.first_name + \
    'Para cambiar su contraseña, por favor click al siguiente enlace:\n' + \
    '%s\n\n' %URL('default', 'cambiarClave/%s' %registration_key, host=request.env.http_host))

    return "Si"  

def cambiarClave():
    registration_key = request.args(0)
    usuario = db(db.auth_user.reset_password_key==registration_key).select().first()
    if not(usuario):
        redirect(URL('default', 'index'))        
    return dict(usuario=usuario)

def claveCambiada():
    clave=request.vars.input
    idUsuario=long(request.vars.idUsuario)
    db(db.auth_user.id == idUsuario).update(reset_password_key="")
    db(db.auth_user.id == idUsuario).update(password=clave)
    return "Si"

def claveCambiadaExitosamente():
    return dict()

def correoRecuperarCuenta():
    return dict()

def login_sin_usbid():
    user=request.vars.user
    pasword=request.vars.pasword
    
    login=auth.login_bare(user,pasword)
    if login:
        return "Si"
    return "No"

def error():
    return dict()

def esRIF(usuario):
    if re.match('^[JGVEP][-][0-9]{8}[-][0-9]{1}$',usuario):
        return True

    return False

@auth.requires_login()
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
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://secure.dst.usb.ve/validate?ticket="+\
              request.vars.getfirst('ticket') +\
              "&service=http%3A%2F%2F"+ request.env.http_host +"%2FSIGESC%2Fdefault%2Flogin_cas"
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
            estado = db(db.t_estado.f_nombre=='Distrito Capital').select()[0]
            a = db.auth_user.insert(
                first_name = us.get('first_name'),
                last_name  = us.get('last_name'),
                username   = usbid,
                password   = db.auth_user.password.validate(clave)[0],
                email      = us.get('email'),
                f_cedula     = us['cedula'],
                f_telefono   = us['phone'],
                f_tipo       = us['tipo'],
                f_estado=estado.id,
                f_confirmado=True
            )

            user = db(db.auth_user.username==usbid).select()[0]
            sede = db(db.t_sede.f_nombre=='Sartenejas').select()[0]
            print us
            db.t_universitario.insert(
                f_usbid   = usbid,
                f_key     = clave,
                f_usuario = user.id,
                f_sede=sede.id
            )

            userUniv = db(db.t_universitario.f_usbid==usbid).select()[0]
            carrera = db(db.t_carrera.f_nombre=='Ingeniería de la Computación').select()[0]
            print carrera

            if (us['tipo'] == "Pregrado") or (us['tipo'] == "Postgrado"):
               # Si es estudiante insertar en su tabla
                db.t_estudiante.insert(
                    f_universitario = userUniv.id,
                    f_carrera       = carrera.id,
                    f_horas=0
                )
            elif us['tipo'] == "Docente":
                # En caso de ser docente, agregar dpto.
                db.t_docente.insert(
                    f_universitario = userUniv.id,
                    f_departamento  = us['dpto']
                )

        else:
            userUniv = db(db.t_universitario.f_usbid==usbid).select()[0]
            clave    = userUniv.f_key


        # Al finalizar login o registro, redireccionamos a home
        auth.login_bare(usbid,clave)
        redirect('home')
    return None

def pictureUsuario():
    if db.auth_user(auth.user_id)['f_foto']:
        return URL('default', 'download', args=db.auth_user(auth.user_id)['f_foto'])
    else:
        return URL('static', 'img/user.png')


def obtenerListaRolesUsuario():
    usuario = db.auth_user(auth.user_id)
    rolesUsuario=[]
    
    if usuario['f_tipo'] in ["Pregrado","Postgrado"]:
        rolesUsuario.append("Estudiante")

    for rol in db(db.auth_membership.user_id==auth.user_id).select():
        rolesUsuario.append(db(db.auth_group.id==rol.group_id).select()[0].role)

    esTutorAcademico= db(db.t_proyecto_tutor.f_tutor==auth.user_id).select().first() !=None

    esTutorComunitario = db(db.t_proyecto_tutor_comunitario.f_tutor==auth.user_id).select().first() !=None

    if esTutorAcademico:
        rolesUsuario.append("Tutor Academico")

    if esTutorComunitario:
        rolesUsuario.append("Tutor Comunitario")

    return rolesUsuario

# Contolador de redireccion de usuarios
@auth.requires_login()
def home():
    usuario = db.auth_user(auth.user_id)
    
    if not(usuario.f_confirmado):
        registration_key = web2py_uuid()
        db(db.auth_user.id == auth.user_id).update(registration_key=registration_key)
        
        mail.send(to=usuario.email, subject='Confirma tu registro', \
          message='Hola %s, Bienvenido al Sistema de Gestion de Servicio Comunitario!\n\n' %usuario.first_name + \
            'Para finalizar su registro, por favor click al siguiente enlace:\n' + \
            '%s\n\n' %URL('default', 'verificarCorreo/%s' %registration_key, host=request.env.http_host))

        redirect(URL("verifiqueCorreo"))
    
    msj      = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)

    return dict(rolesUsuario=obtenerListaRolesUsuario(),picture=pictureUsuario(),bienvenida=msj, host=request.env.http_host)

# @ticket_in_session
#def mostrar_credencial():
#    return dict()

def registro():
    return dict()

def registro_persona_natural():
    return dict(form=auth.register(next=URL('home')))

def registro_persona_juridica():
    return dict(form2=auth.register(next=URL('home')))

"""
@auth.requires_login()
def perfil():
    rolesUsuario=[]
    usuario = db.auth_user(auth.user_id)
    for rol in db(db.auth_membership.user_id==auth.user_id).select():
        rolesUsuario.append(db(db.auth_group.id==rol.group_id).select()[0].role)
    
    if request.args(0) == 'search':
        if not ("Administrador" in rolesUsuerio):
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
        sede = univ.t_docente.select()[0]['f_sede']
        dpto = univ.t_docente.select()[0]['f_departamento']
    elif db.auth_user(auth.user_id)['f_tipo'] in ["Pregrado","Postgrado"]:
        sede    = univ.t_estudiante.select()[0]['f_sede']
        carrera = univ.t_estudiante.select()[0]['f_carrera']
    user = db.auth_user(auth.user_id)
    msj      = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    return dict(form=user,picture=picture,bienvenida=msj,dpto=dpto, sede=sede,carrera=carrera)
"""

@auth.requires_login()
def editar_perfil():
    usuario = db.auth_user(auth.user_id)
    msj      = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    db.auth_user.username.writable=False
    db.auth_user.f_foto.writable  =True
    email=usuario.email
    form = auth.profile()
    form.element('input', _type = 'submit')['_class'] = 'btn btn-primary'
    form.element('input', _type = 'submit')['_value'] = 'Actualizar perfil'

    estudiante = None
    docente    = None

    sedes=[]     

    for sede in db(db.t_sede).select():
        sedes.append(sede.f_nombre)

    carreras=[]     

    for carrera in db(db.t_carrera).select():
        carreras.append(carrera.f_nombre)

    
    if auth.user['f_tipo'] in ["Pregrado","Postgrado"]:
        universitario=db.auth_user(auth.user_id)['t_universitario'].select()[0]
        estudiante = db.auth_user(auth.user_id)['t_universitario'].select()[0]['t_estudiante'].select()[0]
        form[0].insert(-1, TR(LABEL(T('Carrera:')),
                             SELECT(carreras,
                                value=estudiante.f_carrera.f_nombre,
                                _name='carrera')))
        form[0].insert(-1, TR(LABEL(T('Sede:')),
                             SELECT(sedes,
                                value=universitario.f_sede.f_nombre,
                                _name='sede'
                            )))
    elif auth.user['f_tipo']== "Docente":
        universitario=db.auth_user(auth.user_id)['t_universitario'].select()[0]
        docente = db.auth_user(auth.user_id)['t_universitario'].select()[0]['t_docente'].select()[0]
        form[0].insert(-1, TR(LABEL(T('Departamento:')),
                             TD(docente['f_departamento']
                            )))
        form[0].insert(-1, TR(LABEL(T('Sede:')),
                             SELECT(sedes,
                                value=universitario.f_sede.f_nombre,
                                _name='sede'
                            )))

    if form.accepts(request.vars, session, formname='form1'):
        response.flash = 'form accepted'

        if estudiante:

            idCarrera = db(db.t_carrera.f_nombre==form.vars['carrera']).select()[0].id
            idSede = db(db.t_sede.f_nombre==form.vars['sede']).select()[0].id

            f_univ = db.auth_user(auth.user_id)['t_universitario'].select()[0]

            db(db.t_estudiante.f_universitario == f_univ['id']).update(
                f_carrera=idCarrera)

            db(db.t_universitario.id==f_univ.id).update(
                f_sede=idSede)

        elif docente:

            idSede = db(db.t_sede.f_nombre==form.vars['sede']).select()[0].id
            f_univ = db.auth_user(auth.user_id)['t_universitario'].select()[0]

            #db(db.t_docente.f_universitario == f_univ['id']).update(
            #    f_departamento=form.vars['departamento'])

            db(db.t_universitario.id==f_univ.id).update(
                f_sede=idSede)
        print form.vars['email']
        if (email!=form.vars['email']):
            db(db.auth_user.id == usuario.id).update(
                f_confirmado=False)    


    elif form.errors:
        response.flash = 'form has errors'


    return dict(rolesUsuario=obtenerListaRolesUsuario(),form=form,bienvenida=msj,picture=pictureUsuario(),contrasena=auth.change_password())

'''
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
'''

def usuarios():
    return dict(registrados=db(db.auth_user.id!=auth.user_id).select())

def usuarios_detalles():
    idUsuario=request.args(0) or request.vars.id

    if db.auth_user(idUsuario)['f_foto']:
        picture = URL('default', 'download', args=db.auth_user(idUsuario)['f_foto'])
    else:
        picture = URL('static', 'img/user.png')

    sede,dpto,carrera = "","",""
    univ = db.t_universitario(f_usuario=idUsuario)

    if db.auth_user(idUsuario)['f_tipo'] == "Docente":
        sede = univ.t_docente.select()[0]['f_sede']
        dpto = univ.t_docente.select()[0]['f_departamento']
    elif db.auth_user(idUsuario)['f_tipo'] in ["Pregrado","Postgrado"]:
        sede    = univ.t_estudiante.select()[0]['f_sede']
        carrera = univ.t_estudiante.select()[0]['f_carrera']

    tabla= db(db.auth_user.id==idUsuario).select()[0]
    return dict(form=tabla,picture=picture,dpto=dpto, sede=sede,carrera=carrera)

def eliminar_usuario():
    idUsuario=request.vars.id
    db(db.auth_user.id==idUsuario).delete()
    return "Si"

def sedes_admin():
    return dict(sedes=db().select(db.t_sede.ALL))

def comunidades_admin():
    return dict(comunidades=db().select(db.t_comunidad.ALL))

def areas_carreras_admin():
    return dict(areas_carreras=db().select(db.t_area_carrera.ALL))

def carreras_admin():
    return dict(carreras=db().select(db.t_carrera.ALL))

def proyectos_admin():
    return dict(proyectos=db().select(db.t_proyecto_aprobado.ALL))

def roles_admin():
    return dict(usuarios=db().select(db.auth_user.ALL))

def agregar_rol_admin():
    idUsuario=long(request.vars.id)
    usuario=db(db.auth_user.id==idUsuario).select().first()
    return dict(usuario=usuario,roles=db().select(db.auth_group.ALL))

def agregar_rol_admin_listo():
    idUsuario=long(request.vars.idUsuario)
    idRol=long(request.vars.idRol)
    existeRelacion=db((db.auth_membership.user_id==idUsuario) & (db.auth_membership.group_id==idRol)).select().first() !=None
    if existeRelacion:
        return "*El usuario ya posee ese Rol."     

    db.auth_membership.insert(user_id=idUsuario,group_id=idRol)
    relacion=db((db.auth_membership.user_id==idUsuario) & (db.auth_membership.group_id==idRol)).select().first()
    
    return relacion.id

def eliminar_rol_admin():
    idRelacion=long(request.vars.idRelacion)
    db(db.auth_membership.id==idRelacion).delete()
    return "Si"

'''
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
'''
'''
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
        db.t_cursa.insert(f_estudiante=idEstudiante,f_proyecto=idProyecto,f_estado="Pendiente")
        mensaje = "Registro de proyecto exitoso. Volver a proyectos"
    else:
        mensaje = "Usted ya tiene un proyecto inscrito. Volver a proyectos"

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje)
'''
"""def registrarProyectoComoEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    proyectoInscrito = db(db.t_cursa.f_estudiante==idEstudiante).select()
    if not proyectoInscrito:
        db.t_cursa.insert(f_estudiante=idEstudiante,f_project=idProyecto,f_state="2")
        mensaje = "Registro de proyecto exitoso. Volver a proyectos"
    else:
        mensaje = "Usted ya tiene un proyecto inscrito. Volver a proyectos"

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje)
"""
'''
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
'''
'''def estudianteInscribeProyectos():
    x = long (request.args[0])
    return dict(rows = db(db.t_estudiante.id==x).select(),proyectos=db().select(db.t_proyecto.ALL),estudianteID=x)
'''
'''
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
'''

# Reportes
def reportes():
    msj= 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    return dict(rolesUsuario=obtenerListaRolesUsuario(),
        msj = msj,
        comunidades=db().select(db.t_comunidad.ALL),
        areas=db().select(db.t_area.ALL),
        carreras=db().select(db.t_carrera.ALL),
        docentes=db((db.auth_user.f_tipo=="Docente")&(db.auth_user.id==db.t_universitario.f_usuario)&(db.t_docente.f_universitario==db.t_universitario.id)).select()
        )

def home_reportes():
    return dict() 

def obtenerEstudiantesInscritos(idProyecto):
    return db(db.t_cursa.f_proyecto==idProyecto).count()

def obtenerEstudiantesRetirados(idProyecto):
    return db((db.t_cursa.f_proyecto==idProyecto)&(db.t_cursa.f_estado!="Retirado")).count()

def obtenerEstudiantesCulminados(idProyecto):
    return db((db.t_cursa.f_proyecto==idProyecto)&(db.t_cursa.f_estado!="Culminado")).count()

def buscar_proyectos_reportes():
    # Formateo Fecha Inicial
    fecha_inicial = request.vars.fecha_inicial
    fecha_inicial=fecha_inicial.split("/")
    fecha_inicial=datetime.date(int(fecha_inicial[2]),int(fecha_inicial[1]),int(fecha_inicial[0]))
    
    # Formateo Fecha Final
    fecha_final = request.vars.fecha_final
    fecha_final=fecha_final.split("/")
    fecha_final=datetime.date(int(fecha_final[2]),int(fecha_final[1]),int(fecha_final[0]))
    
    codigo = request.vars.codigo
    tipo = request.vars.tipo
    idComunidad = request.vars.idComunidad
    idArea = request.vars.idArea
    estado = request.vars.estado

    #Faltan estos filtros
    culminado = request.vars.culminado
    evaluado = request.vars.evaluado
    organizacion = request.vars.organizacion
    #----

    consulta=db.t_proyecto_aprobado.f_proyecto== db.t_proyecto.id

    #consulta&=db.t_proyecto.f_fechafin>=fecha_inicial
    consulta&=(((db.t_proyecto.f_fechafin>=fecha_inicial)&(db.t_proyecto.f_fechafin<=fecha_final))|((db.t_proyecto.f_fechaini>=fecha_inicial)&(db.t_proyecto.f_fechaini<=fecha_final)))

    if idArea!="All":
        print "area"
        consulta&= db.t_proyecto.f_area==long(idArea)
    if codigo!="":
        print "codigo"
        consulta&= db.t_proyecto_aprobado.f_codigo==codigo  
    if tipo!="All":
        print "tipo"
        if tipo=="Continuo":
            consulta&= db.t_proyecto.f_continuacion==True   
        else:
            consulta&= db.t_proyecto.f_continuacion==False
    if idComunidad!="All":
        print "comunidad"
        consulta&= db.t_proyecto.f_comunidad==long(idComunidad)   
    if estado!="All":
        print "estado"
        consulta&= db.t_proyecto_aprobado.f_estado_proyecto==estado 

    return dict(obtenerEstudiantesInscritos=obtenerEstudiantesInscritos,proyectos=db(consulta).select(),cambiarFormatoFecha=cambiarFormatoFecha)

def buscar_estudiantes_reportes():
    # Formateo Fecha Inicial
    fecha_inicial = request.vars.fecha_inicial
    fecha_inicial=fecha_inicial.split("/")
    fecha_inicial=datetime.date(int(fecha_inicial[2]),int(fecha_inicial[1]),int(fecha_inicial[0]))
    
    # Formateo Fecha Final
    fecha_final = request.vars.fecha_final
    fecha_final=fecha_final.split("/")
    fecha_final=datetime.date(int(fecha_final[2]),int(fecha_final[1]),int(fecha_final[0]))
    
    operacion = request.vars.operacion
    carnet = request.vars.carnet
    idCarrera = request.vars.idCarrera
    sexo = request.vars.sexo

    consulta=db.t_cursa.id== db.t_inscripcion.f_cursa
    consulta&=db.t_cursa.f_estado!="Pendiente"
    consulta&=db.t_cursa.f_proyecto==db.t_proyecto_aprobado.f_proyecto
    consulta&=db.t_cursa.f_estudiante== db.t_estudiante.id
    consulta&=db.t_estudiante.f_universitario==db.t_universitario.id
    consulta&=db.t_universitario.f_usuario==db.auth_user.id

    if (operacion=="All"):
        print "all"
        consulta&=(((db.t_cursa.f_fecha>=fecha_inicial)&(db.t_cursa.f_fecha<=fecha_final))|((db.t_inscripcion.created_on>=fecha_inicial)&(db.t_inscripcion.created_on<=fecha_final)))
    else:
        if (operacion=="Inscripciones"):
            print "inscripciones"
            consulta&=((db.t_inscripcion.created_on>=fecha_inicial)&(db.t_inscripcion.created_on<=fecha_final))
        else:
            print "no inscripciones"
            consulta&=((db.t_cursa.f_fecha>=fecha_inicial)&(db.t_cursa.f_fecha<=fecha_final))
            if (operacion=="Culminaciones"):
                consulta&=db.t_cursa.f_estado=='Culminado'
            if (operacion=="Retiros"):    
                consulta&=db.t_cursa.f_estado=='Retirado' 

    consulta&=db.t_cursa.f_actual==False
    consulta&=db.t_inscripcion.f_actual==False

    if idCarrera!="All":
        print "idCarrera"
        consulta&= db.t_estudiante.f_carrera==long(idCarrera)
    if carnet!="":
        print "carnet"
        consulta&= db.t_universitario.f_usbid==carnet  
    if sexo!="All":
        print "sexo"
        consulta&=db.auth_user.f_sexo==sexo


    return dict(obtenerHorasConfirmadasDeEstudiante=obtenerHorasConfirmadasDeEstudiante,operacion=operacion,registros=db(consulta).select(),cambiarFormatoFecha=cambiarFormatoFecha)

def buscar_tutores_reportes():
    idUsuario=request.vars.idUsuario
    consulta=db.t_proyecto_tutor.f_proyecto==db.t_proyecto.id
    consulta&=db.t_proyecto.id==db.t_proyecto_aprobado.f_proyecto
    consulta&=db.t_proyecto_tutor.f_tutor==db.auth_user.id
    consulta&=db.t_universitario.f_usuario==db.auth_user.id
    consulta&=db.t_universitario.id==db.t_docente.f_universitario

    if idUsuario!="All":
        consulta&=db.t_proyecto_tutor.f_tutor==idUsuario
    if request.vars.departamento!="All":
        docenteid=request.vars.departamento
        departamento=db(db.t_docente.id==docenteid).select().first().f_departamento
        consulta&=db.t_docente.f_departamento==departamento

    return dict(obtenerEstudiantesCulminados=obtenerEstudiantesCulminados,
        obtenerEstudiantesRetirados=obtenerEstudiantesRetirados,
        obtenerEstudiantesInscritos=obtenerEstudiantesInscritos,
        registros=db(consulta).select(),
        cambiarFormatoFecha=cambiarFormatoFecha)


# Coordinador
def coordinador():
    msj= 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    return dict(rolesUsuario=obtenerListaRolesUsuario(),msj = msj)

def home_coord():
    return dict() 

def obtenerInscripcion(idCursa):
    return db(db.t_inscripcion.f_cursa==idCursa).select().first()

def coord_solicitud_inscripcion():
    estudianteCursa = db(db.t_cursa.f_actual==True).select()
    return dict(estudianteCursa=estudianteCursa,obtenerInscripcion=obtenerInscripcion,cambiarFormatoFecha=cambiarFormatoFecha)

def coord_aprobar_solicitud_estudiante():
    idCursa = long(request.vars.idCursa)
    proyecto_cursa=db(db.t_cursa.id==idCursa)
    proyecto_cursa.update(f_valido='Valido')
    proyecto_cursa.update(f_estado='Aprobado')
    return "Si"

def coord_retiros_estudiantes():
    estudianteCursa = db((db.t_cursa.f_actual==True)&(db.t_cursa.f_estado=='Retirado')).select()
    return dict(estudianteCursa=estudianteCursa,obtenerInscripcion=obtenerInscripcion,cambiarFormatoFecha=cambiarFormatoFecha)

def coord_aprobar_retiro_estudiante():
    idCursa = long(request.vars.idCursa)
    proyecto_cursa=db(db.t_cursa.id==idCursa)
    proyecto_cursa.update(f_actual=False)
    proyecto_cursa.update(f_fecha=datetime.datetime.today())
    
    inscripcion=db(db.t_inscripcion.f_cursa==idCursa)
    inscripcion.update(f_actual=False)
    return "Si"

def obtenerHorasConfirmadasDeEstudiante(idCursa):
    horasConfirmadas=0
    actividadesConfirmadas=db((db.t_actividad_estudiante.f_cursa==idCursa) & (db.t_actividad_estudiante.f_confirmada==True)).select()
    for actividad in actividadesConfirmadas:
        horasConfirmadas=horasConfirmadas+ int(actividad.f_horas)

    return horasConfirmadas

def coord_culminaciones_estudiantes():
    estudianteCursa = db((db.t_cursa.f_actual==True)&(db.t_cursa.f_estado=='Culminado')).select()
    return dict(cambiarFormatoFecha=cambiarFormatoFecha,obtenerInscripcion=obtenerInscripcion,estudianteCursa=estudianteCursa,obtenerHorasConfirmadasDeEstudiante=obtenerHorasConfirmadasDeEstudiante)

def coord_aprobar_culminacion_estudiante():
    idCursa = long(request.vars.idCursa)
    cursa=db(db.t_cursa.id==idCursa).select().first()
    proyecto_cursa=db(db.t_cursa.id==idCursa)
    proyecto_cursa.update(f_actual=False)
    proyecto_cursa.update(f_fecha=datetime.datetime.today())

    # Agregar horas confirmadas
    estudiante_actual=db(db.t_estudiante.id==cursa.f_estudiante).select().first()
    estudiante=db(db.t_estudiante.id==cursa.f_estudiante)
    estudiante.update(f_horas=obtenerHorasConfirmadasDeEstudiante(cursa.id)+int(estudiante_actual.f_horas))

    inscripcion=db(db.t_inscripcion.f_cursa==idCursa)
    inscripcion.update(f_actual=False)
    return "Si"

# Administrador
def administrador():
    msj= 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    return dict(rolesUsuario=obtenerListaRolesUsuario(),msj = msj)

def home_admin():
    return dict() 

def admin_usuarios_detalles():
    idUsuario=long(request.vars.id)
    if db.auth_user(idUsuario)['f_foto']:
        picture = URL('default', 'download', args=db.auth_user(idUsuario)['f_foto'])
    else:
        picture = URL('static', 'img/user.png')

    sede,dpto,carrera = "","",""
    tabla= db.auth_user(idUsuario)
    univ = db(db.t_universitario.f_usuario==idUsuario).select().first()
    if (tabla['f_tipo'] == "Docente"):
        sede = univ.f_sede.f_nombre
        dpto = db(db.t_docente.f_universitario==univ).select().first().f_departamento
    if (tabla['f_tipo'] in ["Pregrado","Postgrado"]):
        sede    = univ.f_sede.f_nombre
        carrera = db(db.t_estudiante.f_universitario==univ).select().first().f_carrera
    
    return dict(form=tabla,picture=picture,dpto=dpto, sede=sede,carrera=carrera) 

def admin_proyectos_detalles():
    idProyectoAprobado=long(request.vars.id)
    proyectoAprobado=db(db.t_proyecto_aprobado.id==idProyectoAprobado).select().first()
    proyecto=db(db.t_proyecto.id==proyectoAprobado.f_proyecto.id).select().first()
    idproyecto=proyecto.id
    actividades = db(db.t_actividad.f_proyecto == idproyecto).select()
    objetivos = db(db.t_objetivo.f_proyecto == idproyecto).select()
    plan_operativo = db(db.t_plan_operativo.f_proyecto == idproyecto).select()
    idestudiante=None
    tutores = db((db.t_proyecto_tutor.f_proyecto == idproyecto) &(db.auth_user.id==db.t_proyecto_tutor.f_tutor)).select()

    tutores_comunitarios = db((db.t_proyecto_tutor_comunitario.f_proyecto == idproyecto) &(db.auth_user.id==db.t_proyecto_tutor_comunitario.f_tutor)).select()

    sedes = db(db.t_proyecto_sede.f_proyecto == idproyecto).select()


    return dict(proyectoAprobado=proyectoAprobado,
        proyecto=proyecto,
        actividades=actividades,
        objetivos=objetivos,
        plan_operativo=plan_operativo,
        tutores=tutores,
        tutores_comunitarios=tutores_comunitarios,
        sedes=sedes,
        idestudiante=idestudiante) 

'''
@auth.requires_login()
def admin_perfil():
    rolesUsuario=[]

    for rol in db(db.auth_membership.user_id==auth.user_id).select():
        rolesUsuario.append(db(db.auth_group.id==rol.group_id).select()[0].role)
    
    if request.args(0) == 'search':
        if not ("Administrador" in rolesUsuerio):
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
        sede = univ.t_docente.select()[0]['f_sede']
        dpto = univ.t_docente.select()[0]['f_departamento']
    elif db.auth_user(auth.user_id)['f_tipo'] in ["Pregrado","Postgrado"]:
        sede    = univ.t_estudiante.select()[0]['f_sede']
        carrera = univ.t_estudiante.select()[0]['f_carrera']
    user = db.auth_user(auth.user_id)
    return dict(form=user,picture=picture,dpto=dpto, sede=sede,carrera=carrera)


@auth.requires_login()
def admin_editar_perfil():
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
        docente = db.auth_user(auth.user_id)['t_universitario'].select()[0]['t_docente'].select()[0]
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
            db(db.t_docente.f_universitario == f_univ['id']).update(
                f_sede=form.vars['sede'],
                f_departamento=form.vars['departamento'])
    elif form.errors:
        response.flash = 'form has errors'


    return dict(form=form,contrasena=auth.change_password())

'''
def areas_admin():
    areas=db().select(db.t_area.ALL)
    return dict(areas=areas)

def nueva_area():
    return dict()

def nueva_sede():
    return dict()

def nueva_comunidad():
    return dict()

def nueva_area_carrera():
    return dict()

def nueva_carrera():
    return dict(areas_carreras=db().select(db.t_area_carrera.ALL))

def eliminar_area():
    idArea=request.vars.id
    db(db.t_area.id==idArea).delete()
    return "Si"

def eliminar_proyecto_aprobado():
    idProyectoAprobado=request.vars.id
    db(db.t_proyecto_aprobado.id==idProyectoAprobado).delete()
    return "Si"

def eliminar_sede():
    idSede=request.vars.id
    db(db.t_sede.id==idSede).delete()
    return "Si"

def eliminar_comunidad():
    id=request.vars.id
    db(db.t_comunidad.id==id).delete()
    return "Si"

def eliminar_area_carrera():
    idArea=request.vars.id
    db(db.t_area_carrera.id==idArea).delete()
    return "Si"

def eliminar_carrera():
    idCarrera=request.vars.id
    db(db.t_carrera.id==idCarrera).delete()
    return "Si"

def admin_modificar_area():
    idArea=request.vars.id
    area=db(db.t_area.id==idArea).select().first()  
    return dict(form=area)

def admin_modificar_proyecto_aprobado():
    idProyectoAprobado=request.vars.id
    proyecto_aprobado=db(db.t_proyecto_aprobado.id==idProyectoAprobado).select().first()  
    return dict(form=proyecto_aprobado)

def admin_modificar_sede():
    idSede=request.vars.id
    sede=db(db.t_sede.id==idSede).select().first()  
    return dict(form=sede)

def admin_modificar_comunidad():
    idComunidad=request.vars.id
    comunidad=db(db.t_comunidad.id==idComunidad).select().first()  
    return dict(form=comunidad)


def admin_modificar_area_carrera():
    idArea=request.vars.id
    areaCarrera=db(db.t_area_carrera.id==idArea).select().first()  
    return dict(form=areaCarrera)

def admin_modificar_carrera():
    idCarrera=request.vars.id
    carrera=db(db.t_carrera.id==idCarrera).select().first()  
    return dict(form=carrera,areas_carreras=db().select(db.t_area_carrera.ALL))

def nueva_area_admin_modificada():
    idArea=int(request.vars.id)
    nombreArea=request.vars.nombre
    descripcionArea=request.vars.descripcion
    codigoArea=request.vars.codigo
    estadoArea=request.vars.estado

    if ((nombreArea == '') and (codigoArea == '')):
        return "*Codigo y nombre de area de proyecto vacios."
        
    if (nombreArea == ''):
        return "*Nombre de area de proyecto vacio."
    if (codigoArea == ''):
        return "*Campo codigo vacio."


    existeNombreArea=db((db.t_area.f_nombre.upper()==nombreArea.upper()) & (db.t_area.id!=idArea)).select().first() !=None
    existeCodigoArea=db((db.t_area.f_codigo==codigoArea) & (db.t_area.id!=idArea)).select().first() !=None

    if existeNombreArea and existeCodigoArea:
        return "*Nombre y Codigo de Area ya existentes."
    if existeCodigoArea:
        return "*Codigo de Area ya existente."
    if existeNombreArea:
        return "*Nombre de Area ya existente."

    area=db(db.t_area.id==idArea)
    area.update(f_nombre=nombreArea,
                f_descripcion=descripcionArea,
                f_codigo=codigoArea,
                f_estado=estadoArea)

    return "Exito"

def nueva_carrera_admin_modificada():
    idCarrera=int(request.vars.id)
    nombreCarrera=request.vars.nombre
    idArea=int(request.vars.area)
    codigoCarrera=request.vars.codigo
    estadoCarrera=request.vars.estado

    if ((nombreCarrera == '') and (codigoCarrera == '')):
        return "*Codigo y nombre de la carrera vacios."
    if (nombreCarrera == ''):
        return "*Nombre de la carrera vacio."
    if (codigoCarrera == ''):
        return "*Campo codigo vacio."

    existeNombreCarrera=db((db.t_carrera.f_nombre.upper()==nombreCarrera.upper()) & (db.t_carrera.id!=idCarrera)).select().first() !=None
    existeCodigoCarrera=db((db.t_carrera.f_codigo==codigoCarrera) & (db.t_carrera.id!=idCarrera)).select().first() !=None

    if existeNombreCarrera and existeCodigoCarrera:
        return "*Nombre y Codigo de la carrera ya existentes."
    if existeCodigoCarrera:
        return "*Codigo de carrera ya existente."
    if existeNombreCarrera:
        return "*Nombre de carrera ya existente."

    carrera=db(db.t_carrera.id==idCarrera)
    carrera.update(f_nombre=nombreCarrera,
                f_area_carrera=idArea,
                f_codigo=codigoCarrera,
                f_estado=estadoCarrera)

    return "Exito"

def admin_proyecto_modificado():
    idProyectoAprobado=int(request.vars.id)
    codigoProyecto=request.vars.codigo
    estadoProyecto=request.vars.estado

    if (codigoProyecto == ''):
        return "*Campo codigo vacio."

    existeCodigoProyecto=db((db.t_proyecto_aprobado.f_codigo.upper()==codigoProyecto.upper()) & (db.t_proyecto_aprobado.id!=idProyectoAprobado)).select().first() !=None

    if existeCodigoProyecto:
        return "*Codigo de Proyecto ya existente."

    proyecto=db(db.t_proyecto_aprobado.id==idProyectoAprobado)
    proyecto.update(f_codigo=codigoProyecto,f_estado_proyecto=estadoProyecto)

    return "Exito"

def nueva_sede_admin_modificada():
    idSede=int(request.vars.id)
    nombreSede=request.vars.nombre
    estadoSede=request.vars.estado
        
    if (nombreSede == ''):
        return "*Nombre de Sede vacio."

    existeNombreSede=db((db.t_sede.f_nombre.upper()==nombreSede.upper()) & (db.t_sede.id!=idSede)).select().first() !=None

    if existeNombreSede:
        return "*Nombre de Sede ya existente."

    sede=db(db.t_sede.id==idSede)
    sede.update(f_nombre=nombreSede,
                f_estado=estadoSede)

    return "Exito"

def nueva_comunidad_admin_modificada():
    idComunidad=int(request.vars.id)
    nombreComunidad=request.vars.nombre
    estadoComunidad=request.vars.estado
        
    if (nombreComunidad == ''):
        return "*Nombre de comunidad vacio."

    existeNombreComunidad=db((db.t_comunidad.f_nombre.upper()==nombreComunidad.upper()) & (db.t_comunidad.id!=idComunidad)).select().first() !=None

    if existeNombreComunidad:
        return "*Nombre de comunidad ya existente."

    comunidad=db(db.t_comunidad.id==idComunidad)
    comunidad.update(f_nombre=nombreComunidad,
                f_estado=estadoComunidad)

    return "Exito"

def nueva_area_carrera_admin_modificada():
    idArea=int(request.vars.id)
    nombreArea=request.vars.nombre
    estadoArea=request.vars.estado
        
    if (nombreArea == ''):
        return "*Nombre de Area de Carrera vacio."

    existeNombreAreaCarrera=db((db.t_area_carrera.f_nombre.upper()==nombreArea.upper()) & (db.t_area_carrera.id!=idArea)).select().first() !=None

    if existeNombreAreaCarrera:
        return "*Nombre de Area de Carrera ya existente."

    areaCarrera=db(db.t_area_carrera.id==idArea)
    areaCarrera.update(f_nombre=nombreArea,
                f_estado=estadoArea)

    return "Exito"

def admin_areas_detalles():
    idArea=long(request.vars.id)
    area=db(db.t_area.id==idArea).select().first()

    return dict(form=area)

def nueva_area_admin():
    nombre=request.vars.nombre
    codigo=request.vars.codigo
    descripcion=request.vars.descripcion
    estado=request.vars.estado

    if ((nombre == '') and (codigo == '')):
        return "*Codigo y nombre de area de proyecto vacios."

    if (nombre == ''):
        return "*Nombre de area de proyecto vacio."
    if (codigo == ''):
        return "*Campo codigo vacio."


    existeNombreArea=db(db.t_area.f_nombre.upper()==nombre.upper()).select().first() !=None
    existeCodigoArea=db(db.t_area.f_codigo==codigo).select().first() !=None

    if existeNombreArea and existeCodigoArea:
        return "*Nombre y Codigo de Area ya existentes."
    if existeCodigoArea:
        return "*Codigo de Area ya existente."
    if existeNombreArea:
        return "*Nombre de Area ya existente."

    db.t_area.insert(
        f_nombre=nombre,
        f_codigo=codigo,
        f_descripcion=descripcion,
        f_estado=estado
    )

    area=db(db.t_area.f_codigo==codigo).select().first()

    return area.id

def nueva_sede_admin():
    nombre=request.vars.nombre
    estado=request.vars.estado

    if (nombre == ''):
        return "*Nombre de la Sede vacio."

    existeNombreSede=db(db.t_sede.f_nombre.upper()==nombre.upper()).select().first() !=None

    if existeNombreSede:
        return "*Nombre de Sede ya existente."

    db.t_sede.insert(
        f_nombre=nombre,
        f_estado=estado
    )

    sede=db(db.t_sede.f_nombre==nombre).select().first()
    return sede.id

def nueva_comunidad_admin():
    nombre=request.vars.nombre
    estado=request.vars.estado

    if (nombre == ''):
        return "*Nombre de la comunidad vacio."

    existeNombreComunidad=db(db.t_comunidad.f_nombre.upper()==nombre.upper()).select().first() !=None

    if existeNombreComunidad:
        return "*Nombre de comunidad ya existente."

    db.t_comunidad.insert(
        f_nombre=nombre,
        f_estado=estado
    )

    comunidad=db(db.t_comunidad.f_nombre==nombre).select().first()
    return comunidad.id

def nueva_area_carrera_admin():
    nombre=request.vars.nombre
    estado=request.vars.estado

    if (nombre == ''):
        return "*Nombre de la area de la carrera vacio."

    existeNombreAreaCarrera=db(db.t_area_carrera.f_nombre.upper()==nombre.upper()).select().first() !=None

    if existeNombreAreaCarrera:
        return "*Nombre de area de carrera ya existente."

    db.t_area_carrera.insert(
        f_nombre=nombre,
        f_estado=estado
    )

    areaCarrera=db(db.t_area_carrera.f_nombre==nombre).select().first()
    return areaCarrera.id

def nueva_carrera_admin():
    nombre=request.vars.nombre
    estado=request.vars.estado
    codigo=request.vars.codigo
    idarea=request.vars.area

    if ((codigo == '')and(nombre == '')):
        return "*Nombre y Codigo de la Carrera vacios."
    if (nombre == ''):
        return "*Nombre de la Carrera vacio."
    if (codigo == ''):
        return "*Codigo de la Carrera vacio."

    existeNombreCarrera=db(db.t_carrera.f_nombre.upper()==nombre.upper()).select().first() !=None
    existeCodigoCarrera=db(db.t_carrera.f_codigo.upper()==codigo.upper()).select().first() !=None

    if existeNombreCarrera:
        return "*Nombre de la Carrera ya existente."
    if existeCodigoCarrera:
        return "*Codigo de la Carrera ya existente."

    db.t_carrera.insert(
        f_codigo=codigo,
        f_nombre=nombre,
        f_area_carrera=idarea,
        f_estado=estado
    )

    carrera=db(db.t_carrera.f_nombre==nombre).select().first()
    return carrera.id

'''
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
'''

def cambiarFormatoFecha(fecha):
    return fecha.strftime("%d/%m/%Y")

def actualizar_fechas_tope():
    fechas_tope=db().select(db.t_fechas_tope.ALL)
    return dict(fechas_tope=fechas_tope,cambiarFormatoFecha=cambiarFormatoFecha)

def actualizar_correo_de_envios():
    correo=db().select(db.t_correo_envios.ALL)[0]
    return dict(correo=correo)

def cambiar_correo_de_envios():
    idCorreo = long(request.vars.id)
    email = request.vars.email
    clave=request.vars.clave
    correo=db(db.t_correo_envios.id==idCorreo)
    correo.update(f_email=email,f_clave=clave)
    mail.settings.sender = email
    mail.settings.login = email+":"+clave
    return "Si"

def cambiar_fecha_tope():
    idFecha = long(request.vars.id)
    fecha_inicial = request.vars.fecha_inicial.split("/")
    fecha_inicial=fecha_inicial[2]+"-"+fecha_inicial[1]+"-"+fecha_inicial[0]
    fecha_final=request.vars.fecha_final.split("/")
    fecha_final=fecha_final[2]+"-"+fecha_final[1]+"-"+fecha_final[0]
    fechaTope=db(db.t_fechas_tope.id==idFecha)
    fechaTope.update(f_fecha_inicial=fecha_inicial,f_fecha_final=fecha_final)
    return "Si"

# fin administrador
def proyectos_tutor_comunitario():
    tutor     = db.auth_user(auth.user_id)
    msj       = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    proyectos = db(db.t_proyecto_tutor_comunitario.f_tutor==tutor).select()
    return dict(bienvenida=msj,proyectos=proyectos)

def proyectos_tutor_academico():
    tutor     = db.auth_user(auth.user_id)

    msj       = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    proyectos = db(db.t_proyecto_tutor.f_tutor==tutor).select()
    return dict(bienvenida=msj,proyectos=proyectos)

def proyecto_tutor_academico():
    tutor       = db.auth_user(auth.user_id)
    id_proy     = request.vars.proy
    proyecto    = db(db.t_proyecto.id==id_proy).select().first()
    msj         = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    estudiantes = db((db.t_estudiante.id==db.t_cursa.f_estudiante)&(db.t_cursa.f_proyecto==id_proy)&(db.t_cursa.f_actual==True)).select()
    return dict(estudiantes=estudiantes,bienvenida=msj,proyecto=proyecto)

def proyecto_tutor_comunitario():
    tutor       = db.auth_user(auth.user_id)
    id_proy     = request.vars.proy
    proyecto    = db(db.t_proyecto.id==id_proy).select().first()
    msj         = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    estudiantes = db((db.t_estudiante.id==db.t_cursa.f_estudiante)&(db.t_cursa.f_proyecto==id_proy)&(db.t_cursa.f_actual==True)).select()
    return dict(estudiantes=estudiantes,bienvenida=msj,proyecto=proyecto)

#AJAX confirmacion de actividad
def confirmar_actividad():
    actividad = db(db.t_actividad_estudiante.id==request.vars.id).update(f_confirmada=True)
    return ""

def bitacora_de_estudiante():
    tutor      = db.auth_user(auth.user_id)
    msj        = 'Bienvenid@ %s %s' % (tutor.first_name,tutor.last_name)
    id_est     = request.vars.est
    proyecto   = db((db.t_cursa.f_estudiante==id_est) & (db.t_cursa.f_proyecto==request.vars.proy) &(db.t_cursa.f_actual==True)).select().last()
    estudiante = db(db.t_estudiante.id==id_est).select().first()
    bitacora   = db((db.t_actividad_estudiante.f_cursa==proyecto) & (db.t_actividad_estudiante.f_realizada==True)).select()
    print bitacora
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
        proyecto = db(db.t_cursa.f_estudiante==estudiante).select().last() 
        proy = proyecto.f_proyecto
    except:
        proyecto = None
        proy = None

    print proyecto.f_estado
    #Tutores
    tutores_comunitarios =db(db.t_proyecto_tutor_comunitario.f_proyecto==proy).select()

    tutores = db(db.t_proyecto_tutor.f_proyecto==proy).select()

    #Actividades
    actividades = db(db.t_actividad_estudiante.f_cursa==proyecto.id).select()

    #PlanesOperativosPorActividad
    planoperativo = []
    horas_realizadas = 0

    for row in actividades:
        planoperativo.append(db(db.t_plan_operativo.f_actividad==row.f_actividad).select())
        if row.f_confirmada:
            horas_realizadas += int(row.f_horas)

    if request.env.request_method =='POST':
        if form.process(onvalidation=my_form_processing, keepvalues=True).accepted:
            response.flash = 'form accepted'
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill out the form'
    return dict(rows=usuario, bienvenida=msj,estudianteId=estudiante.id, tutores=tutores,
                proyecto=proyecto, actividades=actividades, planoperativo=planoperativo,
                horas_realizadas=horas_realizadas, tutores_comunitarios=tutores_comunitarios)

def vista_estudiante():
    usuario    = db.auth_user(auth.user_id)
    msj        = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt       = db(db.t_universitario.f_usuario==usuario).select().first()
    estudiante = db(db.t_estudiante.f_universitario==estt).select().first()

    try:
        cursa = db((db.t_cursa.f_estudiante==estudiante.id)& (db.t_cursa.f_valido=="Invalido")).select().last()
        if not cursa:
            cursa = db((db.t_cursa.f_estudiante==estudiante.id)& (db.t_cursa.f_valido=="Valido")).select().last()
            cursa = cursa
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
            if acti.f_confirmada:
                horas_realizadas += int(acti.f_horas)
    pInscrito = 'vacio'
    pActividad = 'no'
    tutor = None
    proyectoInscrito = db((db.t_cursa.f_estudiante==estudiante)).select().last()
    #cursa = db(db.t_cursa.f_estudiante==estudiante).select()
    actividad = None
    if proyecto:
        actividad = db(db.t_actividad_estudiante.f_cursa==proyectoInscrito).select()
    if actividad:
        pActividad = 'si'
    if proyectoInscrito:
        pInscrito = 'proyecto inscrito'
        tutor = db(db.t_inscripcion.f_estudiante==estudiante).select().last()
        aprob_tutor = tutor.f_estado
        aprob_coord = cursa.f_valido
    else:
        aprob_tutor = 'tutorVacio'
        aprob_coord = 'coordVacio'
    print pActividad
    estudianteId = estudiante.id
    return dict(usuario=usuario,estudianteId=estudianteId,horas_confirmadas=horas_realizadas,estudiante=estudiante,
                bienvenida=msj,proyecto=proyecto,pInscrito=pInscrito,pActividad=pActividad,
                aprob_tutor=aprob_tutor,aprob_coord=aprob_coord,cursa=cursa,tutor=tutor,estt=estt)

def retirar_proyecto():
    x = long (request.args[0])
    usuario = db.auth_user(auth.user_id)
    msj     = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt    = db(db.t_universitario.f_usuario==usuario).select().first()
    usuario = db(db.t_estudiante.f_universitario==estt).select().first()

    proyecto  = db((db.t_cursa.f_estudiante==usuario) & (db.t_cursa.f_proyecto==x) & (db.t_cursa.f_actual==True)).select().last()
    
    error=None
    form = SQLFORM.factory(Field('f_informe','upload',uploadfolder=request.folder+'static/pdfs',label=T('Informe'),requires = [IS_LENGTH(maxsize=2097152),IS_UPLOAD_FILENAME(extension='pdf')]))
    if form.process(session=None, formname='test').accepted:
        if form.vars.f_informe:
            print form.vars.f_informe
            db((db.t_cursa.f_estudiante==usuario)&(db.t_cursa.f_proyecto==x)& (db.t_cursa.f_actual==True)).update(f_informe=form.vars.f_informe)
            db((db.t_cursa.f_estudiante==usuario)&(db.t_cursa.f_proyecto==x)& (db.t_cursa.f_actual==True)).update(f_estado='Retirado',f_fecha=datetime.datetime.today())
            return redirect(URL('retirar_proyecto',args=[x]))
        print('form accepted')
    elif form.errors:
        error = "El informe debe estar en formato pdf y no ser mayor a 2Mb"
        print('form has errors')
    else:
        print('please fill the form')

    return dict(estudiante=usuario, bienvenida=msj,proyecto=proyecto)

'''def retiro():
    x = long(request.args[1])
    retiro = db((db.t_cursa.f_estudiante==long(request.args[0])) & (db.t_cursa.f_estado=='Aprobado')).update(f_estado='Retirado',f_fecha=datetime.datetime.today())
    redirect(URL('retirar_proyecto',args=[x]))
    return ""
'''

def culminar_proyecto():
    x = long (request.args[0])
    usuario  = db.auth_user(auth.user_id)
    msj      = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    estt = db(db.t_universitario.f_usuario==usuario).select().first()
    usuario = db(db.t_estudiante.f_universitario==estt).select().first()

    proyecto = db((db.t_cursa.f_estudiante==usuario)&(db.t_cursa.f_proyecto==x)& (db.t_cursa.f_actual==True)).select().last()
    countProyectos=len(db((db.t_cursa.f_estudiante==usuario)&(db.t_cursa.f_estado=="Culminado")).select())

    error = None

    form = SQLFORM.factory(Field('f_informe','upload',uploadfolder=request.folder+'static/pdfs',label=T('Informe'),requires = [IS_LENGTH(maxsize=2097152),IS_UPLOAD_FILENAME(extension='pdf')]))
    if form.process(session=None, formname='test').accepted:
        if form.vars.f_informe:
            db((db.t_cursa.f_estudiante==usuario)&(db.t_cursa.f_proyecto==x)& (db.t_cursa.f_actual==True)).update(f_informe=form.vars.f_informe)
            db((db.t_cursa.f_estudiante==usuario)&(db.t_cursa.f_proyecto==x)& (db.t_cursa.f_actual==True)).update(f_estado="Culminado",f_fecha=datetime.datetime.today())
            return redirect(URL('culminar_proyecto',args=[x]))
        print('form accepted')
    elif form.errors:
        error = "El informe debe estar en formato pdf y no ser mayor a 2Mb"
        print('form has errors')
    else:
        print('please fill the form')

    # Buscamos todas las actividades de todos los proyectos que alguna vez realizó el estudiante.
    horas_realizadas = 0
    todas_actividades = db((db.t_actividad_estudiante.f_cursa==proyecto) & (db.t_actividad_estudiante.f_confirmada==True)).select()
    print todas_actividades
    for acti in todas_actividades:
        if acti.f_realizada:
            horas_realizadas += int(acti.f_horas)
        
    if (countProyectos>1):
        horasDeber=30
    else:
        horasDeber=40
    return dict(horasDeber=horasDeber,horas=horas_realizadas,error=error, estudiante=usuario, bienvenida=msj,proyecto=proyecto)


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
    comunidad_pr  = proy.f_comunidad.f_nombre
    
    retiro = db((db.t_cursa.f_estudiante == x) & (db.t_cursa.f_estado == 'Retirado')).select().last()
    fechaRet = retiro.f_fecha
    idCursa = retiro.id
    
    linea2 = '__________________________________'
    USBID     = est.f_universitario.f_usbid
    Nombre    = est.f_universitario.f_usuario.first_name
    Correo = est.f_universitario.f_usuario.email
    Apellido  = est.f_universitario.f_usuario.last_name
    Carrera   = est.f_carrera.f_nombre
    proyectoAprobado=db(db.t_proyecto_aprobado.f_proyecto==proy.id).select().first()
    codigo_pr = proyectoAprobado.f_codigo
    nombre_pr = proy.f_nombre
    descripcion_pr = proy.f_resumen
    
    horas_realizadas = obtenerHorasConfirmadasDeEstudiante(idCursa)       

    title = "CERTIFICACION DE RETIRO DE SERVICIO COMUNITARIO"

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='test',fontName='Times-Roman',spaceBefore=5,spaceAfter=2,alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='titulo',fontName='Times-Bold',spaceBefore=20,fontSize=12,spaceAfter=16,alignment=TA_CENTER))
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))

    story = []
    story.append(NextPageTemplate('Culminacion'))
    story.append(Paragraph(escape(title),styles["titulo"]))
    story.append(Paragraph(escape('FECHA DE RETIRO: ' + str(fechaRet)),styles["test"]))
    story.append(Paragraph(escape('APELLIDO Y NOMBRE DEL ESTUDIANTE: ' + str(Apellido) +', '+ str(Nombre)),styles["test"]))
    story.append(Paragraph(escape('CARNET: ' + str(USBID)),styles["test"]))
    story.append(Paragraph(escape('CORREO ELECTRÓNICO: ' + str(Correo)),styles["test"]))
    story.append(Paragraph(escape('CARRERA: ' + str(Carrera)),styles["test"]))
    story.append(Paragraph(escape('TITULO DEL PROYECTO DE SERVICIO COMUNITARIO: ' + str(nombre_pr)),styles["test"]))
    story.append(Paragraph(escape('CÓDIGO: ' + str(codigo_pr)),styles["test"]))
    story.append(Paragraph(escape('COMUNIDAD BENEFICIADA: ' +str(comunidad_pr)),styles["test"]))
    story.append(Paragraph(escape('TUTOR(ES) ACADÉMICO(S): '),styles["Heading4"]))
    for proyectoTutorAca in db(db.t_proyecto_tutor).select():
        if (proyectoTutorAca.f_proyecto==proy.id):
            tutor = db(db.auth_user.id==proyectoTutorAca.f_tutor).select()[0]
            tutor_pr_nombre = tutor.first_name
            tutor_pr_apellido = tutor.last_name
            cedulaAca = tutor.f_cedula
            telefonoAca = tutor.f_telefono
            correoAca = tutor.email
            story.append(Paragraph(escape('NOMBRE Y APELLIDO: ' +str(tutor_pr_nombre) + ' ' + str(tutor_pr_apellido)),styles["test"]))
            story.append(Paragraph(escape('CÉDULA DE IDENTIDAD: ' +str(cedulaAca)),styles["test"]))
            story.append(Paragraph(escape('TELÉFONO: ' +str(telefonoAca)),styles["test"]))
            story.append(Paragraph(escape('CORREO ELECTRÓNICO: ' +str(correoAca)),styles["test"]))
            story.append(Paragraph(escape(str(linea2)),styles["test"]))
    
    story.append(Paragraph(escape('CERTIFICO QUE EL ESTUDIANTE CUMPLIÓ CON LOS OBJETIVOS PLANTEADOS DURANTE EL \
        DESARROLLO DEL PROYECTO DE SERVICIO COMUNITARIO POR UN LAPSO DE '+ str(horas_realizadas)+' HORAS, COMO LO ESTABLECE EL \
        REGLAMENTO DE FORMACIÓN COMPLEMENTARIA PROFESIONAL EN SU SECCIÓN 2 DEL SERVICIO COMUNITARIO EN SU ARTÍCULO 24 \
        PARÁGRAFO EVALUACIÓN.'),styles["test"]))
    story.append(Paragraph(escape('CONFORME:'),styles["test"]))
    story.append(Spacer(0,0.6*inch))
    t = Table([
        ['_'*30,'_'*30],
        ['Firma del Tutor ACADÉMICO\n(Firma y Sello del Dpto. Adscripción)', 'Validación de CFCG o COORDEXT\n(Firma y Sello )']
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
    comunidad_pr  = proy.f_comunidad.f_nombre
    
    culminacion = db((db.t_cursa.f_estudiante == x) & (db.t_cursa.f_estado == 'Culminado')).select().last()
    fechaCul = culminacion.f_fecha
    idCursa = culminacion.id
    
    linea2 = '__________________________________'
    USBID     = est.f_universitario.f_usbid
    Nombre    = est.f_universitario.f_usuario.first_name
    Correo = est.f_universitario.f_usuario.email
    Apellido  = est.f_universitario.f_usuario.last_name
    Carrera   = est.f_carrera.f_nombre
    proyectoAprobado=db(db.t_proyecto_aprobado.f_proyecto==proy.id).select().first()
    codigo_pr = proyectoAprobado.f_codigo
    nombre_pr = proy.f_nombre
    descripcion_pr = proy.f_resumen
    
    horas_realizadas = obtenerHorasConfirmadasDeEstudiante(idCursa)

    title = "CERTIFICACION DE CUMPLIMIENTO DE SERVICIO COMUNITARIO"

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='test',fontName='Times-Roman',spaceBefore=5,spaceAfter=2,alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='titulo',fontName='Times-Bold',spaceBefore=20,fontSize=12,spaceAfter=16,alignment=TA_CENTER))
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))

    story = []
    story.append(NextPageTemplate('Culminacion'))
    story.append(Paragraph(escape(title),styles["titulo"]))
    story.append(Paragraph(escape('FECHA DE CULMINACION: ' + str(fechaCul)),styles["test"]))
    story.append(Paragraph(escape('APELLIDO Y NOMBRE DEL ESTUDIANTE: ' + str(Apellido) +', '+ str(Nombre)),styles["test"]))
    story.append(Paragraph(escape('CARNET: ' + str(USBID)),styles["test"]))
    story.append(Paragraph(escape('CORREO ELECTRÓNICO: ' + str(Correo)),styles["test"]))
    story.append(Paragraph(escape('CARRERA: ' + str(Carrera)),styles["test"]))
    story.append(Paragraph(escape('TITULO DEL PROYECTO DE SERVICIO COMUNITARIO: ' + str(nombre_pr)),styles["test"]))
    story.append(Paragraph(escape('CÓDIGO: ' + str(codigo_pr)),styles["test"]))
    story.append(Paragraph(escape('COMUNIDAD BENEFICIADA: ' +str(comunidad_pr)),styles["test"]))
    story.append(Paragraph(escape('TUTOR(ES) ACADÉMICO(S): '),styles["Heading4"]))
    for proyectoTutorAca in db(db.t_proyecto_tutor).select():
        if (proyectoTutorAca.f_proyecto==proy.id):
            tutor = db(db.auth_user.id==proyectoTutorAca.f_tutor).select()[0]
            tutor_pr_nombre = tutor.first_name
            tutor_pr_apellido = tutor.last_name
            cedulaAca = tutor.f_cedula
            telefonoAca = tutor.f_telefono
            correoAca = tutor.email
            story.append(Paragraph(escape('NOMBRE Y APELLIDO: ' +str(tutor_pr_nombre) + ' ' + str(tutor_pr_apellido)),styles["test"]))
            story.append(Paragraph(escape('CÉDULA DE IDENTIDAD: ' +str(cedulaAca)),styles["test"]))
            story.append(Paragraph(escape('TELÉFONO: ' +str(telefonoAca)),styles["test"]))
            story.append(Paragraph(escape('CORREO ELECTRÓNICO: ' +str(correoAca)),styles["test"]))
            story.append(Paragraph(escape(str(linea2)),styles["test"]))
    
    story.append(Paragraph(escape('CERTIFICO QUE EL ESTUDIANTE CUMPLIÓ CON LOS OBJETIVOS PLANTEADOS DURANTE EL \
        DESARROLLO DEL PROYECTO DE SERVICIO COMUNITARIO POR UN LAPSO DE '+ str(horas_realizadas)+' HORAS, COMO LO ESTABLECE EL \
        REGLAMENTO DE FORMACIÓN COMPLEMENTARIA PROFESIONAL EN SU SECCIÓN 2 DEL SERVICIO COMUNITARIO EN SU ARTÍCULO 24 \
        PARÁGRAFO EVALUACIÓN.'),styles["test"]))
    story.append(Paragraph(escape('CONFORME:'),styles["test"]))
    story.append(Spacer(0,0.6*inch))
    t = Table([
        ['_'*30,'_'*30],
        ['Firma del Tutor ACADÉMICO\n(Firma y Sello del Dpto. Adscripción)', 'Validación de CFCG o COORDEXT\n(Firma y Sello )']
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

def genPDF(base_url='applications/SIGESC/templates_pdf/planillaAval/', template_html='template.html',template_css='template.css', output="out.pdf",variables=dict()):
    template = open(base_url+template_html).read()
    contenido = template.format(**variables)
    weasyprint.HTML(string=contenido,base_url=base_url).render(stylesheets=[base_url+template_css]).write_pdf(output)
    pdf = open(output).read()
    os.remove(output)
    return pdf
'''
def proponenteProyecto():
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name,auth.user.last_name)
    idProponente = db(db.t_proponente.f_user==auth.user).select()
    return dict(proyectos = db(db.t_project.f_proponente==idProponente[0]).select(), bienvenida=msj)
'''

def solicitudes_tutor():
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    idTutorAcademico = auth.user.id
    listaProyectosTutores = db(db.t_proyecto_tutor.f_tutor == idTutorAcademico).select()
    listaInscripcion = []
    listaEnviados = []
    for proy in listaProyectosTutores:
        if (db((db.t_cursa.f_proyecto==proy.f_proyecto) &(db.t_cursa.f_valido=="Valido")&(db.t_cursa.f_actual==True)).select().first()!=None):
            listaInscripcion += db((db.t_inscripcion.f_proyecto == proy.f_proyecto) &(db.t_inscripcion.f_actual == True)).select()
    for ins in listaInscripcion:
        act = []
        cursa = db((db.t_cursa.f_estudiante==ins.f_estudiante)&(db.t_cursa.f_actual==True)).select().last()

        act += db(db.t_actividad_estudiante.f_cursa==cursa.id).select()
        if act:
            listaEnviados += [ins]
    return dict(proyectos = listaProyectosTutores, bienvenida=msj,listaInscripcion=listaInscripcion,enviados=listaEnviados)

'''
def solicitud_constancia_coordinacion():
    estudianteCursa = db(db.t_cursa).select()
    #print '----> ', estudianteCursa
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)

    return dict(bienvenida=msj,estudianteCursa=estudianteCursa)
'''
def solicitud_plan_de_trabajo():
    idEstudiante = request.args[1]
    idProyecto = request.args[0]
    proyecto = db(db.t_proyecto.id==idProyecto).select()
    estudiante = db(db.t_estudiante.id==idEstudiante).select()
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    idTutorAcademico = auth.user.id
    listaProyectosTutores = db(db.t_proyecto_tutor.f_tutor == idTutorAcademico).select()
    listaInscripcion = []
    for proy in listaProyectosTutores:
        listaInscripcion += db(db.t_inscripcion.f_proyecto == proy.f_proyecto).select()

    listaActividades = db(db.t_actividad.f_proyecto==idProyecto).select()
    inscripcion = db(db.t_inscripcion.f_estudiante == idEstudiante).select().last()

    listaStringActividades = ''
    for celda in listaActividades:
        listaStringActividades += (str((celda.id))) + '/'

    return dict(proyectos = listaProyectosTutores,bienvenida=msj,listaInscripcion=listaInscripcion,
                estudiante=estudiante[0],proyecto=proyecto[0],listaActividades=listaActividades,
                inscripcion=inscripcion,idProyecto=idProyecto,estudianteID=idEstudiante,
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
    idCursa = db((db.t_cursa.f_estudiante==idEstudiante)&(db.t_cursa.f_proyecto==idProyecto)&(db.t_cursa.f_actual==True)).select().last()
    noExisteCursa=db(db.t_actividad_estudiante.f_cursa==idCursa).select().first()==None
    if noExisteCursa:
        for j in range(len(lista)):
            #idActividad = db(db.t_actividad.id==j).select()
            db.t_actividad_estudiante.insert(f_cursa=idCursa,f_actividad=long(lista[j]),f_horas=int(listaHoras[j]))

    return dict(idProyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje,bienvenida=msj,lista=lista)

'''
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
'''
#@auth.requires(auth.has_membership(role='Administrador') or auth.has_membership(role='Proponentes'))
def propuestas():
    es_adm = 'Coordinador' in auth.user_groups.values()
    es_adm = es_adm or 'Administrador' in auth.user_groups.values()
    es_adm = es_adm or 'Administrador Dex' in auth.user_groups.values()
    es_adm = es_adm or 'Asistente' in auth.user_groups.values()

    if es_adm:
        propuestas = [
            {
                'id': p.f_proyecto,
                'nombre': db.t_proyecto(p.f_proyecto).f_nombre,
                'estado': p.f_estado_propuesta
            } for p in db().select(db.t_propuesta.ALL)
        ]
    else:
        propuestas = [
            {
                'id': p.f_proyecto,
                'nombre': db.t_proyecto(p.f_proyecto).f_nombre,
                'estado': p.f_estado_propuesta
            } for p in db(db.t_propuesta.f_proponente==auth.user.id).select()
        ]
    return dict(rolesUsuario=obtenerListaRolesUsuario(),es_adm = es_adm,propuestas=propuestas,message=T(response.flash))

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
    proyecto =  db(db.t_proyecto.id == proyecto_id).select().first()
    actividades = db(db.t_actividad.f_proyecto == proyecto_id).select()
    objetivos = db(db.t_objetivo.f_proyecto == proyecto_id).select()
    plan_operativo = db(db.t_plan_operativo.f_proyecto == proyecto_id).select()
    
    tutores = db((db.t_proyecto_tutor.f_proyecto == proyecto_id) &(db.auth_user.id==db.t_proyecto_tutor.f_tutor)).select()

    tutores_comunitarios = db((db.t_proyecto_tutor_comunitario.f_proyecto == proyecto_id) &(db.auth_user.id==db.t_proyecto_tutor_comunitario.f_tutor)).select()

    sedes = db(db.t_proyecto_sede.f_proyecto == proyecto_id).select()


    return dict(
        rolesUsuario=obtenerListaRolesUsuario(),
        propuesta = propuesta,
        proyecto = proyecto,
        actividades = actividades,
        sedes=sedes,
        objetivos = objetivos,
        plan_operativo = plan_operativo,
        tutores = tutores,
        tutores_comunitarios = tutores_comunitarios
    )

def verProyectoEstudiante():
    idproyecto = long(request.args[0])
    idestudiante = long(request.args[1])
    proyecto =  db(db.t_proyecto.id == idproyecto).select().first()
    actividades = db(db.t_actividad.f_proyecto == idproyecto).select()
    objetivos = db(db.t_objetivo.f_proyecto == idproyecto).select()
    plan_operativo = db(db.t_plan_operativo.f_proyecto == idproyecto).select()
    
    tutores = db((db.t_proyecto_tutor.f_proyecto == idproyecto) &(db.auth_user.id==db.t_proyecto_tutor.f_tutor)).select()

    tutores_comunitarios = db((db.t_proyecto_tutor_comunitario.f_proyecto == idproyecto) &(db.auth_user.id==db.t_proyecto_tutor_comunitario.f_tutor)).select()

    sedes = db(db.t_proyecto_sede.f_proyecto == idproyecto).select()
    return dict(
        rolesUsuario=obtenerListaRolesUsuario(),
        idestudiante=idestudiante,
        proyecto = proyecto,
        actividades = actividades,
        sedes=sedes,
        objetivos = objetivos,
        plan_operativo = plan_operativo,
        tutores = tutores,
        tutores_comunitarios = tutores_comunitarios
    )

def propuestasEditar():
    proyecto_id = long(request.args[0])
    redirect(URL('propuestasCrear',vars=dict(proyecto_id=proyecto_id)))

def propuestaPredecesor():

    proyectos = db(db.t_proyecto.id==db.t_proyecto_aprobado.f_proyecto).select()

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

    return dict(rolesUsuario=obtenerListaRolesUsuario(),proyectos=proyectos)


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
            'f_sedes',
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
        tutores, tutores_comunitarios,sedes = [], [],[]

        k_del = []

        for k in form.vars:
            if k not in form_paginas[pag]:
                k_del += [k]

        for k in k_del:
            del form.vars[k]

        propuesta = db(db.t_propuesta.f_proyecto==proyecto_id).select()
        if not form.vars.f_proponente:
            form.vars.f_proponente = auth.user.id
        if not form.vars.f_estado_propuesta:
            if propuesta:
                form.vars.f_estado_propuesta = propuesta[0].f_estado_propuesta
            else:
                form.vars.f_estado_propuesta = "Incompleta"
        if not form.vars.f_nombre and proyecto_id:
            form.vars.f_nombre = db.t_proyecto(proyecto_id).f_nombre
        if not form.vars.f_observaciones and proyecto_id:
            if propuesta:
                form.vars.f_observaciones = propuesta[0].f_observaciones
            else:
                form.vars.f_observaciones=""; 

        proyecto_fields = db.t_proyecto._filter_fields(form.vars)
        print proyecto_fields
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
        sedes=form.vars.f_sedes
        print("Tutores",tutores,tutores_comunitarios)
        print("Sedes:",sedes)
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
            if sedes:
                db(db.t_proyecto_sede.f_proyecto==proyecto_id).delete()
                if isinstance(sedes,str):
                    sedes = [sedes]
                for sede_id in sedes:
                    print("sede con id", sede_id)
                    db.t_proyecto_sede.insert(
                        f_proyecto=proyecto_id,
                        f_sede=sede_id
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
        # Esto lo debe hacer el coordinador al aprobar el proyecto
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
        return dict(rolesUsuario=obtenerListaRolesUsuario(),
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
    print("accion:",accion)
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
    lista_tutores = [(tutor.id, '{} {}'.format(tutor.first_name,tutor.last_name)) for tutor in db((db.auth_user.f_tipo == 'Docente')|(db.auth_user.f_tipo == 'Interno')|(db.auth_user.f_tipo == 'Empleado')|(db.auth_user.f_tipo == 'Administrativo')).select()]
    lista_tutores_comunitarios = [(tutor.id, '{} {}'.format(tutor.first_name,tutor.last_name)) for tutor in db(db.auth_user).select()]

    # Obtener lista de sedes
    lista_sedes = [(sede.id, '{}'.format(sede.f_nombre)) for sede in db(db.t_sede).select()]
    
    # Crear form
    if pag < 6:
        db.t_propuesta.f_proponente.notnull = False
        db.t_propuesta.f_proponente.requires = None

        form = SQLFORM.factory(
            db.t_proyecto,
            db.t_propuesta,
            Field(
                'f_sedes',
                requires=IS_IN_SET(lista_sedes, multiple=True)
            ), 
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
        
        #print form.vars.f_estado_propuesta
        print "AQUIIIII"

        #form.vars.f_observaciones="hola"
        #print form.vars.f_observaciones 
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

        if not form.vars.f_sedes:
            sedes_proyecto = [str(t.f_sede)
                for t in db(
                    db.t_proyecto_sede.f_proyecto == proyecto_id
                ).select()
            ]
        else:
            sedes_proyecto = form.vars.f_sedes
        print("sedes com",sedes_proyecto)
        select_sede = form.element('select',_name='f_sedes')
        if select_sede:
            sede_opts = select_sede.elements('option')
            for opt in sede_opts:
                opt['_selected'] = opt['_value'] in sedes_proyecto


    print("form.vars tutores", [k for k in form.vars])
    res = dict(rolesUsuario=obtenerListaRolesUsuario(),
        form=form,
        pag= pag,
        es_adm= es_adm,
        message=T(response.flash),
        actividades=actividades,
        obj_especificos=obj_especificos,
        plan_operativo=plan_operativo,
        tutores=[],
        tutores_comunitarios=[],
        sedes=[],
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
        if form.vars.f_fechaini > form.vars.f_fechafin:
            form.errors.f_fechaini = 'La fecha final del proyecto es menor que la inicial'
            form.errors.f_fechafin = 'La fecha final del proyecto es menor que la inicial'
        print form.vars.f_sedes
        return form

    def hard_validation(form):
        print("Validación fuerte")
        proyecto = db.t_proyecto(form.vars.f_proyecto)
        propuesta = db(db.t_propuesta.f_proyecto==proyecto.id).select()[0]
        actividades = db(db.t_actividad.f_proyecto==proyecto_id).select()
        obj_especificos = db(db.t_objetivo.f_proyecto==proyecto_id).select()
        sedes=db(db.t_proyecto_sede.f_proyecto==proyecto.id).select()
        tutores=db(db.t_proyecto_tutor.f_proyecto==proyecto.id).select()
        tutores_comunitarios=db(db.t_proyecto_tutor_comunitario.f_proyecto==proyecto.id).select()
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
        if not sedes:
            form.errors['f_sedes'] = 'El proyecto debe poseer al menos una sede.'
        if not tutores:
            form.errors['f_tutores'] = 'El proyecto debe poseer al menos un tutor academico.'
        if not tutores_comunitarios:
            form.errors['f_tutores_comunitarios'] = 'El proyecto debe poseer al menos un tutor comunitario.'

        print(form.errors)
        return form
    print accion
    if accion == "registrar":
        def form_validation(form):
            form = hard_validation(form)
    elif accion == "guardar":
        def form_validation(form):
            print "hola suave"
            form = soft_validation(form)
    else:
        # Set form values to project record
        if proyecto_id:
            form.vars = db.t_proyecto(proyecto_id)
            if form.vars.f_fechaini:
                form.vars.f_fechaini = form.vars.f_fechaini.strftime('%d/%m/%Y')
            if form.vars.f_fechafin:
                form.vars.f_fechafin = form.vars.f_fechafin.strftime('%d/%m/%Y')

            propuesta = db(db.t_propuesta.f_proyecto==proyecto_id).select()
            if propuesta:
                form.vars.f_observaciones=propuesta[0].f_observaciones
                form.vars.f_estado_propuesta=propuesta[0].f_estado_propuesta

        def form_validation(form):
            form = form # función de mentira (de default).


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
                    f_estado_propuesta = 'En espera de revision'
                )
                res['estado_propuesta'] = 'En espera de revision'
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
        elif field == 'f_sedes':
            label = 'Sedes'
        elif field == 'f_tutores':
            label = 'Tutores'
        elif field == 'f_tutores_comunitarios':
            label = 'Tutores comunitarios'

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

def agregar_comunidad():
    idProyecto=long(request.vars.id)
    proyecto=db(db.t_proyecto.id==idProyecto).select().first()
    return dict(proyecto=proyecto,comunidades=db().select(db.t_comunidad.ALL))

def agregar_comunidad_listo():
    comunidad=request.vars.comunidad
    existeComunidad=db(db.t_comunidad.f_nombre.upper()==comunidad.upper()).select().first() !=None
    if existeComunidad:
        return "*La comunidad ya existe."     

    db.t_comunidad.insert(f_nombre=comunidad)
    tcomunidad=db(db.t_comunidad.f_nombre==comunidad).select().first()
    return tcomunidad.id

def propuestaPDF():
    base_url='applications/SIGESC/templates_pdf/propuesta/'
    template_css='template.css'
    output="out.pdf"
    if request.post_vars:
        response.headers['Content-Type'] = 'application/pdf; charset=UTF-8'
        pdf = weasyprint.HTML(string=request.post_vars.html).render(stylesheets=[base_url+template_css]).write_pdf()
        return pdf

'''        
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
'''

def estudianteCursa():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    form = SQLFORM(db.t_cursa,fields = ['f_estudiante','f_proyecto'])
    form.vars.f_estudiante = idEstudiante
    form.vars.f_proyecto = idProyecto
    sedes=db(db.t_proyecto_sede.f_proyecto==idProyecto).select()
    print sedes
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
    countProyectos=len(db((db.t_cursa.f_estudiante==idEstudiante)&(db.t_cursa.f_estado=="Culminado")).select())

    if (countProyectos>1):
        horasDeber=30
    else:
        horasDeber=40
        
    return dict(horasDeber=horasDeber,sedes=sedes,proyecto=db(db.t_proyecto_aprobado.f_proyecto==idProyecto).select()[0],estudianteId=idEstudiante,idProyecto=idProyecto)
'''
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
'''
'''
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
'''
def estudiante_plan_trabajo():
    #idProyecto = long(request.args[0])
    idEstudiante = long(request.args[0])
    listaActividades = []
    cursa = db((db.t_cursa.f_estudiante==idEstudiante) &(db.t_cursa.f_actual==True)).select().last()
    print cursa
    listaActividades = db(db.t_actividad_estudiante.f_cursa==cursa).select()
    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    return dict(listaActividades=listaActividades,bienvenida=msj,idEstudiante=idEstudiante)

def rechazar_solicitud_tutor():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    estudiante = db(db.t_estudiante.id==idEstudiante).select().first()
    print '>>>>>> ', estudiante.f_universitario.f_usuario.first_name
    return dict(proyecto=db(db.t_proyecto.id==idProyecto).select()[0], estudiante=estudiante)
'''
def aprobar_solicitud_coordinacion():
    idProyecto = long(request.args[1])
    idEstudiante = long(request.args[0])
    proyecto_cursa=db((db.t_cursa.f_estudiante==idEstudiante)&(db.t_cursa.f_proyecto==idProyecto))
    proyecto_cursa.update(f_valido='Valido')
    proyecto_cursa.update(f_estado='Aprobado')
    proyecto_cursa.update(f_fecha=datetime.datetime.today())

    msj = 'Bienvenid@ %s %s' % (auth.user.first_name, auth.user.last_name)
    return dict(bienvenida=msj)
'''
def eliminar_inscripcion():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    db((db.t_cursa.f_estudiante==idEstudiante)&(db.t_cursa.f_actual==True)).delete()
    db((db.t_inscripcion.f_estudiante==idEstudiante)&(db.t_inscripcion.f_actual==True)).delete()
    mensaje="Solicitud rechazada. Volver a solicitudes."
    return dict(proyecto=idProyecto, mensaje=mensaje)

def aceptarPlanTrabajo():
    estado = request.args[0]
    idEstudiante = long(request.args[1])
    if estado == 'aceptado':
        mensaje="Plan de trabajo aceptado con éxito. Volver."
        db((db.t_inscripcion.f_estudiante==idEstudiante)&(db.t_inscripcion.f_actual==True)).update(f_estado='Aprobado')
    else:
        mensaje="Se ha rechazado el plan de trabajo. Volver."
        cursa = db((db.t_cursa.f_estudiante==idEstudiante)&(db.t_cursa.f_actual==True)).select().last()
        db(db.t_actividad_estudiante.f_cursa==cursa).delete()

    return dict( mensaje=mensaje,estado=estado)

"""def rechazarProyectoEstudiante():
    idProyecto = long(request.args[0])
    db(db.t_cursa.id==idProyecto).update(f_state="3")
    return dict(proyecto=idProyecto)
"""
def registrarProyectoComoEstudiante():
    idProyecto = long(request.args[0])
    idEstudiante = long(request.args[1])
    dropdown = request.args[2]

    db.t_cursa.insert(f_estudiante=idEstudiante,f_proyecto=idProyecto,f_estado="Pendiente",f_valido="Invalido")
    cursa=db(db.t_cursa.f_estudiante==idEstudiante).select().last()
    mensaje = "Registro de proyecto exitoso. Volver al Menú"
    db.t_inscripcion.insert(f_estudiante=idEstudiante,f_proyecto=idProyecto,f_estado="Pendiente",f_horas = dropdown,f_actual=True,f_cursa=cursa.id)

    return dict(proyecto=idProyecto,estudianteID=idEstudiante,mensaje=mensaje,dropdown=dropdown)
'''
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
'''
def estudianteInscribeProyectos():
    x = long (request.args[0])
    usuario    = db.auth_user(auth.user_id)
    universitario=db(db.t_universitario.f_usuario==auth.user_id).select().first()
    estudiante=db(db.t_estudiante.f_universitario==universitario.id).select().first()
    msj        = 'Bienvenid@ %s %s' % (usuario.first_name,usuario.last_name)
    
    ultimoProyectoCursado=db((db.t_cursa.f_estudiante==estudiante)&(db.t_cursa.f_actual==True)).select().last()
    noRespuestaProyecto=(ultimoProyectoCursado!=None)

    print(ultimoProyectoCursado,noRespuestaProyecto)
    mensaje="Registro de proyecto exitoso. Volver al Menú"
    fechaTope1=db(db.t_fechas_tope.f_tipo=="Inscripción").select().first()
    fechaTope2=db(db.t_fechas_tope.f_tipo=="Inscripción Extemporánea").select().first()
    ahora=datetime.datetime.today().date()
    return dict(ultimoProyectoCursado=ultimoProyectoCursado,noRespuestaProyecto=noRespuestaProyecto,ahora=ahora,fechaTope1=fechaTope1,fechaTope2=fechaTope2,estudiante=estudiante,proyectos=db(db.t_proyecto_aprobado.f_estado_proyecto=="Activo").select(),estudianteId=estudiante.id, mensaje=mensaje,bienvenida=msj)


'''
def estudiantesDetalles():
    x = long (request.args[0])
    #return dict(rows = db(db.t_estudiante.id==x).select())
    return dict(rows = db(db.t_estudiante.id==x).select(),estudianteId=x)

def tutoresDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_tutor.id==x).select())


def proyectosDetalles():
    x = long (request.args[0])
    return dict(rows = db(db.t_proyecto.id==x).select())

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
'''
def generarPdfConstanciaInicio():
    x = long (request.args[0])
    y = long (request.args[1])
    est = db(db.t_estudiante.id==x).select()[0]
    iduniv = est.f_universitario
    universitario = db(db.t_universitario.id==iduniv).select()[0]
    userest = db(db.auth_user.id==universitario.f_usuario).select()[0]
    proyecto = db(db.t_proyecto.id==y).select()[0]
    proyectotutor = db(db.t_proyecto_tutor.f_proyecto==proyecto.id).select()[0]
    tutor = db(db.auth_user.id==proyectotutor.f_tutor).select()[0]
    USBID = universitario.f_usbid
    Sede = universitario.f_sede.f_nombre
    Nombre = userest.first_name
    Apellido = userest.last_name
    Cedula = userest.f_cedula
    tlf = userest.f_telefono
    direccion = userest.f_direccion
    Correo = userest.email

    Carrera = est.f_carrera.f_nombre

    Sexo = userest.f_sexo

    inscripcion = db(db.t_inscripcion.f_estudiante == x).select().last()
    fechaIn = inscripcion.created_on
    fechaIn = str(fechaIn)[:-9]
    
    proyectoAprobado=db(db.t_proyecto_aprobado.f_proyecto==proyecto.id).select().first()
    codigo_pr = proyectoAprobado.f_codigo

    nombre_pr = proyecto.f_nombre
    descripcion_pr = proyecto.f_resumen
    area_pr = proyecto.f_area
    estado_pr = 'Activo'
    fecha_ini = '12/01/2016'
    fecha_fin = '26/08/2016'
    #version_pr = proy[0].f_version
    proponente_pr = 'Nombre proponente'
    #user_id = auth.user_id
    
    if db.auth_user(auth.user_id)['f_foto']:
        picture = URL('uploads', args=db.auth_user(auth.user_id)['f_foto'])
        foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".." + picture[15:])
    else:
        picture = URL('static', 'img/user.png')
        foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".." + picture[7:])

    tutor_pr_nombre = tutor.first_name
    tutor_pr_apellido = tutor.last_name

    comunidad_pr = proyecto.f_comunidad.f_nombre
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
    u = inch/10.0

    inscProyRealizado = db(db.t_cursa.f_estudiante==x).select()

    if inscProyRealizado and inscProyRealizado[0].f_valido=="Valido":

        title = '<font size=10><b><u>__CONSTANCIA DE INICIO DE SERVICIO COMUNITARIO__</u></b></font>'
        heading = "Datos del estudiante:"


        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='titles', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='logos', alignment=TA_LEFT))
        style_right = ParagraphStyle(name='right', parent=styles['Normal'], alignment=TA_RIGHT)
        tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
        doc = SimpleDocTemplate(tmpfilename,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=2,bottomMargin=18)
        logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/img/logo_dex.png')
        #foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), picture)
        
        
        #foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/auth_user.f_foto.b5293861dbd3a2a5.313839383234345f31303135333635323832313239383833335f3234393434353833333339393330373038345f6e2e6a7067.jpg')
        salto = '<br />\n'
        linea1 = '__________________________________________________________________________________'
        linea2 = '__________________________________'
        linea3 = '______________'

        story = []
        im = Image(logo,width=90, height=60)
        im.hAlign = 'LEFT'
        im2 = Image(foto,width=70, height=70)
        im2.hAlign = 'right'
        espaciadorDeTabla = Paragraph("", styles["Normal"])
        
     

        tbl_data = [
            [im, espaciadorDeTabla,espaciadorDeTabla, im2],
            [Paragraph("", styles["Normal"]), espaciadorDeTabla,espaciadorDeTabla, Paragraph("", style_right)],
            [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla,]
        ]
        tbl = Table(tbl_data)
        story.append(tbl)
        
        #story.append(im)
        #story.append(im2)
        
        #story.append(Paragraph(salto,styles["Normal"]))
        story.append(Paragraph(title,styles["titles"]))
        #story.append(Paragraph(linea,styles["Normal"]))
        story.append(Spacer(1,2*u))

        story.append(Paragraph(escape('Fecha de Inicio: ' + str(fechaIn)),styles["Normal"]))
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
        story.append(Paragraph(escape('Correo Electrónico: ' + str(Correo)),styles["Normal"]))

        story.append(Paragraph(salto,styles["Normal"]))
        story.append(Paragraph(escape('Información del proyecto: '),styles["Heading2"]))
        story.append(Paragraph(escape('Nombre del proyecto: ' + str(nombre_pr)),styles["Normal"]))
        story.append(Paragraph(escape('Código del proyecto: ' + str(codigo_pr)),styles["Normal"]))
        story.append(Paragraph(escape('Tutor académico: ' +str(tutor_pr_nombre) + ' ' + str(tutor_pr_apellido)),styles["Normal"]))
        story.append(Paragraph(escape('Comunidad: ' + str(comunidad_pr)),styles["Normal"]))
        
        story.append(Paragraph(salto,styles["Normal"]))
        story.append(Paragraph(escape('Validación: '),styles["Heading2"]))
        story.append(Paragraph(escape('Fecha: ' + str(linea3)),styles["Normal"]))
        story.append(Paragraph(escape('Nombre del responsable: ' + str(linea2)),styles["Normal"]))
        story.append(Paragraph(escape('Firma y sello de la dependencia: '),styles["Normal"]))


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
    u = inch/10.0
    est = db(db.t_estudiante.id==x).select()[0]
    iduniv = est.f_universitario
    universitario = db(db.t_universitario.id==iduniv).select()[0]
    userest = db(db.auth_user.id==universitario.f_usuario).select()[0]
    proyecto = db(db.t_proyecto.id==y).select()[0]
    
    inscripcion = db(db.t_inscripcion.f_estudiante == x).select().last()
    fechaIn = inscripcion.created_on
    fechaIn = str(fechaIn)[:-9]
    
    proyectoAprobado=db(db.t_proyecto_aprobado.f_proyecto==proyecto.id).select().first()
    codigo_pr = proyectoAprobado.f_codigo
    
   
    USBID = universitario.f_usbid
    Nombre = userest.first_name
    
    Sede = universitario.f_sede.f_nombre
    
    Apellido = userest.last_name
    Cedula = userest.f_cedula
    tlf = userest.f_telefono
    direccion = userest.f_direccion

    Carrera = est.f_carrera.f_nombre

    Sexo = userest.f_sexo
    Correo = userest.email

    nombre_pr = proyecto.f_nombre
    objetivo_pr = proyecto.f_obj_generales
    descripcion_pr = proyecto.f_resumen
    area_pr = proyecto.f_area
    estado_pr = 'Activo'
    fecha_ini = '12/01/2016'
    fecha_fin = '26/08/2016'
    #version_pr = proy[0].f_version
    proponente_pr = 'Nombre proponente'
    #user_id = auth.user_id
    
    if db.auth_user(auth.user_id)['f_foto']:
        picture = URL('uploads', args=db.auth_user(auth.user_id)['f_foto'])
        foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".." + picture[15:])
    else:
        picture = URL('static', 'img/user.png')
        foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".." + picture[7:])

    comunidad_pr = proyecto.f_comunidad.f_nombre
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
    u = inch/10.0

    inscProyRealizado = db(db.t_cursa.f_estudiante==x).select()

    title = '<font size=10><b><u>__PLANILLA DE INSCRIPCIÓN ESTUDIANTIL DEL PROYECTO DE SERVICIO COMUNITARIO__</u></b></font>'
    heading = "Datos del estudiante:"


    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='titles', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='logos', alignment=TA_LEFT))
    style_right = ParagraphStyle(name='right', parent=styles['Normal'], alignment=TA_RIGHT)
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename,pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=10,bottomMargin=38)
    logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/img/logo_dex.png')
    #foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), picture)
    
    
    #foto = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/auth_user.f_foto.b5293861dbd3a2a5.313839383234345f31303135333635323832313239383833335f3234393434353833333339393330373038345f6e2e6a7067.jpg')
    salto = '<br />\n'
    linea1 = '__________________________________________________________________________________'
    linea2 = '__________________________________'
    linea3 = '______________'
    story = []
    im = Image(logo,width=90, height=60)
    im.hAlign = 'LEFT'
    im2 = Image(foto,width=70, height=70)
    im2.hAlign = 'right'
    espaciadorDeTabla = Paragraph("", styles["Normal"])
    
    

    tbl_data = [
        [im, espaciadorDeTabla,espaciadorDeTabla, im2],
        [Paragraph("", styles["Normal"]), espaciadorDeTabla,espaciadorDeTabla, Paragraph("", style_right)],
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla,]
    ]
    tbl = Table(tbl_data)
    story.append(tbl)
    
    #story.append(im)
    #story.append(im2)
    
    #story.append(Paragraph(salto,styles["Normal"]))
    story.append(Paragraph(title,styles["titles"]))
    #story.append(Paragraph(linea,styles["Normal"]))
    story.append(Spacer(1,2*u))

    story.append(Paragraph(escape('Fecha de Inscripcion: ' + str(fechaIn)),styles["Normal"]))
    #story.append(Paragraph(escape('Período:___________________________________ Año: ______________'),styles["Normal"]))
    story.append(Paragraph(escape(heading),styles["Heading2"]))
    story.append(Paragraph(escape('Carné: ' + str(USBID)),styles["Normal"]))
    story.append(Paragraph(escape('Carrera: ' + str(Carrera)),styles["Normal"]))
    story.append(Paragraph(escape('Nombres: ' + str(Nombre)),styles["Normal"]))
    story.append(Paragraph(escape('Apellidos: ' + str(Apellido)),styles["Normal"]))
    story.append(Paragraph(escape('Cédula de Identidad: ' + str(Cedula)),styles["Normal"]))
    story.append(Paragraph(escape('Teléfono: ' + str(tlf)),styles["Normal"]))
    story.append(Paragraph(escape('Dirección: ' + str(direccion)),styles["Normal"]))
    story.append(Paragraph(escape('Sede: ' + str(Sede)),styles["Normal"]))
    story.append(Paragraph(escape('Sexo: ' + str(Sexo)),styles["Normal"]))
    story.append(Paragraph(escape('Correo Electrónico: ' + str(Correo)),styles["Normal"]))

    story.append(Paragraph(salto,styles["Normal"]))
    story.append(Paragraph(escape('Datos del proyecto: '),styles["Heading2"]))
    story.append(Paragraph(escape('Nombre del proyecto: ' + str(nombre_pr)),styles["Normal"]))
    story.append(Paragraph(escape('Código del proyecto: ' + str(codigo_pr)),styles["Normal"]))
    story.append(Paragraph(escape('Comunidad beneficiada: ' + str(comunidad_pr)),styles["Normal"]))
    
    story.append(Paragraph(escape('Tutor(es) Comunitario(s): '),styles["Heading4"]))
    for proyectoTutorCom in db(db.t_proyecto_tutor_comunitario).select():
        if (proyectoTutorCom.f_proyecto==proyecto.id):
            tutorCom = db(db.auth_user.id==proyectoTutorCom.f_tutor).select()[0]
            tutorCom_pr_nombre = tutorCom.first_name
            tutorCom_pr_apellido = tutorCom.last_name
            cedulaCom = tutorCom.f_cedula
            telefonoCom = tutorCom.f_telefono
            direccionCom = tutorCom.f_direccion
            correoCom = tutorCom.email
            story.append(Paragraph(escape('Nombre y Apellido: ' +str(tutorCom_pr_nombre) + ' ' + str(tutorCom_pr_apellido)),styles["Normal"]))
            story.append(Paragraph(escape('Cédula de identidad: ' +str(cedulaCom)),styles["Normal"]))
            story.append(Paragraph(escape('Dirección: ' +str(direccionCom)),styles["Normal"]))
            story.append(Paragraph(escape('Teléfono: ' +str(telefonoCom)),styles["Normal"]))
            story.append(Paragraph(escape('Correo Electrónico: ' +str(correoCom)),styles["Normal"]))
            story.append(Paragraph(escape(str(linea2)),styles["Normal"]))
    
    
    story.append(Paragraph(escape('Tutor(es) Académico(s): '),styles["Heading4"]))
    for proyectoTutorAca in db(db.t_proyecto_tutor).select():
        if (proyectoTutorAca.f_proyecto==proyecto.id):
            tutor = db(db.auth_user.id==proyectoTutorAca.f_tutor).select()[0]
            tutor_pr_nombre = tutor.first_name
            tutor_pr_apellido = tutor.last_name
            cedulaAca = tutor.f_cedula
            telefonoAca = tutor.f_telefono
            direccionAca = tutor.f_direccion
            correoAca = tutor.email
            story.append(Paragraph(escape('Nombre y Apellido: ' +str(tutor_pr_nombre) + ' ' + str(tutor_pr_apellido)),styles["Normal"]))
            story.append(Paragraph(escape('Cédula de identidad: ' +str(cedulaAca)),styles["Normal"]))
            story.append(Paragraph(escape('Dependencia: ' +str(linea3)),styles["Normal"]))
            story.append(Paragraph(escape('Teléfono: ' +str(telefonoAca)),styles["Normal"]))
            story.append(Paragraph(escape('Correo Electrónico: ' +str(correoAca)),styles["Normal"]))
            story.append(Paragraph(escape(str(linea2)),styles["Normal"]))

    story.append(Paragraph(escape('Organización de Desarrollo Social que promueve el proyecto ( en caso de que aplique): '),styles["Heading4"]))
    story.append(Paragraph(escape('Direccion: ' + str(linea1)),styles["Normal"]))
    story.append(Paragraph(escape('Telefono: ' + str(linea3)),styles["Normal"]))
    story.append(Paragraph(escape('FAX: ' + str(linea3)),styles["Normal"]))
    story.append(Paragraph(escape('Correo Electrónico: ' + str(linea3)),styles["Normal"]))
    
    story.append(Paragraph(escape('Objetivo del proyecto: '),styles["Heading4"]))
    story.append(Paragraph(escape('' + str(objetivo_pr)),styles["Normal"]))

    story.append(Paragraph(escape('Actividades del proyecto: '),styles["Heading4"]))
    
    tbl_data = [
        [Paragraph("Nombre de la Actividad", styles["Heading5"]),espaciadorDeTabla, Paragraph("Resumen", styles["Heading5"])]
    ]
    tbl = Table(tbl_data)
    story.append(tbl)
    
    for actividad in db(db.t_actividad).select():
        if (actividad.f_proyecto == proyecto.id):
            tbl_data = [
                [Paragraph('* ' + str(actividad.f_nombre), styles["Normal"]),espaciadorDeTabla, Paragraph('* ' + str(actividad.f_resumen), styles["Normal"])],
                [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla]
            ]
            tbl = Table(tbl_data)
            story.append(tbl)
    
    tbl_data = [
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla],
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla],
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla],
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla],
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla],
        [Paragraph(linea3, styles["Heading5"]),Paragraph(linea3, styles["Heading5"]), Paragraph('_________'+linea3, styles["Heading5"])],
        [Paragraph('Firma Estudiante', styles["Normal"]),Paragraph('Firma Tutor (a)', styles["Normal"]), Paragraph('Firma CFCG-CEXT', styles["Normal"])],
        [espaciadorDeTabla,espaciadorDeTabla,espaciadorDeTabla]
    ]
    tbl = Table(tbl_data)
    story.append(tbl)   
    
    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data