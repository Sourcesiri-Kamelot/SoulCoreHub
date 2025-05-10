// Common types for SoulCoreHub
namespace soulcorehub.common

use aws.api#service
use aws.auth#sigv4
use aws.protocols#restJson1

// Common structures
structure Pagination {
    maxResults: Integer,
    nextToken: String
}

structure TimeRange {
    startTime: Timestamp,
    endTime: Timestamp
}

structure ResourceMetadata {
    createdAt: Timestamp,
    updatedAt: Timestamp,
    createdBy: String,
    updatedBy: String,
    tags: TagMap
}

// Common maps
map TagMap {
    key: String,
    value: String
}

// Common document type for flexible JSON
document Document

// Timestamp type
@timestampFormat("date-time")
timestamp Timestamp
