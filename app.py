from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    shortened_url = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return f"{self.original_url} -> {self.shortened_url}"

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/history')
def history():
    urls = Url.query.all()
    return render_template('history.html', urls=urls)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    existing_url = Url.query.filter_by(original_url=original_url).first()

    if existing_url:
        return redirect(url_for('show_short_url', shortened_url=existing_url.short_url))

    shortened_url = generate_short_url()
    new_url = Url(original_url=original_url, shortened_url=shortened_url)
    db.session.add(new_url)
    db.session.commit()

    return redirect(url_for('show_short_url', shortened_url=shortened_url))

@app.route('/<string:shortened_url>')
def redirect_to_url(shortened_url):
    url = Url.query.filter_by(shortened_url=shortened_url).first_or_404()
    return redirect(url.original_url)

@app.route('/show/<string:shortened_url>')
def show_short_url(shortened_url):
    url = Url.query.filter_by(shortened_url=shortened_url).first_or_404()
    return render_template('shortened_url.html', shortened_url=request.host_url + url.short_url)

def generate_short_url():
    length = 6
    chars = string.ascii_letters + string.digits
    while True:
        shortened_url = ''.join(random.choice(chars) for _ in range(length))
        if not Url.query.filter_by(shortened_url=shortened_url).first():
            return shortened_url

if __name__ == '__main__':
    app.run(debug=True)

