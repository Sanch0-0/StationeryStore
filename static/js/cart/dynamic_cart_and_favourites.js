function addToFavourite(productId) {
    const form = document.getElementById(`add-to-favourite-form-${productId}`);
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Optionally update the UI to indicate the product was added to favourites
            alert('Product added to favourites!');
        } else {
            alert('Failed to add product to favourites.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function addToCart(productId) {
    const form = document.getElementById(`add-to-cart-form-${productId}`);
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Product added to cart!');

            // Ensure the element exists before trying to update it
            const totalQuantityElement = document.getElementById('cart-total-quantity');
            const totalPriceElement = document.getElementById('cart-total-price');

            if (totalQuantityElement) {
                totalQuantityElement.innerText = data.count_of_products;
            } else {
                console.error('Element with ID "cart-total-quantity" not found');
            }

            if (totalPriceElement) {
                totalPriceElement.innerText = `$ ${data.cart_total_price}`;
            } else {
                console.error('Element with ID "cart-total-price" not found');
            }
        } else {
            alert('Failed to add product to cart.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
