/**
 * Orchestration Types for Multi-LLM Coordination
 * ==============================================
 * 
 * TypeScript interfaces and types for the orchestration system.
 * Defines the communication protocol between MCP server, extension, and AI services.
 */

// =================================================================
// CORE ORCHESTRATION TYPES
// =================================================================

/**
 * Main orchestration command sent from Claude Desktop via MCP server
 */
export interface OrchestrationCommand {
    /** Unique command identifier */
    id: string;

    /** Type of orchestration command */
    type: OrchestrationCommandType;

    /** The prompt to send to AI services */
    prompt: string;

    /** List of target AI services */
    targets: AIServiceTarget[];

    /** Command timeout in seconds */
    timeout: number;

    /** Command priority level */
    priority?: OrchestrationPriority;

    /** Timestamp when command was created */
    timestamp: string;

    /** Source that initiated the command */
    source: string;

    /** Optional metadata */
    metadata?: OrchestrationMetadata;
}

/**
 * Response from orchestration system back to Claude Desktop
 */
export interface OrchestrationResponse {
    /** ID of the original command */
    commandId: string;

    /** Individual responses from each AI service */
    responses: AIServiceResponse[];

    /** Overall success status */
    success: boolean;

    /** Timestamp when response was completed */
    timestamp: string;

    /** Optional error message */
    error?: string;

    /** Processing duration in milliseconds */
    duration?: number;

    /** Response metadata */
    metadata?: ResponseMetadata;
}

// =================================================================
// AI SERVICE TYPES
// =================================================================

/**
 * Supported AI service targets
 */
export type AIServiceTarget =
    | 'chatgpt'
    | 'claude'
    | 'perplexity'
    | 'gemini'
    | 'copilot'
    | 'bard'
    | 'anthropic';

/**
 * Response from individual AI service
 */
export interface AIServiceResponse {
    /** Name of the AI service */
    service: AIServiceTarget;

    /** Response content from the AI */
    content: string;

    /** Success status for this service */
    success: boolean;

    /** Error message if failed */
    error?: string;

    /** Timestamp of response */
    timestamp: string;

    /** Processing time for this service */
    processingTime?: number;

    /** Service-specific metadata */
    serviceMetadata?: ServiceMetadata;
}

/**
 * AI service status information
 */
export interface AIServiceStatus {
    /** Service name */
    service: AIServiceTarget;

    /** Whether service is available */
    available: boolean;

    /** Current tab ID if open */
    tabId?: number;

    /** Last interaction timestamp */
    lastInteraction?: string;

    /** Service health status */
    health: 'healthy' | 'degraded' | 'unavailable';

    /** Response time in milliseconds */
    responseTime?: number;
}

// =================================================================
// COMMAND TYPES
// =================================================================

/**
 * Types of orchestration commands
 */
export type OrchestrationCommandType =
    | 'code_generation'     // Generate code
    | 'code_review'         // Review existing code
    | 'analysis'            // Analyze data/text
    | 'chat'               // General conversation
    | 'research'           // Research topic
    | 'debugging'          // Debug code/issues
    | 'documentation'      // Create documentation
    | 'translation'        // Translate content
    | 'summarization'      // Summarize content
    | 'comparison';        // Compare responses

/**
 * Command priority levels
 */
export type OrchestrationPriority = 'low' | 'normal' | 'high' | 'urgent';

// =================================================================
// METADATA TYPES
// =================================================================

/**
 * Orchestration command metadata
 */
export interface OrchestrationMetadata {
    /** User context information */
    userContext?: string;

    /** Project context */
    projectContext?: string;

    /** Previous command ID if part of chain */
    previousCommandId?: string;

    /** Expected response format */
    expectedFormat?: 'text' | 'code' | 'json' | 'markdown';

    /** Additional parameters */
    parameters?: Record<string, any>;
}

/**
 * Response metadata
 */
export interface ResponseMetadata {
    /** Total tokens used across all services */
    totalTokens?: number;

    /** Cost estimation */
    estimatedCost?: number;

