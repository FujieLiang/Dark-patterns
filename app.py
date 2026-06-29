import os
from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root1234@localhost/dark_patterns"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

# ---------- Database Models ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), default="#7F77DD")

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(120))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    description = db.Column(db.Text)
    harm = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    category = db.relationship("Category", backref="cases")

# ---------- Helper: save uploaded image ----------
def save_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        return "uploads/" + filename
    return None

# ---------- Auth Pages ----------
@app.route("/")
def home():
    return "<h1>Dark Patterns Tracker</h1><p><a href=\"/register-page\">Register</a> | <a href=\"/login-page\">Login</a> | <a href=\"/admin\">Admin</a></p>"

@app.route("/register-page")
def register_page():
    return render_template("register.html")

@app.route("/login-page")
def login_page():
    return render_template("login.html")

# ---------- Auth API ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "This email is already registered"}), 400
    new_user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful", "email": email}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    return jsonify({"message": "Login successful", "email": user.email, "role": user.role}), 200

# ---------- Admin: Case CRUD ----------
@app.route("/admin")
def admin():
    cases = Case.query.all()
    categories = Category.query.all()
    return render_template("admin.html", cases=cases, categories=categories)

@app.route("/admin/cases", methods=["POST"])
def create_case():
    image_url = save_image(request.files.get("image"))
    new_case = Case(
        title=request.form.get("title"),
        website=request.form.get("website"),
        category_id=request.form.get("category_id"),
        description=request.form.get("description"),
        harm=request.form.get("harm"),
        image_url=image_url,
    )
    db.session.add(new_case)
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/cases/<int:case_id>/edit")
def edit_case_page(case_id):
    case = Case.query.get_or_404(case_id)
    categories = Category.query.all()
    return render_template("edit.html", case=case, categories=categories)

@app.route("/admin/cases/<int:case_id>/update", methods=["POST"])
def update_case(case_id):
    case = Case.query.get_or_404(case_id)
    case.title = request.form.get("title")
    case.website = request.form.get("website")
    case.category_id = request.form.get("category_id")
    case.description = request.form.get("description")
    case.harm = request.form.get("harm")
    new_image = save_image(request.files.get("image"))
    if new_image:
        case.image_url = new_image
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/cases/<int:case_id>/delete", methods=["POST"])
def delete_case(case_id):
    case = Case.query.get_or_404(case_id)
    db.session.delete(case)
    db.session.commit()
    return redirect("/admin")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
