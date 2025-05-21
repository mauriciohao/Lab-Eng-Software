// scripts/auth.js

import { API_BASE, setUsuarioLogado, mostrarMensagem, mensagens } from './config.js';

export function inicializarLogin() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const loginId = document.getElementById('loginId').value.trim();
    const password = document.getElementById('password').value;

    try {
      const resposta = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ loginId, password })
      });

      const dados = await resposta.json();

      if (!resposta.ok) {
        mostrarMensagem('error', dados.message || mensagens.loginInvalido);
        return;
      }

      setUsuarioLogado(dados.data);
      window.location.href = 'home.html';
    } catch (erro) {
      console.error(erro);
      mostrarMensagem('error', mensagens.erroPadrao);
    }
  });
}

export function inicializarCadastro() {
  const form = document.getElementById('register-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nome = document.getElementById('nome').value.trim();
    const email = document.getElementById('email').value.trim();
    const username = document.getElementById('username').value.trim();
    const senha = document.getElementById('senha').value;
    const confirmar = document.getElementById('confirmarSenha').value;

    if (senha !== confirmar) {
      mostrarMensagem('error', 'As senhas não coincidem.');
      return;
    }

    try {
      const resposta = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, email, username, senha })
      });

      const dados = await resposta.json();

      if (!resposta.ok) {
        mostrarMensagem('error', dados.message || mensagens.erroPadrao);
        return;
      }

      mostrarMensagem('success', mensagens.cadastroSucesso);
      form.reset();
      setTimeout(() => window.location.href = 'index.html', 3000);
    } catch (erro) {
      console.error(erro);
      mostrarMensagem('error', mensagens.erroPadrao);
    }
  });
}

