// SoulCoreHub Apps model
namespace soulcorehub.apps

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
use smithy.api#references

@simpleService(sdkId: "SoulCoreHubApps")
@restJson1
@sigv4(name: "execute-api")
service SoulCoreHubAppsService {
    version: "2025-05-10",
    operations: [
        GetAppList
    ]
}

// Resources
resource App {
    identifiers: { appId: String },
    create: RegisterApp,
    read: GetAppDetails,
    update: UpdateAppConfig,
    delete: DeleteApp,
    operations: [
        InvokeAppFunction
    ]
}

// Operations
@readonly
@http(method: "GET", uri: "/apps", code: 200)
operation GetAppList {
    input: GetAppListInput,
    output: GetAppListOutput,
    errors: [AuthenticationError]
}

@http(method: "POST", uri: "/apps", code: 201)
operation RegisterApp {
    input: RegisterAppInput,
    output: RegisterAppOutput,
    errors: [ValidationException, ConflictError, AuthenticationError]
}

@readonly
@http(method: "GET", uri: "/apps/{appId}", code: 200)
operation GetAppDetails {
    input: GetAppDetailsInput,
    output: GetAppDetailsOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@idempotent
@http(method: "PUT", uri: "/apps/{appId}", code: 200)
operation UpdateAppConfig {
    input: UpdateAppConfigInput,
    output: UpdateAppConfigOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@idempotent
@http(method: "DELETE", uri: "/apps/{appId}", code: 200)
operation DeleteApp {
    input: DeleteAppInput,
    output: DeleteAppOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError]
}

@http(method: "POST", uri: "/apps/{appId}/functions/{functionName}", code: 200)
operation InvokeAppFunction {
    input: InvokeAppFunctionInput,
    output: InvokeAppFunctionOutput,
    errors: [ValidationException, NotFoundError, AuthenticationError, AppFunctionError]
}

// Structures
structure GetAppListInput {
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @httpQuery("type")
    appType: AppType,
    
    @httpQuery("maxResults")
    maxResults: Integer,
    
    @httpQuery("nextToken")
    nextToken: String
}

structure GetAppListOutput {
    @required
    apps: AppSummaryList,
    
    nextToken: String
}

structure RegisterAppInput {
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    appName: String,
    
    @required
    appType: AppType,
    
    description: String,
    
    entrypoint: String,
    
    config: Document,
    
    metadata: Document
}

structure RegisterAppOutput {
    @required
    appId: String,
    
    @required
    appName: String,
    
    @required
    createdAt: Timestamp
}

structure GetAppDetailsInput {
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    @httpLabel
    appId: String
}

structure GetAppDetailsOutput {
    @required
    appId: String,
    
    @required
    appName: String,
    
    @required
    appType: AppType,
    
    @required
    createdAt: Timestamp,
    
    description: String,
    
    entrypoint: String,
    
    config: Document,
    
    metadata: Document,
    
    functions: FunctionList
}

structure UpdateAppConfigInput {
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    @httpLabel
    appId: String,
    
    appName: String,
    
    description: String,
    
    entrypoint: String,
    
    config: Document,
    
    metadata: Document
}

structure UpdateAppConfigOutput {
    @required
    appId: String,
    
    @required
    updatedAt: Timestamp
}

structure DeleteAppInput {
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    @httpLabel
    appId: String
}

structure DeleteAppOutput {
    @required
    appId: String,
    
    @required
    deletedAt: Timestamp
}

structure InvokeAppFunctionInput {
    @required
    @httpHeader("X-Api-Token")
    token: String,
    
    @required
    @httpLabel
    appId: String,
    
    @required
    @httpLabel
    functionName: String,
    
    parameters: Document,
    
    context: Document
}

structure InvokeAppFunctionOutput {
    @required
    appId: String,
    
    @required
    functionName: String,
    
    @required
    result: Document,
    
    @required
    invokedAt: Timestamp
}

// App-specific structures
structure AppSummary {
    @required
    appId: String,
    
    @required
    appName: String,
    
    @required
    appType: AppType,
    
    description: String
}

structure Function {
    @required
    name: String,
    
    description: String,
    
    parameters: Document
}

// Errors
@error("client")
@httpError(400)
structure AppFunctionError {
    @required
    message: String,
    
    appId: String,
    
    functionName: String,
    
    errorCode: String,
    
    details: Document
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
@httpError(409)
structure ConflictError {
    @required
    message: String,
    
    resourceId: String
}

// Enums
@enum([
    {
        value: "STACKFU",
        name: "STACKFU"
    },
    {
        value: "AIBEFRESH",
        name: "AIBEFRESH"
    },
    {
        value: "ANIMA",
        name: "ANIMA"
    },
    {
        value: "AZUR",
        name: "AZUR"
    },
    {
        value: "EVOVE",
        name: "EVOVE"
    },
    {
        value: "CUSTOM",
        name: "CUSTOM"
    }
])
string AppType

// Lists
list AppSummaryList {
    member: AppSummary
}

list FunctionList {
    member: Function
}

// Common document type for flexible JSON
document Document

// Timestamp type
@timestampFormat("date-time")
timestamp Timestamp
