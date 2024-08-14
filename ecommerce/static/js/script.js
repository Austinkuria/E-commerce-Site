$(document).ready(function() {
    // Get CSRF token from meta tag
    function getCsrfToken() {
        return $('meta[name="csrf-token"]').attr('content');
    }

    // Function to update cart display
    function updateCart() {
        $.ajax({
            url: '/get-cart/', // Django URL to get cart
            method: 'GET',
            success: function(response) {
                $('#cart-count').text(response.cart_items.length); // Update cart item count
                let cartList = $('#cart-list');
                cartList.empty(); // Clear current cart items
                let subtotal = 0;

                if (response.cart_items.length === 0) {
                    cartList.append('<li class="list-group-item text-center">Cart is empty</li>'); // Display message if cart is empty
                } else {
                    response.cart_items.forEach((item, index) => {
                        subtotal += item.price * item.quantity; // Calculate subtotal
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
                $('#cart-subtotal').text(subtotal.toFixed(2)); // Update subtotal display
            }
        });
    }

    // Add item to cart
    $('.add-to-cart').click(function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/add-to-cart/', // Django URL to add item to cart
            method: 'POST',
            data: {
                'product_id': productId,
                'csrfmiddlewaretoken': getCsrfToken() // Include CSRF token
            },
            success: function(response) {
                if (response.status === 'success') {
                    alert('Item added to cart successfully');
                    updateCart(); // Update cart display
                } else {
                    alert('Failed to add item to cart');
                }
            }
        });
    });

    // Remove item from cart
    $(document).on('click', '.remove-from-cart', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/remove-from-cart/', // Django URL to remove item from cart
            method: 'POST',
            data: {
                'product_id': productId,
                'csrfmiddlewaretoken': getCsrfToken() // Include CSRF token
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart(); // Update cart display
                } else {
                    alert('Failed to remove item from cart');
                }
            }
        });
    });

    // Increase item quantity in cart
    $(document).on('click', '.increase-quantity', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/update-cart/', // Django URL to update item quantity
            method: 'POST',
            data: {
                'product_id': productId,
                'action': 'increase',
                'csrfmiddlewaretoken': getCsrfToken() // Include CSRF token
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart(); // Update cart display
                } else {
                    alert('Failed to update item quantity');
                }
            }
        });
    });

    // Decrease item quantity in cart
    $(document).on('click', '.decrease-quantity', function() {
        let productId = $(this).data('id');
        $.ajax({
            url: '/update-cart/', // Django URL to update item quantity
            method: 'POST',
            data: {
                'product_id': productId,
                'action': 'decrease',
                'csrfmiddlewaretoken': getCsrfToken() // Include CSRF token
            },
            success: function(response) {
                if (response.status === 'success') {
                    updateCart(); // Update cart display
                } else {
                    alert('Failed to update item quantity');
                }
            }
        });
    });

    // Placeholder for checkout functionality
    $('#checkout-button').click(function() {
        // Implement checkout logic
        // ...
        alert('Checkout functionality not implemented yet.');
    });

    updateCart(); // Initial cart update
});

// Products modal
document.addEventListener('DOMContentLoaded', function () {
    // Add event listeners to product cards
    document.querySelectorAll('.card a').forEach(function (element) {
        element.addEventListener('click', function (e) {
            e.preventDefault();
            const modal = new bootstrap.Modal(document.getElementById('productModal'));
            const name = element.getAttribute('data-name');
            const price = element.getAttribute('data-price');
            const description = element.getAttribute('data-description');
            const rating = element.getAttribute('data-rating');
            const reviews = element.getAttribute('data-reviews');
            const image = element.getAttribute('data-image');
            
            document.getElementById('modalProductName').textContent = name;
            document.getElementById('modalProductPrice').textContent = 'Ksh ' + price;
            document.getElementById('modalProductDescription').textContent = description;
            document.getElementById('modalProductRating').textContent = 'Rating: ' + rating;
            document.getElementById('modalProductReviews').textContent = 'Reviews: ' + reviews;
            document.getElementById('modalProductImage').src = image;

            modal.show();
        });
    });

})

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
