# Phase 1: PHP Agentic Framework - Skeleton Implementation

## Project Overview

A full PHP agentic framework for SEO optimization using intelligent AI agents. This skeleton provides the foundation with detailed implementation comments for building a production-ready multi-agent system.

**Key Technologies:**
- PHP 8.2+ Backend
- MySQL 8.0+ Database  
- HTML/CSS/JS Frontend (SEO Grove inspired design)
- OpenAI API (gpt-4.1-mini with 1M context window)
- Anthropic API (Claude Sonnet 4 for orchestration)
- Jina Reader/Search API
- Shopify GraphQL Admin API
- Google Search Console API
- Ahrefs API via RapidAPI

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/CSS/JS)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ Admin Panel  │ │  Dashboard   │ │ Agent Views  │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PHP Backend                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ API Routes   │ │ Agent System │ │ CRON Jobs    │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                            │
│  ┌───────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │OpenAI │ │Anthropic│ │  Jina  │ │Shopify │ │ Google │       │
│  └───────┘ └────────┘ └────────┘ └────────┘ └────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
php-agentic-framework/
├── index.php                 # Entry point
├── composer.json            # PHP dependencies
├── .env.example            # Environment variables template
├── config/
│   ├── app.php            # Application configuration
│   ├── database.php       # Database configuration
│   └── agents.php         # Agent-specific configuration
├── database/
│   ├── migrations/        # Database migrations
│   └── schema.sql        # Initial schema
├── src/
│   ├── Core/
│   │   ├── Agent.php              # Base agent class
│   │   ├── AgentManager.php       # Agent lifecycle management
│   │   ├── DecisionEngine.php     # JSON-based decision making
│   │   └── ModelProvider.php      # AI model abstraction
│   ├── Agents/
│   │   ├── OrchestratorAgent.php  # Claude Sonnet 4 orchestrator
│   │   ├── ProductOptimizer.php   # Product optimization agent
│   │   ├── ProductTagger.php      # Product tagging agent
│   │   ├── CollectionAgent.php    # Collection management
│   │   ├── BlogAgent.php          # Blog content generation
│   │   ├── LinkBuilder.php        # Link building agent
│   │   ├── HolidayAgent.php       # Holiday collection agent
│   │   └── LifeEventAgent.php     # Life event collection agent
│   ├── Services/
│   │   ├── JinaService.php        # Jina API integration
│   │   ├── ShopifyService.php     # Shopify GraphQL integration
│   │   ├── SearchConsole.php      # Google Search Console
│   │   └── AhrefsService.php      # Ahrefs API integration
│   ├── Models/
│   │   ├── User.php               # User model
│   │   ├── Store.php              # Store configuration
│   │   ├── Product.php            # Product data
│   │   ├── Collection.php         # Collection data
│   │   └── Task.php               # Agent task tracking
│   ├── Security/
│   │   ├── AccessCode.php         # Access code management
│   │   ├── SQLProtection.php      # SQL injection prevention
│   │   └── APIRateLimiter.php    # Rate limiting
│   └── Utils/
│       ├── Logger.php             # Logging utility
│       ├── JSONValidator.php      # JSON validation
│       └── ErrorHandler.php       # Error handling
├── api/
│   ├── routes.php                 # API route definitions
│   └── middleware.php             # API middleware
├── cron/
│   ├── orchestrator.php          # Main orchestrator CRON
│   └── agents/                   # Individual agent CRON jobs
├── frontend/
│   ├── index.html               # Main dashboard
│   ├── admin.html              # Admin panel
│   ├── css/
│   │   └── style.css          # SEO Grove inspired styles
│   └── js/
│       └── app.js             # Frontend JavaScript
└── logs/                      # Application logs
```

## Core Implementation

### 1. Base Agent Class (src/Core/Agent.php)

```php
<?php
namespace App\Core;

abstract class Agent {
    protected string $name;
    protected string $model;
    protected array $context = [];
    protected ModelProvider $modelProvider;
    protected array $tools = [];
    
    public function __construct(string $name, string $model) {
        $this->name = $name;
        $this->model = $model;
        
        // TODO: Initialize model provider based on model type
        // - If model contains 'claude', use AnthropicProvider
        // - If model contains 'gpt', use OpenAIProvider
        // - Set appropriate parameters (max_tokens, temperature, etc.)
    }
    
