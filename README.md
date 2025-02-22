# Render Monitoring System

The Render Monitoring System is an automated tool designed to monitor the activity status of web applications hosted on the Render platform. It sends alerts to a specified Telex channel when an application becomes inactive for a defined period.

## Features

- Monitors multiple Render-hosted applications.

- Sends notifications to Telex when an application is inactive.

- Configurable inactivity threshold and monitoring interval.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/codefromlani/Render-Monitoring-System

2. Navigate to the project directory:

    cd render-monitoring-system

3. Install Dependencies

    ```bash
    pip install -r requirements.txt


4. Run the Application

    ```bash
    uvicorn main:app --reload

5. Configure Webhook URL
- Update your settings with the appropriate information for Telex in your monitoring payload.

## Sreenshots Of My Integration

![Render Inactivity Alert](Telex%201.png)

## Testing

    ```bash
    curl -X 'POST' \
    'http://localhost:8000/tick' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "channel_id": "YOUR_CHANNEL_ID",
    "return_url": "https://ping.telex.im/v1/webhooks/YOUR_CHANNEL_ID",
    "settings": [
      {
        "label": "app_url",
        "type": "text",
        "required": true,
        "default": "https://your-app-url.onrender.com/"
      },
      {
        "label": "interval",
        "type": "text",
        "required": true,
        "default": "* * * * *"
      }
    ]
    }'
