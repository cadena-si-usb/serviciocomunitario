# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

db.define_table('t_estado',
    Field('f_nombre', type='string', notnull=True,
          label=T('Nombre')),
    format='%(f_nombre)s',
    migrate=settings.migrate)
db.define_table('t_estado_archive',db.t_estado,Field('current_record','reference t_estado',readable=False,writable=False))

auth.settings.extra_fields['auth_user']= [
Field('f_tipo', 
          notnull=True,
          default='Externo',
          writable=False,
          readable=False,
          requires=IS_IN_SET( ['Pregrado',
                               'Postgrado',
                               'Empleado',
                               'Egresado',
                               'Docente',
                               'Interno',
                               'Administrativo',
                               'Organización',
                               'Externo']), 
          label=T('Tipo'),),
Field('f_direccion',type='text',label=T('Direccion'), writable=True,notnull=False),
Field('f_cedula'   ,type="string",unique=True,label=T('Cedula'), writable=True), #notnull=True restriccion relajada por CAS y ldap
Field('f_telefono' ,type="string",label=T('Telefono'), writable=True),
Field('f_sexo' ,requires=IS_IN_SET(['Masculino','Femenino'],error_message='No puede estar vacio.'),label=T('Sexo'), writable=True),
Field('f_estado', type='reference t_estado', default=10,
  requires=IS_IN_DB(db,db.t_estado,'%(f_nombre)s',error_message='No puede estar vacio.'),label=T('Estado'),writable=True),
Field('f_foto',type="upload",
               requires=IS_NULL_OR(IS_IMAGE(extensions=('bmp',
                                                         'gif',
                                                         'jpeg',
                                                         'jpg',
                                                         'png'), 
                                            maxsize=(10000,10000))),
               label=T('Foto'), 
               writable=True,readable=False),
Field('f_confirmado', type='boolean', notnull=False,
          label=T('Confirmacion Correo'), default=False,writable=False,readable=False)]


#auth.settings.logout_next = 'https://secure.dst.usb.ve/logout'
# auth.define_tables(username=True, signature=False)


#Validaciones agregadas RUPDEV
auth.define_tables(username=True, signature=False)
db.auth_user.username.requires   = [IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_NOT_IN_DB(db, db.auth_user.username,error_message='Usuario ya existe en el sistema.'),IS_LENGTH(20,error_message='No puede tener mas de 20 caracteres.')]
db.auth_user.first_name.requires = [IS_MATCH('^[a-z\.A-Z_áéíóúñ\s]*$',error_message='Solo letras'),IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_LENGTH(minsize=2,maxsize=20,error_message='Al menos 2 caracteres y maximo 20 caracteres.')]
db.auth_user.last_name.requires  = [IS_MATCH('^[a-z\.A-Z_áéíóúñ\s]*$',error_message='Solo letras'),IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_LENGTH(minsize=2,maxsize=20,error_message='Al menos 2 caracteres y maximo 20 caracteres.')]
db.auth_user.f_direccion.requires   = [IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_LENGTH(120,error_message='No puede tener mas de 120 caracteres.')]
db.auth_user.f_cedula.requires   = [IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_MATCH('^[0-9]{7,8}$',error_message='Solo numeros, Ejemplo:13730196.'),IS_NOT_IN_DB(db, db.auth_user.f_cedula,error_message='Cedula ya existe en el sistema.')]
db.auth_user.f_telefono.requires = [IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_MATCH('^0[1-9]{3}-[1-9]{7}$',error_message='Formato no reconocido, Ejemplos: 0239-2388765 , 0426-2329724.')]
db.auth_user.email.requires      = [IS_NOT_EMPTY(error_message='No puede estar vacio.'),IS_MATCH('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$',error_message='Formato de correo no reconocido, Ejemplo: example@example.com')]
db.auth_group.description.requires = [IS_LENGTH(160,error_message='No puede tener mas de 160 caracteres.')]
db.auth_group.role.requires = [IS_LENGTH(20,error_message='No puede tener mas de 20 caracteres.')]
db.auth_user.password.requires = [IS_NOT_EMPTY(error_message='No puede estar vacio.')]

from gluon.tools import Mail
mail = Mail()
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'rivasjoel004@gmail.com'
mail.settings.login = 'rivasjoel004@gmail.com:gabyv18730196'
auth.settings.mailer = mail
## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = False
auth.settings.everybody_group_id = auth.id_group('Proponente')
auth.settings.login_next=URL(r=request, c='default', f='home')

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

auth.messages.submit_button = 'Enviar'
auth.messages.verify_password = 'Verificar Contraseña'
auth.messages.new_password = 'Nueva contraseña'
auth.messages.old_password = 'Contraseña anterior'
auth.messages.password_changed = 'Contraseña cambiada'
auth.messages.retrieve_username = 'Su nombre de usuario es: %(username)s'
auth.messages.invalid_login = 'Inicio de sesión inválido'
auth.messages.invalid_user = 'Usuario inválido'
auth.messages.new_password_sent = 'La contraseña ha sido cambiada.'
auth.messages.delete_label = 'Marcar para borrar:'
auth.messages.function_disabled = 'Función deshabilitada'
auth.messages.access_denied = 'Privilegios insuficientes'
auth.messages.registration_verifying = 'Ud. no ha confirmado su registro (email de verificación)'
auth.messages.logged_in = 'Entrar'
auth.messages.email_sent = 'Correo enviado.'
auth.messages.unable_to_send_email = 'No es posible enviar el correo'
auth.messages.email_verified = 'Email verificado'
auth.messages.logged_out = 'Finalizó la sesión.'
auth.messages.registration_successful = 'Registro satisfactorio.'
auth.messages.invalid_email = 'Correo invalido.'
auth.messages.unable_send_email = 'No es posible enviar el email (2)'
auth.messages.invalid_login = 'Login invalido'
auth.messages.invalid_user = 'Usuario invalido'
auth.messages.is_empty = "No puede tener campos vacios"
auth.messages.mismatched_password = "Las contraseñas no coinciden."


