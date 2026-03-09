import os
import io
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKey
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
from vercel_blob import put

load_dotenv()

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = 'static/uploads/perfil'
app.config["ALLOWED_EXTENSIONS"] = {'png', 'jpg', 'jpeg'}
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String, nullable=True)
    foto_perfil = db.Column(db.String, nullable=True)


class Servico(db.Model):
    __tablename__ = "servicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    local = db.Column(db.String(150), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    logradouro = db.Column(db.String(150), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    numero = db.Column(db.String(7), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(20))
    link = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, ForeignKey("usuarios.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "local": self.local,
            "descricao": self.descricao,
            "telefone": self.telefone,
            "link": self.link
        }


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.before_request
def criar_banco():
    db.create_all()


@app.context_processor
def injeta_logado():
    return dict(logado=current_user.is_authenticated)

# rotas publicas
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        nome = request.form["nome"]

        if Usuario.query.filter_by(email=email).first():
            return render_template("registrar.html", erro="Este e-mail já está em uso.")

        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

        novo = Usuario(email=email, senha=senha_hash, nome=nome)
        db.session.add(novo)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("registrar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        user = Usuario.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", erro="Email ou senha incorretos")

    return render_template("login.html")

@app.route("/inicio")
def inicio():
    return render_template("index.html")


@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.json.get("query", "").lower()

    resultados = Servico.query.filter(
        (db.func.lower(Servico.nome).like(f"%{query}%")) |
        (db.func.lower(Servico.local).like(f"%{query}%")) |
        (db.func.lower(Servico.descricao).like(f"%{query}%"))
    ).all()

    print(resultados)

    return jsonify({
        "logado": current_user.is_authenticated,
        "servicos": [s.to_dict() for s in resultados]
    })


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/add", methods=["POST"])
def add():
    data = request.json

    novo = Servico(
        nome=data["nome"],
        local=data["local"],
        descricao=data["descricao"]
    )

    db.session.add(novo)
    db.session.commit()

    return jsonify({"status": "ok", "mensagem": "Serviço cadastrado"})


@app.route("/prestador/<int:id>", methods=["GET"])
def prestador(id):
    try:
        resposta = Usuario.query.get_or_404(id)
        servicos = Servico.query.filter_by(usuario_id=resposta.id).all()
    except:
        resposta = "not found"
    return render_template("prestador.html", usuario=resposta, servicos=servicos)


@app.route("/servico/<int:id>", methods=["GET"])
def servico(id):
    try:
        servico = Servico.query.get_or_404(id)
        prestador = Usuario.query.filter_by(id=servico.usuario_id).first()
        return render_template("pagina-servicos.html", servico=servico, prestador=prestador)
    except:
        servico = "not found"
        return render_template("pagina-servicos.html", servico=servico)



# rotas privadas
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/cadastro-servicos", methods=["GET", "POST"])
@login_required
def cadastro_servicos():
    sucesso = None

    if request.method == "POST":
        nome = request.form["nome"]
        local = f"{request.form['cidade']} - {request.form['uf']}"
        cep = request.form["cep"].replace("-", "")
        logradouro = request.form["logradouro"]
        cidade = request.form['cidade']
        estado = request.form['uf']
        numero = request.form['numero']
        descricao = request.form["descricao"]
        telefone = request.form.get("telefone")
        link = request.form.get("link")
        usuario_id = current_user.id

        novo = Servico(
            nome=nome,
            local=local,
            cep=cep,
            logradouro=logradouro,
            cidade=cidade,
            estado=estado,
            numero=numero,
            descricao=descricao,
            telefone=telefone,
            link=link,
            usuario_id=usuario_id
        )

        db.session.add(novo)
        db.session.commit()

        sucesso = "Serviço cadastrado com sucesso."

    return render_template("cadastro-servicos.html", sucesso=sucesso)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_servico(id):
    servico = Servico.query.get_or_404(id)

    if servico.usuario_id != current_user.id:
        return redirect(url_for("index"))

    if request.method == "POST":
        servico.nome = request.form["nome"]
        servico.local = f"{request.form['cidade']} - {request.form['uf']}"
        servico.cep = request.form["cep"].replace("-", "")
        servico.logradouro = request.form["logradouro"]
        servico.cidade = request.form['cidade']
        servico.estado = request.form['uf']
        servico.numero = request.form['numero']
        servico.telefone = request.form.get("telefone")
        servico.link = request.form.get("link")
        servico.descricao = request.form["descricao"]

        db.session.commit()
        return redirect(url_for("meus_workes"))

    return render_template("edit.html", servico=servico)




