import { API_BASE } from './config.js';

const grupoId = new URLSearchParams(location.search).get('groupId');
const membrosContainer = document.getElementById('membrosContainer');
const form = document.getElementById('membrosForm');

fetch(`${API_BASE}/grupos/${grupoId}`)
  .then(resp => resp.json())
  .then(dados => {
    if (!dados.data || !dados.data.membros) return;
    dados.data.membros.forEach(m => {
      membrosContainer.innerHTML += `
        <div class="form-check">
          <input class="form-check-input" type="checkbox" value="${m.id}" id="membro${m.id}">
          <label class="form-check-label" for="membro${m.id}">${m.email}</label>
        </div>
      `;
    });
  });

form.addEventListener('submit', e => {
  e.preventDefault();
  // 收集选中的成员ID
  const selecionados = Array.from(document.querySelectorAll('.form-check-input:checked')).map(cb => cb.value);
  // 存到 localStorage 或 sessionStorage
  sessionStorage.setItem('membrosSelecionados', JSON.stringify(selecionados));
  // 返回到添加支出页面
  window.location.href = `adicionar-despesa.html?groupId=${grupoId}&manual=1`;
});