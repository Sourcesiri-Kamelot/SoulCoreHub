$version: "2"

namespace aws.auth

/// Adds AWS Signature Version 4 authentication to a service.
@trait(selector: "service")
structure sigv4 {
    /// The name of the signing service to use.
    @required
    name: String,
}
