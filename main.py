# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import os

from agent import BrowserAgent
from computers import BrowserbaseComputer, PlaywrightComputer


PLAYWRIGHT_SCREEN_SIZE = (1440, 900)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the browser agent with a query.")
    parser.add_argument(
        "--query",
        type=str,
        default="""Subject: QA Test
Plan: Comprehensive validation of interactive webpage elements

Objective: Verify that every interactive control renders correctly, responds to all supported input methods (mouse and touch emulation), and reflects the appropriate visual feedback across major browsers and responsive breakpoints.

Checklist:
	1.	Catalog all interactive elements (navigation menus, buttons, links, forms, inputs, sliders, toggles, accordions, carousels, media controls, dialogs/modals, tooltips, drag-and-drop regions, and custom widgets).
	2.	For each element:
	•	Confirm default states, hover/focus/active/disabled styles, loading indicators, and error/success messaging.
	•	Validate accessible name/role semantics (labels, ARIA where applicable) and that assistive cues are present where needed.
	•	Exercise edge cases: empty submissions, invalid inputs, repeated clicks, rapid interactions, and concurrent actions.
	•	Verify state persistence, undo/cancel options, and interaction with dependent elements.
	3.	Assess form behaviors: client/server validation, autofill, copy/paste, masking, character limits, file uploads, and multi-step flows.
	4.	Evaluate dynamic content updates (live regions, auto-refresh, animations) for consistency and accessibility.
	5.	Test responsiveness at key breakpoints (mobile, tablet, desktop) and ensure interactions remain usable without layout shifts or overlaps.
	6.	Capture cross-browser parity notes for Chrome, Firefox, Safari, and Edge; flag vendor-specific quirks.
	7.	Document screenshots or recordings of failures, console/network errors, and reproduction steps for any defects.

Deliverable: Provide a prioritized defect list with reproduction steps, environment details, impacted elements, and recommended fixes.
If all elements work properly, output “Result: PASS” in the end. Otherwise, output “Result: FAIL” in the end.""",
        help="The query for the browser agent to execute.",
    )

    parser.add_argument(
        "--env",
        type=str,
        choices=("playwright", "browserbase"),
        default="playwright",
        help="The computer use environment to use.",
    )
    parser.add_argument(
        "--initial_url",
        type=str,
        default="https://temp-dupe-all-index.s3.us-west-1.amazonaws.com/interactive_webpages/v4/55_newtons-laws-of-motion-in-physics.html",
        help="The inital URL loaded for the computer.",
    )
    parser.add_argument(
        "--highlight_mouse",
        action="store_true",
        default=False,
        help="If possible, highlight the location of the mouse.",
    )
    parser.add_argument(
        "--model",
        default='gemini-2.5-computer-use-preview-10-2025',
        help="Set which main model to use.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="result.txt",
        help="Optional path to write the agent's final response to a text file.",
    )
    args = parser.parse_args()

    if args.env == "playwright":
        env = PlaywrightComputer(
            screen_size=PLAYWRIGHT_SCREEN_SIZE,
            initial_url=args.initial_url,
            highlight_mouse=args.highlight_mouse,
        )
    elif args.env == "browserbase":
        env = BrowserbaseComputer(
            screen_size=PLAYWRIGHT_SCREEN_SIZE,
            initial_url=args.initial_url
        )
    else:
        raise ValueError("Unknown environment: ", args.env)

    with env as browser_computer:
        agent = BrowserAgent(
            browser_computer=browser_computer,
            query=args.query,
            model_name=args.model,
        )
        agent.agent_loop()

        if args.output_file and agent.final_reasoning:
            output_path = os.path.expanduser(args.output_file)
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(agent.final_reasoning)
    return 0


if __name__ == "__main__":
    main()
