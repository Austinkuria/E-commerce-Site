$(document).ready(function() {
    // Initialize cart from localStorage or set to an empty array
    let cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Function to update the cart display and subtotal
    function updateCart() {
        $('#cart-count').text(cart.length); // Update cart item count
        
        let cartList = $('#cart-list');
        cartList.empty(); // Clear current cart items
        let subtotal = 0;
        
        if (cart.length === 0) {
            cartList.append('<li class="list-group-item text-center">Cart is empty</li>'); // Display message if cart is empty
        } else {
            cart.forEach((item, index) => {
                subtotal += item.price * item.quantity; // Calculate subtotal
                cartList.append(`
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            ${item.name} - Ksh ${item.price}
                            <div>
                                <button class="btn btn-sm btn-secondary decrease-quantity" data-index="${index}">-</button>
                                <span class="mx-2">${item.quantity}</span>
                                <button class="btn btn-sm btn-secondary increase-quantity" data-index="${index}">+</button>
                            </div>
                        </div>
                        <button class="btn btn-sm btn-danger remove-from-cart" data-index="${index}">Remove</button>
                    </li>
                `);
            });
        }
        $('#cart-subtotal').text(subtotal.toFixed(2)); // Update subtotal display
    }

    // Add item to cart
    $('.add-to-cart').click(function() {
        let card = $(this).closest('.card');
        let productName = card.find('.card-title').text();
        let productPrice = parseFloat(card.find('.card-text').text().replace('Ksh ', ''));

        let existingItemIndex = cart.findIndex(item => item.name === productName);
        if (existingItemIndex > -1) {
            alert('Item already in cart. To increase quantity, go to the cart.'); // Alert if item is already in cart
        } else {
            cart.push({ name: productName, price: productPrice, quantity: 1 }); // Add new item to cart
            alert('Item added to cart successfully'); // Success alert
        }
        
        localStorage.setItem('cart', JSON.stringify(cart)); // Save cart to localStorage
        updateCart(); // Update cart display
    });

    // Remove item from cart
    $(document).on('click', '.remove-from-cart', function() {
        let index = $(this).data('index');
        cart.splice(index, 1); // Remove item from cart
        localStorage.setItem('cart', JSON.stringify(cart)); // Save updated cart
        updateCart(); // Update cart display
    });

    // Increase item quantity in cart
    $(document).on('click', '.increase-quantity', function() {
        let index = $(this).data('index');
        cart[index].quantity++; // Increment item quantity
        localStorage.setItem('cart', JSON.stringify(cart)); // Save updated cart
        updateCart(); // Update cart display
    });

    // Decrease item quantity in cart
    $(document).on('click', '.decrease-quantity', function() {
        let index = $(this).data('index');
        if (cart[index].quantity > 1) {
            cart[index].quantity--; // Decrement item quantity
        } else {
            cart.splice(index, 1); // Remove item if quantity is 1
        }
        localStorage.setItem('cart', JSON.stringify(cart)); // Save updated cart
        updateCart(); // Update cart display
    });

    // Placeholder for checkout functionality
    $('#checkout-button').click(function() {
        alert('Checkout functionality not implemented yet.');
    });

    updateCart(); // Initial cart update

    // Login form validation
    $('#loginForm').on('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Clear previous validation states
        $(this).removeClass('was-validated');
        $('#loginEmail').removeClass('is-invalid');
        $('#loginPassword').removeClass('is-invalid');

        // Validate form inputs
        if (!validateLoginForm()) {
            $(this).addClass('was-validated');
            return; // Stop form submission if validation fails
        }

        // Clear form fields after submission
        $('#loginEmail').val('');
        $('#loginPassword').val('');

        // Provide user feedback after submission
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
        }

        // Password validation regex
        var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        if (!passwordPattern.test(password)) {
            $('#loginPassword').addClass('is-invalid');
            isValid = false;
        }

        return isValid;
    }

    // Signup form validation
    $('#signUpForm').on('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Clear previous validation states
        $(this).removeClass('was-validated');
        $('#name').removeClass('is-invalid');
        $('#signUpEmail').removeClass('is-invalid');
        $('#signUpPassword').removeClass('is-invalid');
        $('#confirmPassword').removeClass('is-invalid');

        // Validate form inputs
        if (!validateSignUpForm()) {
            $(this).addClass('was-validated');
            return; // Stop form submission if validation fails
        }

        // Clear form fields after submission
        $('#name').val('');
        $('#signUpEmail').val('');
        $('#signUpPassword').val('');
        $('#confirmPassword').val('');

        // Provide user feedback after submission
        alert('Sign up successful!');
    });

    function validateSignUpForm() {
        var name = $('#name').val().trim();
        var email = $('#signUpEmail').val().trim();
        var password = $('#signUpPassword').val().trim();
        var confirmPassword = $('#confirmPassword').val().trim();
        var isValid = true;

        // Name validation
        if (name === '') {
            $('#name').addClass('is-invalid');
            isValid = false;
        }

        // Email validation regex
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            $('#signUpEmail').addClass('is-invalid');
            isValid = false;
        }

        // Password validation regex
        var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        if (!passwordPattern.test(password)) {
            $('#signUpPassword').addClass('is-invalid');
            isValid = false;
        }

        // Confirm password validation
        if (password !== confirmPassword) {
            $('#confirmPassword').addClass('is-invalid');
            isValid = false;
        }

        return isValid;
    }
});
