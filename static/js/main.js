// small UI helpers
document.addEventListener('DOMContentLoaded', () => {
  // focus first input on pages with forms
  const firstInput = document.querySelector('form input');
  if (firstInput) firstInput.focus();
});
