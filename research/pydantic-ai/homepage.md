# PydanticAI Documentation Homepage

**URL:** https://ai.pydantic.dev/
**Scraped:** 2025-07-07

## Key Information

### What is PydanticAI?
- Agent Framework designed to make it less painful to build production-grade applications with Generative AI
- Built by the Pydantic team (validation layer of OpenAI SDK, Anthropic SDK, LangChain, LlamaIndex, etc.)
- Brings "FastAPI feeling to GenAI app development"

### Core Features
- **Model-agnostic**: Supports OpenAI, Anthropic, Gemini, Deepseek, Ollama, Groq, Cohere, and Mistral
- **Type-safe**: Designed for powerful type checking
- **Python-centric Design**: Leverages Python's familiar control flow and agent composition
- **Structured Responses**: Uses Pydantic to validate and structure model outputs
- **Dependency Injection System**: Optional DI system for data and services
- **Streamed Responses**: Provides real-time streaming with immediate validation
- **Graph Support**: Pydantic Graph for complex applications

### Key Models Mentioned
- `google-gla:gemini-1.5-flash` (in hello world example)
- `openai:gpt-4o` (in bank support example)

### Important Code Patterns

#### Basic Agent Creation
```python
from pydantic_ai import Agent

agent = Agent(  
    'google-gla:gemini-1.5-flash',
    system_prompt='Be concise, reply with one sentence.',  
)

result = agent.run_sync('Where does "hello world" come from?')  
```

#### Advanced Agent with Dependencies
```python
from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

@dataclass
class SupportDependencies:  
    customer_id: int
    db: DatabaseConn  

class SupportOutput(BaseModel):  
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description="Whether to block the customer's card")
    risk: int = Field(description='Risk level of query', ge=0, le=10)

support_agent = Agent(  
    'openai:gpt-4o',  
    deps_type=SupportDependencies,
    output_type=SupportOutput,  
    system_prompt=(  
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query.'
    ),
)

@support_agent.system_prompt  
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"The customer's name is {customer_name!r}"

@support_agent.tool  
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> float:
    """Returns the customer's current account balance."""  
    return await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )
```

### Integration with Pydantic Logfire
```python
import logfire

logfire.configure()  
logfire.instrument_asyncpg()  

support_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    system_prompt=(...),
    instrument=True,  # Enable logfire integration
)
```

### Available Documentation Formats
- **llms.txt**: Brief description with links to sections
- **llms-full.txt**: Complete documentation content (may be too large for some LLMs)

### Next Steps for Research
- Read the [docs](https://ai.pydantic.dev/agents/) for building applications
- Check [API Reference](https://ai.pydantic.dev/api/agent/)
- Try [examples](https://ai.pydantic.dev/examples/)

### Critical Insights for PHP Framework
1. **Agent Pattern**: Core concept is Agent class with system prompts, tools, and dependencies
2. **Type Safety**: Heavy use of Pydantic models for validation
3. **Dependency Injection**: Clean pattern for providing data/services to agents
4. **Tool Registration**: @agent.tool decorator pattern for adding capabilities
5. **Multi-Model Support**: Framework supports multiple LLM providers
6. **Async First**: All examples use async/await patterns