@app.route("/meus-workes")
@login_required
def meus_workes():
    resultados = Servico.query.filter_by(usuario_id=current_user.id).all()

    return render_template("meus-workes.html", servicos=resultados)



@app.route("/meu-perfil", methods=["GET", "POST"])
@login_required
def meu_perfil():
    if request.method == "POST":
        if current_user.email != request.form["email"]:
            email = request.form["email"]
            usuario_banco = Usuario.query.filter_by(email=email).first()
            if usuario_banco:
                return render_template("meu-perfil.html", usuario=current_user,
                                       contexto={"mensagem": "Email ja em uso", "erro": True})

        usuario = Usuario.query.filter_by(id=current_user.id).first()

        usuario.nome = request.form["nome"]
        usuario.descricao = request.form["bio"]
        usuario.email = request.form["email"]

        db.session.commit()
        return render_template("meu-perfil.html", usuario=current_user,
                               contexto={"mensagem": "Alterações aplicadas com sucesso", "erro": False})

    return render_template("meu-perfil.html", usuario=current_user)

@app.route("/deletar-servico/<int:id>", methods=["POST"])
@login_required
def deletar_servico(id):
    servico = Servico.query.get_or_404(id)

    if servico.usuario_id != current_user.id:
        return redirect(url_for("index"))

    db.session.delete(servico)
    db.session.commit()

    return redirect(url_for("meus_workes"))


@app.route("/upload-foto", methods=["POST"])
@login_required
def carregar_foto():
    contexto = {"erro": False, "mensagem": ""}

    if 'foto' not in request.files:
        contexto.update({"erro": True, "mensagem": "Nenhum arquivo enviado."})
        return render_template("meu-perfil.html", usuario=current_user, contexto=contexto)

    file = request.files['foto']

    if file.filename == '':
        contexto.update({"erro": True, "mensagem": "Por favor, selecione uma imagem."})
        return render_template("meu-perfil.html", usuario=current_user, contexto=contexto)

    if file and allowed_file(file.filename):
        try:
            img = Image.open(file)

            if img.mode != "RGB":
                img = img.convert("RGB")

            largura_orig, altura_orig = img.size
            target_size = 1080

            if largura_orig < altura_orig:
                nova_largura = target_size
                nova_altura = int((target_size / largura_orig) * altura_orig)
            else:
                nova_altura = target_size
                nova_largura = int((target_size / altura_orig) * largura_orig)

            img = img.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)

            if not os.environ.get('VERCEL'):
                filename = secure_filename(f"perfil_{current_user.id}.jpg")
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename).replace("\\", "/")
                print(save_path)
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                img.save(save_path, "JPEG", quality=80)
                current_user.foto_perfil = save_path
            else:
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)

                blob = put(f"perfil_{current_user.id}.jpg", buffer.read(), {"access": "public", "allowOverwrite": True})

                current_user.foto_perfil = blob.get('url')

            db.session.commit()

            contexto.update({"erro": False, "mensagem": "Foto de perfil atualizada com sucesso!"})
        except Exception as e:
            db.session.rollback()
            contexto.update({"erro": True, "mensagem": f"Erro interno: {str(e)}"})
    else:
        contexto.update({"erro": True, "mensagem": "Formato inválido! Use PNG, JPG ou JPEG."})

    return render_template("meu-perfil.html", usuario=current_user, contexto=contexto)


def allowed_file(filname):
    return '.' in filname and \
        filname.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


if __name__ == "__main__":
    app.run(debug=True)
