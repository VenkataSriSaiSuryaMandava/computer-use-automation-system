from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    EXTRACT = "extract"
    WAIT_FOR = "wait_for"

class CheckpointType(str, Enum):
    URL_CONTAINS = "url_contains"
    ELEMENT_VISIBLE = "element_visible"
    TEXT_PRESENT = "text_present"

class TargetSelector(BaseModel):
    aria_role: Optional[str] = None
    aria_name: Optional[str] = None
    text_content: Optional[str] = None
    css_selector: Optional[str] = None
    xpath: Optional[str] = None
    description: Optional[str] = None

class StepCheckpoint(BaseModel):
    type: CheckpointType
    expected: str
    target: Optional[TargetSelector] = None

class CapabilityStep(BaseModel):
    step_id: str
    action: ActionType
    description: str
    target: Optional[TargetSelector] = None
    value_template: Optional[str] = None
    output_key: Optional[str] = None
    reversible: bool = True
    checkpoint: Optional[StepCheckpoint] = None
    timeout_ms: int = 5000

class CapabilityArtifact(BaseModel):
    capability_id: str
    version: str = "1.0.0"
    description: str
    target_entry_url: str
    inputs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    outputs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    steps: List[CapabilityStep] = Field(default_factory=list)

class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    BUSINESS_OUTCOME = "BUSINESS_OUTCOME"
    RECOVERABLE_RETRY = "RECOVERABLE_RETRY"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"

class StepExecutionLog(BaseModel):
    step_id: str
    action: str
    status: str
    duration_ms: float
    resolved_by: Optional[str] = None
    details: Optional[str] = None

class ExecutionResult(BaseModel):
    status: ExecutionStatus
    capability_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    business_code: Optional[str] = None
    error_message: Optional[str] = None
    failed_step_id: Optional[str] = None
    execution_trace: List[StepExecutionLog] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)