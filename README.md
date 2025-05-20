# Hourly Subnet Scanner

This project is a lightweight application designed to perform hourly subnet scanning using `nmap`, store the results in an SQLite database, send notifications via a Telegram bot, and provide a web dashboard using Flask with HTTP Basic Auth.

## Project Structure

```
hourly-subnet-scanner
├── src
│   ├── scanner.py          # Responsible for scanning subnets and saving results
│   ├── db.py               # Manages SQLite database operations
│   ├── notifier.py          # Implements Telegram bot notifications
│   ├── dashboard
│   │   ├── __init__.py     # Initializes the Flask application
│   │   ├── routes.py       # Defines web dashboard routes
│   │   └── auth.py         # Handles HTTP Basic Authentication
│   └── config.py           # Contains configuration settings
├── requirements.txt         # Lists project dependencies
└── README.md                # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd hourly-subnet-scanner
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application:
   - Update the `src/config.py` file with your database path and Telegram bot token.

## Usage

1. Run the application:
   ```
   python src/scanner.py
   ```

2. Access the web dashboard:
   - Open your web browser and navigate to `http://localhost:80`.

3. Set up your Telegram bot:
   - Follow the instructions provided by the Telegram Bot API to create a bot and obtain your bot token.

## Features

- Hourly subnet scanning using `nmap`.
- Results stored in an SQLite database.
- Notifications sent via a Telegram bot.
- Web dashboard for monitoring scan results with HTTP Basic Auth.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.