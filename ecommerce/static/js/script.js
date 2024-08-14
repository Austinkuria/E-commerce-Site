$(document).ready(function() {
    function getCsrfToken() {
        return $('meta[name="csrf-token"]').attr('content');
    }

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

    $(document).on('click', '.add-to-cart', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/add_to_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'csrfmiddlewaretoken': getCsrfToken()
            },
            success: function(response) {
                if (response.status === 'success') {
                    alert('Item added to cart successfully');
                    updateCart();
                } else {
                    alert('Failed to add item to cart');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error adding to cart:', status, error);
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

    $(document).on('click', '.increase-quantity', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/update_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'action': 'increase',
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
                console.error('Error increasing quantity:', status, error);
            }
        });
    });

    $(document).on('click', '.decrease-quantity', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/update_cart/',
            method: 'POST',
            data: {
                'product_id': productId,
                'action': 'decrease',
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
                console.error('Error decreasing quantity:', status, error);
            }
        });
    });

    $('#checkout-button').click(function() {
        alert('Checkout functionality not implemented yet.');
    });

    updateCart();
});

// Products modal
document.addEventListener('DOMContentLoaded', function() {
    $('#productModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var name = button.data('name'); // Extract info from data-* attributes
        var price = button.data('price');
        var description = button.data('description');
        var rating = button.data('rating');
        var reviews = button.data('reviews');
        var image = button.data('image');

        // Update the modal's content.
        var modal = $(this);
        modal.find('#modalProductName').text(name);
        modal.find('#modalProductPrice').text('Ksh ' + price);
        modal.find('#modalProductDescription').text(description);
        modal.find('#modalProductImage').attr('src', image);
        modal.find('#modalProductReviews').text(reviews);

        // Generate star rating
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

        // Add event listener for add-to-cart button in the modal
        modal.find('.add-to-cart').off('click').on('click', function() {
            let productId = button.data('id'); // Use the ID from the button that triggered the modal
            $.ajax({
                url: '/add_to_cart/',
                method: 'POST',
                data: {
                    'product_id': productId,
                    'csrfmiddlewaretoken': getCsrfToken()
                },
                success: function(response) {
                    if (response.status === 'success') {
                        alert('Item added to cart successfully');
                        updateCart();
                    } else {
                        alert('Failed to add item to cart');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error adding to cart:', status, error);
                }
            });
        });
    });
});

// Login form validation
$(document).ready(function() {
    // Real-time validation for login form
    $('#loginEmail').on('input', function() {
        validateLoginFormField('email');
    });

    $('#loginPassword').on('input', function() {
        validateLoginFormField('password');
    });

    // Login form submission
    $('#loginForm').on('submit', function(event) {
        if (!validateLoginForm()) {
            event.preventDefault(); // Stop form submission if validation fails
            $(this).addClass('was-validated');
            return;
        }

        // Optionally provide user feedback
        alert('Login successful!');
    });

    function validateLoginForm() {
        var email = $('#loginEmail').val().trim();
        var password = $('#loginPassword').val().trim();
        var isValid = true;

        // Email validation regex
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            $('#loginEmail').addClass('is-invalid');
            isValid = false;
        } else {
            $('#loginEmail').removeClass('is-invalid');
        }

        // Password validation regex
        var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        if (!passwordPattern.test(password)) {
            $('#loginPassword').addClass('is-invalid');
            isValid = false;
        } else {
            $('#loginPassword').removeClass('is-invalid');
        }

        return isValid;
    }

    function validateLoginFormField(field) {
        var isValid = true;
        var value = $(`#login${capitalizeFirstLetter(field)}`).val().trim();
        
        if (field === 'email') {
            var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(value)) {
                $(`#login${capitalizeFirstLetter(field)}`).addClass('is-invalid');
                isValid = false;
            } else {
                $(`#login${capitalizeFirstLetter(field)}`).removeClass('is-invalid');
            }
        } else if (field === 'password') {
            var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
            if (!passwordPattern.test(value)) {
                $(`#login${capitalizeFirstLetter(field)}`).addClass('is-invalid');
                isValid = false;
            } else {
                $(`#login${capitalizeFirstLetter(field)}`).removeClass('is-invalid');
            }
        }

        return isValid;
    }

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});
