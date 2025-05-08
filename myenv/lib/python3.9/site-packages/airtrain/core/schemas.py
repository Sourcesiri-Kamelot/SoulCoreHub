from typing import Any, Dict, Optional, Type, Union, cast, get_args, get_origin
from pydantic import BaseModel, ValidationError, create_model
import json
from uuid import UUID, uuid4


class AirtrainSchema(BaseModel):
    """Base schema class for all Airtrain schemas"""

    _schema_id: Optional[UUID] = None
    _schema_version: str = "1.0.0"

    @classmethod
    def _extract_field_type(cls, field_props: Dict) -> Type:
        """
        Extract Python type from field properties

        Args:
            field_props: Field properties from JSON schema

        Returns:
            Python type for the field
        """
        # Handle direct type specification
        if "type" in field_props:
            return cls._map_json_type_to_python(field_props["type"])

        # Handle anyOf/oneOf cases
        for union_key in ["anyOf", "oneOf"]:
            if union_key in field_props:
                types = []
                for type_option in field_props[union_key]:
                    if "type" in type_option:
                        if type_option["type"] == "null":
                            types.append(type(None))
                        else:
                            types.append(
                                cls._map_json_type_to_python(type_option["type"])
                            )

                # If we have types, create a Union
                if types:
                    return Union[tuple(types)] if len(types) > 1 else types[0]

        # Default to Any if type cannot be determined
        return Any

    @classmethod
    def _get_field_config(cls, field_props: Dict) -> tuple:
        """
        Get field type and default value configuration

        Args:
            field_props: Field properties from JSON schema

        Returns:
            Tuple of (field_type, field_default)
        """
        field_type = cls._extract_field_type(field_props)

        # Handle default values
        if "default" in field_props:
            return (field_type, field_props["default"])

        # Handle Optional/Union types
        if get_origin(field_type) is Union and type(None) in get_args(field_type):
            return (field_type, None)

        # No default value
        return (field_type, ...)

    @classmethod
    def from_json_schema(cls, json_schema: str | Dict) -> "AirtrainSchema":
        """
        Create an AirtrainSchema from a JSON schema

        Args:
            json_schema: JSON schema string or dictionary

        Returns:
            AirtrainSchema instance

        Raises:
            ValidationError: If schema is invalid
        """
        if isinstance(json_schema, str):
            json_schema = json.loads(json_schema)

        # Convert JSON schema to Pydantic model
        assert isinstance(json_schema, dict)
        model_fields = {}
        required_fields = json_schema.get("required", [])

        for field_name, field_props in json_schema["properties"].items():
            field_type, field_default = cls._get_field_config(field_props)

            # Override default for required fields
            if field_name in required_fields:
                field_default = ...

            model_fields[field_name] = (field_type, field_default)

        # Create dynamic model using create_model
        DynamicSchema = create_model("DynamicSchema", __base__=cls, **model_fields)

        return cast(AirtrainSchema, DynamicSchema)

    @classmethod
    def from_pydantic_schema(cls, pydantic_schema: Type[BaseModel]) -> "AirtrainSchema":
        """
        Create an AirtrainSchema from a Pydantic model

        Args:
            pydantic_schema: Pydantic model class

        Returns:
            AirtrainSchema instance
        """
        # Get JSON schema from pydantic model
        schema = pydantic_schema.model_json_schema()

        # Create new schema using from_json_schema
        return cls.from_json_schema(schema)

    @staticmethod
    def _map_json_type_to_python(json_type: str) -> Type:
        """Map JSON schema types to Python types"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        assert json_type in type_mapping, f"Unsupported JSON type: {json_type}"
        return type_mapping[json_type]

    def validate_custom(self) -> None:
        """
        Perform custom validation beyond Pydantic's built-in validation
        To be implemented by subclasses

        Raises:
            ValidationError: If custom validation fails
        """
        pass

    def validate_all(self) -> None:
        """
        Perform all validations including Pydantic and custom

        Raises:
            ValidationError: If any validation fails
        """
        # Pydantic validation happens automatically
        try:
            self.validate_custom()
        except Exception as e:
            raise ValidationError(f"Custom validation failed: {str(e)}")

    def publish(self) -> UUID:
        """
        Publish schema to make it available for use

        Returns:
            UUID: Unique identifier for the published schema
        """
        if not self._schema_id:
            self._schema_id = uuid4()
        # TODO: Implement actual publishing logic
        return self._schema_id

    @classmethod
    def get_by_id(cls, schema_id: UUID) -> "AirtrainSchema":
        """
        Retrieve a published schema by ID

        Args:
            schema_id: UUID of the published schema

        Returns:
            AirtrainSchema instance

        Raises:
            ValueError: If schema not found
        """
        # TODO: Implement schema retrieval logic
        raise NotImplementedError("Schema retrieval not implemented yet")


class InputSchema(AirtrainSchema):
    """Schema for task/skill inputs"""

    def validate_input_specific(self) -> None:
        """
        Perform input-specific validations
        To be implemented by subclasses

        Raises:
            ValidationError: If validation fails
        """
        pass

    def validate_custom(self) -> None:
        """
        Override custom validation to include input-specific validation

        Raises:
            ValidationError: If validation fails
        """
        super().validate_custom()
        self.validate_input_specific()


class OutputSchema(AirtrainSchema):
    """Schema for task/skill outputs"""

    def validate_output_specific(self) -> None:
        """
        Perform output-specific validations
        To be implemented by subclasses

        Raises:
            ValidationError: If validation fails
        """
        pass

    def validate_custom(self) -> None:
        """
        Override custom validation to include output-specific validation

        Raises:
            ValidationError: If validation fails
        """
        super().validate_custom()
        self.validate_output_specific()