    /**
     * Main execution method for the agent
     * TODO: Implement the following flow:
     * 1. Gather context from current state
     * 2. Make decision using AI model
     * 3. Execute actions based on decision
     * 4. Update context with results
     * 5. Log all activities
     */
    abstract public function execute(array $input): array;
    
    /**
     * Decision making using JSON structure
     * TODO: Implement JSON-based decision making:
     * 1. Format context and input as structured prompt
     * 2. Request JSON response from AI model
     * 3. Validate JSON structure
     * 4. Extract decision and reasoning
     */
    protected function makeDecision(array $context): array {
        // Implementation placeholder
        return [];
    }
    
    /**
     * Execute tools based on decision
     * TODO: Implement tool execution:
     * 1. Parse tool calls from decision
     * 2. Execute each tool with parameters
     * 3. Collect results
     * 4. Handle errors gracefully
     */
    protected function executeTools(array $toolCalls): array {
        // Implementation placeholder
        return [];
    }
}
```

### 2. Orchestrator Agent (src/Agents/OrchestratorAgent.php)

```php
<?php
namespace App\Agents;

use App\Core\Agent;

class OrchestratorAgent extends Agent {
    private array $activeAgents = [];
    private array $dailyQuota = [];
    
    public function __construct() {
        parent::__construct('Orchestrator', 'claude-3-sonnet-20240229');
        
        // TODO: Initialize with Claude Sonnet 4 specific settings
        // - Set context window to handle multiple agent reports
        // - Configure for complex reasoning and planning
        // - Set up tools for agent management
    }
    
    public function execute(array $input): array {
        // TODO: Implement orchestration logic:
        // 1. Check time of day and determine active period
        // 2. Analyze store context:
        //    - New products to optimize
        //    - Collections needing updates
        //    - Content generation opportunities
        // 3. Calculate daily quota for stickiness:
        //    - Spread tasks throughout the day
        //    - Prioritize high-impact optimizations
        //    - Balance between different agent types
        // 4. Dispatch tasks to appropriate agents
        // 5. Monitor agent progress
        // 6. Prevent duplicate content creation
        
        return ['status' => 'orchestrating'];
    }
    
    /**
     * Analyze store state and determine needed actions
     * TODO: Implement comprehensive store analysis:
     * 1. Query database for current products/collections
     * 2. Check optimization history
     * 3. Identify gaps and opportunities
     * 4. Consider seasonal/holiday relevance
     */
    private function analyzeStoreContext(): array {
        // Implementation placeholder
        return [];
    }
    
    /**
     * Distribute tasks for maximum stickiness
     * TODO: Implement sticky task distribution:
     * 1. Calculate optimal task timing
     * 2. Ensure continuous activity
     * 3. Prioritize visible improvements
     * 4. Track user engagement patterns
     */
    private function distributeTasksForStickiness(array $tasks): array {
        // Implementation placeholder
        return [];
    }
}
```

### 3. Product Optimizing Agent (src/Agents/ProductOptimizer.php)

```php
<?php
namespace App\Agents;

use App\Core\Agent;
use App\Services\JinaService;
use App\Services\ShopifyService;

class ProductOptimizer extends Agent {
    private JinaService $jina;
    private ShopifyService $shopify;
    
    public function __construct() {
        parent::__construct('ProductOptimizer', 'gpt-4.1-mini');
        
        // TODO: Initialize with GPT-4.1-mini settings
        // - Set max_tokens to 10000+ for detailed analysis
        // - Configure for 1M context window
        // - Initialize Jina and Shopify services
    }
    
    public function execute(array $input): array {
        // TODO: Implement product optimization flow:
        // 1. Fetch product details from Shopify
        // 2. Analyze current SERP using Jina search:
        //    - Search for product keywords
        //    - Analyze competitor titles/descriptions
        //    - Extract optimization patterns
        // 3. Generate optimized content:
        //    - SEO-friendly title
        //    - Compelling description
        //    - Meta title and description
        // 4. Update product via Shopify GraphQL
        // 5. Log optimization details
        
        return ['status' => 'optimized'];
    }
    
    /**
     * Perform SERP analysis for product keywords
     * TODO: Implement comprehensive SERP analysis:
     * 1. Use Jina s.jina.ai for search results
     * 2. Scrape top competitors with r.jina.ai
     * 3. Extract SEO patterns and keywords
     * 4. Identify content gaps
     */
    private function analyzeSERP(array $product): array {
        // Implementation placeholder
        return [];
    }
    
