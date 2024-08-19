$(document).ready(function() {
    let csrfToken = getCsrfToken(); // Get the CSRF token once when the document is ready

    // Cache jQuery selectors
    var $cartList = $('#cart-list');
    var $cartCount = $('#cart-count');
    var $cartSubtotal = $('#cart-subtotal');
    var $productModal = $('#productModal');
    var $checkoutButton = $('#checkout-button');
    var $orderNowButton = $('#order-now-button');

    // Function to get CSRF token
    function getCsrfToken() {
        return $('meta[name="csrf-token"]').attr('content');
    }

    // Function to update the cart display
    function updateCart() {
        $.ajax({
            url: '/get_cart/',
            method: 'GET',
            success: function(response) {
                $cartCount.text(response.cart_items.length);
                $cartList.empty();
                let subtotal = 0;

                if (response.cart_items.length === 0) {
                    $cartList.append('<li class="list-group-item text-center">Cart is empty</li>');
                } else {
                    response.cart_items.forEach((item) => {
                        subtotal += item.price * item.quantity;
                        $cartList.append(`
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <div>
                                    ${item.name} - Ksh ${item.price}
                                    <div>
                                        <button class="btn btn-sm btn-secondary decrease-quantity" data-id="${item.id}">-</button>
                                        <span class="mx-2">${item.quantity}</span>
                                        <button class="btn btn-sm btn-secondary increase-quantity" data-id="${item.id}">+</button>
                                    </div>
                                </div>
                                <button class="btn btn-sm btn-danger remove-from-cart" data-id="${item.id}">Remove</button>
                            </li>
                        `);
                    });
                }
                $cartSubtotal.text(subtotal.toFixed(2));
            },
            error: function(xhr, status, error) {
                console.error('Error fetching cart:', status, error);
            }
        });
    }

    // Event listeners for actions
    $(document).on('click', '.add-to-cart, #modal-add-to-cart', function() {
        let productId = $(this).data('id');
        if (!productId) {
            alert('Product ID is missing. Please try again.');
            return;
        }

        $.ajax({
            url: '/add_to_cart/',
            type: 'POST',
            data: {
                product_id: productId,
                csrfmiddlewaretoken: getCsrfToken()
            },
            success: function(response) {
                updateCart();
                console.log("Product added successfully");
            },
            error: function(xhr, status, error) {
                console.error("Error adding to cart: " + error);
            }
        });
    });

    $(document).on('click', '.remove-from-cart', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/remove_from_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'csrfmiddlewaretoken': getCsrfToken()
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart();
                } else {
                    alert('Failed to remove item from cart');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error removing from cart:', status, error);
            }
        });
    });

    $(document).on('click', '.increase-quantity, .decrease-quantity', function() {
        let productId = $(this).data('id');
        let action = $(this).hasClass('increase-quantity') ? 'increase' : 'decrease';
        $.ajax({
            url: '/update_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'action': action,
                'csrfmiddlewaretoken': getCsrfToken()
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart();
                } else {
                    alert('Failed to update item quantity');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error updating quantity:', status, error);
            }
        });
    });

    $productModal.on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var productId = button.data('id');
        var modal = $(this);

        modal.find('#modalProductName').text(button.data('name'));
        modal.find('#modalProductPrice').text('Ksh ' + button.data('price'));
        modal.find('#modalProductDescription').text(button.data('description'));
        modal.find('#modalProductImage').attr('src', button.data('image'));
        modal.find('#modalProductReviews').text(button.data('reviews'));

        var rating = button.data('rating');
        var stars = '';
        for (var i = 0; i < 5; i++) {
            if (i < Math.floor(rating)) {
                stars += '<i class="bi bi-star-fill"></i>';
            } else if (i < rating) {
                stars += '<i class="bi bi-star-half"></i>';
            } else {
                stars += '<i class="bi bi-star"></i>';
            }
        }
        modal.find('#modalProductRating').html(stars);

        modal.find('#modal-add-to-cart').data('id', productId);

        console.log('Product ID set in modal:', productId);
    });

    $('#modal-add-to-cart').on('click', function() {
        var productId = $(this).data('id');
        var quantity = $('#modalProductQuantity').val();
        var productName = $('#modalProductName').text();

        function showSnackbar(message) {
            var snackbar = $('#snackbar');
            snackbar.text(message);
            snackbar.addClass('show');
            setTimeout(function() {
                snackbar.removeClass('show');
            }, 3000);
        }

        if (confirm(`Do you want to add ${quantity} x "${productName}" to your cart?`)) {
            $.ajax({
                url: '/add_to_cart/',
                type: 'POST',
                data: {
                    product_id: productId,
                    quantity: quantity,
                    csrfmiddlewaretoken: getCsrfToken()
                },
                success: function(response) {
                    showSnackbar("Product added to cart successfully!");
                    $productModal.modal('hide');
                },
                error: function(xhr, status, error) {
                    console.error("Error adding to cart: " + error);
                }
            });
        }
    });
    updateCart();
})