$version: "2"

namespace smithy.api

/// Binds an operation to an HTTP method and URI path.
@trait(selector: "operation")
structure http {
    /// The HTTP method to use.
    @required
    method: String,

    /// The HTTP URI path to use.
    @required
    uri: String,

    /// The HTTP response code to use.
    code: Integer,
}

/// Binds a member to an HTTP label.
@trait(selector: "structure > member")
structure httpLabel {}

/// Binds a member to an HTTP query parameter.
@trait(selector: "structure > member")
structure httpQuery {
    /// The name of the query parameter.
    name: String,
}

/// Binds a member to an HTTP header.
@trait(selector: "structure > member")
structure httpHeader {
    /// The name of the header.
    name: String,
}

/// Binds a member to the HTTP payload.
@trait(selector: "structure > member")
structure httpPayload {}

/// Binds a structure to an HTTP error response.
@trait(selector: "structure")
structure httpError {
    /// The HTTP status code to use.
    code: Integer,
}

/// Indicates that an operation is read-only.
@trait(selector: "operation")
structure readonly {}
