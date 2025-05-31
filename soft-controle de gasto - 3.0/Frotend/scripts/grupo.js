// scripts/grupo.js

import {
  API_BASE,
  getUsuarioLogado,
  mostrarMensagem,
  mensagens
} from './config.js';

export function inicializarHome() {
  const usuario = getUsuarioLogado();
  if (!usuario) return;

  carregarGrupos(usuario.id);

  const form = document.getElementById('form-entrar-grupo');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const codigo = document.getElementById('codigoConvite').value.trim();

      try {
        const resposta = await fetch(`${API_BASE}/grupos/entrar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id_usuario: usuario.id,
            codigo_convite: codigo
          })
        });

        const dados = await resposta.json();
        if (!resposta.ok) return mostrarMensagem('error', dados.message);

        mostrarMensagem('success', mensagens.grupoEntrar);
        carregarGrupos(usuario.id);
        form.reset();
      } catch (erro) {
        mostrarMensagem('error', mensagens.erroPadrao);
      }
    });
  }
}

async function carregarGrupos(usuarioId) {
  const url = `${API_BASE}/usuarios/${usuarioId}/grupos`;
  try {
    const resp = await fetch(url);
    const dados = await resp.json();

    const lista = document.getElementById('groupsList');
    const vazio = document.getElementById('noGroups');
    lista.innerHTML = '';

    if (dados.data && dados.data.length > 0) {
      dados.data.forEach(grupo => {
        const div = document.createElement('div');
        div.className = 'card mb-2';
        div.innerHTML = `
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <h5 class="card-title">${grupo.nome}</h5>
              <p class="card-text"><strong>Código:</strong> ${grupo.codigo_convite}</p>
            </div>
            <a href="grupo-detalhes.html?groupId=${grupo.id}" class="btn btn-outline-primary">Abrir</a>
          </div>
        `;
        lista.appendChild(div);
      });
      vazio.style.display = 'none';
    } else {
      vazio.style.display = 'block';
    }
  } catch (erro) {
    mostrarMensagem('error', mensagens.erroPadrao);
  }
}

export function inicializarCriacaoGrupo() {
  const usuario = getUsuarioLogado();
  if (!usuario) return;

  const botao = document.getElementById('criarGrupoBtn');
  if (!botao) return;

  botao.addEventListener('click', async () => {
    const nome = document.getElementById('nomeGrupo').value.trim();
    const descricao = document.getElementById('descricao').value.trim();
    const regras = document.getElementById('regras').value.trim();

    const emails = Array.from(document.querySelectorAll('#listaMembros .email-item')).map(el => el.textContent.trim());

    try {
      const resp = await fetch(`${API_BASE}/grupos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome,
          descricao,
          regras,
          membros: emails,
          id_criador: usuario.id
        })
      });

      const dados = await resp.json();
      if (!resp.ok) return mostrarMensagem('error', dados.message);

      mostrarMensagem('success', mensagens.grupoCriado);

      document.getElementById('inviteCode').value = dados.data.codigo_convite;
      document.getElementById('inviteCodeSection').style.display = 'block';
      document.getElementById('goToDetailsBtn').style.display = 'inline-block';
      document.getElementById('goToDetailsBtn').onclick = () => {
        window.location.href = `grupo-detalhes.html?groupId=${dados.data.id}`;
      };
    } catch (erro) {
      mostrarMensagem('error', mensagens.erroPadrao);
    }
  });
}

export function inicializarGrupoDetalhes() {
  const grupoId = new URLSearchParams(window.location.search).get('id');
  if (!grupoId) return;

  fetch(`${API_BASE}/grupos/${grupoId}`)
    .then(resp => resp.json())
    .then(dados => {
      if (!dados.data) return mostrarMensagem('error', dados.message);

      document.getElementById('groupName').innerText = dados.data.nome;
      document.getElementById('groupInviteCode').innerText = dados.data.codigo_convite;

      const ul = document.getElementById('membersList');
      ul.innerHTML = '';

      dados.data.membros.forEach(membro => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerText = membro.email;
        ul.appendChild(li);
      });

      document.getElementById('addExpenseLink').href += grupoId;
      document.getElementById('expenseListLink').href += grupoId;
    })
    .catch(() => mostrarMensagem('error', mensagens.erroPadrao));
}

