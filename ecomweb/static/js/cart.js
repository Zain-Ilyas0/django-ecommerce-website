function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
}

function openCartPanel() {
    document.getElementById('cart-overlay').classList.add('active');

    fetch(cartPanelUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById('cart-panel-mount').innerHTML = data.html;
            document.getElementById('cart-count').textContent = data.count;
            document.getElementById('cart-panel-mount').classList.add('open');
            bindCartCloseEvents();
        });
}

function closeCartPanel() {
    document.getElementById('cart-panel-mount').classList.remove('open');
    document.getElementById('cart-overlay').classList.remove('active');
}

function bindCartCloseEvents() {
    const closeBtn = document.getElementById('cart-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCartPanel);
    }

    const continueLink = document.getElementById('cart-continue');
    if (continueLink) {
        continueLink.addEventListener('click', function (e) {
            e.preventDefault();
            closeCartPanel();
        });
    }

    document.querySelectorAll('.remove-item-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            fetch(btn.dataset.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('cart-panel-mount').innerHTML = data.html;
                    document.getElementById('cart-count').textContent = data.count;
                    bindCartCloseEvents();
                });
        });
    });
}

function refreshCartCount() {
    fetch(cartPanelUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById('cart-count').textContent = data.count;
        });
}

document.addEventListener('DOMContentLoaded', function () {

    refreshCartCount();
    bindCartCloseEvents();

    const cartToggle = document.getElementById('cart-toggle');
    cartToggle.addEventListener('click', function (e) {
        e.preventDefault();
        openCartPanel();
    });

    document.getElementById('cart-overlay').addEventListener('click', closeCartPanel);

    document.querySelectorAll('.add-to-cart-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(form);

            fetch(form.dataset.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('cart-count').textContent = data.count;
                    openCartPanel();
                });
        });
    });

});