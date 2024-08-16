document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[id^="add-to-cart-form-"]');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
            
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                // Update the cart icon with the new values
                updateCartInfo();
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
        });
    });

    function updateCartInfo() {
        fetch(window.location.href, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newCount = doc.querySelector('.header_cart .cart-total-items .count').textContent;
            const newPrice = doc.querySelector('.header_cart .cart-total-price').textContent;

            // Update the cart icon with the new total quantity and price
            const cartIconCount = document.querySelector('.header_cart .cart-total-items .count');
            const cartIconPrice = document.querySelector('.header_cart .cart-total-price');

            if (cartIconCount) {
                cartIconCount.textContent = newCount;
            }
            if (cartIconPrice) {
                cartIconPrice.textContent = newPrice;
            }
        })
        .catch(error => {
            console.error('There was a problem updating the cart info:', error);
        });
    }
});
