from flask import Blueprint, render_template, request, redirect, current_app, flash, send_file # type: ignore
from models import db, URL
from utils import gerar_codigo_curto
import qrcode # type: ignore
from io import BytesIO


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
        return render_template('index.html', url_curta=url_curta_completa, code=codigo_curto)

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

@main.route('/qrcode/<short_code>')
def serve_qrcode(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first_or_404()
    url_curta_completa = request.host_url + short_code

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_curta_completa)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    byte_io = BytesIO()
    img.save(byte_io, format='PNG')
    byte_io.seek(0)

    return send_file(byte_io, mimetype='image/png', as_attachment=False, download_name=f'qrcode_{short_code}.png')


@main.route('/urls', methods=['GET', 'POST'])
def stats():
    url_encontrada = None
    erro = None

    if request.method == 'POST':
        codigo_curto = request.form['short_code']
        url_entry = URL.query.filter_by(short_code=codigo_curto).first()
        
        if url_entry:
            url_encontrada = url_entry
        else:
            erro = 'Código curto não encontrado.'

    return render_template('stats.html', link=url_encontrada, error=erro)


@main.app_errorhandler(404)
def page_not_found(e):
    
    return render_template('404.html'), 404