// Main SoulCoreHub API model
namespace soulcorehub.api

use aws.api#simpleService
use aws.auth#sigv4
use aws.protocols#restJson1
use smithy.framework#ValidationException
use smithy.api#http
use smithy.api#httpLabel
use smithy.api#httpQuery
use smithy.api#httpHeader
use smithy.api#httpError
use smithy.api#readonly
use smithy.api#idempotent

@simpleService(sdkId: "SoulCoreHub")
@restJson1
@sigv4(name: "execute-api")
service SoulCoreHubService {
    version: "2025-05-10",
    operations: [
        GetMainframeStatus,
        GetClientDetails,
        ExecuteCommand,
        SearchMemory,
        PurgeMemory,
        UpdateAgentConfig
    ]
}

// Resources
resource Client {
    identifiers: { clientId: String },
    create: RegisterClient,
    read: GetClientDetails,
    operations: [
        AuthenticateClient,
        UpdateClientConfig
    ]
}

resource Memory {
    identifiers: { memoryId: String },
    read: GetMemoryState,
    update: UpdateMemoryState,
    operations: [
        SearchMemory,
        PurgeMemory
    ]
}

resource Agent {
    identifiers: { agentId: String },
    read: GetAgentStatus,
    operations: [
        InvokeAgent,
        UpdateAgentConfig
    ]
}

// Operations
@readonly
@http(method: "GET", uri: "/status", code: 200)
operation GetMainframeStatus {
    output: GetMainframeStatusOutput,
    errors: [ServiceUnavailableError]
}

@http(method: "POST", uri: "/clients", code: 201)
operation RegisterClient {
    input: RegisterClientInput,
    output: RegisterClientOutput,
    errors: [ValidationException, ConflictError]
}

@readonly
@http(method: "GET", uri: "/clients/{clientId}", code: 200)
operation GetClientDetails {
    input: GetClientDetailsInput,
    output: GetClientDetailsOutput,
    errors: [ValidationException, NotFoundError]
}

