$version: "2"

namespace aws.api

/// Indicates that a shape is a service.
@trait(selector: "service")
structure service {
    /// The ID to use when generating SDKs.
    @required
    sdkId: String,

    /// The version of the service API.
    @required
    arnNamespace: String,

    /// The version of the service API.
    @required
    cloudFormationName: String,

    /// The version of the service API.
    @required
    cloudTrailEventSource: String,

    /// The version of the service API.
    @required
    endpointPrefix: String,

    /// The error prefix to use when generating SDKs.
    @required
    errorPrefix: String,
}

/// Indicates that a shape is a service.
@trait(selector: "service")
structure simpleService {
    /// The ID to use when generating SDKs.
    @required
    sdkId: String,
}

/// Indicates that a shape is a service.
@trait(selector: "service")
structure apiVersion {
    /// The version of the service API.
    @required
    version: String,
}
