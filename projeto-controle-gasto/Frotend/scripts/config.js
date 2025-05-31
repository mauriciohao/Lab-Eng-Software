// scripts/config.js

export const API_BASE = 'https://lab-eng-software-controle-gasto.onrender.com/api';

// Mensagens globais
export const mensagens = {
  erroPadrao: 'Ocorreu um erro. Tente novamente mais tarde.',
  loginInvalido: 'Email/usuário ou senha inválidos!',
  cadastroSucesso: 'Cadastro realizado com sucesso!',
  grupoCriado: 'Grupo criado com sucesso!',
  despesaCriada: 'Despesa adicionada com sucesso!',
  grupoEntrar: 'Você entrou no grupo com sucesso!',
};

// Sessão
export function getUsuarioLogado() {
  const dados = localStorage.getItem('usuario');
  return dados ? JSON.parse(dados) : null;
}

export function setUsuarioLogado(usuario) {
  localStorage.setItem('usuario', JSON.stringify(usuario));
}

export function limparSessao() {
  localStorage.removeItem('usuario');
}

// Feedback visual
export function mostrarMensagem(tipo, texto) {
  const elemento = document.getElementById(`${tipo}-message`);
  if (!elemento) return;
  elemento.style.display = 'block';
  elemento.innerText = texto;
  setTimeout(() => {
    elemento.style.display = 'none';
  }, 5000);
}

