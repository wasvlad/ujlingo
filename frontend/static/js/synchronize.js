document.addEventListener('DOMContentLoaded', () => {
  const syncBtn = document.getElementById('sync-btn');

  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      syncBtn.disabled = true;
      syncBtn.textContent = 'Synchronizing...';

      try {
        const response = await fetch('/api/admin/sync-words', {
          method: 'POST',
          credentials: 'include'
        });

        const result = await response.json();

        if (response.ok) {
          alert(result.message || 'Words synchronized successfully');
        } else {
          alert(result.detail || 'Failed to synchronize words.');
        }
      } catch (err) {
        console.error('Sync error:', err);
        alert('Failed to synchronize words.');
      } finally {
        syncBtn.disabled = false;
        syncBtn.textContent = 'Synchronize';
      }
    });
  }
});
