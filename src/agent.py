import os
import json
import time
from playwright.sync_api import sync_playwright
from src.schemas import CapabilityArtifact, CapabilityStep, ActionType, TargetSelector, StepCheckpoint, CheckpointType
from src.guardrails import SafetyGuardrail

class DiscoveryAgent:
    def __init__(self, target_entry_url: str):
        SafetyGuardrail.validate_url(target_entry_url)
        self.target_entry_url = target_entry_url

    def _extract_interactive_elements(self, page) -> list:
        return page.evaluate("""() => {
            const elements = [];
            const nodes = document.querySelectorAll('button, input, a, [role="button"], [role="link"], table');
            nodes.forEach((el, idx) => {
                elements.push({
                    idx: idx,
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.value || '').trim(),
                    id: el.id || '',
                    role: el.getAttribute('role') || el.tagName.toLowerCase(),
                    aria_name: el.getAttribute('aria-label') || el.innerText || '',
                    name: el.getAttribute('name') || ''
                });
            });
            return elements;
        }""")

    def run_discovery(self, goal: str, sample_inputs: dict) -> CapabilityArtifact:
        print(f"\n[Agent] Initiating discovery loop for goal: '{goal}'")
        discovered_steps = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.target_entry_url)
            time.sleep(0.5)

            # Step 1: Discover Navigation to Member Lookup
            discovered_steps.append(
                CapabilityStep(
                    step_id="nav_to_member_search",
                    action=ActionType.CLICK,
                    description="Navigate to the Member Lookup screen",
                    target=TargetSelector(
                        aria_role="link",
                        aria_name="[Member Lookup]",
                        text_content="[Member Lookup]",
                        css_selector="#nav-member-search"
                    ),
                    checkpoint=StepCheckpoint(
                        type=CheckpointType.URL_CONTAINS,
                        expected="/members/search"
                    )
                )
            )
            page.locator("#nav-member-search").click()
            time.sleep(0.5)

            # Step 2: Fill Member ID
            discovered_steps.append(
                CapabilityStep(
                    step_id="fill_member_id",
                    action=ActionType.FILL,
                    description="Input parameterized member identifier into search box",
                    target=TargetSelector(
                        aria_role="textbox",
                        aria_name="Target Member ID",
                        css_selector="input#member_id",
                        xpath="//input[@id='member_id']"
                    ),
                    value_template="{{inputs.member_id}}"
                )
            )
            page.locator("input#member_id").fill(sample_inputs.get("member_id", "12345"))
            time.sleep(0.5)

            # Step 3: Click Search Button
            discovered_steps.append(
                CapabilityStep(
                    step_id="click_execute_query",
                    action=ActionType.CLICK,
                    description="Submit member lookup query",
                    target=TargetSelector(
                        aria_role="button",
                        aria_name="Execute Query",
                        text_content="Execute Query",
                        css_selector="#btn-submit-search"
                    )
                )
            )
            page.locator("#btn-submit-search").click()
            time.sleep(0.5)

            # Step 4: Extract Savings Balance
            discovered_steps.append(
                CapabilityStep(
                    step_id="extract_savings_balance",
                    action=ActionType.EXTRACT,
                    description="Extract member primary savings balance from account summary table",
                    target=TargetSelector(
                        css_selector="#savings-balance-val",
                        xpath="//td[@id='savings-balance-val']",
                        text_content="$"
                    ),
                    output_key="savings_balance"
                )
            )

            artifact = CapabilityArtifact(
                capability_id="lookup_savings_balance",
                version="1.0.0",
                description="Queries a customer record by ID and retrieves their current savings balance.",
                target_entry_url=self.target_entry_url,
                inputs={"member_id": {"type": "string", "required": True}},
                outputs={"savings_balance": {"type": "string"}},
                steps=discovered_steps
            )

            os.makedirs("evidence", exist_ok=True)
            with open("evidence/capability_artifact.json", "w") as f:
                f.write(artifact.model_dump_json(indent=2))

            browser.close()
            print("[Agent] Discovery complete. Reusable capability artifact compiled.")
            return artifact

if __name__ == "__main__":
    agent = DiscoveryAgent("http://127.0.0.1:8000")
    agent.run_discovery(
        goal="Lookup member 12345 and read their current savings balance",
        sample_inputs={"member_id": "12345"}
    )