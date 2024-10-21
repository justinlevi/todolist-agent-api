# Chatbot API Documentation

## Overview

This document provides an overview of the Chatbot API endpoints, including how to use streaming chat completions.

## Swagger UI

FastAPI automatically generates interactive API documentation (Swagger UI) for our endpoints. You can access this documentation by navigating to the `/docs` endpoint of our API when it's running.

For example, if you're running the API locally on port 8000, you can access the Swagger UI at:

`http://localhost:8000/docs`

## Endpoints

### POST /v1/chat/completions

Generate a chat completion based on the provided messages and model.

#### Request Body

```json
{
  "model": "string",
  "messages": [
    {
      "role": "string",
      "content": "string"
    }
  ],
  "max_tokens": 0,
  "temperature": 0.7,
  "top_p": 1,
  "n": 1,
  "stream": false
}
```

- `stream`: Set to `true` to receive a streaming response.

#### Response

For non-streaming requests, the response will be a JSON object containing the generated completion.

For streaming requests, the response will be a series of server-sent events (SSE) containing chunks of the generated completion.

## Streaming Chat Completions

To use streaming chat completions:

1. Set the `stream` parameter to `true` in your request.
2. Send a POST request to `/v1/chat/completions`.
3. Handle the server-sent events (SSE) in your client.

### Example: Python Client for Streaming

```python
import requests
import json

def stream_chat_completion(model, messages):
    url = "http://localhost:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "beareryour_api_key_here"
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

### Example: JavaScript Client for Streaming

```javascript
async function streamChatCompletion(model, messages) {
  const response = await fetch("http://localhost:8000/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "beareryour_api_key_here",
    },
    body: JSON.stringify({
      model,
      messages,
      stream: true,
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        if (line.includes("[DONE]")) break;
        const data = JSON.parse(line.slice(6));
        console.log(data.choices[0].delta.content);
      }
    }
  }
}

// Usage
const messages = [{ role: "user", content: "Tell me a joke" }];
streamChatCompletion("default", messages);
```

These examples demonstrate how to consume the streaming API from both Python and JavaScript clients. Adjust the URL and API key as needed for your specific deployment.

## GraphQL

### Example Query

```graphql
query {
  todos {
    id
    title
    completed
    createdAt
  }
}
```

### Example Mutation

```graphql
mutation {
  createTodo(title: "Test Todo") {
    id
    title
    completed
    createdAt
  }
}
```

### updating database with prisma

```
pip install prisma
prisma generate
prisma migrate dev --name init
```