@http(method: "POST", uri: "/clients/{clientId}/authenticate", code: 200)
operation AuthenticateClient {
    input: AuthenticateClientInput,
    output: AuthenticateClientOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@idempotent
@http(method: "PUT", uri: "/clients/{clientId}/config", code: 200)
operation UpdateClientConfig {
    input: UpdateClientConfigInput,
    output: UpdateClientConfigOutput,
    errors: [ValidationException, NotFoundError]
}

@http(method: "POST", uri: "/execute", code: 200)
operation ExecuteCommand {
    input: ExecuteCommandInput,
    output: ExecuteCommandOutput,
    errors: [ValidationException, AuthenticationError, ExecutionError]
}

@readonly
@http(method: "GET", uri: "/memory/{memoryId}", code: 200)
operation GetMemoryState {
    input: GetMemoryStateInput,
    output: GetMemoryStateOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@idempotent
@http(method: "PUT", uri: "/memory/{memoryId}", code: 200)
operation UpdateMemoryState {
    input: UpdateMemoryStateInput,
    output: UpdateMemoryStateOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@http(method: "POST", uri: "/memory/{memoryId}/search", code: 200)
operation SearchMemory {
    input: SearchMemoryInput,
    output: SearchMemoryOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@idempotent
@http(method: "DELETE", uri: "/memory/{memoryId}", code: 200)
operation PurgeMemory {
    input: PurgeMemoryInput,
    output: PurgeMemoryOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@readonly
@http(method: "GET", uri: "/agents/{agentId}/status", code: 200)
operation GetAgentStatus {
    input: GetAgentStatusInput,
    output: GetAgentStatusOutput,
    errors: [ValidationException, NotFoundError]
}

@http(method: "POST", uri: "/agents/{agentId}/invoke", code: 200)
operation InvokeAgent {
    input: InvokeAgentInput,
    output: InvokeAgentOutput,
    errors: [ValidationException, NotFoundError, AgentExecutionError]
}

@idempotent
@http(method: "PUT", uri: "/agents/{agentId}/config", code: 200)
operation UpdateAgentConfig {
    input: UpdateAgentConfigInput,
    output: UpdateAgentConfigOutput,
    errors: [ValidationException, NotFoundError]
}

// Structures
structure GetMainframeStatusOutput {
    @required
    status: String,
    
    @required
    version: String,
    
    @required
    uptime: Long,
    
    activeAgents: Integer,
    
    activeClients: Integer,
    
    memoryUsage: Float,
    
    systemMessages: StringList
}

structure RegisterClientInput {
    @required
    clientName: String,
    
    @required
    clientType: ClientType,
    
    apiKey: String,
    
    callbackUrl: String,
    
    metadata: Document
}

structure RegisterClientOutput {
    @required
    clientId: String,
    
    @required
    apiKey: String,
    
    @required
    createdAt: Timestamp
}

structure GetClientDetailsInput {
    @required
    @httpLabel
    clientId: String
}

structure GetClientDetailsOutput {
    @required
    clientId: String,
    
    @required
    clientName: String,
    
    @required
    clientType: ClientType,
    
    @required
    createdAt: Timestamp,
    
    lastActive: Timestamp,
    
    callbackUrl: String,
    
    metadata: Document
}

structure AuthenticateClientInput {
    @required
    @httpLabel
    clientId: String,
    
    @required
    apiKey: String
}

structure AuthenticateClientOutput {
    @required
    token: String,
    
    @required
    expiresAt: Timestamp
}

structure UpdateClientConfigInput {
    @required
    @httpLabel
    clientId: String,
    
    clientName: String,
    
    callbackUrl: String,
    
    metadata: Document
}

structure UpdateClientConfigOutput {
    @required
    clientId: String,
    
    @required
    updatedAt: Timestamp
}

structure ExecuteCommandInput {
    @required
    command: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    parameters: Document,
    
    context: Document
}

structure ExecuteCommandOutput {
    @required
    executionId: String,
    
    @required
    result: Document,
    
    @required
    executedAt: Timestamp
}

structure GetMemoryStateInput {
    @required
    @httpLabel
    memoryId: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String
}

structure GetMemoryStateOutput {
    @required
    memoryId: String,
    
    @required
    state: Document,
    
    @required
    lastUpdated: Timestamp
}

structure UpdateMemoryStateInput {
    @required
    @httpLabel
    memoryId: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    state: Document,
    
    @httpQuery("mergeStrategy")
    mergeStrategy: MergeStrategy
}

structure UpdateMemoryStateOutput {
    @required
    memoryId: String,
    
    @required
    updatedAt: Timestamp
}

structure SearchMemoryInput {
    @required
    @httpLabel
    memoryId: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    query: String,
    
    filters: Document,
    
    @httpQuery("maxResults")
    maxResults: Integer
}

structure SearchMemoryOutput {
    @required
    memoryId: String,
    
    @required
    results: DocumentList,
    
    @required
    searchedAt: Timestamp
}

structure PurgeMemoryInput {
    @required
    @httpLabel
    memoryId: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @httpQuery("purgeType")
    purgeType: PurgeType
}

structure PurgeMemoryOutput {
    @required
    memoryId: String,
    
    @required
    purgedAt: Timestamp
}

structure GetAgentStatusInput {
    @required
    @httpLabel
    agentId: String
}

structure GetAgentStatusOutput {
    @required
    agentId: String,
    
    @required
    agentName: String,
    
    @required
    status: AgentStatus,
    
    @required
    lastActive: Timestamp,
    
    capabilities: StringList,
    
    metadata: Document
}

structure InvokeAgentInput {
    @required
    @httpLabel
    agentId: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    action: String,
    
    parameters: Document,
    
    context: Document
}

structure InvokeAgentOutput {
    @required
    invocationId: String,
    
    @required
    result: Document,
    
    @required
    invokedAt: Timestamp
}

structure UpdateAgentConfigInput {
    @required
    @httpLabel
    agentId: String,
    
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    agentName: String,
    
    capabilities: StringList,
    
    metadata: Document
}

structure UpdateAgentConfigOutput {
    @required
    agentId: String,
    
    @required
    updatedAt: Timestamp
}

// Errors
@error("server")
@httpError(503)
structure ServiceUnavailableError {
    @required
    message: String
}

@error("client")
@httpError(409)
structure ConflictError {
    @required
    message: String,
    
    resourceId: String
}

@error("client")
@httpError(404)
structure NotFoundError {
    @required
    message: String,
    
    resourceType: String,
    
    resourceId: String
}

@error("client")
@httpError(401)
structure AuthenticationError {
    @required
    message: String
}

@error("client")
@httpError(400)
structure ExecutionError {
    @required
    message: String,
    
    errorCode: String,
    
    details: Document
}

@error("client")
@httpError(400)
structure AgentExecutionError {
    @required
    message: String,
    
    agentId: String,
    
    errorCode: String,
    
    details: Document
}

// Enums
@enum([
    {
        value: "APP",
        name: "APPLICATION"
    },
    {
        value: "SERVICE",
        name: "SERVICE"
    },
    {
        value: "AGENT",
        name: "AGENT"
    },
    {
        value: "SYSTEM",
        name: "SYSTEM"
    }
])
string ClientType

@enum([
    {
        value: "REPLACE",
        name: "REPLACE"
    },
    {
        value: "MERGE",
        name: "MERGE"
    },
    {
        value: "APPEND",
        name: "APPEND"
    }
])
string MergeStrategy

@enum([
    {
        value: "FULL",
        name: "FULL"
    },
    {
        value: "PARTIAL",
        name: "PARTIAL"
    }
])
string PurgeType

@enum([
    {
        value: "ACTIVE",
        name: "ACTIVE"
    },
    {
        value: "INACTIVE",
        name: "INACTIVE"
    },
    {
        value: "BUSY",
        name: "BUSY"
    },
    {
        value: "ERROR",
        name: "ERROR"
    }
])
string AgentStatus

// Lists
list StringList {
    member: String
}

list DocumentList {
    member: Document
}

// Common document type for flexible JSON
document Document

// Timestamp type
@timestampFormat("date-time")
timestamp Timestamp
