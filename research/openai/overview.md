# OpenAI API Documentation Overview

**URL:** https://platform.openai.com/docs/overview
**Scraped:** 2025-07-07

## Key Information

### Models Available
- **GPT-4.1**: Flagship GPT model for complex tasks
- **o4-mini**: Faster, more affordable reasoning model  
- **o3**: Most powerful reasoning model

### API Structure
```bash
curl https://api.openai.com/v1/responses \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4.1",
        "input": "Write a one-sentence bedtime story about a unicorn."
    }'
```

### Python Client
```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
```

### Key Capabilities
1. **Text and prompting**: Basic text generation
2. **Images and vision**: Image analysis and generation
3. **Audio and speech**: Transcription and TTS
4. **Structured Outputs**: JSON schema adherence
5. **Function calling**: Tool use
6. **Streaming**: Real-time responses
7. **Batch processing**: Bulk operations
8. **Reasoning**: Complex task execution
9. **Agents**: Agentic applications
10. **Realtime API**: Live conversations

### Agent-Specific Features
- **Building agents**: Core agent functionality
- **Voice agents**: Audio-enabled agents
- **Agents SDK Python**: Official Python SDK
- **Agents SDK TypeScript**: Official TypeScript SDK

### Tools Available
- **Remote MCP**: Model Context Protocol
- **Web search**: Internet search capability
- **File search**: Document search
- **Image generation**: DALL-E integration
- **Code interpreter**: Code execution
- **Computer use**: Screen interaction

### Authentication
- Uses `Authorization: Bearer $OPENAI_API_KEY` header
- API keys managed through platform dashboard

### Rate Limits & Usage
- Documented rate limits available
- Usage tracking and monitoring
- Prompt caching for efficiency

### Critical Models for PHP Framework
1. **GPT-4.1 Mini**: For vision and bulk tasks (as specified in initial.md)
2. **GPT-4.1**: For complex orchestration tasks if needed

### PHP Integration Considerations
- HTTP client needed for API calls
- JSON handling for requests/responses
- Error handling for rate limits and failures
- Authentication token management
- Async handling for better performance

### Key Endpoints Structure
- Base URL: `https://api.openai.com/v1/`
- Main endpoint: `/responses` (for new API)
- Legacy: `/chat/completions` (for older models)
- Authentication via Bearer token in headers

### Important for Our Framework
1. **Model naming**: Use exact model names like "gpt-4.1"
2. **Error handling**: Implement proper HTTP status code handling
3. **Rate limiting**: Respect API limits
4. **JSON structure**: Follow OpenAI's request/response format
5. **Streaming support**: Consider streaming for long responses