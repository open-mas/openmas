TASK: Define Communication Pattern Engine API
Objective: To define a comprehensive API for the Communication Pattern Engine that enables standardized agent interaction patterns across all protocols while maintaining SIMF compatibility and reasoning agnosticism.

Related Finding from PLANNING.MD: 1.4.2 Communication Pattern Engine Missing API

Key Deliverables:

- A fully specified IPatternEngine interface (Python ABC) with methods for pattern registration, execution, and lifecycle management
- Pydantic models for all pattern-related data structures (PatternDefinition, PatternConfig, PatternResult, etc.)
- Clear specification of SIMF integration for pattern execution across protocols
- Updated documentation in the communication patterns architecture documents
- Examples illustrating how different patterns (request-response, publish-subscribe, delegation) use the interface

Detailed Sub-Tasks/Actions:

1. Review Existing Documentation:
   - Thoroughly review `refactoring_work/design/07_communication_patterns/` for current pattern concepts and implementations
   - Analyze `refactoring_work/design/01_architecture/internal_message_format_standard.md` for SIMF integration requirements
   - Examine completed TASK files (IProtocolAdapter, message handling) for interface consistency patterns
   - Review existing pattern definitions in `refactoring_work/design/07_communication_patterns/patterns/` for comprehensive coverage

2. Define Core IPatternEngine Interface:
   - Create the main interface as a Python ABC with these core methods:
     * `async def register_pattern(self, pattern: PatternDefinition) -> None:` - Register a new communication pattern
     * `async def execute_pattern(self, pattern_name: str, config: PatternConfig, message: InternalMessageFormat) -> PatternResult:` - Execute a specific pattern
     * `async def get_available_patterns(self) -> List[PatternInfo]:` - Get list of registered patterns
     * `async def create_pattern_instance(self, pattern_name: str, config: PatternConfig) -> IPatternInstance:` - Create pattern instance for stateful patterns
     * `def supports_protocol(self, pattern_name: str, protocol_type: str) -> bool:` - Check protocol compatibility
     * `async def validate_pattern_config(self, pattern_name: str, config: PatternConfig) -> ValidationResult:` - Validate pattern configuration
   - Ensure all methods have explicit type hints and detailed docstrings
   - Include pattern discovery and capability checking mechanisms

3. Define Supporting Pydantic Models:
   - PatternDefinition(BaseModel): Core pattern specification
     * `name: str` - Unique pattern identifier
     * `version: str` - Pattern version following semantic versioning
     * `description: str` - Human-readable pattern description
     * `supported_protocols: List[str]` - Compatible protocols
     * `pattern_type: PatternType` - Pattern category (request-response, publish-subscribe, etc.)
     * `options_schema: Dict[str, Any]` - JSON schema for pattern options
     * `implementation_class: str` - Python class implementing the pattern
   - PatternConfig(BaseModel): Pattern execution configuration
     * `pattern_name: str` - Pattern to execute
     * `options: Dict[str, Any]` - Pattern-specific options
     * `timeout: Optional[int]` - Pattern execution timeout
     * `retry_policy: Optional[RetryPolicy]` - Retry configuration
     * `protocol_adaptations: Dict[str, Dict[str, Any]]` - Protocol-specific adaptations
   - PatternResult(BaseModel): Pattern execution result
     * `success: bool` - Whether pattern execution succeeded
     * `result_data: Optional[Any]` - Pattern-specific result data
     * `messages: List[InternalMessageFormat]` - Messages generated/received
     * `execution_time: float` - Pattern execution duration
     * `metadata: Dict[str, Any]` - Pattern-specific metadata
   - Define supporting enums: PatternType, PatternStatus
   - Define error hierarchy: PatternError, PatternNotFoundError, PatternConfigError, PatternExecutionError

4. Define IPatternInstance Interface:
   - Create interface for stateful pattern instances:
     * `async def start(self) -> None:` - Initialize pattern instance
     * `async def stop(self) -> None:` - Cleanup pattern instance
     * `async def process_message(self, message: InternalMessageFormat) -> Optional[PatternResult]:` - Process incoming message
     * `async def get_status(self) -> PatternInstanceStatus:` - Get current instance status
     * `async def update_config(self, config: PatternConfig) -> None:` - Update pattern configuration
   - Support for long-running patterns like streaming and delegation

