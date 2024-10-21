# Chatbot API

A production-grade FastAPI API designed for building chatbots. This API provides a robust foundation for developing conversational interfaces, leveraging the speed and simplicity of FastAPI.

## Features

- List available language models
- Retrieve details of specific models
- Generate chat completions (streaming and non-streaming)
- Structured logging
- Comprehensive test coverage
- Docker support for easy deployment

## Development Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/api.git
   cd api
   ```

2. Install dependencies:

   ```
   poetry install
   ```

3. Generate requirements.txt file:

   ```
   poetry export -f requirements.txt --output requirements.txt --without-hashes
   ```

4. Set up environment variables:

   ```
   cp .env.example .env
   ```

   Edit the `.env` file with your specific configurations.

5. Set up pre-commit hooks:
   ```
   poetry run pre-commit install
   ```

## Running the Project

To run the project locally:

```
poetry run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Testing

To run tests:

```
poetry run pytest
```

## Deployment

(Add deployment instructions specific to your chosen hosting platform)

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

For detailed API usage, including streaming examples, see the [API Documentation](docs/api.md).

## Development

This project uses pre-commit hooks to ensure code quality. After installing the project dependencies, set up the pre-commit hooks:

```
poetry run pre-commit install
```

Now, the hooks will run automatically on every commit.

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. The workflow is defined in `.github/workflows/ci-cd.yml`. It runs tests, linting, and type checking on every push and pull request. When changes are pushed to the main branch, it also builds and pushes a Docker image.

## Docker

To run the project using Docker:

1. Build the Docker image:

   ```
   docker build -t api .
   ```

2. Run the Docker container:
   ```
   docker run -p 8080:8080 -e API_KEY=your_api_key api
   ```

For local development with hot-reloading:

1. Start the services using docker-compose:

   ```
   docker-compose up --build
   ```

2. To stop the services:
   ```
   docker-compose down
   ```

The API will be available at `http://localhost:8080`.

## Deployment

Ensure you have the latest requirements.txt build form the poetry via:

```
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

To deploy the API to a Linux server:

1. Ensure Docker is installed on your server.
2. Copy the `deploy.sh` script to your server.
3. Set the necessary environment variables on your server:
   ```
   export API_KEY=your_api_key
   export ALLOWED_ORIGINS=your_allowed_origins
   export ALLOWED_HOSTS=your_allowed_hosts
   ```
4. Run the deployment script:
   ```
   ./deploy.sh
   ```

This will pull the latest changes, build a new Docker image, stop the existing container (if any), and start a new container with the updated code.

## Streaming Chat Completions

This API supports streaming chat completions. To use streaming:

1. Set the `stream` parameter to `true` in your request.
2. Handle the server-sent events (SSE) in your client.

Example Python client code for streaming:

```python
import requests

def stream_chat_completion(model, messages):
    url = "http://localhost:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "bearer your_api_key_here"
    }
    data = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    with requests.post(url, json=data, headers=headers, stream=True) as response:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    chunk = json.loads(decoded_line[6:])
                    yield chunk
                elif decoded_line == "data: [DONE]":
                    break

# Usage
messages = [{"role": "user", "content": "Tell me a joke"}]
for chunk in stream_chat_completion("default", messages):
    print(chunk['choices'][0]['delta']['content'], end='', flush=True)
```

For more detailed examples and usage instructions, refer to the [API Documentation](docs/api.md).

## Deployment to Fly.io

To deploy this FastAPI application to Fly.io, follow these steps:

1. Install the Fly CLI:

   ```
   curl -L https://fly.io/install.sh | sh
   ```

2. Log in to your Fly account:

   ```
   fly auth login
   ```

3. Initialize your Fly app (if not already done):

   ```
   fly launch
   ```

   This will create a `fly.toml` file if it doesn't exist.

4. Deploy your application:

   ```
   fly deploy
   ```

5. Open your deployed application:
   ```
   fly open
   ```

For more detailed information, refer to the [Fly.io FastAPI documentation](https://fly.io/docs/python/frameworks/fastapi/).

## OpenWebUI Settings

### local

- http://host.docker.internal:8000/v1
- your-secret-api-\*\*\*

## Livekit playground

- https://agents-playground.livekit.io/
- currently using test cloud env

## OpenAPI (Swagger) Docs

https://capital-region-urology.fly.dev/docs#/
https://capital-region-urology.fly.dev/redoc

https://capital-region-urology.fly.dev/v1

## Fly.io

https://fly.io/apps/capital-region-urology

## Gotchas

- Ensure your ALLOWED_HOSTS and ALLOWED_ORIGINS in .env includes the domain or host a request is coming from.

## testing connections

testing that models load

```
curl -X GET "http://localhost:8000/v1/models" \
     -H "Authorization: Bearer your-secret-api-key"
```

testing chat completions w/o streaming

```
 curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -H "Authorization: bearer your-secret-api-key" \
     -d '{
       "model": "default",
       "messages": [{"role": "user", "content": "Say this is a test!"}],
       "stream": false
     }'
```

## Qdrant prepping data on server

```
fly console

# adding curl
 apt-get update && apt-get install -y curl



 python src/prep_data.py generate
```
