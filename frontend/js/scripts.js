$(document).ready(function() {
        let cart = JSON.parse(localStorage.getItem('cart')) || [];
        
        function updateCart() {
            $('#cart-count').text(cart.length);
            
            // Update the cart section in the modal
            let cartList = $('#cart-list');
            cartList.empty();
            if (cart.length === 0) {
                cartList.append('<li class="list-group-item text-center">Cart is empty</li>');
            } else {
                cart.forEach((item, index) => {
                    cartList.append(`
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            ${item.name} - Ksh ${item.price}
                            <button class="btn btn-sm btn-danger remove-from-cart" data-index="${index}">Remove</button>
                        </li>
                    `);
                });
            }
        }

        $('.add-to-cart').click(function() {
            let card = $(this).closest('.card');
            let productName = card.find('.card-title').text();
            let productPrice = card.find('.card-text').text().replace('Ksh ', '');
    
            cart.push({ name: productName, price: productPrice });
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCart();
        });
    
        $(document).on('click', '.remove-from-cart', function() {
            let index = $(this).data('index');
            cart.splice(index, 1);
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCart();
        });

        updateCart();
    });