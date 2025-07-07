# Comprehensive Research Summary for PHP Agentic Framework

**Research Date:** 2025-07-07
**Total Pages Scraped:** 8 initial pages + deep documentation

## Key Findings

### 1. PydanticAI Framework Architecture
- **Agent-based system** with dependency injection
- **Tool registration** via decorators (@agent.tool, @agent.tool_plain)
- **System prompts** (static and dynamic)
- **Structured outputs** using Pydantic models
- **Multi-model support** (OpenAI, Anthropic, Gemini, etc.)
- **Async-first design** throughout

### 2. Model Requirements from INITIAL.md
- **Claude Sonnet 4** for orchestrator (exact name: `claude-sonnet-4-20250514`)
- **GPT 4.1 Mini** for vision and bulk tasks (exact name: `gpt-4.1`)
- **Multi-model provider support** required

### 3. Core Agent Patterns
```python
# Basic Agent Structure
agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDependencies,
    output_type=MyOutput,
    system_prompt="instructions"
)

# Tool Registration
@agent.tool
async def my_tool(ctx: RunContext[MyDeps], param: str) -> str:
    return await ctx.deps.service.call(param)
```

### 4. PHP Framework Requirements
Based on research, our PHP framework needs:

#### Core Components
1. **Agent Class** - Central orchestrator
2. **Tool System** - Function calling mechanism
3. **Dependency Injection** - Clean service provision
4. **Model Providers** - OpenAI, Anthropic support
5. **HTTP Client** - For API calls
6. **JSON Handling** - Request/response serialization
7. **CRON Integration** - For scheduling

#### Agent Types Needed (from INITIAL.md)
1. **Orchestrator Agent** (Claude Sonnet 4)
2. **Product Optimizing Agent** (GPT 4.1 Mini)
3. **Product Tagging Agent** (GPT 4.1 Mini)
4. **Collection Agent** (GPT 4.1 Mini)
5. **Blog Agent** (Claude Sonnet 4)
6. **Link Building Agent** (Claude Sonnet 4 + GPT 4.1 Mini)
7. **Holiday Collection Agent** (Claude Sonnet 4)
8. **Life Event Collection Agent** (Claude Sonnet 4)

### 5. Shopify Integration Requirements
- **GraphQL Admin API** for products and collections
- **Authentication** via access tokens
- **Rate limiting** handling
- **Product object** manipulation
- **Collection object** creation and management

### 6. Jina Integration Requirements
- **Reader API** (r.jina.ai) for content extraction
- **Search API** (s.jina.ai) for SERP analysis
- **Authentication** via Bearer token
- **Rate limiting** (20 RPM without key, 500 RPM with key)

### 7. Key Technical Decisions

#### Model Provider Integration
- **OpenAI**: Use exact model name "gpt-4.1" for GPT 4.1 Mini
- **Anthropic**: Use exact model name "claude-sonnet-4-20250514" for Claude Sonnet 4
- **HTTP clients** needed for both providers
- **Error handling** for rate limits and failures

#### Tool System Design
- **Function-based tools** like PydanticAI
- **Context injection** for dependencies
- **Async support** for I/O operations
- **Tool registration** system

#### Architecture Patterns
- **Dependency injection** for services (Shopify, Jina, etc.)
- **Event-driven** orchestration
- **CRON-based** scheduling
- **Database persistence** for state
- **Secure access control** system

### 8. Frontend/Dashboard Requirements
- **Real-time updates** for agent activities
- **Notification system** for user feedback
- **Agent control** (on/off toggles)
- **Data visualization** for results
- **Responsive design** (mobile-friendly)

### 9. Security Considerations
- **SQL injection protection**
- **Access code system** with admin generation
- **API key management** (never in code)
- **Rate limiting** respect
- **Error handling** without data leaks

### 10. Integration APIs Confirmed
- **Shopify GraphQL Admin API**: Products, Collections, Store data
- **OpenAI API**: GPT models with function calling
- **Anthropic API**: Claude models with tool use
- **Jina Reader/Search**: Content extraction and SERP analysis
- **Google Search Console**: Performance monitoring
- **Ahrefs API**: SEO metrics (via RapidAPI)

## Critical Implementation Notes

### Model Names (Sacred Truth)
- **NEVER** change model names from INITIAL.md specifications
- **GPT 4.1 Mini** is specifically required for vision/bulk tasks
- **Claude Sonnet 4** is specifically required for orchestration

### Agent Intelligence Requirements
- **Decision making** capabilities
- **Detailed research** using Jina
- **Competitor analysis** before content creation
- **Relevancy checking** for store context
- **Content generation** that's genuinely useful

### Stickiness Strategy
- **Long-running processes** to keep users engaged
- **Comprehensive optimization** of entire catalogs
- **Progressive enhancement** over time
- **Year-long engagement** target

This research provides the foundation for creating both Phase 1 (skeleton) and Phase 2 (production-ready) implementations of the PHP agentic framework.