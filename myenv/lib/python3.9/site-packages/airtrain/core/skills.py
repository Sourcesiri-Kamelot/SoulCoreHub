from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Generic, TypeVar
from uuid import UUID, uuid4
import time
import functools
from .schemas import InputSchema, OutputSchema

# Import telemetry
from airtrain.telemetry import (
    telemetry,
    SkillInitTelemetryEvent,
    SkillProcessTelemetryEvent,
)

# Generic type variables for input and output schemas
InputT = TypeVar("InputT", bound=InputSchema)
OutputT = TypeVar("OutputT", bound=OutputSchema)


class Skill(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all skills in Airtrain.
    Each skill must define input/output schemas and implement core processing logic.
    """

    input_schema: Type[InputT]
    output_schema: Type[OutputT]
    _skill_id: Optional[UUID] = None
    _original_process = None

    def __init__(self):
        """Initialize the skill and capture telemetry."""
        # Initialize skill_id if not already set
        if not self._skill_id:
            self._skill_id = uuid4()
        
        # Monkey patch the process method if it hasn't been patched yet
        # This allows us to add telemetry without changing the API
        if not hasattr(self.__class__, '_patched_process'):
            # Store the original process method implementation from this instance
            # This is crucial for proper behavior with inheritance
            self.__class__._original_process = self.__class__.process
            
            # Create a wrapper function that will capture telemetry
            def _create_wrapper(original_method):
                @functools.wraps(original_method)
                def wrapped_process(instance, input_data):
                    start_time = time.time()
                    error = None
                    
                    try:
                        # Call the original process method
                        result = original_method(instance, input_data)
                        return result
                    except Exception as e:
                        error = str(e)
                        raise
                    finally:
                        duration = time.time() - start_time
                        
                        try:
                            # Serialize input data for telemetry
                            serialized_input = None
                            try:
                                # Convert input_data to dict if it's a Pydantic model
                                if hasattr(input_data, "dict"):
                                    serialized_input = input_data.dict()
                                # If it's a dataclass
                                elif hasattr(input_data, "__dataclass_fields__"):
                                    from dataclasses import asdict
                                    serialized_input = asdict(input_data)
                                # Fallback
                                else:
                                    serialized_input = {
                                        "__str__": str(input_data)
                                    }
                            except Exception:
                                # If serialization fails, provide simple info
                                serialized_input = {"error": "Failed to serialize input data"}
                            
                            telemetry.capture(
                                SkillProcessTelemetryEvent(
                                    skill_id=str(instance.skill_id),
                                    skill_class=instance.__class__.__name__,
                                    input_schema=instance.input_schema.__name__,
                                    output_schema=instance.output_schema.__name__,
                                    input_data=serialized_input,
                                    duration_seconds=duration,
                                    error=error,
                                )
                            )
                        except Exception:
                            # Silently continue if telemetry fails
                            pass
                
                return wrapped_process
            
            # Replace the process method with our wrapped version at the class level
            self.__class__.process = _create_wrapper(self.__class__._original_process)
            
            # Mark this class as patched to prevent double-patching
            self.__class__._patched_process = True
        
        # Capture telemetry for initialization
        try:
            telemetry.capture(
                SkillInitTelemetryEvent(
                    skill_id=str(self.skill_id),
                    skill_class=self.__class__.__name__,
                )
            )
        except Exception:
            # Silently continue if telemetry fails
            pass

    @abstractmethod
    def process(self, input_data: InputT) -> OutputT:
        """
        Process the input and generate output according to defined schemas.

        Args:
            input_data: Validated input conforming to input_schema

        Returns:
            Output conforming to output_schema

        Raises:
            ProcessingError: If processing fails
        """
        pass

    def __call__(self, input_data: InputT) -> OutputT:
        """Make the skill callable, with input/output validation."""
        self.validate_input(input_data)
        result = self.process(input_data)
        self.validate_output(result)
        return result

    def validate_input(self, input_data: Any) -> None:
        """
        Validate input data before processing.

        Args:
            input_data: Raw input data

        Raises:
            InputValidationError: If validation fails
        """
        if not isinstance(input_data, self.input_schema):
            raise InputValidationError(
                f"Input must be an instance of {self.input_schema.__name__}"
            )
        input_data.validate_all()

    def validate_output(self, output_data: Any) -> None:
        """
        Validate output data after processing.

        Args:
            output_data: Processed output data

        Raises:
            OutputValidationError: If validation fails
        """
        if not isinstance(output_data, self.output_schema):
            raise OutputValidationError(
                f"Output must be an instance of {self.output_schema.__name__}"
            )
        output_data.validate_all()

    def evaluate(self, test_dataset: Optional["Dataset"] = None) -> "EvaluationResult":
        """
        Evaluate skill performance.

        Args:
            test_dataset: Optional dataset for evaluation

        Returns:
            EvaluationResult containing metrics
        """
        if not test_dataset:
            test_dataset = self.get_default_test_dataset()

        results = []
        for test_case in test_dataset:
            try:
                output = self.process(test_case.input)
                results.append(self.compare_output(output, test_case.expected))
            except Exception as e:
                results.append(EvaluationError(str(e)))

        return EvaluationResult(results)

    def get_default_test_dataset(self) -> "Dataset":
        """Get default test dataset for evaluation"""
        raise NotImplementedError("No default test dataset provided")

    def compare_output(self, actual: OutputT, expected: OutputT) -> Dict:
        """
        Compare actual output with expected output

        Args:
            actual: Actual output from processing
            expected: Expected output from test case

        Returns:
            Dictionary containing comparison metrics
        """
        raise NotImplementedError("Output comparison not implemented")

    @property
    def skill_id(self) -> UUID:
        """Unique identifier for the skill"""
        if not self._skill_id:
            self._skill_id = uuid4()
        return self._skill_id


class ProcessingError(Exception):
    """Raised when skill processing fails"""

    pass


class InputValidationError(Exception):
    """Raised when input validation fails"""

    pass


class OutputValidationError(Exception):
    """Raised when output validation fails"""

    pass


class EvaluationError:
    """Represents an error during evaluation"""

    def __init__(self, message: str):
        self.message = message


class EvaluationResult:
    """Contains results from skill evaluation"""

    def __init__(self, results: list):
        self.results = results

    def get_metrics(self) -> Dict:
        """Calculate evaluation metrics"""
        return {
            "total_cases": len(self.results),
            "successful": len(
                [r for r in self.results if not isinstance(r, EvaluationError)]
            ),
            "failed": len([r for r in self.results if isinstance(r, EvaluationError)]),
            "results": self.results,
        }


class Dataset:
    """Represents a test dataset for skill evaluation"""

    def __init__(self, test_cases: list):
        self.test_cases = test_cases

    def __iter__(self):
        return iter(self.test_cases)
