$(document).ready(function() {
    // Retrieve the CSRF token
    let csrfToken = getCsrfToken();

    // Cache jQuery selectors for performance
    var $cartList = $('#cart-list');
    var $cartCount = $('#cart-count');
    var $cartSubtotal = $('#cart-subtotal');
    var $productModal = $('#productModal');
    var $checkoutButton = $('#checkout-button');
    var $orderNowButton = $('#order-now-button');

    // Set up global AJAX settings
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    });

    // Function to get CSRF token from meta tag
    function getCsrfToken() {
        return $('meta[name="csrf-token"]').attr('content');
    }

    // Update the cart display
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

    // Populate and display product details in the modal
    $(document).ready(function() {
        $('#productModal').on('show.bs.modal', function(event) {
            var button = $(event.relatedTarget); // Button that triggered the modal
            var productId = button.data('id');
            var productName = button.data('name');
            var productPrice = button.data('price');
            var productDescription = button.data('description');
            var productImage = button.data('image');
            var productRating = button.data('rating');
            var productReviews = button.data('reviews');
    
            // Update modal content with product details
            var modal = $(this);
            modal.find('#modalProductName').text(productName);
            modal.find('#modalProductPrice').text('Ksh ' + productPrice);
            modal.find('#modalProductDescription').text(productDescription);
            modal.find('#modalProductImage').attr('src', productImage);
            modal.find('#modalProductReviews').text(productReviews);
    
            // Create star rating display
            var stars = '';
            for (var i = 0; i < 5; i++) {
                if (i < Math.floor(productRating)) {
                    stars += '<i class="bi bi-star-fill"></i>';
                } else if (i < productRating) {
                    stars += '<i class="bi bi-star-half"></i>';
                } else {
                    stars += '<i class="bi bi-star"></i>';
                }
            }
            modal.find('#modalProductRating').html(stars);
    
            modal.find('#modal-add-to-cart').data('id', productId);

            // Bind the product data to the "Order Now" button
            modal.find('#order-now-button').data('id', productId);
            modal.find('#order-now-button').data('name', productName);
            modal.find('#order-now-button').data('price', productPrice);
            modal.find('#order-now-button').data('description', productDescription);
        
        });
    
        // Handle "Order Now" button click
    $('#order-now-button').on('click', function() {
        var productId = $(this).data('id');
        var productName = $(this).data('name');
        var productPrice = $(this).data('price');
        var productDescription = $(this).data('description');
        var productQuantity = document.getElementById('modalProductQuantity').value; // Get quantity


        if (productId !== undefined && productName !== undefined && productPrice !== undefined && productDescription !== undefined  && productQuantity !== undefined) {
            // Redirect to checkout with product details
            window.location.href = `/checkout/?product_id=${productId}&product_name=${encodeURIComponent(productName)}&product_price=${productPrice}&product_description=${encodeURIComponent(productDescription)}&product_quantity=${productQuantity}`;
        } else {
            console.error('Product details are missing, unable to proceed to checkout.');
        }
    });

    });
    
    // Handle adding a product to the cart
    $('#modal-add-to-cart').on('click', function() {
        var productId = $(this).data('id');
        var quantity = $('#modalProductQuantity').val();
        var productName = $('#modalProductName').text();
        var productPrice = parseFloat($('#modalProductPrice').text().replace('Ksh ', ''));
        function showSnackbar(message) {
            var snackbar = $('#snackbar');
            snackbar.text(message);
            snackbar.addClass('show');
            setTimeout(function() {
                snackbar.removeClass('show');
            }, 3000);
        }

        if (confirm(`Add ${quantity} x "${productName}" to your cart?`)) {
            $.ajax({
                url: '/add_to_cart/',
                type: 'POST',
                data: {
                    product_id: productId,
                    quantity: quantity,
                    price: productPrice,
                    csrfmiddlewaretoken: csrfToken
                },
                success: function(response) {
                    showSnackbar("Product added to cart!");
                    $('#productModal').modal('hide'); // Close the modal
                    updateCart(); // Refresh the cart display
                },
                error: function(xhr, status, error) {
                    console.error("Error adding to cart: " + error);
                }
            });
        }
    });

    // Remove an item from the cart
    $(document).on('click', '.remove-from-cart', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/remove_from_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart(); // Refresh the cart display
                } else {
                    alert('Failed to remove item from cart');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error removing from cart:', status, error);
            }
        });
    });

    // Update quantity of an item in the cart
    $(document).on('click', '.increase-quantity, .decrease-quantity', function() {
        let productId = $(this).data('id');
        let action = $(this).hasClass('increase-quantity') ? 'increase' : 'decrease';
        $.ajax({
            url: '/update_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'action': action,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart(); // Refresh the cart display
                } else {
                    alert('Failed to update item quantity');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error updating quantity:', status, error);
            }
        });
    });
});

