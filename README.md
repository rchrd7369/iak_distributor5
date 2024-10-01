# Integrated Corporate Application - Distributor Module

This is the **Distributor Module** of an integrated corporate application, built using **Flask** and **Firebase Firestore** for managing distributor-related operations like order tracking, shipping cost estimation, and order status updates. The application includes key features such as managing distributor orders, confirming shipments, and tracking shipping status using tracking numbers (resi).

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Distributor module allows users to:
- Manage distributors, add or confirm orders.
- Calculate shipping costs based on the origin and destination cities as well as the package weight.
- Track shipments by entering a tracking number (resi).
- Update and manage shipping statuses via an admin interface.

## Features

- **Login System**: Authenticate users before granting access to the admin interface.
- **Order Management**: Admins can add, edit, confirm, and delete distributor orders.
- **Shipping Cost Calculation**: Automatically calculates shipping costs based on the selected origin, destination cities, and weight.
- **Real-time Database**: Integrates with **Firebase Firestore** to store and retrieve distributor orders and shipping data.
- **Order Tracking**: Users can check the status of their orders using a tracking number (resi).
- **Shipping Status Update**: Admins can update the shipping status and move completed orders to history.

## Technologies Used

- **Python**: Backend development.
- **Flask**: Lightweight web framework for building the application.
- **Firebase**: Firestore is used to store and manage distributor data.
- **HTML/CSS**: To structure and style the web interface.
- **JavaScript**: Adds interactivity for functionalities like password visibility toggling and form handling.

## Setup Instructions

To set up the project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/afifilhamh/iak_distributor5.git
cd distributor-module
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Firebase

- Create a Firebase project and set up Firestore.
- Download the service account key from Firebase and save it in the root directory with the filename `ladju_distributor.json`.
  
### 5. Run the Application

```bash
python app.py
```

The application should now be running on `http://localhost:5000`.

## Usage

Once the application is running, here’s how you can use it:

### User Features

1. **Login**: Users must log in through `/login`. Credentials are validated using data stored in Firebase.
2. **Order Tracking**: Visitors can check the status of their orders using their tracking number (resi) by entering it on the homepage.

### Admin Features

1. **Admin Dashboard**: Once logged in, users can access the admin interface where they can:
   - View all distributor orders.
   - Confirm orders by calculating shipping costs based on distance and weight.
   - Update order statuses (e.g., "Kurir mengambil paket", "Pesanan Selesai").
   - Delete completed orders from the history.
   
2. **Shipping Cost Calculation**: The system calculates shipping costs based on predefined distances between cities (`JARAK_KOTA`) and the package weight. Admins can then confirm the cost and finalize the shipment.

### Routes

- `/login`: User login page.
- `/logout`: Logs out the current session.
- `/admin`: Admin dashboard for managing orders.
- `/api/distributor5/orders/cek_ongkir`: API route for checking shipping costs.
- `/api/distributor5/orders/fix_kirim`: API route for confirming an order.
- `/update_status`: Update the status of a shipment.
- `/`: Home page, allows users to check order status by entering a tracking number.

## Contributing

Contributions are welcome! To contribute to this project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
