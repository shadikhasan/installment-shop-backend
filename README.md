# Installment Shop Backend (version 1.0)

Installment Shop Backend is a robust API for an e-commerce platform that enables customers to purchase products with flexible installment payment plans. It features secure OTP-based registration, JWT authentication, installment tracking, email notifications, and comprehensive admin reports. Built with Django REST Framework (DRF), this project is ideal for developers looking to explore or contribute to a scalable e-commerce backend.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Technologies](#technologies)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Postman Collection](#postman-collection)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

### Secure Authentication:
- Email-based registration with 6-digit OTP verification (10-minute expiry).
- JWT-based login with access and refresh tokens.
- Profile management for updating user details.

### Product Management:
- Public product listings for all users.
- Admin-only CRUD operations for products (create, update, delete).

### Installment Payments:
- Flexible purchase system with customizable installment plans.
- **Validations**:
  - First installment ≥ 30% of total price (or full amount for single installment).
  - Late payments incur a 10% penalty.
- Track paid and due amounts for each installment.

### Notifications:
- Automated email reminders for upcoming installment due dates.

### Admin Dashboard & Reports:
- Weekly and monthly payment summaries for admins.
- Interactive charts visualizing total purchases, paid, and due amounts (last 6 months).
- User statistics (total, verified, unverified users).

### User Dashboard:
- Displays total due, paid amounts, purchase history, and installment status.

### Frontend Integration Ready:
- Supports data tables with pagination and live search.
- Toast notifications for user feedback (success/error).

## Demo

**Live URL**: *Coming Soon* (Deployed on Heroku/Vercel)

**Screenshots**:
- Admin Dashboard: *View*
- User Purchase History: *View*

> **Note**: To test the API locally, follow the Installation steps.

## Technologies

- **Backend**: Python 3.8+, Django 4.2, Django REST Framework 3.14
- **Authentication**: `django-rest-framework-simplejwt`
- **Database**: SQLite (default), supports PostgreSQL/MySQL
- **Email**: Django’s `send_mail` for OTP and notifications
- **API Testing**: Postman
- **Version Control**: Git, GitHub
- **Deployment**: Heroku/Vercel (configurable)

## Installation

### Prerequisites

- Python 3.8+
- Git
- Virtualenv (recommended)
- Postman (for API testing)

### Steps

1. **Clone the Repository**:
```bash
git clone https://github.com/shadikhasan/installment-shop-backend.git
cd installment-shop-backend
```

2. **Set Up a Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**:
Create a `.env` file in the project root:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

> **Tip**: Use a Gmail App Password for `EMAIL_HOST_PASSWORD` if 2FA is enabled.

5. **Apply Migrations**:
```bash
python manage.py migrate
```

6. **Create an Admin User**:
```bash
python manage.py createsuperuser
```

7. **Run the Server**:
```bash
python manage.py runserver
```

Access the API at `http://127.0.0.1:8000`.

## API Endpoints

The API is organized into logical groups for ease of use:

| Group | Endpoint | Method | Description | Permissions |
|-------|----------|--------|-------------|-------------|
| **Auth** | `/accounts/register/` | POST | Register a new user (sends OTP) | Public |
|  | `/accounts/verify-otp/` | POST | Verify OTP to activate account | Public |
|  | `/accounts/login/` | POST | Login to obtain JWT tokens | Public |
|  | `/accounts/profile/` | GET/PATCH | View or update user profile | Authenticated |
| **Products** | `/products/` | GET/POST | List or create products | GET: Public, POST: Admin |
|  | `/products/{id}/` | GET/PUT/DELETE | Manage a specific product | Admin |
| **Purchases** | `/purchases/create/` | POST | Create a purchase with installments | Authenticated |
|  | `/purchases/` | GET | List all purchases | Admin |
|  | `/purchases/my/` | GET | List user’s purchases | Authenticated |
| **Installments** | `/installments/` | GET | List user’s installments | Authenticated |
|  | `/installments/next-due/` | GET | Get next due installment | Authenticated |
|  | `/installments/pay/{id}/` | POST | Pay an installment | Authenticated |
| **Dashboard** | `/public/global-summary/` | GET | Get total products | Public |
|  | `/user/summary/` | GET | Get user’s summary (due, paid, etc.) | Authenticated |
|  | `/user-stats/` | GET | Get user statistics | Admin |
| **Reports** | `/reports/chart/summary/` | GET | Monthly payment summary (charts) | Admin |
|  | `/reports/payment-summary/weekly/` | GET | Weekly user payment summary | Admin |
|  | `/reports/payment-summary/monthly/` | GET | Monthly user payment summary | Admin |

### Example Request

**POST** `/purchases/create/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Body**:
```json
{
  "product": 1,
  "quantity": 2,
  "first_installment_amount": 6000,
  "installment_count": 3
}
```

**Response (201)**:
```json
{
  "id": 1,
  "product_name": "Laptop",
  "total_price": 20000,
  "quantity": 2,
  "first_installment_amount": 6000,
  "installment_count": 3,
  "status": "due"
}
```

**Validations**:
- `first_installment_amount` ≥ 30% of total price if `installment_count > 1`.
- `installment_count ≥ 1`.
- No overpayment allowed.

## Postman Collection

A comprehensive Postman collection is available in the repository (`Django_OTP_JWT_API.postman_collection.json`). It includes:

- All API endpoints with sample requests and responses.
- Environment variables (`base_url`, `access_token`).
- Detailed validations (e.g., OTP expiry, late payment penalties).
- Organized into folders: Auth, Products, Purchases, Installments, Dashboard, Reports.

### Import Instructions

1. Open Postman.
2. Go to File > Import and select the JSON file.
3. Configure environment variables:
   - `base_url`: http://127.0.0.1:8000 or your live URL.
   - `access_token`: Obtained from `/accounts/login/`.

## Database Schema

The database schema includes the following core models:

- **Customer**: Stores user details (username, email, password, OTP, verification status).
- **Product**: Stores product details (name, price).
- **Purchase**: Links customers to products with total price, quantity, and installment details.
- **Installment**: Tracks individual installments (paid amount, due amount, due date, status).

> Note: An ERD is available at `docs/erd.png` (create using draw.io if not present).

## Contributing

We welcome contributions to enhance the project! To contribute:

1. **Fork the Repository**:
```bash
git clone https://github.com/shadikhasan/installment-shop-backend.git
```

2. **Create a Feature Branch**:
```bash
git checkout -b feature/your-feature
```

3. **Commit Changes**:
```bash
git commit -m "Add your feature"
```

4. **Push and Create a Pull Request**:
```bash
git push origin feature/your-feature
```

Then open a pull request on GitHub with a clear description of your changes.

### Guidelines

- Follow [PEP 8](https://pep8.org/) for Python code.
- Write clear commit messages (e.g., “Add pagination to purchases endpoint”).
- Include tests for new features (use Django’s test framework).
- Update documentation if necessary.

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as per the license terms.

## Contact

- **GitHub**: [shadikhasan](https://github.com/shadikhasan)
- **Email**: shadik.sk420@gmail.com

> For questions, feedback, or collaboration, open an issue or reach out directly. Happy coding! 🚀