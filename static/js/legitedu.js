// LegitEdu — Main JS

document.addEventListener('DOMContentLoaded', function () {

    // ── Sticky navbar shadow ──
    const navbar = document.querySelector('.main-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 60) {
            navbar && navbar.classList.add('scrolled');
        } else {
            navbar && navbar.classList.remove('scrolled');
        }
    });

    // ── Auto-dismiss alerts ──
    document.querySelectorAll('.alert:not(.alert-danger)').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert && bsAlert.close();
        }, 4000);
    });

    // ── Pause ticker on hover ──
    const ticker = document.querySelector('.ticker-track');
    if (ticker) {
        ticker.addEventListener('mouseenter', () => ticker.style.animationPlayState = 'paused');
        ticker.addEventListener('mouseleave', () => ticker.style.animationPlayState = 'running');
    }

    // ── Smooth scroll for anchor links ──
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ── Live search suggestion (debounced) ──
    const searchInput = document.querySelector('.search-form input');
    if (searchInput) {
        let timer;
        searchInput.addEventListener('input', function () {
            clearTimeout(timer);
            timer = setTimeout(() => {
                // Future: fetch suggestions from /api/posts/?search=...
            }, 300);
        });
    }
});

// Newsletter AJAX + WhatsApp popup
(function () {
    function getCSRF() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    document.querySelectorAll('.newsletter-form').forEach(form => {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const emailInput = form.querySelector('input[name="email"]');
            const btn = form.querySelector('button[type="submit"]');
            const original = btn ? btn.innerHTML : '';
            if (btn) { btn.disabled = true; btn.innerHTML = 'Joining...'; }
            try {
                form.classList.add('is-loading');
                let feedback = form.querySelector('.newsletter-feedback');
                if (!feedback) {
                    feedback = document.createElement('span');
                    feedback.className = 'newsletter-feedback';
                    form.appendChild(feedback);
                }
                feedback.textContent = '';
                const data = new FormData(form);
                const res = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRF(), 'X-Requested-With': 'XMLHttpRequest' },
                    body: data
                });
                const json = await res.json();
                feedback.textContent = json.message || 'Thank you.';
                feedback.className = 'newsletter-feedback ' + (json.ok ? 'text-success' : 'text-danger');
                if (json.ok && emailInput) emailInput.value = '';
            } catch (err) {
                let feedback = form.querySelector('.newsletter-feedback');
                if (!feedback) { feedback = document.createElement('span'); feedback.className = 'newsletter-feedback'; form.appendChild(feedback); }
                feedback.textContent = 'Could not subscribe now. Please try again.';
                feedback.className = 'newsletter-feedback text-danger';
            } finally {
                form.classList.remove('is-loading');
                if (btn) { btn.disabled = false; btn.innerHTML = original; }
            }
        });
    });

    const joinModalEl = document.getElementById('whatsappJoinModal');
    if (joinModalEl && !localStorage.getItem('legiteduWhatsappPopupSeen')) {
        setTimeout(() => {
            const modal = new bootstrap.Modal(joinModalEl);
            modal.show();
            localStorage.setItem('legiteduWhatsappPopupSeen', '1');
        }, 1800);
    }
})();
