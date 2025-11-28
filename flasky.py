import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


# Obtém o diretório base do arquivo atual (útil para criar o caminho do banco)
basedir = os.path.abspath(os.path.dirname(__file__))



# Cria a aplicação Flask e SQLite
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Inicializa extensões
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Relacionamento: uma Role possui vários Users
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

# Tabela de alunos
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# Formulário para cadastro de alunos
class NameForm(FlaskForm):
    name = StringField('Cadastre o novo Aluno:', validators=[DataRequired()])
    role = SelectField('Disciplina associada:', choices=[
        ('DSWA5', 'DSWA5'),
        ('GPSA5', 'GPSA5'),
        ('IHCA5', 'IHCA5'),
        ('SODA5', 'SODA5'),
        ('PJIA5', 'PJIA5'),
        ('TCOA5', 'TCOA5'),
    ])
    submit = SubmitField('Cadastrar')


# Permite acessar db, User e Role diretamente no shell do Flask
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


# Renderiza uma página customizada para erro 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404


 # Renderiza uma página customizada para erro 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Rota principal apenas renderiza a página inicia
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', current_time=datetime.utcnow())


# Página de cadastro e listagem de alunos
@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    form = NameForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user:
            flash('Estudante já existe na base de dados!')
        else:
            role = Role.query.filter_by(name=form.role.data).first()
            if not role:
                role = Role(name=form.role.data)
                db.session.add(role)

            user = User(username=form.name.data, role=role)
            db.session.add(user)
            db.session.commit()

            flash('Estudante cadastrado com sucesso!')
        return redirect(url_for('alunos'))

    # Consulta todos os usuários cadastrados para listar na página
    users = User.query.all()
    
    return render_template('alunos.html', form=form, users=users)
    
