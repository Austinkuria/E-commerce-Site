
# E-Commerce Website

## Overview

This project is a fully functional e-commerce website built using Django for the backend and HTML, CSS, Bootstrap, and JavaScript for the frontend. It includes features like product listing, shopping cart functionality, user authentication, and order management.

---

## Features

### User Features:
- **User Authentication**: Users can sign up, log in, and manage their profiles securely.
- **Product Browsing**: Browse a variety of products with detailed descriptions, images, and prices.
- **Cart Management**: Add, update, or remove products from the shopping cart, and view a summary of items.
- **Order Placement**: Users can place orders and view their order history.
- **Responsive Design**: The website is fully responsive and works seamlessly across mobile, tablet, and desktop devices.
- **Profile Management**: Users can update their profile information, including email, phone number, and profile picture.

### Admin Features:
- **Product Management**: Admins can add, update, or delete products from the inventory.
- **Order Management**: View and manage customer orders.
- **User Management**: Manage users and their access to the platform.

---

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Bootstrap, JavaScript, jQuery
- **Database**: SQLite (for development)
- **Others**: Django Authentication, Django Forms, Django Templating Engine

---

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Austinkuria/E-commerce-Site.git
   ```
2. Change into the project directory:
   ```bash
   cd E-commerce-Site
   cd ecommerce
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Migrate the database:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

---

## Project Structure

```
ecommerce-site/
│
├── ecommerce/            # Main Django project folder
│   ├── settings.py       # Settings for Django
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI entry point for the project
│   └── ...
│
├── myapp/                # Django app for the e-commerce site
│   ├── models.py         # Database models
│   ├── views.py          # Views for handling requests
│   ├── forms.py          # Forms for handling user input
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JavaScript, and images
│
├── manage.py             # Django's command-line utility
├── db.sqlite3            # SQLite database file
└── requirements.txt      # Project dependencies
```

---

## How to Use

1. **User Registration**: Sign up using the registration form.
2. **Add to Cart**: Select products to add to the cart and adjust quantities as needed.
3. **Checkout**: Review items in the cart and complete the order process.
4. **User Profile**: Update personal information and view order history.

---

## Future Enhancements

- **Payment Integration**: Add secure payment gateways for order completion.
- **Order Tracking**: Implement real-time order tracking functionality.
- **Wishlist**: Add the ability for users to save items to a wishlist.
- **Product Reviews**: Allow users to leave reviews and ratings for products.
- **Browse Products**: View products by categories or search by keyword.

---

## Contributions

Contributions are welcome! Please fork this repository and submit a pull request if you have any features or improvements you'd like to add.

---

### **Project Description**

The **E-commerce Site** is an online shopping platform designed for a seamless user experience. It allows users to browse products, add them to the cart, and manage their orders. Admins have full control over product management, user accounts, and order processing. 

This project aims to be a comprehensive solution for businesses looking to sell products online, with scalability in mind for future upgrades like payment integration, wishlist functionality, and product reviews. The website is built using Django and adheres to modern web development practices, offering responsive design and an easy-to-use interface for users and administrators alike.
