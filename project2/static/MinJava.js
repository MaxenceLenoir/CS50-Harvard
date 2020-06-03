// Charger la valeur actuelle de l'identifiant
document.addEventListener('DOMContentLoaded', function() {

  // Connect to websocket
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // When connected, configure buttons
  socket.on('connect', () => {

    socket.emit('join');

    // Forget user's last channel when clicked on '+ Channel'
    document.querySelector('#nouvellechaine').addEventListener('click', () => {
        localStorage.removeItem('derniere_chaine');
    });

    // When user leaves channel redirect to '/'
    document.querySelector('#quitter').addEventListener('click', () => {

        // Notify the server user has left
        socket.emit('quit');

        localStorage.removeItem('derniere_chaine');
        window.location.replace('/');
    })

    // Forget user's last channel when logged out
    document.querySelector('#logout').addEventListener('click', () => {
        localStorage.removeItem('derniere_chaine');
    });

    // 'Enter' key on textarea also sends a message
    // https://developer.mozilla.org/en-US/docs/Web/Events/keydown
    document.querySelector('#message').addEventListener("keydown", event => {
        if (event.key == "Enter") {
            document.getElementById("BoutonMessage").click();
        }
    });

    // Send button emits a "message sent" event
    document.querySelector('#BoutonMessage').onclick = () => {
        
      // Save time in format HH:MM:SS
      let timestamp = new Date;
      timestamp = timestamp.toLocaleTimeString();

      // Save user input
      let msg = document.querySelector("#message").value;

      socket.emit('envoi message', msg, timestamp);
      
      // Clear input
      document.querySelector("#message").value = '';
  };
});

socket.on('status', data => {

  // Broadcast message of joined user.
  let row = '<' + `${data.msg}` + '>'
  document.querySelector('#chat').value += row + '\n';

  // Save user current channel on localStorage
  localStorage.setItem('derniere_chaine', data.chaine)
})

 // When a message is announced, add it to the textarea.
 socket.on('annonce message', data => {

  // Format message
  let row = '<' + `${data.timestamp}` + '> - ' + '[' + `${data.user}` + ']:  ' + `${data.msg}`
  document.querySelector('#chat').value += row + '\n'
})

});