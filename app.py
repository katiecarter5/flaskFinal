from functools import wraps
from flask import Flask, render_template, abort, request, redirect, url_for, g
import flask_login
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/{}'.format(app.root_path, 'final.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'b2de7FkqvkMyqzNFzxCkgnPKIGP6i4Rc'

db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = {'user': {'password': 'secret'}}


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    user.is_authenticated = request.form['password'] == users[email]['password']

    return user


class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(500), nullable=False)


class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(500), nullable=False)


class Shape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(500), nullable=False)


db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
            <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
            '''
    email = request.form['email']
    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('index'))

    return 'Bad login'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/browse')
def browse():
    letters = Letter.query.all()
    colors = Color.query.all()
    shapes = Shape.query.all()
    return render_template('browse.html', letters=letters, colors=colors, shapes=shapes)


@app.route('/letter/<name>')
def letter(name):
    letters = Letter.query.filter(Letter.name == name).first()
    return render_template('letter.html', letters=letters)


@app.route('/color/<name>')
def color(name):
    colors = Color.query.filter(Color.name == name).first()
    return render_template('color.html', colors=colors)


@app.route('/shape/<name>')
def shape(name):
    shapes = Shape.query.filter(Shape.name == name).first()
    return render_template('shape.html', shapes=shapes)


@app.route('/admin')
@flask_login.login_required
def admin():
    return render_template('admin/ad_home.html')


@app.route('/ad_letter')
@flask_login.login_required
def ad_letter():
    letters = Letter.query.all()
    return render_template('admin/ad_letter.html', letters=letters)


@app.route('/ad_letter/create', methods=("GET", "POST"))
@flask_login.login_required
def create_letter():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']

        error = None

        if not request.form['name']:
            error = 'Name is required'

        if error is None:
            letter = Letter(name=name, desc=desc)
            db.session.add(letter)
            db.session.commit()
            return redirect(url_for('ad_letter'))

    letter = Letter.query.all()
    return render_template('admin/letter_form.html', letter=letter)


@app.route('/admin/letter/edit/<id>', methods=("GET", "POST"))
@flask_login.login_required
def edit_letter(id):
    letter = Letter.query.get_or_404(id)

    if request.method == 'POST':
        letter.name = request.form['name']
        letter.desc = request.form['desc']

        error = None

        if not request.form['name']:
            error = 'Name is required'

        if error is None:
            db.session.commit()
            return redirect(url_for('ad_letter'))

    return render_template('admin/letter_form.html', name=letter.name, desc=letter.desc)


#color


@app.route('/admin/color')
@flask_login.login_required
def admin_color():
    color = Color.query.all()
    return render_template('admin/ad_color.html', color=color)


@app.route('/admin/color/create', methods=("GET", "POST"))
@flask_login.login_required
def create_color():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']

        error = None

        if not request.form['name']:
            error = 'Name is required'

        if error is None:
            color = Color(name=name, desc=desc)
            db.session.add(color)
            db.session.commit()
            return redirect(url_for('ad_color'))

    color = Color.query.all()
    return render_template('admin/color_form.html', color=color)


@app.route('/admin/color/edit/<id>', methods=('GET', 'POST'))
@flask_login.login_required
def edit_color(id):
    color = Color.query.get_or_404(id)

    if request.method == 'POST':
        color.name = request.form['name']
        color.desc = request.form['desc']


        error = None

        if not request.form['name']:
            error = 'Name is required'

        if error is None:
            db.session.commit()
            return redirect(url_for('ad_color'))

    return render_template('admin/color_form.html', name=color.name, desc=color.desc)


@app.route('/delete_color/<id>')
@flask_login.login_required
def delete_color(id):
    color = Color.query.get_or_404(id)
    db.session.delete(color)
    db.session.commit()
    return redirect(url_for('ad_color'))


# @app.route('/delete_color/<id>')
# @flask_login.login_required
# def delete_color(id):
#     color = Color.query.get_or_404(id)
#     db.session.delete(color)
#     db.session.commit()
#     return redirect(url_for('ad_color'))


# shape


@app.route('/admin/shape')
@flask_login.login_required
def admin_shape():
    shape = Shape.query.all()
    return render_template('admin/ad_shape.html', shape=shape)


@app.route('/admin/shape/create', methods=("GET", "POST"))
@flask_login.login_required
def create_shape():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']

        error = None

        if not request.form['name']:
            error = 'Name is required'

        if error is None:
            shape = Shape(name=name, desc=desc)
            db.session.add(shape)
            db.session.commit()
            return redirect(url_for('ad_shape'))

    shape = Shape.query.all()
    return render_template('admin/shape_form.html', shape=shape)


@app.route('/admin/shape/edit/<id>', methods=('GET', 'POST'))
@flask_login.login_required
def edit_shape(id):
    shape = Shape.query.get_or_404(id)

    if request.method == 'POST':
        shape.name = request.form['name']
        shape.desc = request.form['desc']


        error = None

        if not request.form['name']:
            error = 'Name is required'

        if error is None:
            db.session.commit()
            return redirect(url_for('ad_shape'))

    return render_template('admin/shape_form.html', name=shape.name, desc=shape.desc)


@app.route('/delete_shape/<id>')
@flask_login.login_required
def delete_shape(id):
    shape = Shape.query.get_or_404(id)
    db.session.delete(color)
    db.session.commit()
    return redirect(url_for('ad_shape'))


# @app.route('/delete_shape/<id>')
# @flask_login.login_required
# def delete_shape(id):
#     shape = Shape.query.get_or_404(id)
#     db.session.delete(shape)
#     db.session.commit()
#     return redirect(url_for('ad_shape'))


if __name__ == '__main__':
    app.run()