async function checkSession() {
  try {
    const res = await fetch('/api/admin/validate-session', {
      method: 'GET',
      credentials: 'include'
    });

    if (!res.ok) {
      window.location.href = '/html/login.html';
    }
  } catch (error) {
    console.error('Session validation error:', error);
    window.location.href = '/html/login.html';
  }
}
