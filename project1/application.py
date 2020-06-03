import os, json

from flask import Flask, session,  render_template, request, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from model import *

from werkzeug.security import check_password_hash, generate_password_hash

import requests

app = Flask(__name__)

# Verification du bon parametrage de la variable "DATABASE_URL" (à faire dans la commance avec "export")
if not os.getenv("DATABASE_URL"):
      raise RuntimeError("DATABASE_URL is not set")

# Configuration de session (Ici, j'ai pas tout compris ...)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Session(app)

# Set up la database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Chemin vers la page d'accueil, on initialise la variable de session : None (Non connecté)
@app.route("/")
def index():
  global MonCompte
  MonCompte = None
  return render_template("Accueil.html")

# Chemin vers la page d'inscription
@app.route("/inscription", methods = ["GET", "POST"])
def inscription():

  # Si on arrive sur cette page via une saisie utilisateur, passage dans la branche ci-dessous>
  # Sinon rendez-vous à la fin
  if request.method == "POST":

    # Liste de messages d'erreur en fonction des saisies utilisateurs

    if not request.form.get("name"):
      return render_template("Erreur.html", message="Idenfiant non saisi")

    elif not request.form.get("password"):
      return render_template("Erreur.html", message="Mot de passe non saisi")
    
    elif not request.form.get("confirmation"):
      return render_template("Erreur.html", message="Confirmation mot de passe non saisi")
    
    # Comparaison des identifiants présents dans la base de données et de la saisie de l'utilisateur
    userCheck = db.execute("SELECT * FROM users WHERE name = :name", {"name":request.form.get("name")}).fetchone()

    # Si non nul, identifiant déjà utilisé
    if userCheck:
      return render_template("Erreur.html", message="Le nom d'utilisateur a déjà été utilisé")

    # Vérification de la correspondance du mot de passe et de la confirmation
    elif not request.form.get("password") == request.form.get("confirmation"):
      return render_template("Erreur.html", message="Les mots de passe ne correspondent pas.")

    # Cryptage du mot de passe  
    hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
  
    # Insertion des données saisies dans la base de données
    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name":request.form.get("name"), "password":hashedPassword})

    # On commit les changement (= validation)
    db.commit()
    
    # Message flash
    #flash('Account created', 'info')

    # On redirige vers la page d'accueil une fois l'inscription terminée
    return redirect("/")

  # Ouverture de la page d'inscription
  else:
    return render_template("Inscription.html")

# Chemin vers la page de Login
@app.route("/login", methods = ["GET", "POST"])
def login():

  # On redéfinit la valeur comme nulle avant la connexion (normalement, pas nécessaire si l'utilisateur s'est deloggé correctement)
  global MonCompte
  MonCompte = None
  
  # Si on arrive sur cette page via une saisie utilisateur, passage dans la branche ci-dessous>
  # Sinon rendez-vous à la fin
  if request.method == "POST":

    # Liste de messages d'erreur en fonction des saisies utilisateurs

    if not request.form.get("name"):
      return render_template("Erreur.html", message="Idenfiant non saisi")

    if not request.form.get("password"):
      return render_template("Erreur.html", message="Mot de passe non saisi")

    recherche_user = db.execute("SELECT * FROM users WHERE name = :name", {"name":request.form.get("name")}).fetchone()

    if recherche_user == None:
      return render_template("Erreur.html", message="Cet identifiant n'existe pas")
    
    elif not check_password_hash(recherche_user.password, request.form.get("password")):
      return render_template("Erreur.html", message="Le mot de passe et l'identifiant ne correspondent pas")

    if recherche_user == None:
      return render_template("Erreur.html", message="L'ID et/ou le mot de passe renseigné n'est pas le bon  ")  

    # Si tout est OK, on garde en mémoire le nom d'utilisateur dans la variable globale et on se dirige vers la page suivante
    MonCompte = request.form.get("name")
    return redirect("/MonCompte") 
  
  # Ouverture de la page de Login
  else:
    return render_template("Login.html")

# Chemin vers la page de Logout
@app.route("/logout")
def logout():

  # On réinitialise la variable global d'idendification comme "None"
  global MonCompte
  MonCompte = None

  # Ouverture de la page de Logout   
  return render_template("Logout.html")

# Chemin vers la page de Login
@app.route("/MonCompte", methods = ["GET", "POST"])
def MonCompte():

  # Si on arrive sur cette page est que la variable d'idenfication est vide, alors Erreur
  if MonCompte != None:

    if request.method == "POST":
      
      # Si on ne saisi aucune valeur dans la barre de recherche, erreur.
      # "request.value.get" permet de segmenter les différents mots saisis par l'utilisateur

      if not request.values.get("livre"):
        return render_template("Erreur.html", message="Aucune recherche saisie")

      # On recherche toutes les potentielles correspondances avec les mots saisis

      recherche_bouquin = "%" + request.values.get("livre") + "%"

       # On passe la première lettre des mots saisis en majuscule

      recherche_bouquin.title()

      rows = db.execute("SELECT id, isbn, title, author, year FROM books WHERE\
                          isbn LIKE :recherche_bouquin OR \
                          title LIKE :recherche_bouquin OR \
                          author LIKE :recherche_bouquin LIMIT 15", {"recherche_bouquin":recherche_bouquin})

      if rows.rowcount == 0:
        return render_template("Erreur.html", message="Pas de bouquins trouvés ..")

      # On renvoie dans la variable "livres", tous les résultats trouvés
      livres = rows.fetchall()
      return render_template("Resultat.html", livres=livres, MonCompte=MonCompte)

    else:
      return render_template("MonCompte.html", MonCompte=MonCompte)
  
  else:
    return render_template("Erreur.html", message="Accès refusé. Vous n'êtes pas connecté")

