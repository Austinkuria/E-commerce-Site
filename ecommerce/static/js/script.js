$(document).ready(function() {
    let csrfToken = getCsrfToken(); // Get the CSRF token once when the document is ready

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
                $('#cart-count').text(response.cart_items.length);
                let cartList = $('#cart-list');
                cartList.empty();
                let subtotal = 0;

                if (response.cart_items.length === 0) {
                    cartList.append('<li class="list-group-item text-center">Cart is empty</li>');
                } else {
                    response.cart_items.forEach((item) => {
                        subtotal += item.price * item.quantity;
                        cartList.append(`
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
                $('#cart-subtotal').text(subtotal.toFixed(2));
            },
            error: function(xhr, status, error) {
                console.error('Error fetching cart:', status, error);
            }
        });
    }

    // Event listener for adding an item to the cart
    $(document).on('click', '.add-to-cart, #modal-add-to-cart', function() {
        let productId = $(this).data('id');

        // Ensure the product ID is valid
        if (!productId) {
            alert('Product ID is missing. Please try again.');
            return;
        }

        $.ajax({
            url: '/add_to_cart/',
            type: 'POST',
            data: {
                product_id: productId, // Correctly set the product ID
                csrfmiddlewaretoken: getCsrfToken() // Use the CSRF token getter function
            },
            success: function(response) {
                updateCart(); // Refresh the cart display after adding the item
                console.log("Product added successfully");
            },
            error: function(xhr, status, error) {
                console.error("Error adding to cart: " + error);
            }
        });
    });

    // Event listener for removing an item from the cart
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

    // Event listener for increasing or decreasing item quantity
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

    // Set up the modal when it’s shown
    $('#productModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var productId = button.data('id'); // Extract product ID from the triggering element
        var modal = $(this);

        // Populate modal fields
        modal.find('#modalProductName').text(button.data('name'));
        modal.find('#modalProductPrice').text('Ksh ' + button.data('price'));
        modal.find('#modalProductDescription').text(button.data('description'));
        modal.find('#modalProductImage').attr('src', button.data('image'));
        modal.find('#modalProductReviews').text(button.data('reviews'));

        // Populate star ratings
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

        // Set the correct product ID in the modal’s add-to-cart button
        modal.find('#modal-add-to-cart').data('id', productId);

        // Debugging: Log the product ID to ensure it’s correct
        console.log('Product ID set in modal:', productId);
    });

    // Checkout button functionality
    $('#checkout-button').click(function() {
        alert('Checkout functionality not implemented yet.');
    });

    // Confirmation functionality
    $('#modal-add-to-cart').on('click', function() {
        var productId = $(this).data('id');
        var quantity = $('#modalProductQuantity').val();
        var productName = $('#modalProductName').text();
     //snackbar functionality
        function showSnackbar(message) {
            var snackbar = $('#snackbar');
            snackbar.text(message);
            snackbar.addClass('show');
            setTimeout(function() {
                snackbar.removeClass('show');
            }, 3000);
        }       
        // Show a confirmation dialog
        if (confirm(`Do you want to add ${quantity} x "${productName}" to your cart?`)) {
            // Proceed to add to cart
            $.ajax({
                url: '/add_to_cart/',
                type: 'POST',
                data: {
                    product_id: productId,
                    quantity: quantity,
                    csrfmiddlewaretoken: getCsrfToken()
                },
                success: function(response) {
                    // Show a snackbar or tooltip notification
                    showSnackbar("Product added to cart successfully!");
    
                    // Optionally close the modal
                    $('#productModal').modal('hide');
                },
                error: function(xhr, status, error) {
                    console.error("Error adding to cart: " + error);
                }
            });
        }
    });

   

    // Initialize the cart when the page loads
    updateCart();
});

 