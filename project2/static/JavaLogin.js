// Charger la valeur actuelle de l'identifiant
document.addEventListener('DOMContentLoaded', () => {

  //On afficher l'identifiant avec lequel on est connecté si c'est le cas
  if (localStorage.getItem('identifiant')){
    identifiant = localStorage.getItem('identifiant');
    document.querySelector('#identifiant').value = localStorage.getItem('identifiant');
  };

  //Change le nom d'identifiant lorsque l'on clique sur le bouton de connexion
  document.querySelector('#BoutonConnexion').onclick = function() {
    identifiant = document.querySelector('#identifiant').value;
    localStorage.setItem('identifiant', identifiant);
  };
});