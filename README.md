# TFB Online Banking System

[Live Demo](https://tfbonlinebank.tfbfoundation.org/)

The TFB Online Banking System is a web-based banking management platform that allows users to perform essential banking activities. Built using Python and Django, it supports account management, transfers, loans, and more, while providing a secure authentication system.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Test Credentials](#test-credentials)
- [API Endpoints](#api-endpoints)
- [Technologies Used](#technologies-used)
- [Admin Access](#admin-access)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Authentication**: Secure registration, login, and logout functionalities.
- **Withdraw**: Allows users to withdraw money from their accounts.
- **Transfer**: Supports transferring funds between accounts.
- **Loan**: Enables users to request and manage loans.
- **Deposit**: Provides functionality to deposit funds into accounts.

## Getting Started

### Prerequisites
- Python 3.x
- Django
- Django Rest Framework

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/jagadishchakma/tfbOnlineBank-backend
    ```
2. Navigate to the project directory:
    ```bash
    cd tfb-online-banking
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the migrations:
    ```bash
    python manage.py migrate
    ```
5. Start the development server:
    ```bash
    python manage.py runserver
    ```
6. Open your web browser and go to `http://localhost:8000` to access the application.

## Usage

Visit the [live demo](https://tfbonlinebank.tfbfoundation.org/) to explore the features.

### Admin
Use the following credentials to log in and explore the banking functionalities:
- **Admin**
  - username: `admin`
  - Password: `123`

## API Endpoints

Below is a list of the API endpoints available in the system:

- **Authentication**
  - `POST /accounts/register/`: Register a new user.
  - `GET /accounts/active/<uid64>/<token>/`: Activate a new user account.
  - `POST /accounts/login/`: User login.
  - `POST /accounts/logout/`: User logout.
  - `POST /accounts/pass_change/`: Change the user password.

- **Account Management**
  - `GET /accounts/search/<str:account>/`: Search for an account.
  - `POST /accounts/upload/profile/`: Upload a profile picture.
  - `PATCH /accounts/update/profile/`: Update profile information.

- **Quick Transfer**
  - `POST /accounts/quick/add/now/time/`: Add a quick transfer option.
  - `GET /accounts/quick/list/all/`: List all quick transfers.

- **Balance Management**
  - `POST /accounts/balance/update/`: Update the account balance.
  - `POST /accounts/balance/withdraw/`: Withdraw funds from the account.
  - `POST /accounts/balance/transfer/`: Transfer funds between accounts.

- **Transactions**
  - `GET /accounts/transactions/`: View all transactions.
  - `GET /accounts/transactions/<str:type>/`: Filter transactions by type.
  - `GET /accounts/transaction/<int:id>/`: View transaction details.
  - `GET /accounts/transactions/list/all/`: List all transactions.
  - `PATCH /accounts/transaction/read/update/<int:id>/`: Mark a transaction as read.

- **Loans**
  - `POST /accounts/loans/`: Apply for a loan.
  - `GET /accounts/loans/list/all/`: View all loan requests.
  - `POST /accounts/loan/pay/<int:id>/`: Make a loan payment.

## Technologies Used
- **Backend**: Python, Django, Django Rest Framework
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Hosting**: Vercel (Frontend), Heroku (Backend)

## Admin Access
Access the admin panel for administrative tasks:

[Admin Panel](https://tfbonlinebank.tfbfoundation.org/admin)

## Contributing
Contributions are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
