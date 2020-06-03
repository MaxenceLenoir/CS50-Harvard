from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
 
class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)

class Book(db.Model):
  __tablename__ = "books"
  id = db.Column(db.Integer, primary_key=True)
  isbn = db.Column(db.String, unique=True)
  title = db.Column(db.String, nullable=False)
  author = db.Column(db.String, nullable=False)
  year = db.Column(db.String, nullable=False)

class Avis(db.Model):
  __tablename__ = "avis"
  id = db.Column(db.Integer, primary_key=True)
  id_user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  id_book = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
  commentaire = db.Column(db.String)
  note = db.Column(db.Integer, nullable=False)