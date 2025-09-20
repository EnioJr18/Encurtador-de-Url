# app.py

import string
import random
from flask import Flask, render_template, request, redirect  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)


def gerar_codigo_curto():
    caracteres = string.ascii_letters + string.digits
    codigo = ''.join(random.choices(caracteres, k=6))
    return codigo


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_original = request.form['url']
        codigo_curto = gerar_codigo_curto()

        while URL.query.filter_by(short_code=codigo_curto).first() is not None:
            codigo_curto = gerar_codigo_curto()

        nova_url = URL(original_url=url_original, short_code=codigo_curto)
        db.session.add(nova_url)
        db.session.commit()

        url_curta_completa = request.host_url + codigo_curto
        return render_template('index.html', url_curta=url_curta_completa)

    return render_template('index.html')


@app.route('/<codigo_curto>')
def redirecionar_url(codigo_curto):
    url_entry = URL.query.filter_by(short_code=codigo_curto).first_or_404()
    return redirect(url_entry.original_url)


@app.route('/urls')
def listar_urls():
    urls = URL.query.all()
    return render_template('urls.html', urls=urls)


if __name__ == '__main__':
    app.run(debug=True)
