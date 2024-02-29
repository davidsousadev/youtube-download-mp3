// Função para reproduzir o áudio
function playAudio(audioId) {
    var audio = document.getElementById("audio" + audioId);
    audio.play();
}

// Função para pausar o áudio
function pauseAudio(audioId) {
    var audio = document.getElementById("audio" + audioId);
    audio.pause();
}