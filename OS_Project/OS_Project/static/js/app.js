const processTableBody = document.querySelector('#processTable tbody');
const addProcessBtn = document.querySelector('#addProcessBtn');
const resetBtn = document.querySelector('#resetBtn');
const calculateBtn = document.querySelector('#calculateBtn');
const algorithmHidden = document.querySelector('#algorithmHidden');
const algorithmCards = document.querySelectorAll('.algorithm-card');
const algorithmStatus = document.querySelector('#algorithmStatus');
const quantumGroup = document.querySelector('#quantumGroup');
const priorityColumns = document.querySelectorAll('.priority-column');
const processDataField = document.querySelector('#processData');
const toast = document.querySelector('#toast');
const themeToggle = document.querySelectorAll('#themeToggle');
const tableWrap = document.querySelector('.table-wrap');
const formActions = document.querySelector('.form-actions');
const simulationForm = document.querySelector('#simulationForm');

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove('show'), 3000);
}

function getSelectedAlgorithm() {
  return algorithmHidden ? algorithmHidden.value.trim() : '';
}

function setSelectedAlgorithm(value) {
  if (!algorithmHidden) return;

  const selectedCard = Array.from(algorithmCards).find(card => card.dataset.algo === value);
  if (!selectedCard) {
    algorithmHidden.value = '';
    algorithmCards.forEach(card => {
      card.classList.remove('selected');
      card.setAttribute('aria-pressed', 'false');
    });
    if (algorithmStatus) {
      algorithmStatus.textContent = 'No algorithm selected';
    }
    updateAlgorithmFields();
    updateControlsVisibility();
    return;
  }

  algorithmHidden.value = value;
  algorithmCards.forEach(card => {
    const selected = card.dataset.algo === value;
    card.classList.toggle('selected', selected);
    card.setAttribute('aria-pressed', selected ? 'true' : 'false');
  });

  if (algorithmStatus) {
    const label = selectedCard.querySelector('.algorithm-card__title');
    algorithmStatus.textContent = label ? `Selected: ${label.textContent}` : 'Selected algorithm updated';
  }

  updateAlgorithmFields();
  updateControlsVisibility();
}

function algorithmRequiresPriority(algorithm) {
  if (!algorithm) return false;
  return algorithm.toLowerCase().includes('priority');
}

function updateAlgorithmFields() {
  const algorithm = getSelectedAlgorithm();

  if (quantumGroup) {
    quantumGroup.classList.toggle('hidden', algorithm !== 'round_robin');
  }

  const showPriority = algorithmRequiresPriority(algorithm);
  document.querySelectorAll('.priority-column').forEach(column => {
    column.classList.toggle('hidden', !showPriority);
  });
}

function updateControlsVisibility() {
  const selected = Boolean(getSelectedAlgorithm());
  if (tableWrap) tableWrap.classList.toggle('hidden', !selected);
  if (formActions) formActions.classList.toggle('hidden', !selected);
  if (selected && processTableBody && processTableBody.children.length === 0) {
    renderTable();
  }
}

function createRow(process = { pid: '', arrival: '', burst: '', priority: '' }) {
  const row = document.createElement('tr');
  row.innerHTML = `
    <td><input type="text" name="pid" value="${process.pid}" placeholder="P1" required></td>
    <td><input type="number" min="0" step="1" name="arrival" value="${process.arrival}" placeholder="0" required></td>
    <td><input type="number" min="1" step="1" name="burst" value="${process.burst}" placeholder="5" required></td>
    <td class="priority-column hidden"><input type="number" min="0" name="priority" value="${process.priority}" placeholder="1"></td>
    <td class="action-cell"><button type="button" class="button button-secondary remove-btn">Remove</button></td>
  `;
  return row;
}

function renderTable() {
  if (!processTableBody) return;
  processTableBody.innerHTML = '';
  processTableBody.appendChild(createRow());
  updateAlgorithmFields();
}

