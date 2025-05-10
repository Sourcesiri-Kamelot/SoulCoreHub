$version: "2"

namespace smithy.api

/// Indicates that an operation is idempotent.
@trait(selector: "operation")
structure idempotent {}

/// Indicates that a shape references another resource.
@trait(selector: "structure > member")
structure references {
    /// The resource that is referenced.
    resource: String,
}
