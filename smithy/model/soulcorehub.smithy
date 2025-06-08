// SoulCoreHub API Model
namespace com.soulcorehub

use aws.protocols#restJson1
use aws.api#service
use aws.auth#sigv4
use smithy.framework#ValidationException

/// SoulCoreHub API - Core services for AI agents, content, and commerce
@service(sdkId: "SoulCoreHubApi")
@restJson1
@sigv4(name: "execute-api")
service SoulCoreHubApi {
    version: "2025-05-11",
    operations: [
        // Agent operations
        GetAgent,
        ListAgents,
        InvokeAgent,
        CreateAgent,
        UpdateAgent,
        DeleteAgent,
        
        // Content operations
        GetContent,
        ListContent,
        CreateContent,
        UpdateContent,
        DeleteContent,
        
        // Commerce operations
        GetProduct,
        ListProducts,
        CreateProduct,
        UpdateProduct,
        DeleteProduct,
        
        // Cultural operations
        GetWorld,
        ListWorlds,
        CreateWorld,
        UpdateWorld,
        DeleteWorld,
        
        // System operations
        GetSystemStatus,
        ExecuteCommand
    ],
    errors: [
        ValidationException,
        ResourceNotFoundException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

//=====================
// Agent Operations
//=====================

/// Get information about an agent
@http(method: "GET", uri: "/agents/{agentId}")
operation GetAgent {
    input: GetAgentInput,
    output: GetAgentOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure GetAgentInput {
    /// ID of the agent to retrieve
    @required
    @httpLabel
    agentId: String
}

structure GetAgentOutput {
    /// The agent information
    @required
    agent: Agent
}

/// List all available agents
@http(method: "GET", uri: "/agents")
@paginated(inputToken: "nextToken", outputToken: "nextToken", pageSize: "limit")
operation ListAgents {
    input: ListAgentsInput,
    output: ListAgentsOutput,
    errors: [
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure ListAgentsInput {
    /// Maximum number of agents to return
    @httpQuery("limit")
    limit: Integer,
    
    /// Token for pagination
    @httpQuery("nextToken")
    nextToken: String,
    
    /// Filter by agent type
    @httpQuery("type")
    type: String,
    
    /// Filter by agent status
    @httpQuery("status")
    status: AgentStatus
}

structure ListAgentsOutput {
    /// List of agents
    @required
    agents: AgentList,
    
    /// Token for pagination
    nextToken: String
}

/// Invoke an agent with a prompt
@http(method: "POST", uri: "/agents/{agentId}/invoke")
operation InvokeAgent {
    input: InvokeAgentInput,
    output: InvokeAgentOutput,
    errors: [
        ResourceNotFoundException,
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure InvokeAgentInput {
    /// ID of the agent to invoke
    @required
    @httpLabel
    agentId: String,
    
    /// Prompt for the agent
    @required
    prompt: String,
    
    /// Additional parameters
    parameters: Parameters,
    
    /// Context for the agent
    context: Context,
    
    /// Maximum tokens to generate
    maxTokens: Integer,
    
    /// Temperature for generation
    temperature: Float,
    
    /// Stream the response
    stream: Boolean
}

structure InvokeAgentOutput {
    /// Response from the agent
    @required
    response: String,
    
    /// Metadata about the response
    metadata: Metadata,
    
    /// Usage information
    usage: UsageInfo
}

/// Create a new agent
@http(method: "POST", uri: "/agents")
operation CreateAgent {
    input: CreateAgentInput,
    output: CreateAgentOutput,
    errors: [
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure CreateAgentInput {
    /// Name of the agent
    @required
    name: String,
    
    /// Description of the agent
    description: String,
    
    /// Type of the agent
    @required
    type: String,
    
    /// Configuration for the agent
    @required
    configuration: AgentConfiguration,
    
    /// Tags for the agent
    tags: Tags
}

structure CreateAgentOutput {
    /// The created agent
    @required
    agent: Agent
}

/// Update an existing agent
@http(method: "PUT", uri: "/agents/{agentId}")
operation UpdateAgent {
    input: UpdateAgentInput,
    output: UpdateAgentOutput,
    errors: [
        ResourceNotFoundException,
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure UpdateAgentInput {
    /// ID of the agent to update
    @required
    @httpLabel
    agentId: String,
    
    /// Name of the agent
    name: String,
    
    /// Description of the agent
    description: String,
    
    /// Configuration for the agent
    configuration: AgentConfiguration,
    
    /// Status of the agent
    status: AgentStatus,
    
    /// Tags for the agent
    tags: Tags
}

structure UpdateAgentOutput {
    /// The updated agent
    @required
    agent: Agent
}

/// Delete an agent
@http(method: "DELETE", uri: "/agents/{agentId}")
operation DeleteAgent {
    input: DeleteAgentInput,
    output: DeleteAgentOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure DeleteAgentInput {
    /// ID of the agent to delete
    @required
    @httpLabel
    agentId: String
}

structure DeleteAgentOutput {
    /// ID of the deleted agent
    @required
    agentId: String
}

//=====================
// Content Operations
//=====================

/// Get content by ID
@http(method: "GET", uri: "/content/{contentId}")
operation GetContent {
    input: GetContentInput,
    output: GetContentOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure GetContentInput {
    /// ID of the content to retrieve
    @required
    @httpLabel
    contentId: String
}

structure GetContentOutput {
    /// The content information
    @required
    content: Content
}

/// List all content
@http(method: "GET", uri: "/content")
@paginated(inputToken: "nextToken", outputToken: "nextToken", pageSize: "limit")
operation ListContent {
    input: ListContentInput,
    output: ListContentOutput,
    errors: [
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure ListContentInput {
    /// Maximum number of content items to return
    @httpQuery("limit")
    limit: Integer,
    
    /// Token for pagination
    @httpQuery("nextToken")
    nextToken: String,
    
    /// Filter by content type
    @httpQuery("type")
    contentType: ContentType,
    
    /// Filter by creator
    @httpQuery("creator")
    creator: String
}

structure ListContentOutput {
    /// List of content items
    @required
    contentItems: ContentList,
    
    /// Token for pagination
    nextToken: String
}

/// Create new content
@http(method: "POST", uri: "/content")
operation CreateContent {
    input: CreateContentInput,
    output: CreateContentOutput,
    errors: [
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure CreateContentInput {
    /// Title of the content
    @required
    title: String,
    
    /// Content body
    @required
    body: String,
    
    /// Content type
    @required
    contentType: ContentType,
    
    /// Creator of the content
    creator: String,
    
    /// Tags for the content
    tags: Tags
}

structure CreateContentOutput {
    /// The created content
    @required
    content: Content
}

/// Update existing content
@http(method: "PUT", uri: "/content/{contentId}")
operation UpdateContent {
    input: UpdateContentInput,
    output: UpdateContentOutput,
    errors: [
        ResourceNotFoundException,
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure UpdateContentInput {
    /// ID of the content to update
    @required
    @httpLabel
    contentId: String,
    
    /// Title of the content
    title: String,
    
    /// Content body
    body: String,
    
    /// Tags for the content
    tags: Tags
}

structure UpdateContentOutput {
    /// The updated content
    @required
    content: Content
}

/// Delete content
@http(method: "DELETE", uri: "/content/{contentId}")
operation DeleteContent {
    input: DeleteContentInput,
    output: DeleteContentOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure DeleteContentInput {
    /// ID of the content to delete
    @required
    @httpLabel
    contentId: String
}

structure DeleteContentOutput {
    /// ID of the deleted content
    @required
    contentId: String
}

//=====================
// Commerce Operations
//=====================

/// Get product by ID
@http(method: "GET", uri: "/products/{productId}")
operation GetProduct {
    input: GetProductInput,
    output: GetProductOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure GetProductInput {
    /// ID of the product to retrieve
    @required
    @httpLabel
    productId: String
}

structure GetProductOutput {
    /// The product information
    @required
    product: Product
}

/// List all products
@http(method: "GET", uri: "/products")
@paginated(inputToken: "nextToken", outputToken: "nextToken", pageSize: "limit")
operation ListProducts {
    input: ListProductsInput,
    output: ListProductsOutput,
    errors: [
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure ListProductsInput {
    /// Maximum number of products to return
    @httpQuery("limit")
    limit: Integer,
    
    /// Token for pagination
    @httpQuery("nextToken")
    nextToken: String,
    
    /// Filter by product category
    @httpQuery("category")
    category: String,
    
    /// Filter by product type
    @httpQuery("type")
    productType: ProductType
}

structure ListProductsOutput {
    /// List of products
    @required
    products: ProductList,
    
    /// Token for pagination
    nextToken: String
}

/// Create a new product
@http(method: "POST", uri: "/products")
operation CreateProduct {
    input: CreateProductInput,
    output: CreateProductOutput,
    errors: [
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure CreateProductInput {
    /// Name of the product
    @required
    name: String,
    
    /// Description of the product
    @required
    description: String,
    
    /// Price of the product
    @required
    price: Float,
    
    /// Product type
    @required
    productType: ProductType,
    
    /// Category of the product
    @required
    category: String,
    
    /// Inventory count
    inventory: Integer,
    
    /// Product images
    images: ImageList,
    
    /// Tags for the product
    tags: Tags
}

structure CreateProductOutput {
    /// The created product
    @required
    product: Product
}

/// Update an existing product
@http(method: "PUT", uri: "/products/{productId}")
operation UpdateProduct {
    input: UpdateProductInput,
    output: UpdateProductOutput,
    errors: [
        ResourceNotFoundException,
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure UpdateProductInput {
    /// ID of the product to update
    @required
    @httpLabel
    productId: String,
    
    /// Name of the product
    name: String,
    
    /// Description of the product
    description: String,
    
    /// Price of the product
    price: Float,
    
    /// Inventory count
    inventory: Integer,
    
    /// Product images
    images: ImageList,
    
    /// Tags for the product
    tags: Tags
}

structure UpdateProductOutput {
    /// The updated product
    @required
    product: Product
}

/// Delete a product
@http(method: "DELETE", uri: "/products/{productId}")
operation DeleteProduct {
    input: DeleteProductInput,
    output: DeleteProductOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure DeleteProductInput {
    /// ID of the product to delete
    @required
    @httpLabel
    productId: String
}

structure DeleteProductOutput {
    /// ID of the deleted product
    @required
    productId: String
}

//=====================
// Cultural Operations
//=====================

/// Get world by ID
@http(method: "GET", uri: "/worlds/{worldId}")
operation GetWorld {
    input: GetWorldInput,
    output: GetWorldOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure GetWorldInput {
    /// ID of the world to retrieve
    @required
    @httpLabel
    worldId: String
}

structure GetWorldOutput {
    /// The world information
    @required
    world: World
}

/// List all worlds
@http(method: "GET", uri: "/worlds")
@paginated(inputToken: "nextToken", outputToken: "nextToken", pageSize: "limit")
operation ListWorlds {
    input: ListWorldsInput,
    output: ListWorldsOutput,
    errors: [
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure ListWorldsInput {
    /// Maximum number of worlds to return
    @httpQuery("limit")
    limit: Integer,
    
    /// Token for pagination
    @httpQuery("nextToken")
    nextToken: String,
    
    /// Filter by creator
    @httpQuery("creator")
    creator: String
}

structure ListWorldsOutput {
    /// List of worlds
    @required
    worlds: WorldList,
    
    /// Token for pagination
    nextToken: String
}

/// Create a new world
@http(method: "POST", uri: "/worlds")
operation CreateWorld {
    input: CreateWorldInput,
    output: CreateWorldOutput,
    errors: [
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure CreateWorldInput {
    /// Name of the world
    @required
    name: String,
    
    /// Description of the world
    @required
    description: String,
    
    /// Creator of the world
    @required
    creator: String,
    
    /// Tags for the world
    tags: Tags
}

structure CreateWorldOutput {
    /// The created world
    @required
    world: World
}

/// Update an existing world
@http(method: "PUT", uri: "/worlds/{worldId}")
operation UpdateWorld {
    input: UpdateWorldInput,
    output: UpdateWorldOutput,
    errors: [
        ResourceNotFoundException,
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure UpdateWorldInput {
    /// ID of the world to update
    @required
    @httpLabel
    worldId: String,
    
    /// Name of the world
    name: String,
    
    /// Description of the world
    description: String,
    
    /// Regions in the world
    regions: RegionMap,
    
    /// Characters in the world
    characters: CharacterMap,
    
    /// Events in the world
    events: EventMap,
    
    /// Lore of the world
    lore: LoreMap,
    
    /// Tags for the world
    tags: Tags
}

structure UpdateWorldOutput {
    /// The updated world
    @required
    world: World
}

/// Delete a world
@http(method: "DELETE", uri: "/worlds/{worldId}")
operation DeleteWorld {
    input: DeleteWorldInput,
    output: DeleteWorldOutput,
    errors: [
        ResourceNotFoundException,
        AccessDeniedException,
        InternalServerException
    ]
}

structure DeleteWorldInput {
    /// ID of the world to delete
    @required
    @httpLabel
    worldId: String
}

structure DeleteWorldOutput {
    /// ID of the deleted world
    @required
    worldId: String
}

//=====================
// System Operations
//=====================

/// Get system status
@http(method: "GET", uri: "/system/status")
operation GetSystemStatus {
    input: GetSystemStatusInput,
    output: GetSystemStatusOutput,
    errors: [
        AccessDeniedException,
        InternalServerException
    ]
}

structure GetSystemStatusInput {
    /// Components to include in status
    @httpQuery("components")
    components: StringList
}

structure GetSystemStatusOutput {
    /// Overall system status
    @required
    status: SystemStatus,
    
    /// Status of individual components
    @required
    components: ComponentStatusMap,
    
    /// System metrics
    metrics: SystemMetrics,
    
    /// System version
    @required
    version: String
}

/// Execute a system command
@http(method: "POST", uri: "/system/command")
operation ExecuteCommand {
    input: ExecuteCommandInput,
    output: ExecuteCommandOutput,
    errors: [
        ValidationException,
        AccessDeniedException,
        ThrottlingException,
        InternalServerException
    ]
}

structure ExecuteCommandInput {
    /// Command to execute
    @required
    command: String,
    
    /// Arguments for the command
    args: StringList,
    
    /// Environment variables
    env: StringMap,
    
    /// Working directory
    workingDirectory: String,
    
    /// Timeout in seconds
    timeout: Integer
}

structure ExecuteCommandOutput {
    /// Command output
    @required
    output: String,
    
    /// Exit code
    @required
    exitCode: Integer,
    
    /// Error output
    error: String,
    
    /// Execution time in milliseconds
    executionTime: Long
}

//=====================
// Common Structures
//=====================

/// Agent information
structure Agent {
    /// Unique identifier for the agent
    @required
    agentId: String,
    
    /// Name of the agent
    @required
    name: String,
    
    /// Description of the agent
    description: String,
    
    /// Type of the agent
    @required
    type: String,
    
    /// Configuration for the agent
    @required
    configuration: AgentConfiguration,
    
    /// Capabilities of the agent
    capabilities: StringList,
    
    /// Status of the agent
    @required
    status: AgentStatus,
    
    /// Creation timestamp
    @required
    createdAt: Timestamp,
    
    /// Last update timestamp
    updatedAt: Timestamp,
    
    /// Tags for the agent
    tags: Tags
}

/// List of agents
@length(min: 0, max: 100)
list AgentList {
    member: Agent
}

/// Agent status
enum AgentStatus {
    ACTIVE,
    INACTIVE,
    TRAINING,
    ERROR
}

/// Agent configuration
document AgentConfiguration

/// Content information
structure Content {
    /// Unique identifier for the content
    @required
    contentId: String,
    
    /// Title of the content
    @required
    title: String,
    
    /// Content body
    @required
    body: String,
    
    /// Content type
    @required
    contentType: ContentType,
    
    /// Creator of the content
    creator: String,
    
    /// Creation timestamp
    @required
    createdAt: Timestamp,
    
    /// Last update timestamp
    updatedAt: Timestamp,
    
    /// URL to access the content
    url: String,
    
    /// Tags for the content
    tags: Tags
}

/// List of content items
@length(min: 0, max: 100)
list ContentList {
    member: Content
}

/// Content type
enum ContentType {
    BLOG,
    EBOOK,
    SOCIAL,
    DOCUMENTATION,
    WORLDBUILDING
}

/// Product information
structure Product {
    /// Unique identifier for the product
    @required
    productId: String,
    
    /// Name of the product
    @required
    name: String,
    
    /// Description of the product
    @required
    description: String,
    
    /// Price of the product
    @required
    price: Float,
    
    /// Product type
    @required
    productType: ProductType,
    
    /// Category of the product
    @required
    category: String,
    
    /// Inventory count
    inventory: Integer,
    
    /// Product images
    images: ImageList,
    
    /// Creation timestamp
    @required
    createdAt: Timestamp,
    
    /// Last update timestamp
    updatedAt: Timestamp,
    
    /// Tags for the product
    tags: Tags
}

/// List of products
@length(min: 0, max: 100)
list ProductList {
    member: Product
}

/// Product type
enum ProductType {
    OWN,
    AFFILIATE
}

/// Image information
structure Image {
    /// URL of the image
    @required
    url: String,
    
    /// Alt text for the image
    alt: String,
    
    /// Width of the image in pixels
    width: Integer,
    
    /// Height of the image in pixels
    height: Integer
}

/// List of images
@length(min: 0, max: 10)
list ImageList {
    member: Image
}

/// World information
structure World {
    /// Unique identifier for the world
    @required
    worldId: String,
    
    /// Name of the world
    @required
    name: String,
    
    /// Description of the world
    @required
    description: String,
    
    /// Creator of the world
    @required
    creator: String,
    
    /// Regions in the world
    regions: RegionMap,
    
    /// Characters in the world
    characters: CharacterMap,
    
    /// Events in the world
    events: EventMap,
    
    /// Lore of the world
    lore: LoreMap,
    
    /// Creation timestamp
    @required
    createdAt: Timestamp,
    
    /// Last update timestamp
    updatedAt: Timestamp,
    
    /// Tags for the world
    tags: Tags
}

/// List of worlds
@length(min: 0, max: 100)
list WorldList {
    member: World
}

/// Region information
structure Region {
    /// Name of the region
    @required
    name: String,
    
    /// Description of the region
    @required
    description: String,
    
    /// Climate of the region
    climate: String,
    
    /// Notable locations in the region
    notableLocations: StringList
}

/// Map of region IDs to regions
map RegionMap {
    key: String,
    value: Region
}

/// Character information
structure Character {
    /// Name of the character
    @required
    name: String,
    
    /// Role of the character
    @required
    role: String,
    
    /// Description of the character
    @required
    description: String,
    
    /// Traits of the character
    traits: StringList,
    
    /// Relationships with other characters
    relationships: StringMap
}

/// Map of character IDs to characters
map CharacterMap {
    key: String,
    value: Character
}

/// Event information
structure Event {
    /// Name of the event
    @required
    name: String,
    
    /// Date of the event
    date: String,
    
    /// Description of the event
    @required
    description: String
}

/// Map of event IDs to events
map EventMap {
    key: String,
    value: Event
}

/// Lore information
structure Lore {
    /// Name of the lore
    @required
    name: String,
    
    /// Content of the lore
    @required
    content: String
}

/// Map of lore IDs to lore
map LoreMap {
    key: String,
    value: Lore
}

/// System status
enum SystemStatus {
    HEALTHY,
    DEGRADED,
    UNAVAILABLE
}

/// Component status
structure ComponentStatus {
    /// Status of the component
    @required
    status: SystemStatus,
    
    /// Message about the component status
    message: String,
    
    /// Last check timestamp
    @required
    lastChecked: Timestamp
}

/// Map of component names to component status
map ComponentStatusMap {
    key: String,
    value: ComponentStatus
}

/// System metrics
structure SystemMetrics {
    /// CPU usage percentage
    cpuUsage: Float,
    
    /// Memory usage percentage
    memoryUsage: Float,
    
    /// Disk usage percentage
    diskUsage: Float,
    
    /// Network in bytes per second
    networkIn: Long,
    
    /// Network out bytes per second
    networkOut: Long,
    
    /// Active requests
    activeRequests: Integer,
    
    /// Requests per second
    requestsPerSecond: Float
}

/// Usage information
structure UsageInfo {
    /// Prompt tokens
    promptTokens: Integer,
    
    /// Completion tokens
    completionTokens: Integer,
    
    /// Total tokens
    totalTokens: Integer,
    
    /// Processing time in milliseconds
    processingTimeMs: Long
}

/// Context for agent invocation
document Context

/// Additional parameters
map Parameters {
    key: String,
    value: String
}

/// Metadata about responses
map Metadata {
    key: String,
    value: String
}

/// Tags for resources
map Tags {
    key: String,
    value: String
}

/// Map of strings
map StringMap {
    key: String,
    value: String
}

/// List of strings
@length(min: 0, max: 100)
list StringList {
    member: String
}

/// Timestamp in ISO 8601 format
string Timestamp

//=====================
// Error Structures
//=====================

/// Resource not found exception
@error("client")
@httpError(404)
structure ResourceNotFoundException {
    /// Error message
    @required
    message: String,
    
    /// Resource type
    resourceType: String,
    
    /// Resource ID
    resourceId: String
}

/// Access denied exception
@error("client")
@httpError(403)
structure AccessDeniedException {
    /// Error message
    @required
    message: String
}

/// Throttling exception
@error("client")
@httpError(429)
structure ThrottlingException {
    /// Error message
    @required
    message: String,
    
    /// Retry after seconds
    retryAfterSeconds: Integer
}

/// Internal server exception
@error("server")
@httpError(500)
structure InternalServerException {
    /// Error message
    @required
    message: String,
    
    /// Request ID
    requestId: String
}
