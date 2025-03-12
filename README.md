# EnFund - Django Channels Chat Application

A real-time chat application built with Django Channels and WebSocket support.

## Deployed Application
- Production URL: https://enfund-production.up.railway.app

## Prerequisites
- Python 3.10 or higher
- Redis server
- Docker and Docker Compose (optional, for containerized setup)

## Local Setup (Without Docker)

1. Clone the repository
```bash
git clone <your-repository-url>
cd enfund
```

2. Create and activate virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
Create a `.env` file in the root directory with the following variables:
```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDIRECT_URI=your_redirect_uri
REDIS_URL=redis://localhost:6379
```

5. Run Redis Server
- Windows: Start Redis server from the installed location
- Linux/Mac: `redis-server`

6. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Run the development server
```bash
daphne -b 0.0.0.0 -p 8000 enfund.asgi:application
```

## Docker Setup

1. Build and run using Docker Compose
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

## WebSocket Connection

Connect to the WebSocket endpoint:
```
ws://localhost:8000/ws/chat/
```

## API Documentation

### Postman Documentation

[Postman Docs for REST](https://documenter.getpostman.com/view/32604647/2sAYk8ui8m)

Create a client and reciever windows with this address,
```
ws://localhost:8000/ws/chat/
```
Connect to the websockets, then send and receive messages




### WebSocket Message Format

Send message:
```json
{
    "message": "Your message here"
}
```

Receive message:
```json
{
    "message": "Received message"
}
```


## Tech Stack
- Django
- Django Channels
- Redis
- Docker
- WebSocket