    /**
     * Generate optimized product content
     * TODO: Implement AI-driven content generation:
     * 1. Create prompt with SERP insights
     * 2. Generate multiple variations
     * 3. Select best based on SEO criteria
     * 4. Ensure brand voice consistency
     */
    private function generateOptimizedContent(array $product, array $serpData): array {
        // Implementation placeholder
        return [];
    }
}
```

### 4. Jina Service Integration (src/Services/JinaService.php)

```php
<?php
namespace App\Services;

class JinaService {
    private string $apiKey;
    private string $searchEndpoint = 'https://s.jina.ai/';
    private string $readerEndpoint = 'https://r.jina.ai/';
    
    public function __construct(string $apiKey) {
        $this->apiKey = $apiKey;
    }
    
    /**
     * Search using Jina search API
     * TODO: Implement search functionality:
     * 1. Build search query with operators
     * 2. Add language and country parameters
     * 3. Execute HTTP request with auth header
     * 4. Parse and return results
     */
    public function search(string $query, array $options = []): array {
        // Implementation placeholder
        // Use search operators like "write for us" + niche keywords
        // Set language and country based on store configuration
        return [];
    }
    
    /**
     * Convert webpage to LLM-readable markdown
     * TODO: Implement reader functionality:
     * 1. Validate URL
     * 2. Add auth header with Bearer token
     * 3. Execute request
     * 4. Return markdown content
     */
    public function readPage(string $url): string {
        // Implementation placeholder
        return '';
    }
}
```

### 5. Database Schema (database/schema.sql)

```sql
-- Users and access control
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    access_code VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- TODO: Add fields for:
    -- - last_login
    -- - subscription_status
    -- - usage_limits
);

-- Store configuration
CREATE TABLE stores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    shopify_domain VARCHAR(255) NOT NULL,
    shopify_access_token TEXT NOT NULL,
    live_url VARCHAR(255),
    country_focus VARCHAR(50),
    base_language VARCHAR(10) DEFAULT 'en',
    active_languages JSON,
    -- TODO: Add fields for:
    -- - business_description
    -- - target_keywords
    -- - competitor_urls
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Products tracking
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id INT NOT NULL,
    shopify_product_id VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    optimization_status ENUM('pending', 'optimized', 'failed') DEFAULT 'pending',
    last_optimized TIMESTAMP NULL,
    optimization_data JSON,
    -- TODO: Add fields for:
    -- - original_title
    -- - serp_analysis_data
    -- - performance_metrics
    FOREIGN KEY (store_id) REFERENCES stores(id)
);

-- Collections management
CREATE TABLE collections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id INT NOT NULL,
    shopify_collection_id VARCHAR(100),
    title VARCHAR(500),
    type ENUM('manual', 'smart', 'holiday', 'life_event') DEFAULT 'manual',
    optimization_status ENUM('pending', 'optimized', 'failed') DEFAULT 'pending',
    -- TODO: Add fields for:
    -- - relevance_score
    -- - product_count
    -- - generation_prompt
    FOREIGN KEY (store_id) REFERENCES stores(id)
);

-- Agent task tracking
CREATE TABLE agent_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_name VARCHAR(100) NOT NULL,
    store_id INT NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    priority INT DEFAULT 5,
    scheduled_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    result_data JSON,
    -- TODO: Add fields for:
    -- - retry_count
    -- - error_message
    -- - execution_time
    FOREIGN KEY (store_id) REFERENCES stores(id)
);

-- Agent activity logs
CREATE TABLE agent_activities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_name VARCHAR(100) NOT NULL,
    store_id INT NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- TODO: Add fields for:
    -- - tokens_used
    -- - api_costs
    -- - performance_impact
    FOREIGN KEY (store_id) REFERENCES stores(id)
);

-- Create indexes for performance
CREATE INDEX idx_products_store_status ON products(store_id, optimization_status);
CREATE INDEX idx_collections_store_type ON collections(store_id, type);
CREATE INDEX idx_tasks_status_scheduled ON agent_tasks(status, scheduled_at);
CREATE INDEX idx_activities_agent_time ON agent_activities(agent_name, created_at);
```

### 6. Environment Configuration (.env.example)

```bash
# Application Settings
APP_NAME="PHP Agentic Framework"
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:8080

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=agentic_framework
DB_USERNAME=root
DB_PASSWORD=

# AI Model API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model Configuration
# IMPORTANT: Use gpt-4.1-mini with 1M context window
OPENAI_MODEL=gpt-4.1-mini
OPENAI_MAX_TOKENS=10000
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Jina API Configuration
JINA_API_KEY=jina_...