5. Specify SIMF Integration Requirements:
   - Detail how patterns must use SIMF for all message exchange
   - Specify pattern metadata preservation in SIMF headers
   - Define protocol adaptation through IProtocolAdapter interface
   - Document pattern-specific SIMF payload type requirements
   - Specify cross-protocol pattern execution mechanisms

6. Define Pattern Lifecycle Management:
   - Specify pattern registration and discovery procedures
   - Define pattern versioning and compatibility checking
   - Detail pattern instance creation and cleanup
   - Specify pattern dependency management
   - Define pattern extension and customization mechanisms

7. Create Pattern Implementation Examples:
   - Provide conceptual examples for core patterns: request-response, publish-subscribe, delegation
   - Show how patterns integrate with IProtocolAdapter for different protocols
   - Demonstrate SIMF usage for pattern execution
   - Include error handling and edge case examples for pattern scenarios

8. Update Documentation:
   - Create new document: `refactoring_work/design/07_communication_patterns/pattern_engine_api.md`
   - Update `refactoring_work/design/07_communication_patterns/design_principles.md` to reference the new API
   - Update `refactoring_work/design/07_communication_patterns/README.md` to include API documentation
   - Ensure `refactoring_work/design/01_architecture/components_summary.md` reflects the new interface

Cross-references to be checked/updated:
- `refactoring_work/design/07_communication_patterns/design_principles.md`
- `refactoring_work/design/01_architecture/internal_message_format_standard.md`
- `refactoring_work/design/07_communication_patterns/README.md`
- `refactoring_work/design/01_architecture/components_summary.md`
- `refactoring_work/archive/phase_1/TASK_define_iprotocol_adapter_interface.md` (for integration patterns)
- `refactoring_work/design/completed/TASK_define_agent_framework_message_handling_api.md` (for SIMF usage)

Verification:
- Are all methods in IPatternEngine explicitly defined with typed parameters and return values?
- Do the Pydantic models cover all necessary pattern configuration and execution information?
- Is SIMF integration clearly specified with examples for major pattern types?
- Are error handling and edge cases properly documented?
- Is the interface consistent with existing completed interfaces (IProtocolAdapter, IMessageHandler)?
- Can different pattern types (request-response, publish-subscribe, streaming, delegation) all reasonably use this interface?
- Are protocol-specific adaptations properly abstracted while maintaining flexibility?
- Does the API support both stateless and stateful pattern execution?

Progress Notes:
- **Task Status**: IN_PROGRESS
- Sub-task 1: Review Existing Documentation - **COMPLETED**
  - Reviewed `refactoring_work/design/07_communication_patterns/` - confirmed pattern architecture with registry, factory, and base classes
  - Analyzed `refactoring_work/design/01_architecture/internal_message_format_standard.md` - SIMF provides comprehensive payload types for all patterns 
  - Examined completed TASK files (IProtocolAdapter, message handling) - established interface patterns using Pydantic models, async methods, and detailed docstrings
  - Reviewed existing pattern definitions - request-response, publish-subscribe, streaming, delegation patterns well defined
  - Confirmed SIMF supports pattern metadata preservation and cross-protocol execution

- Sub-task 2: Define Core IPatternEngine Interface - **COMPLETED**  
  - Created comprehensive IPatternEngine ABC with all required methods: register_pattern, execute_pattern, create_pattern_instance, get_available_patterns, supports_protocol, validate_pattern_config
  - All methods have explicit type hints using Pydantic models and detailed docstrings
  - Included IPatternInstance interface for stateful patterns with start, stop, process_message, get_status, update_config methods
  - Followed established patterns from completed TASK files for consistency

- Sub-task 3: Define Supporting Pydantic Models - **COMPLETED**
  - Created PatternDefinition(BaseModel) with name, version, description, pattern_type, supported_protocols, options_schema, implementation_class fields
  - Created PatternConfig(BaseModel) with pattern_name, options, timeout, retry_policy, protocol_adaptations, observability fields
  - Created PatternResult(BaseModel) with success, result_data, messages, execution_time, error tracking, metadata
  - Created supporting models: RetryPolicy, ObservabilityConfig, ValidationResult, PatternInfo, PatternCapabilities, PatternInstanceStatus
  - Defined comprehensive error hierarchy: PatternError, PatternNotFoundError, PatternConfigError, PatternExecutionError, PatternRegistrationError, UnsupportedProtocolError
  - Defined PatternType enum for consistent pattern categorization

