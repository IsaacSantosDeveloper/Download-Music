document.getElementById("previewBtn").addEventListener("click", async () => {
  const url = document.getElementById("video-url").value;
  const videoId = extractVideoId(url);

  const modal = document.getElementById("previewModal");
  const modalBody = document.getElementById("modalBody");

  if (videoId) {
    const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;

    try {
      const response = await fetch(`https://noembed.com/embed?url=https://www.youtube.com/watch?v=${videoId}`);
      const data = await response.json();

      console.log("Dados recebidos:", data); // <- Isso ajuda a ver se a API está funcionando

      const title = data.title || "Título não encontrado";

      modalBody.innerHTML = `
        <div class="track">
          <img src="${thumbnailUrl}" alt="Thumbnail" />
          <div>${title}</div>
        </div>
      `;
    } catch (error) {
      console.error("Erro ao buscar título:", error);
      modalBody.innerHTML = "Erro ao buscar o título.";
    }
  } else {
    modalBody.innerHTML = "URL inválida ou vídeo não encontrado.";
  }

  modal.style.display = "block";
});

function extractVideoId(url) {
  const regex = /(?:youtu\.be\/|youtube\.com\/(?:watch\?(?:.*&)?v=|embed\/|v\/))([^?&"'>]+)/;
  const match = url.match(regex);
  return match ? match[1] : null;
}
