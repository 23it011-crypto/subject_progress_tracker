document.addEventListener('DOMContentLoaded', () => {
    // Login Validation
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const username = loginForm.username.value.trim();
            const password = loginForm.password.value.trim();
            let hasError = false;
            
            if (!username) {
                hasError = true;
                showError(loginForm.username, 'Username is required');
            }
            if (!password) {
                hasError = true;
                showError(loginForm.password, 'Password is required');
            }
            
            if (hasError) {
                e.preventDefault();
            }
        });
    }

    function showError(input, message) {
        input.style.borderColor = '#ef4444';
        // Could add a message element
    }

    // Teacher Progress Preview
    const checkboxes = document.querySelectorAll('.unit-checkbox');
    const progressBar = document.getElementById('preview-progress');
    const progressText = document.getElementById('preview-text');
    const totalUnitsInput = document.getElementById('total-units-count');
    
    if (checkboxes.length > 0 && totalUnitsInput) {
        const total = parseInt(totalUnitsInput.value);
        
        checkboxes.forEach(cb => {
            cb.addEventListener('change', updatePreview);
        });
        
        function updatePreview() {
            const checked = document.querySelectorAll('.unit-checkbox:checked').length;
            const pct = Math.round((checked / total) * 100);
            
            if (progressBar) {
                progressBar.style.width = pct + '%';
                
                // Remove old colors
                progressBar.classList.remove('bg-green', 'bg-yellow', 'bg-red');
                
                if (pct === 100) {
                    progressBar.classList.add('bg-green');
                } else if (pct >= 50) {
                    progressBar.classList.add('bg-yellow');
                } else {
                    progressBar.classList.add('bg-red');
                }
            }
            
            if (progressText) {
                progressText.innerText = pct + '% Completed';
            }
        }
        // Initial call
        updatePreview();
    }
});