function collectProcessData() {
  if (!processTableBody || !processDataField) return [];

  const rows = Array.from(processTableBody.querySelectorAll('tr')).map(row => {
    const pid = row.querySelector('[name="pid"]')?.value.trim() || '';
    const arrival = parseInt(row.querySelector('[name="arrival"]')?.value, 10);
    const burst = parseInt(row.querySelector('[name="burst"]')?.value, 10);
    const priorityInput = row.querySelector('[name="priority"]');
    const priority = priorityInput ? parseInt(priorityInput.value, 10) : NaN;
    return {
      pid,
      arrival: Number.isNaN(arrival) ? 0 : arrival,
      burst: Number.isNaN(burst) ? 0 : burst,
      priority: Number.isNaN(priority) ? 0 : priority,
    };
  }).filter(process => process.pid.length > 0);

  processDataField.value = JSON.stringify(rows);
  return rows;
}

function submitSimulation() {
  if (!algorithmHidden || !algorithmHidden.value) {
    showToast('Please select an algorithm.');
    return;
  }

  const rows = collectProcessData();
  if (!rows.length) {
    showToast('Add at least one process.');
    return;
  }

  if (simulationForm) {
    simulationForm.submit();
  }
}

function bindProcessTableActions() {
  if (!processTableBody) return;

  processTableBody.addEventListener('click', (event) => {
    const removeBtn = event.target.closest('.remove-btn');
    if (!removeBtn) return;
    const row = removeBtn.closest('tr');
    if (row) {
      row.remove();
      collectProcessData();
    }
  });
}

function initAlgorithmCards() {
  if (!algorithmCards.length) return;

  algorithmCards.forEach(card => {
    card.addEventListener('click', () => {
      setSelectedAlgorithm(card.dataset.algo);
    });
    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setSelectedAlgorithm(card.dataset.algo);
      }
    });
  });
}

function toggleThemeMode() {
  document.body.classList.toggle('light');
  const mode = document.body.classList.contains('light') ? 'light' : 'dark';
  window.localStorage.setItem('themeMode', mode);
}

function restoreTheme() {
  const savedMode = window.localStorage.getItem('themeMode');
  if (savedMode === 'light') {
    document.body.classList.add('light');
  } else {
    document.body.classList.remove('light');
  }
}

function renderGanttSegments() {
  const ganttView = document.querySelector('.gantt-view');
  if (!ganttView) return;
  const totalTime = parseFloat(ganttView.dataset.totalTime) || 1;
  const segments = Array.from(ganttView.querySelectorAll('.gantt-segment'));
  segments.forEach(segment => {
    const start = parseFloat(segment.dataset.start) || 0;
    const end = parseFloat(segment.dataset.end) || 0;
    const width = totalTime > 0 ? ((end - start) / totalTime) * 100 : 0;
    segment.style.left = `${(start / totalTime) * 100}%`;
    segment.style.width = `${width}%`;
    segment.style.background = segment.dataset.color || '#6f7dff';
  });
}

function init() {
  restoreTheme();

  if (themeToggle.length) {
    themeToggle.forEach(button => button.addEventListener('click', toggleThemeMode));
  }

  initAlgorithmCards();
  if (getSelectedAlgorithm()) {
    setSelectedAlgorithm(getSelectedAlgorithm());
  }

  if (processTableBody) {
    bindProcessTableActions();
    if (addProcessBtn) {
      addProcessBtn.addEventListener('click', () => {
        processTableBody.appendChild(createRow());
        updateAlgorithmFields();
        collectProcessData();
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        renderTable();
        collectProcessData();
      });
    }
    if (calculateBtn) {
      calculateBtn.addEventListener('click', submitSimulation);
    }
    updateAlgorithmFields();
    updateControlsVisibility();
  }

  renderGanttSegments();
}

window.addEventListener('DOMContentLoaded', init);

