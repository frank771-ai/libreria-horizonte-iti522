const rows = document.querySelector('#productRows');
const resultMessage = document.querySelector('#resultMessage');
const dialog = document.querySelector('#productDialog');
const form = document.querySelector('#productForm');
const formMessage = document.querySelector('#formMessage');
const stockFilter = document.querySelector('#stockFilter');
const categoryFilter = document.querySelector('#categoryFilter');
const money = new Intl.NumberFormat('es-CR', { style: 'currency', currency: 'CRC' });
let products = [];

function escapeHtml(value) {
  const element = document.createElement('span');
  element.textContent = String(value ?? '');
  return element.innerHTML;
}

function showToast(message) {
  const toast = document.querySelector('#toast');
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2300);
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Error HTTP ${response.status}`);
  }
  return response.json();
}

async function loadCategories() {
  const categories = await request('/api/categories');
  categoryFilter.innerHTML = '<option value="">Todas</option>' + categories
    .map(category => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`)
    .join('');
}

function render() {
  rows.innerHTML = products.map(product => `
    <tr>
      <td>${product.id}</td>
      <td><strong>${escapeHtml(product.code)}</strong></td>
      <td class="name-cell">${escapeHtml(product.name)}</td>
      <td>${escapeHtml(product.category)}</td>
      <td>${money.format(Number(product.price))}</td>
      <td><span class="stock ${product.quantity === 0 ? 'out' : ''}">${product.quantity}</span></td>
      <td>${new Date(product.registration_date).toLocaleDateString('es-CR')}</td>
      <td><div class="row-actions">
        <button class="edit" data-edit="${product.id}">Editar</button>
        <button class="danger" data-delete="${product.id}">Eliminar</button>
      </div></td>
    </tr>`).join('');

  document.querySelector('#totalProducts').textContent = products.length;
  document.querySelector('#availableProducts').textContent = products.filter(p => p.quantity > 0).length;
  document.querySelector('#outProducts').textContent = products.filter(p => p.quantity === 0).length;
  resultMessage.textContent = `${products.length} producto(s) encontrado(s)`;
}

async function loadProducts() {
  resultMessage.textContent = 'Cargando…';
  const params = new URLSearchParams({ stock: stockFilter.value });
  if (categoryFilter.value) params.set('category', categoryFilter.value);
  try {
    products = await request(`/api/products?${params}`);
    render();
  } catch (error) {
    resultMessage.textContent = error.message;
    rows.innerHTML = '';
  }
}

function openForm(product = null) {
  form.reset();
  formMessage.textContent = '';
  document.querySelector('#productId').value = product?.id || '';
  document.querySelector('#dialogTitle').textContent = product ? 'Editar producto' : 'Nuevo producto';
  if (product) {
    for (const field of ['code', 'name', 'category', 'price', 'quantity']) {
      document.querySelector(`#${field}`).value = product[field];
    }
  }
  dialog.showModal();
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  formMessage.textContent = '';
  const id = document.querySelector('#productId').value;
  const payload = {
    code: document.querySelector('#code').value,
    name: document.querySelector('#name').value,
    category: document.querySelector('#category').value,
    price: Number(document.querySelector('#price').value),
    quantity: Number(document.querySelector('#quantity').value),
  };
  try {
    await request(id ? `/api/products/${id}` : '/api/products', {
      method: id ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    dialog.close();
    await loadCategories();
    await loadProducts();
    showToast(id ? 'Producto actualizado' : 'Producto creado');
  } catch (error) {
    formMessage.textContent = error.message;
  }
});

rows.addEventListener('click', async event => {
  const editId = event.target.dataset.edit;
  const deleteId = event.target.dataset.delete;
  if (editId) openForm(products.find(product => product.id === Number(editId)));
  if (deleteId && window.confirm('¿Desea eliminar este producto?')) {
    try {
      await request(`/api/products/${deleteId}`, { method: 'DELETE' });
      await loadCategories();
      await loadProducts();
      showToast('Producto eliminado');
    } catch (error) {
      showToast(error.message);
    }
  }
});

document.querySelector('#newProduct').addEventListener('click', () => openForm());
document.querySelector('#closeDialog').addEventListener('click', () => dialog.close());
document.querySelector('#cancelDialog').addEventListener('click', () => dialog.close());
stockFilter.addEventListener('change', loadProducts);
categoryFilter.addEventListener('change', loadProducts);

async function init() {
  try {
    const health = await request('/health');
    if (health.status === 'ok') {
      const badge = document.querySelector('#healthBadge');
      badge.textContent = '● Servicio operativo';
      badge.classList.add('ok');
    }
    await loadCategories();
    await loadProducts();
  } catch (error) {
    resultMessage.textContent = error.message;
  }
}

init();
