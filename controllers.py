from flask import Blueprint, render_template, request, redirect, current_app, flash # type: ignore
from models import db, URL
from utils import gerar_codigo_curto


main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_original = request.form['url']
        codigo_curto = request.form.get('custom_url')

        if codigo_curto:
            existente = URL.query.filter_by(short_code=codigo_curto).first()
            if existente:
                flash('O código curto personalizado já está em uso. Tente outro.', 'error')
                return render_template('index.html')
            
            else:
                codigo_curto = codigo_curto
        else:
            codigo_curto = gerar_codigo_curto()
            while URL.query.filter_by(short_code=codigo_curto).first():
                codigo_curto = gerar_codigo_curto()

        

        nova_url = URL(original_url=url_original, short_code=codigo_curto)
        db.session.add(nova_url)
        db.session.commit()

        url_curta_completa = request.host_url + codigo_curto
        return render_template('index.html', url_curta=url_curta_completa)

    return render_template('index.html')

@main.route('/<codigo_curto>')
def redirecionar_url(codigo_curto):
    url_entry = URL.query.filter_by(short_code=codigo_curto).first_or_404()
    
    url_entry.click_count += 1
    url_entry.acesso_data = db.func.now()
    
    db.session.commit()

    
    return redirect(url_entry.original_url)

@main.route('/urls')
def listar_urls():
    urls = URL.query.all()
    return render_template('urls.html', urls=urls)