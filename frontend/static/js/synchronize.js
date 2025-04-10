document.addEventListener('DOMContentLoaded', () => {
  const syncBtn = document.getElementById('sync-btn');

  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      try {
        const response = await fetch('/api/admin/migrate-words', {
          method: 'POST',
          credentials: 'include'
        });

        const result = await response.json();
        alert(result.message || 'Words synchronized successfully');
      } catch (err) {
        console.error('Sync error:', err);
        alert('Failed to synchronize words.');
      }
    });
  }
});
