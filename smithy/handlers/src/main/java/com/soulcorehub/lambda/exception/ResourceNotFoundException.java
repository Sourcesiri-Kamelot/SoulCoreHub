package com.soulcorehub.lambda.exception;

/**
 * Exception thrown when a resource is not found
 */
public class ResourceNotFoundException extends RuntimeException {
    private final String resourceType;
    private final String resourceId;

    /**
     * Creates a new ResourceNotFoundException
     *
     * @param message      The error message
     * @param resourceType The type of resource
     * @param resourceId   The ID of the resource
     */
    public ResourceNotFoundException(String message, String resourceType, String resourceId) {
        super(message);
        this.resourceType = resourceType;
        this.resourceId = resourceId;
    }

    /**
     * Gets the resource type
     *
     * @return The resource type
     */
    public String getResourceType() {
        return resourceType;
    }

    /**
     * Gets the resource ID
     *
     * @return The resource ID
     */
    public String getResourceId() {
        return resourceId;
    }
}
