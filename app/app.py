from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKey

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
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
<<<<<<< Updated upstream
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(20))
=======
    descricao = db.Column(db.String, nullable=True)
>>>>>>> Stashed changes


class Servico(db.Model):
    __tablename__ = "servicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    local = db.Column(db.String(150), nullable=False)
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
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", erro="Email ou senha incorretos")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/cadastro-servicos", methods=["GET", "POST"])
@login_required
def cadastro_servicos():
    if request.method == "POST":
        nome = request.form["nome"]
        local = request.form["local"]
        descricao = request.form["descricao"]
        telefone = request.form.get("telefone")
        link = request.form.get("link")
        usuario_id = current_user.id

        novo = Servico(
            nome=nome,
            local=local,
            descricao=descricao,
            telefone=telefone,
            link=link,
            usuario_id=usuario_id
        )

        db.session.add(novo)
        db.session.commit()
        return render_template("cadastro-servicos.html", sucesso="Serviço cadastrado!")

    return render_template("cadastro-servicos.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_servico(id):
    servico = Servico.query.get_or_404(id)

    if request.method == "POST":
        servico.nome = request.form["nome"]
        servico.local = request.form["local"]
        servico.descricao = request.form["descricao"]

        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit.html", servico=servico)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


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
    except:
        resposta = "not found"
    return render_template("prestador.html", usuario=resposta)

if __name__ == "__main__":
    app.run(debug=True)