# Chemin vers la page des résultats (inutile ici)
@app.route("/resultat", methods = ["GET", "POST"])
def resultat():

  return render_template("Resultat.html", MonCompte=MonCompte)

# Chemin vers la page d'un livre en particulier
@app.route("/livre/<isbn>", methods = ["GET", "POST"])
def livre(isbn):

  # Si on arrive sur cette page via une saisie utilisateur, la branche suivante est déclenchée
  if request.method == "POST":

    # On récupère l'id du livre grâce à l'ibsn présent dans l'URL
    row = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    id_book = row.id

    # On recupère l'id user grâce à la variable globale
    row = db.execute("SELECT id FROM users WHERE name=:name", {"name":MonCompte}).fetchone()
    id_user = row.id

    # On recupère le commentaire et la note saisie par l'utilisateur
    commentaire = request.form.get("commentaire")
    note = request.form.get("note")

    # On cherche dans la base de données si l'utilisateur n'a pas déjà laissé un avis sur ce livre
    row = db.execute("SELECT * FROM avis WHERE id_book =:id_book AND id_user =:id_user", {"id_book":id_book, "id_user":id_user}).fetchone()

    # S'il y a un avis => Erreur
    if row != None:
      return render_template("Erreur.html", message="Vous avez déjà sais un commentaire pour ce livre")

    # Sinon, on ajoute le commentaire et la note dans la base de données
    else:     
      db.execute("INSERT INTO avis(id_user, id_book, commentaire, note) VALUES (:id_user, :id_book, :commentaire, :note)", {"id_user":id_user, "id_book":id_book, "commentaire":commentaire, "note":note})
      db.commit()
      return redirect ("/livre/" + isbn)
  
  # Si on arrive sur cette page par une autre manière, la branche suivante est déclenchée
  else:

    # On recupère les infos du livre grâce à l'isbn de l'URL
    row = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn})

    # On les stock dans la variable "bookInfo"
    bookInfo = row.fetchall()

    # Recuperation de la clé depuis la variable "GOODREADS_KEY" (à faire dans la commance avec "export")
    key = os.getenv("GOODREADS_KEY")
    
    # Recuperation des données depuis l'API Goodreads selon recommandation "Get review statistics given a list of ISBNs"
    recuperation_cle = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    reponse = recuperation_cle.json()

    # On ne garde en mémoire que le premier résultat renvoyé par l'API (ce qui est normalement déjà le cas)
    reponse = reponse["books"][0]

    # On ajoute ces données dans la variable bookInfo 
    bookInfo.append(reponse)
          
    # On recupère l'id du livre grâce à l'isbn de l'URL
    row = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn})
    book = row.fetchone()
    book = book.id

    # On recupère tous les noms commentaires et notes ainsi que le nom d'utilisateur associé pour le livre en question
    results = db.execute("SELECT users.name, commentaire, note FROM users INNER JOIN avis ON users.id = avis.id_user WHERE id_book = :book", {"book": book})
    avis = results.fetchall()

    return render_template("Livre.html", avis=avis, bookInfo=bookInfo, MonCompte=MonCompte)

@app.route("/api/<isbn>", methods = ["GET"])
def livreapi(isbn):

  # Retourne les infos d'un livre
  livre_api = db.execute("SELECT title, isbn, author, year, COUNT(avis.id) as compt_avis, AVG(avis.note) as moyenne_avis FROM books INNER JOIN avis ON books.id = avis.id_book WHERE isbn = :isbn GROUP BY title, author, year, isbn", {"isbn": isbn}).fetchone()
  
  if livre_api == None:
    return jsonify({"error": "Numero du livre invalide"}), 422
  
  return jsonify({
          "title": livre_api.title,
          "isbn": livre_api.isbn,
          "author": livre_api.author,
          "year": livre_api.year,
          "compt_avis": livre_api.compt_avis,
          "moyenne_avis": float('%.2f'%(livre_api.moyenne_avis))
          })

#def SupprimerMonAvis(isbn_livre):

#  row_user = db.execute("SELECT id FROM users WHERE name=:name", {"name":MonCompte}).fetchone()
#  id_user = row_user.id

#  row_livre = db.execute("SELECT id FROM books WHERE isbn=:isbn", {"isbn":isbn_livre}).fetchone()
#  id_livre = row_livre.id

#  row_avis = db.execute("SELECT * FROM avis WHERE id_book =:id_book AND id_user =:id_user", {"id_book":id_livre, "id_user":id_user}).fetchone()

#  if row != None:
#    db.execute("DELETE * FROM avis WHERE id_user=:id_user AND id_book=:id_book",{"id_user":MonCompte, "id_book":id_book})
#    return render_template("Erreur.html", message="Votre Commentaire a bien été supprimer")
  
#  else:
#    return render_template("Erreur.html", message="Il n'y a pas de commentaire à supprimer")