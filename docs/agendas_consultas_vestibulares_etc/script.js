// ── DADOS ESTÁTICOS ──
let cards = [
  {
    id: 1,
    title: "Fundamentos de álgebra",
    materia: "matematica",
    desc: "Apostilas completa sobre equações do 1° e 2° grau com exercícios resolvidos",
    link: "#",
  },
  {
    id: 2,
    title: "Mecânica clássica",
    materia: "fisica",
    desc: "Mecânica Clássica, onde você entende como as coisas se movem e por que param.",
    link: "#",
  },
  {
    id: 3,
    title: "Conceitos geográficos",
    materia: "geografia",
    desc: "Para entender qualquer assunto de geografia, você precisa desses quatro termos: Espaço Geográfico, Lugar, território, Região",
    link: "#",
  },
  {
    id: 4,
    title: "Pré - História",
    materia: "historia",
    desc: "História é a ciência que estuda as ações humanas ao longo do tempo.",
    link: "#",
  },
  {
    id: 5,
    title: "Metafísica",
    materia: "filosofia",
    desc: 'Investiga o que existe além do físico. O que é o tempo? O que é a consciência? O que faz de você, "você"?',
    link: "#",
  },
  {
    id: 6,
    title: "Interpretação de texto",
    materia: "redacao",
    desc: "A redação, especialmente no modelo dissertativo-argumentativo (o mais cobrado em concursos e faculdades), é basicamente um exercício de lógica: você apresenta um problema, defende um ponto de vista e sugere uma solução.",
    link: "#",
  },
];

let agendas = [
  {
    id: 1,
    materia: "Matemática",
    titulo: "Plantão de Dúvidas: Álgebra",
    data: "2026-05-20",
    horario: "14:00",
    voluntario: "João Silva",
    vagas_atuais: 5,
    vagas_totais: 15,
  },
  {
    id: 2,
    materia: "Redação",
    titulo: "Aulão de Estrutura ENEM",
    data: "2026-05-22",
    horario: "19:00",
    voluntario: "Maria Fernanda",
    vagas_atuais: 20,
    vagas_totais: 20,
  },
  {
    id: 3,
    materia: "Física",
    titulo: "Resolução de Exercícios: Mecânica",
    data: "2026-05-25",
    horario: "16:30",
    voluntario: "Pedro Souza",
    vagas_atuais: 12,
    vagas_totais: 30,
  },
];

let nextId = 7;
let currentRole = "aluno";
let currentFilter = "all";

const materiaLabels = {
  matematica: "Matemática",
  fisica: "Física",
  quimica: "Química",
  biologia: "Biologia",
  historia: "História",
  geografia: "Geografia",
  filosofia: "Filosofia",
  redacao: "Redação",
  sociologia: "Sociologia",
  ingles: "Inglês",
  espanhol: "Espanhol",
  ecologia: "Ecologia",
  gramatica: "Gramática",
  literatura: "Literatura",
  fisiologia: "Fisiologia",
};

// ── NAVEGAÇÃO ──
function showPage(name) {
  document
    .querySelectorAll(".page")
    .forEach((p) => p.classList.remove("active"));
  document.getElementById("page-" + name).classList.add("active");

  document
    .querySelectorAll(".nav-links a")
    .forEach((a) => a.classList.remove("active"));
  const navEl = document.getElementById("nav-" + name);
  if (navEl) navEl.classList.add("active");

  if (name === "agenda") {
    renderAgendas();
  }
  if (name === "conteudos") {
    renderCards();
  }
}

// ── MODO ALUNO / PROFESSOR ──
function setRole(role) {
  currentRole = role;

  document.querySelectorAll(".role-tab").forEach((tab, index) => {
    const isActive =
      (index === 0 && role === "aluno") ||
      (index === 1 && role === "professor");
    tab.classList.toggle("active", isActive);
  });

  document.getElementById("addBtn").style.display =
    role === "professor" ? "flex" : "none";
  document.getElementById("professorNotice").style.display =
    role === "professor" ? "flex" : "none";

  renderCards();
}

// ── FILTRO ──
function filterCards(filter) {
  currentFilter = filter;
  closeDropdown();
  renderCards();
}

function setFilterLabel(label) {
  document.querySelector(".filter-btn").innerHTML = label + " <span>▾</span>";
  document.querySelectorAll(".dropdown-item").forEach((item) => {
    item.classList.toggle("selected", item.textContent.trim() === label);
  });
}

function toggleDropdown() {
  document.getElementById("filterDropdown").classList.toggle("open");
}

function closeDropdown() {
  document.getElementById("filterDropdown").classList.remove("open");
}

document.addEventListener("click", function (e) {
  if (!e.target.closest(".filter-dropdown")) closeDropdown();
});

// ── FORMULÁRIO DE ADIÇÃO (ESTÁTICO) ──
function toggleAddForm() {
  document.getElementById("addForm").classList.toggle("open");
}

