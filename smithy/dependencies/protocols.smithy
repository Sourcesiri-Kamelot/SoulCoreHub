$version: "2"

namespace aws.protocols

/// Adds the AWS JSON 1.0 protocol to a service.
@trait(selector: "service")
structure awsJson1_0 {}

/// Adds the AWS JSON 1.1 protocol to a service.
@trait(selector: "service")
structure awsJson1_1 {}

/// Adds the AWS Query protocol to a service.
@trait(selector: "service")
structure awsQuery {}

/// Adds the AWS EC2 Query protocol to a service.
@trait(selector: "service")
structure ec2Query {}

/// Adds the REST JSON 1 protocol to a service.
@trait(selector: "service")
structure restJson1 {}

/// Adds the REST XML protocol to a service.
@trait(selector: "service")
structure restXml {}
