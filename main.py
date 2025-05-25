import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from models import User, Note, Task, db
from functools import wraps
import random
import datetime
from werkzeug.utils import secure_filename
import calendar
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///dados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = 'GUILHERMECASTRO'
UPLOAD_FOLDER = 'static/img/users_profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

default_profile_pics = ['profile1.png', 'profile2.png', 'profile3.png', 'profile4.png', 'profile5.png',
                'profile6.png', 'profile7.png', 'profile8.png', 'profile9.png', 'profile10.png']

meses_portugues = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
dias_semana_portugues = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

@app.route('/')
def home():
    return render_template('home.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method=='POST':     
        primeiro_nome=request.form.get('primeiro_nome')
        email=request.form.get('email')
        senha=request.form.get('senha')
        confirmar_senha=request.form.get('confirmar_senha')
        email_duplicado=User.query.filter_by(email=email).first()
        
        if email_duplicado:
            flash('Este e-mail já está cadastrado no sistema, faça login', 'error')
            return render_template('registro.html', primeiro_nome=primeiro_nome, email=email)
        
        if senha != confirmar_senha:
            flash('As senhas nao coincidem, Tente novamente', 'error')
            return render_template('registro.html', primeiro_nome=primeiro_nome, email=email)
        
        if  len(primeiro_nome.split()) > 1:
            flash('Por favor, digite apenas o seu primeiro nome.', 'error')
            return render_template('registro.html', primeiro_nome=primeiro_nome, email=email)
        
        else:
            random_profile_pic = random.choice(default_profile_pics)
            user = User(first_name=primeiro_nome, email=email, profile_pic=random_profile_pic)
            user.set_password(senha)
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso', 'success')
            return redirect(url_for('login'))          
    
    return render_template('registro.html') 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        senha=request.form.get('senha')
        email_existente=User.query.filter_by(email=email).first()
        if email_existente and email_existente.check_password(senha):
            session['user_id'] = email_existente.id
            hoje = datetime.date.today()
            hoje = datetime.date.today()
            data_formatada = f"{hoje.day:02d}-{hoje.month:02d}-{hoje.year}"
            return redirect(url_for('dashboard_dia_url', data=data_formatada))
        elif email_existente:
            flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    return render_template('login.html')

@app.route('/dashboard/<data>') # data é "dd-mm-yyyy"
@login_required
def dashboard_dia_url(data):
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    current_datetime_for_fallback = datetime.datetime.now() # Para fallback nos formulários e se data for inválida

    try:
        dia, mes, ano = map(int, data.split('-'))
        data_obj = datetime.date(ano, mes, dia)
        data_exibicao = f"{data_obj.day:02d}/{data_obj.month:02d}/{data_obj.year}" # Formato dd/mm/yyyy para exibir

        # Calcular datas para os botões de navegação
        dia_anterior_obj = data_obj - datetime.timedelta(days=1)
        dia_seguinte_obj = data_obj + datetime.timedelta(days=1)

        # Formatar para o parâmetro 'data' do URL (dd-mm-yyyy)
        link_dia_anterior = f"{dia_anterior_obj.day:02d}-{dia_anterior_obj.month:02d}-{dia_anterior_obj.year}"
        link_dia_seguinte = f"{dia_seguinte_obj.day:02d}-{dia_seguinte_obj.month:02d}-{dia_seguinte_obj.year}"

    except ValueError:
        flash('Formato de data inválido na URL do dashboard.', 'error')
        # Redireciona para a agenda do ano atual em caso de erro de data
        return redirect(url_for('agenda', ano=current_datetime_for_fallback.year))

    nota_do_dia = Note.query.filter_by(user_id=user_id, date=data_obj).first()
    tarefas_do_dia = Task.query.filter_by(user_id=user_id, date=data_obj).all()

    return render_template('dashboard.html',
                           user=user,
                           data_exibicao=data_exibicao,
                           data_param_original=data, # data no formato dd-mm-yyyy
                           now=current_datetime_for_fallback, # Usado nos formulários como fallback
                           nota=nota_do_dia,
                           tarefas=tarefas_do_dia,
                           prev_date_link=link_dia_anterior,  # Nova variável
                           next_date_link=link_dia_seguinte) # Nova variável

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    now = datetime.datetime.now()

    # Pega a data de onde o usuário veio, para o botão "Voltar"
    last_viewed_date_str = request.args.get('from_date') # Formato esperado: dd-mm-yyyy

    if not last_viewed_date_str: # Fallback
        last_viewed_date_str = now.strftime('%d-%m-%Y')

    if request.method == 'POST':
        new_name = request.form.get('nome')
        if len(new_name.split()) > 1:
            flash('Por favor, digite apenas o seu primeiro nome.', 'error')
        else:
            user.first_name = new_name
            db.session.commit()
            flash('Nome atualizado com sucesso!', 'success')
        # Ao re-renderizar após POST, também passe data_filtrada
        return render_template('perfil.html',
                               user=user,
                               now=now,
                               default_pics_list=default_profile_pics, # Não esqueça esta lista
                               data_filtrada=last_viewed_date_str)

    return render_template('perfil.html',
                           user=user,
                           now=now,
                           default_pics_list=default_profile_pics, # E aqui também
                           data_filtrada=last_viewed_date_str)

@app.route('/atualizar_foto', methods=['POST'])
@login_required
def atualizar_foto():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    nova_foto = request.files.get('nova_foto')

    if nova_foto:
        if allowed_file(nova_foto.filename):
            filename = secure_filename(nova_foto.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            nova_foto.save(filepath)
            if user.profile_pic not in ['default1.png', 'default2.png', ..., 'default10.png']:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            elif user.profile_pic != 'default.png':
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            user.profile_pic = filename
            db.session.commit()
            flash('Foto de perfil atualizada com sucesso!', 'success')
        else:
            flash('Formato de arquivo não permitido.', 'error')
    return redirect(url_for('perfil'))

@app.route('/agenda')
@login_required
def agenda():
    hoje = datetime.date.today()
    # Tenta pegar o ano da URL se existir (caso você queira essa funcionalidade)
    # Para este problema específico, o 'ano_selecionado' para a lógica da agenda pode ser o do from_date ou hoje.
    # Vamos manter a lógica original do ano, e focar no from_date para o botão voltar.
    ano_selecionado = request.args.get('ano', default=hoje.year, type=int)

    cal = calendar.Calendar(firstweekday=0)
    calendario_ano = {}
    now = datetime.datetime.now() # 'now' para fallback

    for mes in range(1, 13):
        dias_do_mes = cal.monthdays2calendar(ano_selecionado, mes)
        calendario_ano[mes] = dias_do_mes

    # Pega a data de onde o usuário veio, para o botão "Voltar"
    last_viewed_date_str = request.args.get('from_date') # Formato esperado: dd-mm-yyyy

    if not last_viewed_date_str: # Fallback se não for fornecido
        last_viewed_date_str = now.strftime('%d-%m-%Y')

    return render_template('agenda.html',
                           calendario=calendario_ano,
                           meses=meses_portugues,
                           dias_semana=dias_semana_portugues,
                           ano=ano_selecionado, # O ano que a agenda está mostrando
                           now=now,
                           data_filtrada=last_viewed_date_str, # Para o botão "Voltar"
                           # Você pode adicionar dia_atual, mes_atual, ano_atual se precisar para destacar o dia na agenda
                           dia_atual=now.day,
                           mes_atual=now.month,
                           ano_atual=now.year )
    
@app.route('/salvar_nota', methods=['POST'])
@login_required
def salvar_nota():
    user_id = session.get('user_id')
    content = request.form.get('content')
    data_str = request.form.get('data')

    if not data_str:
        flash('Erro ao salvar a nota: data não especificada.', 'error')
        return redirect(request.referrer)

    try:
        ano, mes, dia = map(int, data_str.split('-'))
        data_nota = datetime.date(ano, mes, dia)
    except ValueError:
        flash('Erro ao salvar a nota: formato de data inválido.', 'error')
        return redirect(request.referrer)

    nota = Note.query.filter_by(user_id=user_id, date=data_nota).first()

    if nota:
        nota.content = content
        nota.updated_at = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
        db.session.commit()
        flash('Nota atualizada com sucesso!', 'success')
    else:
        nova_nota = Note(content=content, date=data_nota, user_id=user_id)
        db.session.add(nova_nota)
        db.session.commit()
        flash('Nota salva com sucesso!', 'success')

    return redirect(request.referrer)

@app.route('/adicionar_tarefa', methods=['POST'])
@login_required
def adicionar_tarefa():
    user_id = session.get('user_id')
    nome_tarefa = request.form.get('nome_tarefa')
    data_str = request.form.get('data')
    cor_tarefa = request.form.get('cor_tarefa')

    if not nome_tarefa:
        flash('O nome da tarefa não pode estar vazio.', 'error')
        return redirect(request.referrer)

    if not data_str:
        flash('Erro ao adicionar tarefa: data não especificada.', 'error')
        return redirect(request.referrer)

    try:
        ano, mes, dia = map(int, data_str.split('-'))
        data_tarefa = datetime.date(ano, mes, dia)
    except ValueError:
        flash('Erro ao adicionar tarefa: formato de data inválido.', 'error')
        return redirect(request.referrer)

    nova_tarefa = Task(name=nome_tarefa, date=data_tarefa, user_id=user_id, color=cor_tarefa)
    db.session.add(nova_tarefa)
    db.session.commit()
    flash('Tarefa adicionada com sucesso!', 'success')

    return redirect(request.referrer)

@app.route('/toggle_tarefa/<int:tarefa_id>', methods=['POST'], endpoint='toggle_tarefa')
@login_required
def toggle_tarefa(tarefa_id):
    tarefa = Task.query.get_or_404(tarefa_id)
    if tarefa.user_id != session.get('user_id'):
        flash('Você não tem permissão para alterar esta tarefa.', 'error')
        return redirect(request.referrer)
    tarefa.done = not tarefa.done
    db.session.commit()
    return redirect(request.referrer)

@app.route('/deletar_tarefa/<int:tarefa_id>', methods=['POST'])
@login_required
def deletar_tarefa(tarefa_id):
    user_id = session.get('user_id')
    tarefa = Task.query.get_or_404(tarefa_id)

    # Verifica se a tarefa pertence ao usuário logado
    if tarefa.user_id != user_id:
        flash('Você não tem permissão para deletar esta tarefa.', 'error')
        # Redireciona para a página anterior ou para o dashboard do dia da tarefa
        data_redirect = f"{tarefa.date.day:02d}-{tarefa.date.month:02d}-{tarefa.date.year}"
        return redirect(request.referrer or url_for('dashboard_dia_url', data=data_redirect))

    try:
        db.session.delete(tarefa)
        db.session.commit()
        flash('Tarefa deletada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar a tarefa: {str(e)}', 'error')

    data_redirect = f"{tarefa.date.day:02d}-{tarefa.date.month:02d}-{tarefa.date.year}"
    return redirect(request.referrer or url_for('dashboard_dia_url', data=data_redirect))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

