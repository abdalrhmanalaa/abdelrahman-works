import os
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# =====================
# Models
# =====================

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    service = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(50), default="pending")

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(500))

with app.app_context():
    db.create_all()

# =====================
# Admin Login
# =====================

ADMIN_USER = "admin"
ADMIN_PASS_HASH = generate_password_hash("1234")  # غيرها

# =====================
# Routes
# =====================

@app.route("/")
def home():
    projects = Project.query.all()
    return render_template("index.html", projects=projects)

@app.route("/send", methods=["POST"])
def send():
    msg = Message(
        name=request.form.get("name"),
        email=request.form.get("email"),
        message=request.form.get("message")
    )
    db.session.add(msg)
    db.session.commit()
    return redirect("/")

@app.route("/order", methods=["POST"])
def order():
    new_order = Order(
        name=request.form.get("name"),
        service=request.form.get("service"),
        phone=request.form.get("phone")
    )
    db.session.add(new_order)
    db.session.commit()
    return "حول على فودافون كاش وابعِت سكرين على واتساب ✅"

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and check_password_hash(ADMIN_PASS_HASH, password):
            session["admin"] = True
            return redirect("/admin")

    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    messages = Message.query.all()
    orders = Order.query.all()

    return render_template("admin.html",
        messages=messages,
        orders=orders,
        total_messages=Message.query.count(),
        total_orders=Order.query.count(),
        total_projects=Project.query.count()
    )

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "")

    if "سعر" in msg:
        reply = "الأسعار تبدأ من 500 جنيه 💰"
    elif "وقت" in msg:
        reply = "3 إلى 7 أيام ⏳"
    else:
        reply = "ابعت تفاصيلك وهساعدك 👌"

    return jsonify({"reply": reply})

@app.route("/add_project", methods=["POST"])
def add_project():
    if not session.get("admin"):
        return redirect("/login")

    file = request.files['image']
    title = request.form.get("title")

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        project = Project(title=title, image_url=filename)
        db.session.add(project)
        db.session.commit()

    return redirect("/admin")

@app.route("/delete/<string:item_type>/<int:id>")
def delete_item(item_type, id):
    if not session.get("admin"):
        return redirect("/login")

    if item_type == "msg":
        item = Message.query.get(id)
    elif item_type == "order":
        item = Order.query.get(id)
    else:
        item = None

    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

if __name__ == "__main__":
    app.run()