# Shopify Configuration (Set per store in database)
# SHOPIFY_API_VERSION=2024-01

# Google Search Console
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Ahrefs via RapidAPI
RAPIDAPI_KEY=
AHREFS_API_HOST=ahrefs-dr-rank-checker.p.rapidapi.com

# Security Settings
ACCESS_CODE_LENGTH=16
SESSION_LIFETIME=7200
RATE_LIMIT_PER_MINUTE=60

# CRON Settings
ORCHESTRATOR_SCHEDULE="*/5 * * * *"  # Every 5 minutes
AGENT_BATCH_SIZE=10
MAX_CONCURRENT_AGENTS=5

# Logging
LOG_CHANNEL=daily
LOG_LEVEL=debug
```

### 7. Frontend Structure (frontend/index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Agent Dashboard</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <header class="dashboard-header">
            <div class="container">
                <h1 class="heading-1">SEO Agent Dashboard</h1>
                <nav class="dashboard-nav">
                    <!-- TODO: Add navigation items -->
                    <!-- - Overview -->
                    <!-- - Agents -->
                    <!-- - Products -->
                    <!-- - Collections -->
                    <!-- - Analytics -->
                    <!-- - Settings -->
                </nav>
            </div>
        </header>

        <!-- Main Content -->
        <main class="dashboard-main">
            <div class="container">
                <!-- Agent Status Grid -->
                <section class="agent-grid">
                    <!-- TODO: Create agent status cards -->
                    <!-- Each card should show: -->
                    <!-- - Agent name and status -->
                    <!-- - Current task -->
                    <!-- - Tasks completed today -->
                    <!-- - Real-time activity feed -->
                </section>

                <!-- Activity Feed -->
                <section class="activity-feed">
                    <!-- TODO: Implement real-time activity updates -->
                    <!-- - Use WebSocket or polling -->
                    <!-- - Show agent decisions -->
                    <!-- - Display optimization results -->
                    <!-- - Include performance metrics -->
                </section>

                <!-- Quick Actions -->
                <section class="quick-actions">
                    <!-- TODO: Add action buttons -->
                    <!-- - Run all agents -->
                    <!-- - Stop all agents -->
                    <!-- - View reports -->
                    <!-- - Configure agents -->
                </section>
            </div>
        </main>
    </div>
    
    <script src="js/app.js"></script>
</body>
</html>
```

### 8. CSS Structure (frontend/css/style.css)

```css
/* SEO Grove Inspired Design System */
/* TODO: Implement complete design system from designsystem.md */

:root {
    /* Colors from SEO Grove */
    --grove-green: #22c55e;
    --grove-pink: #ef2b70;
    --grove-dark: #1e293b;
    --grove-secondary: #64748b;
    
    /* Spacing */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    
    /* Typography */
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --text-base: 0.875rem;
    --text-lg: 1rem;
    --text-xl: 1.125rem;
    --text-2xl: 1.25rem;
    --text-3xl: 1.5rem;
}

/* TODO: Implement responsive grid system */
/* TODO: Create component classes for cards, buttons, forms */
/* TODO: Add animation classes for loading states */
/* TODO: Implement dark mode support */
```

### 9. CRON Orchestrator (cron/orchestrator.php)

```php
<?php
require_once __DIR__ . '/../vendor/autoload.php';

use App\Agents\OrchestratorAgent;
use App\Core\AgentManager;

/**
 * Main orchestrator CRON job
 * Runs every 5 minutes to coordinate all agents
 */

try {
    // TODO: Implement orchestrator CRON logic:
    // 1. Initialize orchestrator agent
    // 2. Get all active stores
    // 3. For each store:
    //    a. Check current time vs store timezone
    //    b. Determine if within active hours
    //    c. Calculate remaining daily quota
    //    d. Dispatch appropriate tasks
    // 4. Monitor running agents
    // 5. Handle failed tasks
    // 6. Update metrics
    
    $orchestrator = new OrchestratorAgent();
    $agentManager = new AgentManager();
    
    // Get stores requiring attention
    $stores = []; // TODO: Fetch from database
    
    foreach ($stores as $store) {
        // Check if we should process this store
        if (!shouldProcessStore($store)) {
            continue;
        }
        
        // Execute orchestration
        $result = $orchestrator->execute([
            'store_id' => $store['id'],
            'context' => getStoreContext($store)
        ]);
        
        // Log results
        logOrchestrationResult($result);
    }
    
} catch (Exception $e) {
    // TODO: Implement error handling
    // - Log error
    // - Send alert if critical
    // - Attempt recovery
    error_log("Orchestrator CRON error: " . $e->getMessage());
}

/**
 * Helper functions
 * TODO: Implement these helper functions
 */
function shouldProcessStore(array $store): bool {
    // Check store active status, subscription, etc.
    return true;
}

function getStoreContext(array $store): array {
    // Gather comprehensive store context
    return [];
}

function logOrchestrationResult(array $result): void {
    // Log orchestration outcomes
}
```