function addCard() {
  const title = document.getElementById("fTitle").value.trim();
  const materia = document.getElementById("fMateria").value;
  const desc = document.getElementById("fDesc").value.trim();
  const link = document.getElementById("fLink").value.trim() || "#";

  if (!title || !desc) {
    showToast("⚠️ Preencha título e descrição!");
    return;
  }

  // Adiciona o novo card na lista estática
  cards.push({
    id: nextId++,
    title: title,
    materia: materia,
    desc: desc,
    link: link,
  });

  // Limpa os campos do formulário
  document.getElementById("fTitle").value = "";
  document.getElementById("fDesc").value = "";
  document.getElementById("fLink").value = "";
  document.getElementById("addForm").classList.remove("open");

  // Atualiza a tela
  renderCards();
  showToast("✅ Conteúdo publicado (Memória local)!");
}

function deleteCardLocal(id) {
  // Filtra o array estático removendo o card com o id correspondente
  cards = cards.filter((c) => c.id !== id);
  renderCards();
  showToast("🗑️ Conteúdo removido (Memória local).");
}

// ── RENDERIZAÇÃO DOS CARDS (ESTÁTICO) ──
function renderCards() {
  const grid = document.getElementById("cardsGrid");
  if (!grid) return;

  grid.innerHTML = "";

  const filters = currentFilter === "all" ? null : currentFilter.split(",");
  const filtered = filters
    ? cards.filter((c) => filters.includes(c.materia))
    : cards;

  if (filtered.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><span>📭</span><p>Nenhum conteúdo encontrado.</p></div>`;
    return;
  }

  grid.innerHTML = filtered
    .map((c) => {
      const label = materiaLabels[c.materia] || c.materia;

      const actionButtons =
        currentRole === "professor"
          ? `<div class="card-actions"><button class="btn-delete" onclick="deleteCardLocal(${c.id})">Excluir</button></div>`
          : `<a class="btn-download" href="${c.link}" target="_blank">Baixar conteúdo</a>`;

      return `
        <div class="content-card" data-materia="${c.materia}">
          <div class="card-top">
            <div class="card-icon">🎓</div>
            <span class="badge badge-${c.materia}">${label}</span>
          </div>
          <div class="card-title">${c.title}</div>
          <div class="card-desc">${c.desc}</div>
          ${actionButtons}
        </div>`;
    })
    .join("");
}

// ── RENDERIZAÇÃO DAS AGENDAS (ESTÁTICO) ──
function renderAgendas() {
  const container = document.getElementById("agendasGrid");
  if (!container) return;

  container.innerHTML = "";

  if (agendas.length === 0) {
    container.innerHTML = "<p>Nenhuma monitoria agendada no momento.</p>";
    return;
  }

  container.innerHTML = agendas
    .map((a) => {
      const classeCor = a.materia
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");

      return `
        <article class="card">
            <div class="card-header">
                <span class="badge ${classeCor}">${a.materia}</span>
                <span class="vagas">👥 ${a.vagas_atuais}/${a.vagas_totais}</span>
            </div>
            <h2>${a.titulo}</h2>
            <p class="sub">&nbsp;</p> 
            <div class="info-item">📅 ${a.data}</div>
            <div class="info-item">🕒 ${a.horario}</div>
            <p class="voluntario">Volunt: ${a.voluntario}</p>
            <a href="#" class="btn-inscrever-agenda">Inscrever-se</a>
        </article>
        `;
    })
    .join("");
}

// ── TOAST ──
function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

// ── INICIALIZAÇÃO ──
renderCards();

// ── LÓGICA DE INSCRIÇÃO DA AGENDA ──
function mostrarNotificacaoAgenda(mensagem) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast show";
  toast.style.position = "static";
  toast.innerHTML = `<span>✓</span> ${mensagem}`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-inscrever-agenda")) {
    e.preventDefault();
    const botao = e.target;

    if (
      botao.classList.contains("esgotado") &&
      !botao.classList.contains("inscrito")
    )
      return;

    const card = botao.closest(".card");
    const titulo = card.querySelector("h2").textContent;
    const vagasElemento = card.querySelector(".vagas");
    let [atuais, totais] = vagasElemento.textContent
      .replace("👥 ", "")
      .split("/")
      .map(Number);

    if (!botao.classList.contains("inscrito")) {
      if (atuais < totais) {
        atuais++;
        botao.textContent = "CANCELAR INSCRIÇÃO";
        botao.classList.add("inscrito");
        mostrarNotificacaoAgenda(`Inscrição confirmada em: ${titulo}`);
      }
    } else {
      atuais--;
      botao.textContent = "INSCREVER-SE";
      botao.classList.remove("inscrito");
    }

    vagasElemento.textContent = `👥 ${atuais}/${totais}`;

    if (atuais >= totais && !botao.classList.contains("inscrito")) {
      botao.textContent = "ESGOTADO";
      botao.classList.add("esgotado");
    } else if (atuais < totais) {
      botao.classList.remove("esgotado");
      if (botao.textContent === "ESGOTADO") botao.textContent = "INSCREVER-SE";
    }
  }
});

// Verifica a rota ao carregar a página
window.addEventListener("DOMContentLoaded", () => {
  const hash = window.location.hash;
  if (hash) {
    const pageId = hash.replace("#page-", "");
    showPage(pageId);
  } else {
    showPage("home");
  }
});