- Sub-task 4: Define IPatternInstance Interface - **COMPLETED** 
  - Created comprehensive IPatternInstance interface for stateful patterns
  - Included lifecycle methods (start, stop) and message processing (process_message)
  - Added configuration updates (update_config) and status monitoring (get_status, get_metrics)
  - Supports long-running patterns like streaming, delegation, and collaborative workflows

- Sub-task 5: Specify SIMF Integration Requirements - **COMPLETED**
  - Detailed pattern metadata preservation in SIMF headers with communication_pattern, pattern_version, pattern_instance_id fields
  - Specified cross-protocol pattern execution mechanisms through SIMF as common format
  - Documented protocol adaptation requirements showing how patterns map to different protocols
  - Defined pattern-specific SIMF payload type handling and metadata preservation requirements

- Sub-task 6: Define Pattern Lifecycle Management - **COMPLETED**
  - Specified pattern registration and discovery procedures through register_pattern, unregister_pattern, get_available_patterns methods
  - Defined pattern versioning with semantic versioning support in PatternDefinition model
  - Detailed pattern instance creation and cleanup with create_pattern_instance, shutdown_pattern_instance, list_pattern_instances
  - Specified pattern dependency management through PatternCapabilities dependencies field
  - Included pattern extension and customization through PatternDefinition and implementation_class fields

- Sub-task 7: Create Pattern Implementation Examples - **COMPLETED**
  - Provided conceptual examples for pattern registration, execution, and discovery in the API specification
  - Demonstrated basic pattern execution with request-response pattern showing SIMF integration
  - Included stateful pattern instance example with streaming pattern showing lifecycle management
  - Added pattern discovery and validation example showing configuration checking
  - Showed cross-protocol pattern execution example with different protocols
  - Included error handling and edge case examples for pattern scenarios

- Sub-task 8: Update Documentation - **COMPLETED**
  - Created new comprehensive document: `refactoring_work/design/07_communication_patterns/pattern_engine_api.md`
  - Updated `refactoring_work/design/07_communication_patterns/design_principles.md` to reference the new API with dedicated section
  - Updated `refactoring_work/design/07_communication_patterns/README.md` to include API documentation in the documentation structure table
  - All cross-references are consistent and point to the canonical interface definition

**Verification Completed**:
- ✅ All methods in IPatternEngine explicitly defined with typed parameters and return values
- ✅ Pydantic models cover all necessary pattern configuration and execution information (PatternDefinition, PatternConfig, PatternResult, PatternCapabilities, etc.)
- ✅ SIMF integration clearly specified with examples for pattern execution including metadata preservation and cross-protocol support
- ✅ Error handling and edge cases properly documented with comprehensive error hierarchy
- ✅ Interface consistent with existing completed interfaces (follows same patterns as IProtocolAdapter, IMessageHandler)
- ✅ Different pattern types (request-response, publish-subscribe, streaming, delegation) can all reasonably use this interface
- ✅ Protocol-specific adaptations properly abstracted while maintaining flexibility through protocol_adaptations configuration
- ✅ API supports both stateless and stateful pattern execution through execute_pattern and create_pattern_instance methods

**Decision Notes**:
- **Interface Design**: Used Abstract Base Class (ABC) pattern consistent with other OpenMAS interfaces for clear contracts
- **Async-First**: All core methods are async to support non-blocking pattern execution across all protocols
- **SIMF Integration**: Ensured all pattern execution preserves SIMF metadata and enables cross-protocol communication
- **Dual Execution Model**: Provided both stateless execution (execute_pattern) and stateful instances (create_pattern_instance) to support all pattern types
- **Configuration Flexibility**: Used comprehensive PatternConfig model with protocol_adaptations for protocol-specific customization
- **Error Hierarchy**: Created specific error types for different failure modes to enable targeted error handling
- **Capabilities Discovery**: Added pattern discovery and capability checking to enable dynamic pattern usage

**Task Status**: COMPLETE

All deliverables completed and verification criteria satisfied. The Communication Pattern Engine API is ready for immediate implementation. 