### 10. API Routes (api/routes.php)

```php
<?php
use Slim\App;
use Slim\Routing\RouteCollectorProxy;

return function (App $app) {
    // TODO: Implement comprehensive API routes
    
    // Authentication routes
    $app->group('/api/auth', function (RouteCollectorProxy $group) {
        $group->post('/login', 'AuthController:login');
        $group->post('/validate-code', 'AuthController:validateAccessCode');
        $group->post('/logout', 'AuthController:logout');
    });
    
    // Admin routes
    $app->group('/api/admin', function (RouteCollectorProxy $group) {
        $group->post('/generate-code', 'AdminController:generateAccessCode');
        $group->get('/users', 'AdminController:listUsers');
        $group->get('/system-status', 'AdminController:systemStatus');
    })->add('AdminMiddleware');
    
    // Agent management routes
    $app->group('/api/agents', function (RouteCollectorProxy $group) {
        $group->get('/', 'AgentController:list');
        $group->post('/{agent}/start', 'AgentController:start');
        $group->post('/{agent}/stop', 'AgentController:stop');
        $group->get('/{agent}/status', 'AgentController:status');
        $group->get('/{agent}/logs', 'AgentController:logs');
    })->add('AuthMiddleware');
    
    // Store configuration routes
    $app->group('/api/store', function (RouteCollectorProxy $group) {
        $group->post('/setup', 'StoreController:setup');
        $group->get('/config', 'StoreController:getConfig');
        $group->put('/config', 'StoreController:updateConfig');
        $group->post('/verify-shopify', 'StoreController:verifyShopify');
    })->add('AuthMiddleware');
    
    // Dashboard data routes
    $app->group('/api/dashboard', function (RouteCollectorProxy $group) {
        $group->get('/stats', 'DashboardController:stats');
        $group->get('/activity', 'DashboardController:recentActivity');
        $group->get('/metrics', 'DashboardController:performanceMetrics');
    })->add('AuthMiddleware');
};
```

## Implementation Tasks

### Phase 1 Checklist

1. **Core Infrastructure**
   - [ ] Set up PHP project with Composer
   - [ ] Configure database connections
   - [ ] Implement base Agent class
   - [ ] Create model provider abstraction
   - [ ] Set up logging system

2. **Security Framework**
   - [ ] Implement access code generation
   - [ ] Create SQL injection protection
   - [ ] Set up API rate limiting
   - [ ] Configure CORS and CSRF protection

3. **Agent System**
   - [ ] Create orchestrator agent skeleton
   - [ ] Implement agent state management
   - [ ] Set up CRON job structure
   - [ ] Create agent communication system

4. **External Services**
   - [ ] Jina API client skeleton
   - [ ] Shopify GraphQL client skeleton
   - [ ] OpenAI/Anthropic client skeleton
   - [ ] Google Search Console skeleton

5. **Frontend Structure**
   - [ ] Create dashboard HTML structure
   - [ ] Implement SEO Grove design system
   - [ ] Set up real-time update mechanism
   - [ ] Create responsive layouts

6. **Database Schema**
   - [ ] Create migration system
   - [ ] Implement initial schema
   - [ ] Set up indexes
   - [ ] Create seed data

## Next Steps for Phase 2

Phase 2 will implement:
- Complete agent intelligence with decision-making
- Full Jina integration for SERP analysis
- Production-ready API endpoints
- Real-time dashboard updates
- Comprehensive error handling
- Performance optimizations
- Monitoring and analytics
- Complete security implementation

## Quality Score

**Confidence Level: 9/10**

This skeleton provides:
- Clear architecture and structure
- Detailed implementation comments
- Comprehensive TODO items
- Integration points for all services
- Security considerations
- Scalability planning

The AI implementing Phase 2 will have all necessary context to create a production-ready system.