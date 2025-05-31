// scripts/main.js

import { getUsuarioLogado, limparSessao } from './config.js';
import * as auth from './auth.js';
import * as grupo from './grupo.js';
import * as despesas from './despesas.js';

document.addEventListener('DOMContentLoaded', () => {
  const usuario = getUsuarioLogado();

  // Redirecionamento básico se necessário
  if (location.pathname.endsWith('home.html') && !usuario) {
    location.href = 'index.html';
  }

  // Roteamento automático por página
  const pagina = location.pathname;

  if (pagina.endsWith('index.html')) {
    auth.inicializarLogin();
  }

  if (pagina.endsWith('cadastro.html')) {
    auth.inicializarCadastro();
  }

  if (pagina.endsWith('home.html')) {
    grupo.inicializarHome();
  }

  if (pagina.endsWith('criar-grupo.html')) {
    grupo.inicializarCriacaoGrupo();
  }

  if (pagina.endsWith('grupo-detalhes.html')) {
    grupo.inicializarGrupoDetalhes();
  }

  if (pagina.endsWith('adicionar-despesa.html')) {
    despesas.inicializarCriacaoDespesa();
  }

  if (pagina.endsWith('despesa-detalhes.html')) {
    despesas.inicializarListaDespesas();
  }

  if (pagina.endsWith('gerar-pagamento.html')) {
    despesas.inicializarPagamentoPIX();
  }

  // Botão de logout/limpar sessão
  const botaoLogout = document.getElementById('clearDataButton');
  if (botaoLogout) {
    botaoLogout.addEventListener('click', () => {
      limparSessao();
      location.href = 'index.html';
    });
  }
});

