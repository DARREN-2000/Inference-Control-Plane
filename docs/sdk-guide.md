# SDK Guide

Because Laminar is fully API-compatible with standard OpenAI specifications, you do not need a proprietary SDK to use it. You can simply use the official OpenAI SDKs for Python, Node.js, and other languages, and configure them to point to your Laminar instance.

This guide demonstrates how to configure the most popular SDKs.

## Python (OpenAI SDK)

Install the OpenAI Python SDK:
```bash
pip install openai
```

### Basic Initialization
Override the `base_url` to point to your Laminar instance, and use your Laminar API key.

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1", # Your Laminar URL
    api_key=os.environ.get("LAMINAR_API_KEY")
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about proxies."}
    ]
)

print(response.choices[0].message.content)
```

### Passing User IDs for Tracking
To track usage on a per-user basis in Laminar, pass the `user` parameter.

```python
response = client.chat.completions.create(
    model="claude-3-5-sonnet", # Laminar will route this to Anthropic
    messages=[{"role": "user", "content": "Hello!"}],
    user="customer_internal_id_123"
)
```

### Laminar-Specific Parameters
If you need to pass Laminar-specific arguments (like dynamic fallbacks or cache bypass) that are not natively supported by the standard SDK types, you can pass them as `extra_body`.

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_body={
        "laminar_fallback_models": ["gpt-3.5-turbo"],
        "laminar_cache_bypass": True
    }
)
```

---

## Node.js / TypeScript (OpenAI SDK)

Install the SDK:
```bash
npm install openai
```

### Basic Initialization

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1', // Your Laminar URL
  apiKey: process.env.LAMINAR_API_KEY,
});

async function main() {
  const completion = await client.chat.completions.create({
    messages: [{ role: 'system', content: 'You are a helpful assistant.' }],
    model: 'gpt-4o',
    user: 'tenant_user_456'
  });

  console.log(completion.choices[0].message.content);
}

main();
```

### Streaming Responses

Laminar fully supports SSE streaming.

```typescript
async function streamResponse() {
  const stream = await client.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Tell me a story.' }],
    stream: true,
  });

  for await (const chunk of stream) {
    process.stdout.write(chunk.choices[0]?.delta?.content || '');
  }
}
```

---

## LangChain Integration

If you use LangChain, you can easily point it to Laminar by using the `ChatOpenAI` class and modifying the `openai_api_base`.

### Python LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_base="http://localhost:8000/v1",
    openai_api_key="sk-laminar-your-key",
    model_name="claude-3-5-sonnet" # LangChain thinks it's OpenAI, Laminar routes it.
)

response = llm.invoke("What is the capital of Spain?")
print(response.content)
```

## Migration Checklist

When migrating an existing application to Laminar:
1. Update `base_url` (or `openai_api_base`) in your SDK initialization.
2. Replace the `api_key` with your Laminar API key.
3. Ensure your Laminar server has the necessary provider API keys (OpenAI, Anthropic) configured in its environment.
4. *No changes to your prompt logic or response parsing are required!*
