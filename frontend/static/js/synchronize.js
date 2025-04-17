document.addEventListener('DOMContentLoaded', () => {
  const syncWordsBtn = document.getElementById('sync-words-btn');
  const syncSentencesBtn = document.getElementById('sync-sentences-btn');

  if (syncWordsBtn) {
    syncWordsBtn.addEventListener('click', async () => {
      syncWordsBtn.disabled = true;
      syncWordsBtn.textContent = 'Synchronizing Words...';

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
        syncWordsBtn.disabled = false;
        syncWordsBtn.textContent = 'Sync Words';
      }
    });
  }

  if (syncSentencesBtn) {
    syncSentencesBtn.addEventListener('click', async () => {
      syncSentencesBtn.disabled = true;
      syncSentencesBtn.textContent = 'Synchronizing Sentences...';

      try {
        const response = await fetch('/api/admin/sync-sentences', {
          method: 'POST',
          credentials: 'include'
        });

        const result = await response.json();

        if (response.ok) {
          alert(result.message || 'Sentences migrated successfully');
        } else {
          alert(result.detail || 'Failed to synchronize sentences.');
        }
      } catch (err) {
        console.error('Sync error:', err);
        alert('Failed to synchronize sentences.');
      } finally {
        syncSentencesBtn.disabled = false;
        syncSentencesBtn.textContent = 'Sync Sentences';
      }
    });
  }
});
