import os

from collections import deque

from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room

from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chaines = []

utilisateurs=[]

Messages = dict()

@app.route("/", methods = ["GET", "POST"])  
@login_required
def index():

  return render_template("Accueil.html", chaines=chaines)

@app.route("/Login", methods=['GET','POST'])
def signin():
  ''' Save the username on a Flask session 
  after the user submit the sign in form '''

  # Effacer le nom présent en mémoire
  session.clear()

  nom = request.form.get("nom")
  
  if request.method == "POST":

    if len(nom) < 1 or nom is '':
      return render_template("Error.html")

    if nom in utilisateurs:
      return render_template("Error.html")                   
    
    utilisateurs.append(nom)

    session['nom'] = nom

    # Garder en mémoire dans les cookies le nom de l'utilisateur si on ferme le navigateur.
    session.permanent = True

    return redirect("/")

  else:

    return render_template("Login.html")

@app.route("/Logout", methods = ["GET", "POST"])  
def logout():

  try:
    utilisateurs.remove(session['nom'])
  except ValueError:
    pass

  session.clear()

  return redirect("/")

@app.route("/Accueil", methods = ["GET", "POST"])  
def accueil():

  nouvellechaine = request.form.get("nouvellechaine")

  if request.method == "POST":

    if not nouvellechaine:
      return "Erreur, pas de nom saisi"
    
    if nouvellechaine in chaines:
      return "Erreur, chaine déjà existante"
    
    chaines.append(nouvellechaine)

    Messages[nouvellechaine] = deque()

    return redirect("/chaine/" + nouvellechaine )
  
  else:

    return render_template("Accueil.html", chaines = chaines)

@app.route("/chaine/<chaine>", methods = ["GET", "POST"])  
def entrer_chaine(chaine):
  
  session['chaine_actuelle'] = chaine

  if request.method == "POST":
        
    return redirect("/")
  
  else:
    
    return render_template("Chaine.html", chaines = chaines, messages = Messages[chaine])

@socketio.on("join", namespace='/')
def join():
    """ Send message to announce that user has entered the channel """
    
    # Save current channel to join room.
    salle = session.get('chaine_actuelle')

    join_room(salle)
    
    emit('status', {'userJoined': session.get('nom'), 'chaine': salle, 'msg': session.get('nom') + ' est entré sur le chat'}, salle=salle, broadcast=True)

@socketio.on("quit", namespace='/')
def quit():
    """ Send message to announce that user has left the channel """

    salle = session.get('chaine_actuelle')

    leave_room(salle)

    emit('status', {'msg': session.get('nom') + ' a quitté le chat'}, salle=salle, broadcast=True)


@socketio.on('envoi message')
def envoi_msg(msg, timestamp):

  salle = session.get('chaine_actuelle')
  
  if len(Messages[salle]) > 100:
    # Pop the oldest message
    Messages[salle].popleft()

  Messages[salle].append([timestamp, session.get('nom'), msg])

  emit('annonce message', {'timestamp': timestamp,'user':session.get('nom'), 'msg': msg}, salle=salle, broadcast=True)