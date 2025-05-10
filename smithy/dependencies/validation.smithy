$version: "2"

namespace smithy.framework

/// An error returned when a client's input fails validation.
@error("client")
structure ValidationException {
    /// The message describing the validation failure.
    @required
    message: String,

    /// The specific validation failures.
    fieldErrors: FieldErrors,
}

/// A map of field names to validation errors.
map FieldErrors {
    key: String,
    value: FieldError,
}

/// A validation error for a specific field.
structure FieldError {
    /// The validation error message.
    @required
    message: String,

    /// The path to the field that failed validation.
    path: String,
}
