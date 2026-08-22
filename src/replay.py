import time
from playwright.sync_api import sync_playwright, Page, Locator
from src.schemas import (
    CapabilityArtifact, ExecutionResult, ExecutionStatus, ActionType, 
    CheckpointType, StepExecutionLog, TargetSelector
)
from src.guardrails import SafetyGuardrail
from src.hitl import EscalationManager

class DeterministicReplayEngine:
    def __init__(self, artifact: CapabilityArtifact):
        self.artifact = artifact

    def _resolve_locator(self, page: Page, target: TargetSelector) -> tuple[Locator, str]:
        # Strategy 1: Accessibility Role & Name (most resilient to markup drift)
        if target.aria_role and target.aria_name:
            loc = page.get_by_role(target.aria_role, name=target.aria_name)
            if loc.count() > 0:
                return loc.first, "aria_role_and_name"

        # Strategy 2: Explicit CSS Selector / ID
        if target.css_selector:
            loc = page.locator(target.css_selector)
            if loc.count() > 0:
                return loc.first, "css_selector"

        # Strategy 3: XPath
        if target.xpath:
            loc = page.locator(f"xpath={target.xpath}")
            if loc.count() > 0:
                return loc.first, "xpath"

        # Strategy 4: Exact Semantic Text Fallback
        if target.text_content:
            loc = page.get_by_text(target.text_content, exact=True)
            if loc.count() > 0:
                return loc.first, "text_content"

        raise LookupError(f"Locator resolution exhausted across all strategies for target: {target}")

    def _evaluate_checkpoint(self, page: Page, checkpoint) -> bool:
        if checkpoint.type == CheckpointType.URL_CONTAINS:
            return checkpoint.expected in page.url
        elif checkpoint.type == CheckpointType.TEXT_PRESENT:
            return checkpoint.expected in page.content()
        elif checkpoint.type == CheckpointType.ELEMENT_VISIBLE and checkpoint.target:
            loc, _ = self._resolve_locator(page, checkpoint.target)
            return loc.is_visible()
        return True

    def replay(self, inputs: dict) -> ExecutionResult:
        SafetyGuardrail.validate_url(self.artifact.target_entry_url)
        extracted_data = {}
        execution_trace = []
        interventions = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.artifact.target_entry_url)

            for step in self.artifact.steps:
                step_start = time.time()
                try:
                    # TIER 1: Check for Known Business Outcomes / Error Banners
                    if page.locator("#error-banner").count() > 0 and page.locator("#error-banner").is_visible():
                        err_text = page.locator("#error-banner").inner_text()
                        if "404" in err_text or "not exist" in err_text.lower():
                            browser.close()
                            return ExecutionResult(
                                status=ExecutionStatus.BUSINESS_OUTCOME,
                                capability_id=self.artifact.capability_id,
                                business_code="MEMBER_NOT_FOUND",
                                error_message=SafetyGuardrail.sanitize_string(err_text),
                                failed_step_id=step.step_id,
                                execution_trace=execution_trace
                            )

                    # Execute Step Action
                    resolved_strategy = "direct"
                    if step.action == ActionType.CLICK:
                        loc, resolved_strategy = self._resolve_locator(page, step.target)
                        loc.click(timeout=step.timeout_ms)

                    elif step.action == ActionType.FILL:
                        val = step.value_template
                        for k, v in inputs.items():
                            val = val.replace(f"{{{{inputs.{k}}}}}", str(v))
                        loc, resolved_strategy = self._resolve_locator(page, step.target)
                        loc.fill(val, timeout=step.timeout_ms)

                    elif step.action == ActionType.EXTRACT:
                        # Re-verify business error banner before extraction attempt
                        if page.locator("#error-banner").count() > 0 and page.locator("#error-banner").is_visible():
                            err_text = page.locator("#error-banner").inner_text()
                            browser.close()
                            return ExecutionResult(
                                status=ExecutionStatus.BUSINESS_OUTCOME,
                                capability_id=self.artifact.capability_id,
                                business_code="MEMBER_NOT_FOUND",
                                error_message=SafetyGuardrail.sanitize_string(err_text),
                                execution_trace=execution_trace
                            )
                        loc, resolved_strategy = self._resolve_locator(page, step.target)
                        raw_text = loc.inner_text().strip()
                        extracted_data[step.output_key] = raw_text

                    # Verify Step Checkpoint
                    if step.checkpoint:
                        if not self._evaluate_checkpoint(page, step.checkpoint):
                            raise AssertionError(f"Step checkpoint '{step.checkpoint.type}' validation failed.")

                    execution_trace.append(StepExecutionLog(
                        step_id=step.step_id,
                        action=step.action.value,
                        status="SUCCESS",
                        duration_ms=round((time.time() - step_start) * 1000, 2),
                        resolved_by=resolved_strategy
                    ))

                except Exception as e:
                    # TIER 3: Hard Failure & Human Escalation Seam
                    execution_trace.append(StepExecutionLog(
                        step_id=step.step_id,
                        action=step.action.value,
                        status="FAILED",
                        duration_ms=round((time.time() - step_start) * 1000, 2),
                        details=str(e)
                    ))
                    
                    intervened = EscalationManager.request_human_intervention(
                        page=page,
                        reason=str(e),
                        context={"capability_id": self.artifact.capability_id, "step_id": step.step_id}
                    )
                    if intervened:
                        interventions.append(step.step_id)
                        continue
                    else:
                        browser.close()
                        return ExecutionResult(
                            status=ExecutionStatus.FAILED,
                            capability_id=self.artifact.capability_id,
                            error_message=str(e),
                            failed_step_id=step.step_id,
                            execution_trace=execution_trace,
                            interventions=interventions
                        )

            browser.close()
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                capability_id=self.artifact.capability_id,
                data=SafetyGuardrail.sanitize_payload(extracted_data),
                execution_trace=execution_trace,
                interventions=interventions
            )

if __name__ == "__main__":
    with open("evidence/capability_artifact.json") as f:
        artifact_data = CapabilityArtifact.model_validate_json(f.read())
    
    engine = DeterministicReplayEngine(artifact_data)
    
    print("\n--- REPLAY TEST 1: Valid Member (Happy Path) ---")
    res1 = engine.replay({"member_id": "12345"})
    print(res1.model_dump_json(indent=2))

    print("\n--- REPLAY TEST 2: Invalid Member (Expected Business Outcome) ---")
    res2 = engine.replay({"member_id": "88888"})
    print(res2.model_dump_json(indent=2))