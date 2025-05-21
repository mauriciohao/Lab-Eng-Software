// scripts/despesas.js

import {
  API_BASE,
  getUsuarioLogado,
  mostrarMensagem,
  mensagens
} from './config.js';

export function inicializarCriacaoDespesa() {
  const usuario = getUsuarioLogado();
  if (!usuario) return;

  const grupoId = new URLSearchParams(location.search).get('groupId');
  if (!grupoId) return;

  const form = document.getElementById('expense-form');
  const dataInput = document.getElementById('data');
  const dataLimiteInput = document.getElementById('dataLimite');

  // Controlar data limite
  dataInput.addEventListener('change', () => {
    const data = new Date(dataInput.value);
    if (data.toString() === 'Invalid Date') return;
    const limite = new Date(data);
    limite.setDate(data.getDate() + 30);
    dataLimiteInput.min = data.toISOString().split('T')[0];
    dataLimiteInput.max = limite.toISOString().split('T')[0];
    dataLimiteInput.disabled = false;
  });

  // Alternar entre divisão automática e manual
  document.getElementById('autoSplit').addEventListener('change', () => {
    document.getElementById('manualSplitSection').style.display = 'none';
  });

  document.getElementById('manualSplit').addEventListener('change', async () => {
    const response = await fetch(`${API_BASE}/grupos/${grupoId}`);
    const grupo = await response.json();
    const container = document.getElementById('manualSplitForm');
    container.innerHTML = '';
    grupo.data.membros.forEach(m => {
      container.innerHTML += `
        <div class="input-group mb-2">
          <span class="input-group-text">${m.email}</span>
          <input type="number" class="form-control" data-email="${m.email}" data-id="${m.id}" min="0" step="0.01">
        </div>
      `;
    });
    document.getElementById('manualSplitSection').style.display = 'block';
  });

  // Submissão do formulário
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const dados = {
      name: document.getElementById('nomeDespesa').value.trim(),
      description: document.getElementById('descricao').value.trim(),
      establishment: document.getElementById('estabelecimento').value.trim(),
      category: document.getElementById('expenseCategory').value,
      amount: parseFloat(document.getElementById('valor').value),
      date: document.getElementById('data').value,
      due_date: document.getElementById('dataLimite').value,
      payer_id: usuario.id,
      group_id: grupoId,
      settlement_type: document.getElementById('autoSplit').checked ? 'igual' : 'manual'
    };

    if (!document.getElementById('autoSplit').checked) {
      dados.manual_debts = {};
      document.querySelectorAll('#manualSplitForm input').forEach(input => {
        const id = input.getAttribute('data-id');
        const valor = parseFloat(input.value);
        if (valor > 0) dados.manual_debts[id] = valor;
      });
    }

    try {
      const resp = await fetch(`${API_BASE}/expenses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });

      const resposta = await resp.json();
      if (!resp.ok) return mostrarMensagem('error', resposta.message);

      mostrarMensagem('success', mensagens.despesaCriada);
      form.reset();
    } catch (erro) {
      mostrarMensagem('error', mensagens.erroPadrao);
    }
  });
}

export function inicializarListaDespesas() {
  const grupoId = new URLSearchParams(location.search).get('groupId');
  if (!grupoId) return;

  fetch(`${API_BASE}/groups/${grupoId}/expenses`)
    .then(resp => resp.json())
    .then(dados => {
      const corpo = document.getElementById('expenseTableBody');
      corpo.innerHTML = '';

      dados.data.forEach(d => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><input type="checkbox" data-id="${d.id}"></td>
          <td>${d.name}</td>
          <td>${d.date}</td>
          <td>${d.establishment || '-'}</td>
          <td>${d.category || '-'}</td>
          <td>R$ ${d.amount.toFixed(2)}</td>
          <td>${d.due_date || '-'}</td>
          <td>${d.status}</td>
          <td><a href="gerar-pagamento.html?id=${d.id}" class="btn btn-sm btn-outline-success">PIX</a></td>
        `;
        corpo.appendChild(tr);
      });
    })
    .catch(() => mostrarMensagem('error', mensagens.erroPadrao));
}

export function inicializarPagamentoPIX() {
  const despesaId = new URLSearchParams(location.search).get('id');
  if (!despesaId) return;

  fetch(`${API_BASE}/expenses/${despesaId}`)
    .then(resp => resp.json())
    .then(d => {
      if (!d.data) return mostrarMensagem('error', d.message);
      document.getElementById('expenseDetails').innerHTML = `
        <p><strong>Descrição:</strong> ${d.data.description}</p>
        <p><strong>Valor:</strong> R$ ${d.data.amount.toFixed(2)}</p>
        <p><strong>Status:</strong> ${d.data.status}</p>
      `;
    });

  document.getElementById('copyPixKeyBtn')?.addEventListener('click', () => {
    const key = document.getElementById('pixKey').textContent;
    navigator.clipboard.writeText(key);
    mostrarMensagem('success', 'Chave PIX copiada!');
  });
}
