# Lang-Learning

This project aims to provide a platform for language learning.

## Key Features & Benefits

*   **User Authentication:** Secure user accounts with email and password-based authentication.
*   **Instructor Profiles:**  Detailed profiles for instructors showcasing their expertise.
*   **Course Management:**  (Future Feature) Ability to create, manage, and enroll in language courses.
*   **Subscription Management:** (Future Feature) Implement subscription plans for access to premium features.
*   **Dockerized Deployment:**  Easy deployment with Docker.

## Prerequisites & Dependencies

Before you begin, ensure you have met the following requirements:

*   **Python 3.12.1:**  The project is built using Python 3.12.1.
*   **pip:**  Python package installer.
*   **Docker:** For containerization.
*   **Git:** For version control.

## Installation & Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/benedixit34/lang-learning.git
    cd lang-learning
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install git+https://github.com/SY-2024/drf-stripe-subscription.git
    ```

4.  **Database Setup:**  Configure the database settings (e.g., in `settings.py`). This step depends on your database choice (e.g., PostgreSQL, MySQL, SQLite).  You'll likely need to create a database and set the appropriate credentials in the Django settings file.

5.  **Run Migrations:**

    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Start the development server:**

    ```bash
    python manage.py runserver
    ```

8.  **Docker Setup (Alternative):**

    ```bash
    docker build -t lang-learning .
    docker run -p 8000:8000 lang-learning
    ```

## Usage Examples & API Documentation

(Detailed API documentation will be provided in future versions. Below are basic examples).

*   **Accessing the Admin Panel:**

    Navigate to `/admin` in your browser.  Use the superuser credentials created earlier.

*   **Basic User Authentication (Example):**

    The project utilizes `app/accounts/backends.py` for email-based authentication.

## Configuration Options

The project can be configured via environment variables or within the Django settings file (`settings.py`). Common configuration options include:

*   **Database settings:**  Database engine, name, user, password, host, and port.
*   **Secret key:**  A unique secret key for the Django project.  **Important:**  Do not expose this key in your repository or public configuration.  Set it as an environment variable.
*   **Debug mode:**  Enable or disable debug mode.  Set to `False` in production.
*   **Allowed hosts:**  A list of allowed hostnames for the Django project.

## Acknowledgments
*   [drf-stripe-subscription](https://github.com/SY-2024/drf-stripe-subscription):  Used for Stripe subscription integration.
