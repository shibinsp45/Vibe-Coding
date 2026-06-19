# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.workflow import Workflow

from expense_agent.agent import root_agent


def test_agent_graph_topology() -> None:
    """Verifies that the graph is correctly defined and is an instance of Workflow."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "expense_agent"

    # Check that START node is registered in the edges
    nodes_in_edges = set()
    for edge in root_agent.graph.edges:
        nodes_in_edges.add(edge.from_node.name)
        nodes_in_edges.add(edge.to_node.name)

    assert "__START__" in nodes_in_edges
    assert "extract_expense" in nodes_in_edges
    assert "route_expense" in nodes_in_edges