    /** Quality scores */
    qualityScores?: QualityScore[];

    /** Response similarity analysis */
    similarity?: SimilarityAnalysis;
}

/**
 * Service-specific metadata
 */
export interface ServiceMetadata {
    /** Model used by the service */
    model?: string;

    /** Tokens used */
    tokensUsed?: number;

    /** Service version */
    version?: string;

    /** Rate limit information */
    rateLimit?: RateLimitInfo;
}

/**
 * Quality scoring for responses
 */
export interface QualityScore {
    /** Metric name */
    metric: string;

    /** Score value (0-1) */
    score: number;

    /** Score explanation */
    explanation?: string;
}

/**
 * Response similarity analysis
 */
export interface SimilarityAnalysis {
    /** Overall similarity score */
    overallSimilarity: number;

    /** Pairwise similarity matrix */
    pairwiseScores: PairwiseScore[];

    /** Consensus areas */
    consensus?: string[];

    /** Divergent areas */
    divergences?: string[];
}

/**
 * Pairwise similarity score
 */
export interface PairwiseScore {
    /** First service */
    service1: AIServiceTarget;

    /** Second service */
    service2: AIServiceTarget;

    /** Similarity score (0-1) */
    similarity: number;
}

/**
 * Rate limit information
 */
export interface RateLimitInfo {
    /** Requests remaining */
    remaining: number;

    /** Reset time */
    resetTime: string;

    /** Request limit */
    limit: number;
}

// =================================================================
// EVENT TYPES
// =================================================================

/**
 * Events emitted during orchestration
 */
export type OrchestrationEvent =
    | 'command_received'
    | 'command_started'
    | 'service_connected'
    | 'service_response_received'
    | 'command_completed'
    | 'command_failed'
    | 'service_error';

/**
 * Event data structure
 */
export interface OrchestrationEventData {
    /** Event type */
    event: OrchestrationEvent;

    /** Command ID */
    commandId: string;

    /** Service involved (if applicable) */
    service?: AIServiceTarget;

    /** Event timestamp */
    timestamp: string;

    /** Event details */
    details?: Record<string, any>;
}

// =================================================================
// CONFIGURATION TYPES
// =================================================================

/**
 * Orchestration system configuration
 */
export interface OrchestrationConfig {
    /** Default timeout for commands */
    defaultTimeout: number;

    /** Maximum concurrent commands */
    maxConcurrentCommands: number;

    /** Retry configuration */
    retryConfig: RetryConfig;

    /** Service-specific configurations */
    serviceConfigs: Record<AIServiceTarget, ServiceConfig>;

    /** Quality thresholds */
    qualityThresholds: QualityThresholds;
}

/**
 * Retry configuration
 */
export interface RetryConfig {
    /** Maximum retry attempts */
    maxRetries: number;

    /** Retry delay in milliseconds */
    retryDelay: number;

    /** Exponential backoff multiplier */
    backoffMultiplier: number;
}

/**
 * Service-specific configuration
 */
export interface ServiceConfig {
    /** Whether service is enabled */
    enabled: boolean;

    /** Service timeout override */
    timeout?: number;

    /** Service weight for consensus */
    weight: number;

    /** Service-specific parameters */
    parameters?: Record<string, any>;
}

/**
 * Quality thresholds
 */
export interface QualityThresholds {
    /** Minimum similarity for consensus */
    minSimilarity: number;

    /** Minimum response length */
    minResponseLength: number;

    /** Maximum response time */
    maxResponseTime: number;
}

// =================================================================
// UTILITY TYPES
// =================================================================

/**
 * Result wrapper type
 */
export type OrchestrationResult<T> = {
    success: true;
    data: T;
} | {
    success: false;
    error: string;
    code?: string;
};

/**
 * Progress callback type
 */
export type ProgressCallback = (progress: {
    commandId: string;
    completedServices: number;
    totalServices: number;
    currentService?: AIServiceTarget;
}) => void;

/**
 * Service availability map
 */
export type ServiceAvailabilityMap = Record<AIServiceTarget, boolean>; 