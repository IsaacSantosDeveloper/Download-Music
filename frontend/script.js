let selectedFormat = "mp4";

document.querySelectorAll(".format").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".format").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    selectedFormat = button.dataset.format;
  });
});

document.getElementById("downloadBtn").addEventListener("click", () => {
  const url = document.getElementById("video-url").value.trim();

  if (!url) {
    document.getElementById("status").innerText = "Por favor, cole uma URL.";
    return;
  }

  document.getElementById("status").innerText = "Preparando download...";

  // Quando tivermos o back-end, aqui chamaremos ele:
  fetch("http://localhost:5000/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, format: selectedFormat })
  })
    .then(res => res.blob())
    .then(blob => {
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = "playlist.zip";
      link.click();
      document.getElementById("status").innerText = "Download iniciado!";
    })
    .catch(err => {
      console.error(err);
      document.getElementById("status").innerText = "Erro ao baixar.";
    });
});


  document.getElementById('video-url').addEventListener('input', async function () {
    const url = this.value;
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) return;

    const previewDiv = document.getElementById('preview');
    previewDiv.innerHTML = 'Carregando informações...';

    try {
      const res = await fetch('/get_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      const data = await res.json();
      const titulo = data.title;

      previewDiv.innerHTML = `
        <h3>${titulo}</h3>
        <audio controls src="/downloads/${data.folder}/${titulo}.mp3"></audio>
      `;
    } catch (err) {
      previewDiv.innerHTML = 'Erro ao buscar informações do vídeo.';
    }
  });

  