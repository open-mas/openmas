# Advanced Communication Pattern Integration (Part 2)

This document continues the demonstration of advanced usage of OpenMAS communication patterns, focusing on how patterns can be combined and integrated to solve complex multi-agent scenarios.

## 2. Collaborative Decision-Making System

This example demonstrates how multiple agents can collaborate on complex decisions using a combination of Publish-Subscribe, Request-Response, and Event-Based patterns.

![Collaborative Decision-Making](../assets/collaborative_decision_making.png)

### Key Pattern Integration:
- **Publish-Subscribe** for broadcasting decision topics and collecting votes
- **Request-Response** for obtaining detailed information and expertise
- **Event-Based** for notifications of decision status changes

### Example Implementation:

```python
class DecisionMakingCoordinator:
    """Agent responsible for coordinating collaborative decision-making processes."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.pubsub_pattern = None
        self.request_response_pattern = None
        self.event_pattern = None

        # Decision state
        self.active_decisions = {}
        self.voting_results = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.pubsub_pattern = await pattern_registry.get_pattern(
            "publish_subscribe",
            self.config.get("patterns", {}).get("publish_subscribe")
        )

        self.request_response_pattern = await pattern_registry.get_pattern(
            "request_response",
            self.config.get("patterns", {}).get("request_response")
        )

        self.event_pattern = await pattern_registry.get_pattern(
            "event_based",
            self.config.get("patterns", {}).get("event_based")
        )

        # Create topics for decision-making
        await self.pubsub_pattern.create_topic(
            topic_id="decision_proposals",
            metadata={
                "description": "New decision proposals requiring collaboration",
                "schema": "decision_proposal_schema"
            }
        )

        await self.pubsub_pattern.create_topic(
            topic_id="decision_votes",
            metadata={
                "description": "Votes on active decision proposals",
                "schema": "decision_vote_schema"
            }
        )

        # Subscribe to decision votes
        await self.pubsub_pattern.subscribe(
            topic_id="decision_votes",
            callback=self.handle_vote
        )

        # Subscribe to decision events
        await self.event_pattern.subscribe(
            event_type="decision_status_change",
            callback=self.handle_status_change
        )

    async def propose_decision(self, decision_type, context_data, required_expertise=None, deadline=None):
        """Propose a new collaborative decision."""
        decision_id = str(uuid.uuid4())

        # Initialize decision state
        self.active_decisions[decision_id] = {
            "id": decision_id,
            "type": decision_type,
            "status": "proposed",
            "context": context_data,
            "required_expertise": required_expertise or [],
            "proposed_at": datetime.now().isoformat(),
            "deadline": deadline,
            "participants": set(),
            "votes": {},
            "expert_opinions": {},
            "final_decision": None
        }

        # Initialize voting results
        self.voting_results[decision_id] = {
            "votes_count": 0,
            "votes_breakdown": {},
            "quorum_reached": False
        }

        # Step 1: Use Event-Based pattern to notify about new decision
        await self.event_pattern.emit_event(
            event_type="decision_status_change",
            content={
                "decision_id": decision_id,
                "new_status": "proposed",
                "timestamp": datetime.now().isoformat(),
                "initiator_id": self.agent_id
            }
        )

        # Step 2: Use Publish-Subscribe to broadcast the decision proposal
        await self.pubsub_pattern.publish(
            topic_id="decision_proposals",
            content={
                "decision_id": decision_id,
                "type": decision_type,
                "context_summary": self.summarize_context(context_data),
                "required_expertise": required_expertise,
                "deadline": deadline,
                "initiator_id": self.agent_id
            }
        )

        # Step 3: Request expert opinions if specific expertise is required
        if required_expertise:
            for expertise in required_expertise:
                # Find agents with the required expertise
                agents_with_expertise = await self.find_agents_with_expertise(expertise)

                for expert_agent_id in agents_with_expertise:
                    # Request expert opinion using Request-Response pattern
                    response = await self.request_response_pattern.send_request(
                        target_agent_id=expert_agent_id,
                        request_type="expert_opinion",
                        content={
                            "decision_id": decision_id,
                            "decision_type": decision_type,
                            "context_data": context_data,
                            "requested_expertise": expertise
                        }
                    )

                    if response and "opinion" in response:
                        # Store the expert opinion
                        self.active_decisions[decision_id]["expert_opinions"][expert_agent_id] = {
                            "expertise": expertise,
                            "opinion": response["opinion"],
                            "confidence": response.get("confidence", 1.0),
                            "reasoning": response.get("reasoning", "")
                        }

        return {
            "decision_id": decision_id,
            "status": "proposed",
            "message": "Decision proposal has been broadcast"
        }

    async def handle_vote(self, message):
        """Handle incoming votes on decision proposals."""
        content = message.get("content", {})
        decision_id = content.get("decision_id")
        voter_id = content.get("voter_id")
        vote = content.get("vote")

        if not (decision_id and voter_id and vote):
            # Invalid vote message
            return

        # Check if decision exists and is still open
        if decision_id not in self.active_decisions:
            # Decision doesn't exist
            return

        decision = self.active_decisions[decision_id]
        if decision["status"] not in ["proposed", "deliberating"]:
            # Decision is no longer accepting votes
            return

        # Record the vote
        decision["votes"][voter_id] = {
            "vote": vote,
            "timestamp": datetime.now().isoformat(),
            "rationale": content.get("rationale", "")
        }

        # Add to participants set
        decision["participants"].add(voter_id)

        # Update voting results
        self.voting_results[decision_id]["votes_count"] += 1

        if vote not in self.voting_results[decision_id]["votes_breakdown"]:
            self.voting_results[decision_id]["votes_breakdown"][vote] = 0
        self.voting_results[decision_id]["votes_breakdown"][vote] += 1

        # Check if we've reached quorum
        quorum_size = self.config.get("decision_making", {}).get("quorum_size", 3)
        if len(decision["participants"]) >= quorum_size:
            self.voting_results[decision_id]["quorum_reached"] = True

            # If this is the first time reaching quorum, update status to deliberating
            if decision["status"] == "proposed":
                decision["status"] = "deliberating"

                # Emit event for status change
                await self.event_pattern.emit_event(
                    event_type="decision_status_change",
                    content={
                        "decision_id": decision_id,
                        "new_status": "deliberating",
                        "timestamp": datetime.now().isoformat(),
                        "votes_count": self.voting_results[decision_id]["votes_count"],
                        "votes_breakdown": self.voting_results[decision_id]["votes_breakdown"]
                    }
                )

                # Publish deliberation phase notification
                await self.pubsub_pattern.publish(
                    topic_id="decision_proposals",
                    content={
                        "decision_id": decision_id,
                        "status_update": "deliberating",
                        "current_votes": self.voting_results[decision_id]["votes_breakdown"],
                        "expert_opinions_available": bool(decision["expert_opinions"])
                    }
                )

        # Check if deadline has been reached or all expected participants have voted
        should_finalize = False

        if decision.get("deadline"):
            deadline = datetime.fromisoformat(decision["deadline"])
            if datetime.now() > deadline:
                should_finalize = True

        # If all expected participants have voted
        expected_participants = self.config.get("decision_making", {}).get("expected_participants", [])
        if expected_participants and set(expected_participants).issubset(decision["participants"]):
            should_finalize = True

        # Check if we have a clear majority
        votes_breakdown = self.voting_results[decision_id]["votes_breakdown"]
        if votes_breakdown:
            top_vote = max(votes_breakdown.items(), key=lambda x: x[1])
            total_votes = sum(votes_breakdown.values())

            # If top vote has more than 50% of all votes
            if top_vote[1] > total_votes / 2:
                should_finalize = True

        if should_finalize and decision["status"] != "finalized":
            await self.finalize_decision(decision_id)

    async def finalize_decision(self, decision_id):
        """Finalize a decision based on votes and expert opinions."""
        if decision_id not in self.active_decisions:
            return

        decision = self.active_decisions[decision_id]

        # Calculate the final decision
        votes_breakdown = self.voting_results[decision_id]["votes_breakdown"]
        if not votes_breakdown:
            final_outcome = "no_consensus"
            winning_option = None
        else:
            # Find option with most votes
            winning_option = max(votes_breakdown.items(), key=lambda x: x[1])[0]

            # Check if it's a tie
            top_votes = max(votes_breakdown.values())
            if list(votes_breakdown.values()).count(top_votes) > 1:
                final_outcome = "tie"
            else:
                final_outcome = "majority_vote"

        # Consider expert opinions
        expert_opinions = decision["expert_opinions"]
        expert_consensus = None

        if expert_opinions:
            # Group opinions by their recommendations
            opinion_groups = {}
            for agent_id, opinion_data in expert_opinions.items():
                opinion_value = opinion_data["opinion"]
                if opinion_value not in opinion_groups:
                    opinion_groups[opinion_value] = []
                opinion_groups[opinion_value].append((agent_id, opinion_data["confidence"]))

            if opinion_groups:
                # Find the expert consensus (weighted by confidence)
                expert_weights = {}
                for opinion, agents in opinion_groups.items():
                    expert_weights[opinion] = sum(confidence for _, confidence in agents)

                expert_consensus = max(expert_weights.items(), key=lambda x: x[1])[0]

        # Determine the final decision (combine votes and expert opinions)
        if final_outcome == "no_consensus" and expert_consensus is not None:
            # Use expert opinion if no clear consensus from votes
            final_decision = expert_consensus
            rationale = "Decision based on expert opinions due to lack of voting consensus"
        elif final_outcome == "tie" and expert_consensus is not None:
            # Use expert opinion to break ties
            final_decision = expert_consensus
            rationale = "Decision based on expert opinions to break voting tie"
        else:
            # Go with the majority vote
            final_decision = winning_option
            rationale = f"Decision based on majority vote ({final_outcome})"

        # Update decision status
        decision["status"] = "finalized"
        decision["final_decision"] = {
            "outcome": final_decision,
            "rationale": rationale,
            "voting_summary": {
                "total_votes": self.voting_results[decision_id]["votes_count"],
                "breakdown": self.voting_results[decision_id]["votes_breakdown"]
            },
            "expert_input": bool(expert_opinions),
            "finalized_at": datetime.now().isoformat()
        }

        # Emit event for decision finalization
        await self.event_pattern.emit_event(
            event_type="decision_status_change",
            content={
                "decision_id": decision_id,
                "new_status": "finalized",
                "final_decision": final_decision,
                "rationale": rationale,
                "timestamp": datetime.now().isoformat()
            }
        )

        # Publish final decision
        await self.pubsub_pattern.publish(
            topic_id="decision_proposals",
            content={
                "decision_id": decision_id,
                "status_update": "finalized",
                "final_decision": final_decision,
                "rationale": rationale,
                "voting_summary": {
                    "total_votes": self.voting_results[decision_id]["votes_count"],
                    "breakdown": self.voting_results[decision_id]["votes_breakdown"]
                }
            }
        )

    async def handle_status_change(self, message):
        """Handle decision status change events."""
        content = message.get("content", {})
        decision_id = content.get("decision_id")
        new_status = content.get("new_status")

        if not (decision_id and new_status):
            return

        # If this is our own event, ignore it
        if content.get("initiator_id") == self.agent_id:
            return

        # Update local state if we have this decision
        if decision_id in self.active_decisions:
            self.active_decisions[decision_id]["status"] = new_status

    async def find_agents_with_expertise(self, expertise):
        """Find agents with specific expertise using the agent directory."""
        # This would integrate with the agent directory service
        # For this example, we'll mock a simple lookup
        expertise_directory = {
            "risk_assessment": ["risk_analyst_1", "risk_analyst_2"],
            "market_analysis": ["market_expert_1", "market_expert_2"],
            "financial_modeling": ["financial_expert"],
            "regulatory_compliance": ["compliance_officer"],
            "technical_feasibility": ["tech_expert_1", "tech_expert_2", "tech_expert_3"]
        }

        return expertise_directory.get(expertise, [])

    def summarize_context(self, context_data):
        """Create a summary of the context data for decision proposals."""
        # In a real implementation, this might use a knowledge reasoning module
        # For this example, we'll return a simple string summary
        return f"Decision context with {len(context_data)} data points"


class ExpertAdvisor:
    """Agent specialized in providing expert opinions for collaborative decisions."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config
        self.areas_of_expertise = config.get("expertise", [])

        # Initialize patterns
        self.request_response_pattern = None
        self.pubsub_pattern = None

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.request_response_pattern = await pattern_registry.get_pattern(
            "request_response",
            self.config.get("patterns", {}).get("request_response")
        )

        self.pubsub_pattern = await pattern_registry.get_pattern(
            "publish_subscribe",
            self.config.get("patterns", {}).get("publish_subscribe")
        )

        # Subscribe to decision proposals
        await self.pubsub_pattern.subscribe(
            topic_id="decision_proposals",
            callback=self.process_decision_proposal
        )

        # Register request handlers
        await self.request_response_pattern.register_handler(
            request_type="expert_opinion",
            handler=self.provide_expert_opinion
        )

    async def process_decision_proposal(self, message):
        """Process decision proposals from the publish-subscribe system."""
        content = message.get("content", {})

        # Check if this is a new proposal
        if "decision_id" in content and "required_expertise" in content:
            required_expertise = content["required_expertise"]

            # Check if we have any of the required expertise
            matching_expertise = set(required_expertise).intersection(set(self.areas_of_expertise))

            if matching_expertise:
                # We have relevant expertise, should we vote proactively?
                if self.config.get("proactive_voting", False):
                    # Request full context to form an opinion
                    decision_id = content["decision_id"]
                    initiator_id = content["initiator_id"]

                    # Get the full context using Request-Response
                    full_context = await self.request_response_pattern.send_request(
                        target_agent_id=initiator_id,
                        request_type="decision_context",
                        content={
                            "decision_id": decision_id,
                            "requesting_agent_id": self.agent_id,
                            "expertise_areas": list(matching_expertise)
                        }
                    )

                    if full_context and "context_data" in full_context:
                        # Form an opinion based on our expertise
                        opinion = await self.form_expert_opinion(
                            decision_id,
                            content["type"],
                            full_context["context_data"],
                            list(matching_expertise)[0]  # Use first matching expertise
                        )

                        # Submit our vote
                        await self.pubsub_pattern.publish(
                            topic_id="decision_votes",
                            content={
                                "decision_id": decision_id,
                                "voter_id": self.agent_id,
                                "vote": opinion["recommendation"],
                                "rationale": opinion["reasoning"],
                                "expertise_used": list(matching_expertise)
                            }
                        )

    async def provide_expert_opinion(self, request):
        """Handle requests for expert opinions."""
        content = request.get("content", {})
        decision_id = content.get("decision_id")
        decision_type = content.get("decision_type")
        context_data = content.get("context_data")
        requested_expertise = content.get("requested_expertise")

        # Verify we have the requested expertise
        if requested_expertise not in self.areas_of_expertise:
            return {
                "error": "Requested expertise not available",
                "available_expertise": self.areas_of_expertise
            }

        # Form an expert opinion
        opinion = await self.form_expert_opinion(
            decision_id,
            decision_type,
            context_data,
            requested_expertise
        )

        return opinion

    async def form_expert_opinion(self, decision_id, decision_type, context_data, expertise_area):
        """Form an expert opinion based on the agent's reasoning capabilities."""
        # In a real implementation, this would use the agent's reasoning module
        # For this example, we'll return a mock opinion

        # This demonstrates the reasoning agnosticism of OpenMAS
        # Different expert agents could use different reasoning approaches:
        # - Rule-based reasoning
        # - BDI (Belief-Desire-Intention)
        # - LLM-based reasoning
        # - Knowledge representation and reasoning

        reasoning_module = self.get_reasoning_module()

        # Analyze the context data using the appropriate reasoning approach
        analysis_result = await reasoning_module.analyze(
            context_data,
            expertise_area,
            decision_type
        )

        return {
            "decision_id": decision_id,
            "opinion": analysis_result.get("recommendation"),
            "confidence": analysis_result.get("confidence", 0.8),
            "reasoning": analysis_result.get("explanation"),
            "expertise": expertise_area
        }

    def get_reasoning_module(self):
        """Get the appropriate reasoning module based on configuration."""
        # This demonstrates the flexibility of using different reasoning approaches
        reasoning_type = self.config.get("reasoning", {}).get("type", "rule_based")

        # Simply return a mock for this example
        return MockReasoningModule(reasoning_type)


class VotingParticipant:
    """Agent that participates in collaborative decisions by voting."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.pubsub_pattern = None
        self.request_response_pattern = None

        # Voting history
        self.voting_history = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.pubsub_pattern = await pattern_registry.get_pattern(
            "publish_subscribe",
            self.config.get("patterns", {}).get("publish_subscribe")
        )

        self.request_response_pattern = await pattern_registry.get_pattern(
            "request_response",
            self.config.get("patterns", {}).get("request_response")
        )

        # Subscribe to decision proposals
        await self.pubsub_pattern.subscribe(
            topic_id="decision_proposals",
            callback=self.handle_decision_proposal
        )

    async def handle_decision_proposal(self, message):
        """Handle incoming decision proposals."""
        content = message.get("content", {})

        # Check if this is a new proposal or status update
        if "status_update" in content:
            # This is a status update
            decision_id = content.get("decision_id")
            status = content.get("status_update")

            if decision_id in self.voting_history:
                self.voting_history[decision_id]["current_status"] = status

                if status == "finalized":
                    # Record the final outcome
                    self.voting_history[decision_id]["final_outcome"] = content.get("final_decision")
                    self.voting_history[decision_id]["outcome_rationale"] = content.get("rationale")
        else:
            # This is a new proposal
            decision_id = content.get("decision_id")
            decision_type = content.get("type")

            # Skip if we've already seen this decision
            if decision_id in self.voting_history:
                return

            # Record the new proposal
            self.voting_history[decision_id] = {
                "decision_id": decision_id,
                "type": decision_type,
                "received_at": datetime.now().isoformat(),
                "current_status": "proposed",
                "vote": None,
                "vote_timestamp": None
            }

            # Determine if we should vote on this proposal
            if self.should_vote_on_proposal(content):
                # Get full context if needed
                initiator_id = content.get("initiator_id")
                context_data = None

                if self.config.get("request_full_context", True):
                    # Request full context using Request-Response
                    response = await self.request_response_pattern.send_request(
                        target_agent_id=initiator_id,
                        request_type="decision_context",
                        content={
                            "decision_id": decision_id,
                            "requesting_agent_id": self.agent_id
                        }
                    )

                    if response and "context_data" in response:
                        context_data = response["context_data"]

                # Form and submit vote
                await self.form_and_submit_vote(decision_id, decision_type, context_data)

    def should_vote_on_proposal(self, proposal):
        """Determine if this agent should vote on a given proposal."""
        # Apply voting policy from config
        voting_policy = self.config.get("voting_policy", "vote_on_all")

        if voting_policy == "vote_on_all":
            return True

        if voting_policy == "vote_on_types":
            # Only vote on specific decision types
            allowed_types = self.config.get("decision_types", [])
            return proposal.get("type") in allowed_types

        if voting_policy == "vote_if_expert":
            # Only vote if we have relevant expertise
            required_expertise = proposal.get("required_expertise", [])
            agent_expertise = self.config.get("expertise", [])
            return bool(set(required_expertise).intersection(set(agent_expertise)))

        return False

    async def form_and_submit_vote(self, decision_id, decision_type, context_data):
        """Form and submit a vote for a decision."""
        # In a real implementation, this would use the agent's reasoning module
        # For this example, we'll return a simple mock vote

        # This demonstrates the reasoning agnosticism of OpenMAS
        reasoning_module = self.get_reasoning_module()

        vote_result = await reasoning_module.decide(
            decision_id,
            decision_type,
            context_data
        )

        # Record our vote
        self.voting_history[decision_id]["vote"] = vote_result.get("vote")
        self.voting_history[decision_id]["vote_timestamp"] = datetime.now().isoformat()
        self.voting_history[decision_id]["vote_rationale"] = vote_result.get("rationale")

        # Submit the vote
        await self.pubsub_pattern.publish(
            topic_id="decision_votes",
            content={
                "decision_id": decision_id,
                "voter_id": self.agent_id,
                "vote": vote_result.get("vote"),
                "rationale": vote_result.get("rationale")
            }
        )

    def get_reasoning_module(self):
        """Get the appropriate reasoning module based on configuration."""
        # This demonstrates the flexibility of using different reasoning approaches
        reasoning_type = self.config.get("reasoning", {}).get("type", "simple")

        # Simply return a mock for this example
        return MockReasoningModule(reasoning_type)


# Mock implementation for the example
class MockReasoningModule:
    """Mock reasoning module for example purposes."""

    def __init__(self, reasoning_type):
        self.reasoning_type = reasoning_type

    async def analyze(self, context_data, expertise_area, decision_type):
        """Mock analysis method."""
        # In a real implementation, this would use the appropriate reasoning approach
        return {
            "recommendation": "approve",  # or reject, modify, etc.
            "confidence": 0.85,
            "explanation": f"Analysis based on {expertise_area} expertise using {self.reasoning_type} reasoning"
        }

    async def decide(self, decision_id, decision_type, context_data):
        """Mock decision method."""
        # In a real implementation, this would use the appropriate reasoning approach
        options = ["approve", "reject", "abstain", "need_more_info"]
        return {
            "vote": random.choice(options),
            "rationale": f"Decision using {self.reasoning_type} reasoning"
        }
```

### Key Points:
- The coordinator agent creates topics for proposals and votes, demonstrating the Publish-Subscribe pattern
- Agents request detailed information using Request-Response when needed
- Status changes are broadcast using the Event-Based pattern
- The system demonstrates OpenMAS's reasoning agnosticism with different agent types using various reasoning approaches
- Communication remains protocol-independent, working identically across different transport layers

## 3. Distributed Monitoring System

This example demonstrates how to implement a distributed monitoring system that combines Streaming and Event-Based patterns for real-time data collection and analysis.

![Distributed Monitoring](../assets/distributed_monitoring.png)

### Key Pattern Integration:
- **Streaming** for continuous transmission of monitoring data
- **Event-Based** for alerts and notifications based on monitoring thresholds

### Example Implementation:

```python
class MonitoringCoordinator:
    """Central coordinator for distributed monitoring system."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.streaming_pattern = None
        self.event_pattern = None

        # Monitoring state
        self.active_streams = {}
        self.monitoring_targets = {}
        self.alert_rules = {}
        self.alert_history = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.streaming_pattern = await pattern_registry.get_pattern(
            "streaming",
            self.config.get("patterns", {}).get("streaming")
        )

        self.event_pattern = await pattern_registry.get_pattern(
            "event_based",
            self.config.get("patterns", {}).get("event_based")
        )

        # Set up event subscriptions
        await self.event_pattern.subscribe(
            event_type="monitor_registration",
            callback=self.handle_monitor_registration
        )

        await self.event_pattern.subscribe(
            event_type="target_registration",
            callback=self.handle_target_registration
        )

        await self.event_pattern.subscribe(
            event_type="alert_rule_update",
            callback=self.handle_alert_rule_update
        )

        # Set up streaming handlers
        self.streaming_pattern.register_stream_processor(
            stream_type="system_metrics",
            processor=self.process_system_metrics
        )

        self.streaming_pattern.register_stream_processor(
            stream_type="application_metrics",
            processor=self.process_application_metrics
        )

        self.streaming_pattern.register_stream_processor(
            stream_type="network_metrics",
            processor=self.process_network_metrics
        )

        # Load alert rules from configuration
        self.alert_rules = self.config.get("alert_rules", {})

    async def handle_monitor_registration(self, event):
        """Handle registration of a new monitoring agent."""
        content = event.get("content", {})
        monitor_id = content.get("monitor_id")
        capabilities = content.get("capabilities", [])
        targets = content.get("targets", [])

        if not monitor_id:
            return

        # Register the monitor
        for target_id in targets:
            if target_id not in self.monitoring_targets:
                self.monitoring_targets[target_id] = {
                    "id": target_id,
                    "monitors": {},
                    "streams": {}
                }

            self.monitoring_targets[target_id]["monitors"][monitor_id] = {
                "capabilities": capabilities,
                "registered_at": datetime.now().isoformat()
            }

        # Acknowledge registration
        await self.event_pattern.emit_event(
            event_type="monitor_registration_ack",
            content={
                "monitor_id": monitor_id,
                "coordinator_id": self.agent_id,
                "accepted_targets": targets,
                "timestamp": datetime.now().isoformat()
            }
        )

    async def handle_target_registration(self, event):
        """Handle registration of a new monitoring target."""
        content = event.get("content", {})
        target_id = content.get("target_id")
        target_type = content.get("target_type")
        metrics = content.get("available_metrics", [])

        if not target_id:
            return

        # Register the target
        if target_id not in self.monitoring_targets:
            self.monitoring_targets[target_id] = {
                "id": target_id,
                "type": target_type,
                "available_metrics": metrics,
                "monitors": {},
                "streams": {},
                "registered_at": datetime.now().isoformat()
            }
        else:
            # Update existing target
            self.monitoring_targets[target_id].update({
                "type": target_type,
                "available_metrics": metrics,
                "updated_at": datetime.now().isoformat()
            })

        # Find suitable monitors for this target
        await self.assign_monitors_to_target(target_id)

    async def handle_alert_rule_update(self, event):
        """Handle updates to alert rules."""
        content = event.get("content", {})
        rule_id = content.get("rule_id")
        rule_definition = content.get("rule_definition")

        if not (rule_id and rule_definition):
            return

        # Update the rule
        self.alert_rules[rule_id] = rule_definition

        # Propagate rule to relevant monitors
        target_ids = rule_definition.get("target_ids", [])
        target_types = rule_definition.get("target_types", [])

        affected_targets = set()

        # Add targets by ID
        for target_id in target_ids:
            if target_id in self.monitoring_targets:
                affected_targets.add(target_id)

        # Add targets by type
        for target_id, target_info in self.monitoring_targets.items():
            if target_info.get("type") in target_types:
                affected_targets.add(target_id)

        # Notify monitors of the new rule
        for target_id in affected_targets:
            target = self.monitoring_targets[target_id]
            for monitor_id in target["monitors"]:
                await self.event_pattern.emit_event(
                    event_type="alert_rule_assignment",
                    content={
                        "rule_id": rule_id,
                        "rule_definition": rule_definition,
                        "target_id": target_id,
                        "monitor_id": monitor_id
                    }
                )

    async def assign_monitors_to_target(self, target_id):
        """Assign suitable monitors to a target based on capabilities."""
        if target_id not in self.monitoring_targets:
            return

        target = self.monitoring_targets[target_id]
        target_metrics = target.get("available_metrics", [])

        # Find monitors with matching capabilities
        assigned_monitors = []

        for monitor_id, monitor_info in self.get_all_monitors().items():
            capabilities = monitor_info.get("capabilities", [])

            # Check if monitor can handle this target's metrics
            if any(metric in capabilities for metric in target_metrics):
                # Assign this monitor to the target
                if monitor_id not in target["monitors"]:
                    target["monitors"][monitor_id] = {
                        "capabilities": capabilities,
                        "assigned_at": datetime.now().isoformat()
                    }

                assigned_monitors.append(monitor_id)

        # Notify assigned monitors
        for monitor_id in assigned_monitors:
            await self.event_pattern.emit_event(
                event_type="monitor_assignment",
                content={
                    "monitor_id": monitor_id,
                    "target_id": target_id,
                    "metrics": target_metrics,
                    "coordinator_id": self.agent_id
                }
            )

        # Set up streams for the target
        await self.setup_target_streams(target_id)

    async def setup_target_streams(self, target_id):
        """Set up streams for monitoring a target."""
        if target_id not in self.monitoring_targets:
            return

        target = self.monitoring_targets[target_id]

        # Group metrics by type
        metric_groups = {
            "system_metrics": [],
            "application_metrics": [],
            "network_metrics": []
        }

        for metric in target.get("available_metrics", []):
            if metric.startswith("system."):
                metric_groups["system_metrics"].append(metric)
            elif metric.startswith("app."):
                metric_groups["application_metrics"].append(metric)
            elif metric.startswith("net."):
                metric_groups["network_metrics"].append(metric)

        # Create streams for each metric group
        for stream_type, metrics in metric_groups.items():
            if not metrics:
                continue

            # Create a stream for this metric group
            stream = await self.streaming_pattern.create_stream(
                stream_type=stream_type,
                metadata={
                    "target_id": target_id,
                    "metrics": metrics,
                    "created_by": self.agent_id
                }
            )

            # Store the stream ID
            if stream_type not in target["streams"]:
                target["streams"][stream_type] = []

            target["streams"][stream_type].append(stream.stream_id)

            # Store in active streams map
            self.active_streams[stream.stream_id] = {
                "type": stream_type,
                "target_id": target_id,
                "metrics": metrics,
                "created_at": datetime.now().isoformat()
            }

            # Notify monitors about the new stream
            for monitor_id in target["monitors"]:
                await self.event_pattern.emit_event(
                    event_type="stream_assignment",
                    content={
                        "stream_id": stream.stream_id,
                        "stream_type": stream_type,
                        "target_id": target_id,
                        "metrics": metrics,
                        "monitor_id": monitor_id
                    }
                )

    async def process_system_metrics(self, stream_id, data):
        """Process incoming system metrics data."""
        if stream_id not in self.active_streams:
            return

        stream_info = self.active_streams[stream_id]
        target_id = stream_info["target_id"]

        # Check alert rules
        await self.check_alert_rules(target_id, "system_metrics", data)

        # Store historical data (in a real implementation)
        # self.metrics_store.store(target_id, "system_metrics", data)

    async def process_application_metrics(self, stream_id, data):
        """Process incoming application metrics data."""
        if stream_id not in self.active_streams:
            return

        stream_info = self.active_streams[stream_id]
        target_id = stream_info["target_id"]

        # Check alert rules
        await self.check_alert_rules(target_id, "application_metrics", data)

    async def process_network_metrics(self, stream_id, data):
        """Process incoming network metrics data."""
        if stream_id not in self.active_streams:
            return

        stream_info = self.active_streams[stream_id]
        target_id = stream_info["target_id"]

        # Check alert rules
        await self.check_alert_rules(target_id, "network_metrics", data)

    async def check_alert_rules(self, target_id, metric_type, data):
        """Check if any alert rules are triggered by the metrics data."""
        # Find rules that apply to this target and metric type
        triggered_alerts = []

        for rule_id, rule in self.alert_rules.items():
            # Check if rule applies to this target
            target_ids = rule.get("target_ids", [])
            target_types = rule.get("target_types", [])
            metric_patterns = rule.get("metric_patterns", [])

            target_matches = (
                target_id in target_ids or
                self.monitoring_targets[target_id].get("type") in target_types
            )

            if not target_matches:
                continue

            # Check if rule applies to these metrics
            rule_conditions = rule.get("conditions", [])
            for condition in rule_conditions:
                metric_name = condition.get("metric")

                # Skip if metric not in this data
                if metric_name not in data:
                    continue

                # Check threshold condition
                threshold = condition.get("threshold")
                comparison = condition.get("comparison", "gt")
                current_value = data[metric_name]

                alert_triggered = False

                if comparison == "gt" and current_value > threshold:
                    alert_triggered = True
                elif comparison == "lt" and current_value < threshold:
                    alert_triggered = True
                elif comparison == "eq" and current_value == threshold:
                    alert_triggered = True
                elif comparison == "ne" and current_value != threshold:
                    alert_triggered = True
                elif comparison == "gte" and current_value >= threshold:
                    alert_triggered = True
                elif comparison == "lte" and current_value <= threshold:
                    alert_triggered = True

                if alert_triggered:
                    triggered_alerts.append({
                        "rule_id": rule_id,
                        "target_id": target_id,
                        "metric_name": metric_name,
                        "current_value": current_value,
                        "threshold": threshold,
                        "comparison": comparison,
                        "severity": rule.get("severity", "info")
                    })

        # Emit alerts for triggered rules
        for alert in triggered_alerts:
            alert_id = str(uuid.uuid4())

            # Store in alert history
            if target_id not in self.alert_history:
                self.alert_history[target_id] = []

            self.alert_history[target_id].append({
                "id": alert_id,
                "timestamp": datetime.now().isoformat(),
                **alert
            })

            # Emit alert event
            await self.event_pattern.emit_event(
                event_type="monitoring_alert",
                content={
                    "alert_id": alert_id,
                    "timestamp": datetime.now().isoformat(),
                    **alert
                }
            )

    def get_all_monitors(self):
        """Get all registered monitors across all targets."""
        all_monitors = {}

        for target_id, target in self.monitoring_targets.items():
            for monitor_id, monitor_info in target.get("monitors", {}).items():
                if monitor_id not in all_monitors:
                    all_monitors[monitor_id] = monitor_info

        return all_monitors


class MonitoringAgent:
    """Agent responsible for collecting metrics from targets."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.streaming_pattern = None
        self.event_pattern = None

        # Monitoring state
        self.assigned_targets = {}
        self.assigned_streams = {}
        self.alert_rules = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.streaming_pattern = await pattern_registry.get_pattern(
            "streaming",
            self.config.get("patterns", {}).get("streaming")
        )

        self.event_pattern = await pattern_registry.get_pattern(
            "event_based",
            self.config.get("patterns", {}).get("event_based")
        )

        # Set up event subscriptions
        await self.event_pattern.subscribe(
            event_type="monitor_assignment",
            callback=self.handle_monitor_assignment
        )

        await self.event_pattern.subscribe(
            event_type="stream_assignment",
            callback=self.handle_stream_assignment
        )

        await self.event_pattern.subscribe(
            event_type="alert_rule_assignment",
            callback=self.handle_alert_rule_assignment
        )

        # Register with coordinator
        await self.register_with_coordinator()

    async def register_with_coordinator(self):
        """Register this monitor with the monitoring coordinator."""
        coordinator_id = self.config.get("coordinator_id")

        if not coordinator_id:
            return

        # Announce our capabilities and targets
        await self.event_pattern.emit_event(
            event_type="monitor_registration",
            content={
                "monitor_id": self.agent_id,
                "capabilities": self.config.get("capabilities", []),
                "targets": self.config.get("target_ids", [])
            }
        )

    async def handle_monitor_assignment(self, event):
        """Handle assignment to monitor a target."""
        content = event.get("content", {})
        target_id = content.get("target_id")

        # Check if this assignment is for us
        if content.get("monitor_id") != self.agent_id:
            return

        # Store assignment
        self.assigned_targets[target_id] = {
            "id": target_id,
            "metrics": content.get("metrics", []),
            "assigned_at": datetime.now().isoformat(),
            "streams": {}
        }

        # Start monitoring if needed
        if self.config.get("auto_start_monitoring", True):
            await self.start_monitoring(target_id)

    async def handle_stream_assignment(self, event):
        """Handle assignment to a monitoring stream."""
        content = event.get("content", {})
        stream_id = content.get("stream_id")
        target_id = content.get("target_id")

        # Check if this assignment is for us
        if content.get("monitor_id") != self.agent_id:
            return

        # Check if we're monitoring this target
        if target_id not in self.assigned_targets:
            return

        # Store stream assignment
        stream_type = content.get("stream_type")

        self.assigned_streams[stream_id] = {
            "id": stream_id,
            "type": stream_type,
            "target_id": target_id,
            "metrics": content.get("metrics", []),
            "assigned_at": datetime.now().isoformat()
        }

        # Update target's streams
        if stream_type not in self.assigned_targets[target_id]["streams"]:
            self.assigned_targets[target_id]["streams"][stream_type] = []

        self.assigned_targets[target_id]["streams"][stream_type].append(stream_id)

    async def handle_alert_rule_assignment(self, event):
        """Handle assignment of an alert rule."""
        content = event.get("content", {})
        rule_id = content.get("rule_id")
        target_id = content.get("target_id")

        # Check if this assignment is for us
        if content.get("monitor_id") != self.agent_id:
            return

        # Store the rule
        self.alert_rules[rule_id] = {
            "id": rule_id,
            "target_id": target_id,
            "definition": content.get("rule_definition", {}),
            "assigned_at": datetime.now().isoformat()
        }

    async def start_monitoring(self, target_id):
        """Start monitoring a target."""
        if target_id not in self.assigned_targets:
            return

        # In a real implementation, this would set up metrics collection
        # For this example, we'll simulate periodic metrics updates

        # Start background task for metrics collection
        asyncio.create_task(self.collect_metrics_task(target_id))

    async def collect_metrics_task(self, target_id):
        """Background task to collect and stream metrics."""
        target = self.assigned_targets[target_id]

        # Collect metrics at the configured interval
        interval = self.config.get("collection_interval_ms", 10000) / 1000.0  # Convert to seconds

        while target_id in self.assigned_targets:
            try:
                # Collect metrics (simulated in this example)
                metrics = await self.collect_target_metrics(target_id)

                # Stream the metrics to appropriate streams
                await self.stream_metrics(target_id, metrics)

            except Exception as e:
                # Log error
                print(f"Error collecting metrics for {target_id}: {str(e)}")

            # Wait for next collection interval
            await asyncio.sleep(interval)

    async def collect_target_metrics(self, target_id):
        """Collect metrics from a target (simulated for this example)."""
        # In a real implementation, this would use appropriate protocols to
        # collect actual metrics from the target system

        # This demonstrates the protocol independence of OpenMAS:
        # The same monitoring code works regardless of whether metrics are
        # collected via HTTP, SNMP, local collectors, etc.

        # For this example, generate simulated metrics
        metrics = {}

        # System metrics
        metrics["system.cpu.usage"] = random.uniform(0, 100)
        metrics["system.memory.used_percent"] = random.uniform(0, 100)
        metrics["system.disk.used_percent"] = random.uniform(0, 95)

        # Application metrics
        metrics["app.requests.count"] = random.randint(1000, 10000)
        metrics["app.requests.latency_ms"] = random.uniform(1, 500)
        metrics["app.errors.count"] = random.randint(0, 100)

        # Network metrics
        metrics["net.bandwidth.mbps"] = random.uniform(1, 1000)
        metrics["net.connections.active"] = random.randint(10, 5000)
        metrics["net.packets.dropped"] = random.randint(0, 100)

        return metrics

    async def stream_metrics(self, target_id, metrics):
        """Stream collected metrics to appropriate streams."""
        if target_id not in self.assigned_targets:
            return

        target = self.assigned_targets[target_id]

        # Group metrics by type
        metric_groups = {
            "system_metrics": {},
            "application_metrics": {},
            "network_metrics": {}
        }

        for metric_name, value in metrics.items():
            if metric_name.startswith("system."):
                metric_groups["system_metrics"][metric_name] = value
            elif metric_name.startswith("app."):
                metric_groups["application_metrics"][metric_name] = value
            elif metric_name.startswith("net."):
                metric_groups["network_metrics"][metric_name] = value

        # Send metrics to appropriate streams
        for stream_type, metric_data in metric_groups.items():
            if not metric_data:
                continue

            # Find streams for this metric type
            if stream_type not in target["streams"]:
                continue

            # Send to all streams of this type
            for stream_id in target["streams"][stream_type]:
                await self.streaming_pattern.send_to_stream(
                    stream_id=stream_id,
                    content={
                        "timestamp": datetime.now().isoformat(),
                        "target_id": target_id,
                        "collector_id": self.agent_id,
                        **metric_data
                    }
                )

        # Check local alert rules if enabled
        if self.config.get("local_alert_checking", True):
            await self.check_alert_rules(target_id, metrics)

    async def check_alert_rules(self, target_id, metrics):
        """Check if any local alert rules are triggered."""
        # Find rules for this target
        triggered_alerts = []

        for rule_id, rule in self.alert_rules.items():
            if rule["target_id"] != target_id:
                continue

            rule_def = rule["definition"]
            conditions = rule_def.get("conditions", [])

            for condition in conditions:
                metric_name = condition.get("metric")

                # Skip if metric not in data
                if metric_name not in metrics:
                    continue

                # Check threshold condition
                threshold = condition.get("threshold")
                comparison = condition.get("comparison", "gt")
                current_value = metrics[metric_name]

                alert_triggered = False

                if comparison == "gt" and current_value > threshold:
                    alert_triggered = True
                elif comparison == "lt" and current_value < threshold:
                    alert_triggered = True
                elif comparison == "eq" and current_value == threshold:
                    alert_triggered = True
                elif comparison == "ne" and current_value != threshold:
                    alert_triggered = True
                elif comparison == "gte" and current_value >= threshold:
                    alert_triggered = True
                elif comparison == "lte" and current_value <= threshold:
                    alert_triggered = True

                if alert_triggered:
                    triggered_alerts.append({
                        "rule_id": rule_id,
                        "target_id": target_id,
                        "metric_name": metric_name,
                        "current_value": current_value,
                        "threshold": threshold,
                        "comparison": comparison,
                        "severity": rule_def.get("severity", "info")
                    })

        # Report triggered alerts via events
        for alert in triggered_alerts:
            alert_id = str(uuid.uuid4())

            await self.event_pattern.emit_event(
                event_type="monitoring_alert",
                content={
                    "alert_id": alert_id,
                    "detector_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    **alert
                }
            )
```

### Key Points:
- The system integrates Streaming for continuous metrics data flow
- Events provide real-time notifications for alerts and state changes
- Demonstrates clear separation between communication patterns and underlying monitoring logic
- Maintains protocol independence, enabling metrics collection via various protocols
- Supports reasoning agnosticism, allowing different agents to use different reasoning approaches for analyzing metrics

## 4. Dynamic Task Allocation System

This example demonstrates a dynamic task allocation system that combines Delegation and Pipeline patterns for flexible and efficient distribution of work across heterogeneous agents.

![Dynamic Task Allocation](../assets/dynamic_task_allocation.png)

### Key Pattern Integration:
- **Delegation** for dynamic task assignment based on agent capabilities
- **Pipeline** for structured multi-stage task processing

### Example Implementation:

```python
class TaskOrchestrator:
    """Orchestrator for dynamic task allocation across agent network."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.delegation_pattern = None
        self.pipeline_pattern = None

        # Task state
        self.active_tasks = {}
        self.agent_capabilities = {}
        self.agent_workloads = {}
        self.pipeline_templates = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.delegation_pattern = await pattern_registry.get_pattern(
            "delegation",
            self.config.get("patterns", {}).get("delegation")
        )

        self.pipeline_pattern = await pattern_registry.get_pattern(
            "pipeline",
            self.config.get("patterns", {}).get("pipeline")
        )

        # Register delegation handlers
        await self.delegation_pattern.register_policy_handler(
            policy_name="capability_matching",
            handler=self.capability_matching_policy
        )

        await self.delegation_pattern.register_policy_handler(
            policy_name="workload_balancing",
            handler=self.workload_balancing_policy
        )

        await self.delegation_pattern.register_policy_handler(
            policy_name="priority_based",
            handler=self.priority_based_policy
        )

        # Load pipeline templates
        self.pipeline_templates = self.config.get("pipeline_templates", {})

    async def register_agent(self, agent_id, capabilities, workload_capacity):
        """Register an agent with its capabilities and workload capacity."""
        self.agent_capabilities[agent_id] = {
            "id": agent_id,
            "capabilities": capabilities,
            "registered_at": datetime.now().isoformat()
        }

        self.agent_workloads[agent_id] = {
            "current_tasks": 0,
            "max_capacity": workload_capacity,
            "last_updated": datetime.now().isoformat()
        }

        return {
            "status": "registered",
            "agent_id": agent_id,
            "registry_id": self.agent_id
        }

    async def update_agent_workload(self, agent_id, current_tasks):
        """Update an agent's current workload."""
        if agent_id not in self.agent_workloads:
            return {"status": "error", "message": "Agent not registered"}

        self.agent_workloads[agent_id].update({
            "current_tasks": current_tasks,
            "last_updated": datetime.now().isoformat()
        })

        return {"status": "updated"}

    async def submit_task(self, task_type, task_data, allocation_policy="auto"):
        """Submit a new task for processing."""
        task_id = str(uuid.uuid4())

        # Determine the appropriate allocation approach based on task type
        if task_type in self.pipeline_templates:
            # This task type has a pipeline template, use pipeline pattern
            return await self.process_via_pipeline(task_id, task_type, task_data)
        else:
            # Use delegation pattern for simple tasks
            return await self.process_via_delegation(task_id, task_type, task_data, allocation_policy)

    async def process_via_delegation(self, task_id, task_type, task_data, allocation_policy):
        """Process a task using the delegation pattern."""
        # Initialize task state
        self.active_tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "status": "delegating",
            "submitted_at": datetime.now().isoformat(),
            "allocation_approach": "delegation",
            "delegation_id": None,
            "assigned_agent": None,
            "completion_time": None,
            "result": None
        }

        # Delegate the task
        delegation_result = await self.delegation_pattern.delegate_task(
            task_type=task_type,
            task_data={
                "task_id": task_id,
                **task_data
            },
            policy=allocation_policy
        )

        # Update task state
        self.active_tasks[task_id]["delegation_id"] = delegation_result.delegation_id
        self.active_tasks[task_id]["status"] = "delegated"

        # Return task ID for tracking
        return {
            "task_id": task_id,
            "status": "delegated",
            "delegation_id": delegation_result.delegation_id
        }

    async def process_via_pipeline(self, task_id, task_type, task_data):
        """Process a task using the pipeline pattern."""
        # Get the pipeline template for this task type
        template = self.pipeline_templates.get(task_type)

        if not template:
            return {
                "status": "error",
                "message": f"No pipeline template found for task type: {task_type}"
            }

        # Initialize task state
        self.active_tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "status": "pipeline_starting",
            "submitted_at": datetime.now().isoformat(),
            "allocation_approach": "pipeline",
            "pipeline_id": None,
            "stages": [],
            "completion_time": None,
            "result": None
        }

        # Start the pipeline
        pipeline_result = await self.pipeline_pattern.start_pipeline(
            pipeline_type=task_type,
            stages=template["stages"],
            input_data=task_data
        )

        # Update task state
        self.active_tasks[task_id]["pipeline_id"] = pipeline_result.pipeline_id
        self.active_tasks[task_id]["status"] = "pipeline_running"
        self.active_tasks[task_id]["stages"] = template["stages"]

        # Return task ID for tracking
        return {
            "task_id": task_id,
            "status": "pipeline_running",
            "pipeline_id": pipeline_result.pipeline_id
        }

    async def get_task_status(self, task_id):
        """Get the current status of a task."""
        if task_id not in self.active_tasks:
            return {"status": "not_found"}

        task = self.active_tasks[task_id]

        # If task is completed, just return its status
        if task["status"] in ["completed", "failed"]:
            return {
                "task_id": task_id,
                "status": task["status"],
                "result": task["result"],
                "completion_time": task["completion_time"]
            }

        # Update status based on allocation approach
        if task["allocation_approach"] == "delegation":
            # Check delegation status
            delegation_id = task["delegation_id"]
            delegation_status = await self.delegation_pattern.get_delegation_status(delegation_id)

            if delegation_status["status"] == "completed":
                # Delegation completed
                task["status"] = "completed"
                task["completion_time"] = datetime.now().isoformat()
                task["result"] = delegation_status["result"]
                task["assigned_agent"] = delegation_status["assigned_agent"]
            elif delegation_status["status"] == "failed":
                # Delegation failed
                task["status"] = "failed"
                task["completion_time"] = datetime.now().isoformat()
                task["error"] = delegation_status.get("error")
            else:
                # Still in progress
                task["status"] = "in_progress"
                task["assigned_agent"] = delegation_status.get("assigned_agent")

        elif task["allocation_approach"] == "pipeline":
            # Check pipeline status
            pipeline_id = task["pipeline_id"]
            pipeline_status = await self.pipeline_pattern.get_pipeline_status(pipeline_id)

            if pipeline_status["status"] == "success":
                # Pipeline completed successfully
                task["status"] = "completed"
                task["completion_time"] = datetime.now().isoformat()
                task["result"] = pipeline_status["output"]
            elif pipeline_status["status"] in ["failed", "aborted"]:
                # Pipeline failed
                task["status"] = "failed"
                task["completion_time"] = datetime.now().isoformat()
                task["error"] = pipeline_status.get("error")
            else:
                # Still in progress
                task["status"] = "pipeline_running"
                task["current_stage"] = pipeline_status.get("current_stage")
                task["progress"] = pipeline_status.get("progress")

        return {
            "task_id": task_id,
            "status": task["status"],
            **{k: v for k, v in task.items() if k not in ["id", "status"]}
        }

    async def capability_matching_policy(self, task_type, task_data):
        """Delegation policy that matches task to agent capabilities."""
        required_capabilities = task_data.get("required_capabilities", [])

        if not required_capabilities:
            # If no specific capabilities required, default to workload balancing
            return await self.workload_balancing_policy(task_type, task_data)

        # Find agents with all required capabilities
        matching_agents = []

        for agent_id, agent_info in self.agent_capabilities.items():
            agent_capabilities = agent_info.get("capabilities", [])

            # Check if agent has all required capabilities
            if all(cap in agent_capabilities for cap in required_capabilities):
                # Check if agent is at capacity
                workload = self.agent_workloads.get(agent_id, {"current_tasks": 0, "max_capacity": 0})

                if workload["current_tasks"] < workload["max_capacity"]:
                    matching_agents.append({
                        "agent_id": agent_id,
                        "workload": workload["current_tasks"] / max(workload["max_capacity"], 1)
                    })

        if not matching_agents:
            # No matching agents available
            return None

        # Sort by lowest workload
        matching_agents.sort(key=lambda x: x["workload"])

        # Return the best match
        return matching_agents[0]["agent_id"]

    async def workload_balancing_policy(self, task_type, task_data):
        """Delegation policy that balances workload across agents."""
        # Find agents that can handle this task type
        capable_agents = []

        for agent_id, agent_info in self.agent_capabilities.items():
            agent_capabilities = agent_info.get("capabilities", [])

            # Check if agent can handle this task type
            if task_type in agent_capabilities or "*" in agent_capabilities:
                workload = self.agent_workloads.get(agent_id, {"current_tasks": 0, "max_capacity": 0})

                if workload["current_tasks"] < workload["max_capacity"]:
                    capable_agents.append({
                        "agent_id": agent_id,
                        "workload": workload["current_tasks"] / max(workload["max_capacity"], 1)
                    })

        if not capable_agents:
            # No agents available
            return None

        # Sort by lowest workload
        capable_agents.sort(key=lambda x: x["workload"])

        # Return the agent with the lowest workload
        return capable_agents[0]["agent_id"]

    async def priority_based_policy(self, task_type, task_data):
        """Delegation policy that prioritizes tasks by importance."""
        priority = task_data.get("priority", 5)  # Default to medium priority (1-10 scale)

        # For high priority tasks (7-10), allocate to least loaded agent that can handle it
        if priority >= 7:
            # Find any agent that can handle it, sorted by lowest workload
            agents = []

            for agent_id, agent_info in self.agent_capabilities.items():
                agent_capabilities = agent_info.get("capabilities", [])

                if task_type in agent_capabilities or "*" in agent_capabilities:
                    workload = self.agent_workloads.get(agent_id, {"current_tasks": 0, "max_capacity": 0})
                    agents.append({
                        "agent_id": agent_id,
                        "workload": workload["current_tasks"] / max(workload["max_capacity"], 1)
                    })

            if agents:
                # Sort by workload
                agents.sort(key=lambda x: x["workload"])
                return agents[0]["agent_id"]

        # For medium priority tasks (4-6), use normal capability matching
        elif priority >= 4:
            return await self.capability_matching_policy(task_type, task_data)

        # For low priority tasks (1-3), use any available agent
        else:
            # Find any agent with capacity remaining
            available_agents = []

            for agent_id, workload in self.agent_workloads.items():
                if workload["current_tasks"] < workload["max_capacity"]:
                    available_agents.append(agent_id)

            if available_agents:
                # Choose randomly to distribute load
                return random.choice(available_agents)

        # No suitable agent found
        return None


class TaskExecutor:
    """Agent responsible for executing delegated tasks."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.delegation_pattern = None
        self.pipeline_pattern = None

        # Task state
        self.capabilities = config.get("capabilities", [])
        self.max_workload = config.get("max_concurrent_tasks", 5)
        self.current_tasks = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.delegation_pattern = await pattern_registry.get_pattern(
            "delegation",
            self.config.get("patterns", {}).get("delegation")
        )

        self.pipeline_pattern = await pattern_registry.get_pattern(
            "pipeline",
            self.config.get("patterns", {}).get("pipeline")
        )

        # Register with orchestrator
        orchestrator_id = self.config.get("orchestrator_id")

        if orchestrator_id:
            # Use request-response to register (could be any other pattern too)
            request_response = await pattern_registry.get_pattern(
                "request_response",
                self.config.get("patterns", {}).get("request_response")
            )

            await request_response.send_request(
                target_agent_id=orchestrator_id,
                request_type="register_agent",
                content={
                    "agent_id": self.agent_id,
                    "capabilities": self.capabilities,
                    "workload_capacity": self.max_workload
                }
            )

        # Register as a task handler for delegation pattern
        for capability in self.capabilities:
            await self.delegation_pattern.register_task_handler(
                task_type=capability,
                handler=self.handle_delegated_task
            )

        # Register as a stage handler for pipeline pattern
        for capability in self.capabilities:
            if capability.startswith("stage."):
                stage_name = capability[6:]  # Remove "stage." prefix
                await self.pipeline_pattern.register_stage_handler(
                    stage_name=stage_name,
                    handler=self.handle_pipeline_stage
                )

    async def handle_delegated_task(self, task):
        """Handle a delegated task."""
        # Extract task details
        task_id = task.get("task_id")
        task_type = task.get("task_type")
        task_data = task.get("task_data", {})

        # Check if we have capacity
        if len(self.current_tasks) >= self.max_workload:
            return {
                "status": "rejected",
                "reason": "capacity_exceeded"
            }

        # Check if we have the capability
        if task_type not in self.capabilities and "*" not in self.capabilities:
            return {
                "status": "rejected",
                "reason": "capability_mismatch"
            }

        # Accept the task
        self.current_tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "data": task_data,
            "status": "processing",
            "started_at": datetime.now().isoformat()
        }

        # Update orchestrator about workload
        await self.update_workload()

        try:
            # Process the task (in a real implementation, this would use reasoning modules)
            # This demonstrates OpenMAS's reasoning agnosticism - different executors could use
            # different reasoning approaches (rule-based, LLM, BDI, etc.)
            result = await self.process_task(task_type, task_data)

            # Update task status
            self.current_tasks[task_id]["status"] = "completed"
            self.current_tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self.current_tasks[task_id]["result"] = result

            # Clean up
            completed_task = self.current_tasks.pop(task_id)

            # Update orchestrator about workload
            await self.update_workload()

            # Return success
            return {
                "status": "completed",
                "result": result,
                "processing_time": (datetime.fromisoformat(completed_task["completed_at"]) -
                                   datetime.fromisoformat(completed_task["started_at"])).total_seconds()
            }

        except Exception as e:
            # Handle failure
            self.current_tasks[task_id]["status"] = "failed"
            self.current_tasks[task_id]["error"] = str(e)
            self.current_tasks[task_id]["failed_at"] = datetime.now().isoformat()

            # Clean up
            failed_task = self.current_tasks.pop(task_id)

            # Update orchestrator about workload
            await self.update_workload()

            # Return failure
            return {
                "status": "failed",
                "error": str(e)
            }

    async def handle_pipeline_stage(self, stage, input_data):
        """Handle a stage in a pipeline."""
        stage_name = stage.get("id")
        capability = f"stage.{stage_name}"

        # Check if we have the capability
        if capability not in self.capabilities:
            return {
                "status": "rejected",
                "reason": "capability_mismatch"
            }

        # Check if we have capacity
        if len(self.current_tasks) >= self.max_workload:
            return {
                "status": "rejected",
                "reason": "capacity_exceeded"
            }

        # Create a task ID for tracking
        task_id = str(uuid.uuid4())

        # Accept the task
        self.current_tasks[task_id] = {
            "id": task_id,
            "type": "pipeline_stage",
            "stage": stage_name,
            "data": input_data,
            "status": "processing",
            "started_at": datetime.now().isoformat()
        }

        # Update orchestrator about workload
        await self.update_workload()

        try:
            # Process the stage
            result = await self.process_pipeline_stage(stage_name, input_data)

            # Update task status
            self.current_tasks[task_id]["status"] = "completed"
            self.current_tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self.current_tasks[task_id]["result"] = result

            # Clean up
            completed_task = self.current_tasks.pop(task_id)

            # Update orchestrator about workload
            await self.update_workload()

            # Return success
            return {
                "status": "success",
                "output": result
            }

        except Exception as e:
            # Handle failure
            self.current_tasks[task_id]["status"] = "failed"
            self.current_tasks[task_id]["error"] = str(e)
            self.current_tasks[task_id]["failed_at"] = datetime.now().isoformat()

            # Clean up
            failed_task = self.current_tasks.pop(task_id)

            # Update orchestrator about workload
            await self.update_workload()

            # Return failure
            return {
                "status": "failed",
                "error": str(e)
            }

    async def update_workload(self):
        """Update the orchestrator about current workload."""
        orchestrator_id = self.config.get("orchestrator_id")

        if not orchestrator_id:
            return

        # Use request-response to update workload
        request_response = await self.context.get_pattern_registry().get_pattern(
            "request_response",
            self.config.get("patterns", {}).get("request_response")
        )

        await request_response.send_request(
            target_agent_id=orchestrator_id,
            request_type="update_agent_workload",
            content={
                "agent_id": self.agent_id,
                "current_tasks": len(self.current_tasks)
            }
        )

    async def process_task(self, task_type, task_data):
        """Process a delegated task with the appropriate reasoning module."""
        # In a real implementation, this would use different reasoning approaches
        # based on the task type or agent configuration

        # Simulate task processing
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate work

        # For this example, return a simple result
        return {
            "processed_by": self.agent_id,
            "processing_type": self.config.get("reasoning_type", "default"),
            "result_data": f"Processed {task_type} task"
        }

    async def process_pipeline_stage(self, stage_name, input_data):
        """Process a pipeline stage with the appropriate reasoning module."""
        # In a real implementation, this would use different reasoning approaches
        # based on the stage requirements

        # Simulate stage processing
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate work

        # For this example, enhance the input data based on stage
        if stage_name == "data_extraction":
            # Simulate extracting key data points
            return {
                "extracted_data": {
                    "key_points": ["point1", "point2", "point3"],
                    "entities": ["entity1", "entity2"],
                    "original_data": input_data
                }
            }
        elif stage_name == "data_enrichment":
            # Simulate enriching data with additional context
            return {
                "enriched_data": {
                    **input_data,
                    "additional_context": {
                        "source": "knowledge_base",
                        "confidence": 0.87,
                        "related_entities": ["related1", "related2"]
                    }
                }
            }
        elif stage_name == "analysis":
            # Simulate analyzing the data
            return {
                "analysis_results": {
                    "input": input_data,
                    "findings": ["finding1", "finding2"],
                    "confidence": 0.95,
                    "recommendations": ["rec1", "rec2"]
                }
            }
        elif stage_name == "summarization":
            # Simulate summarizing the results
            return {
                "summary": "Concise summary of the analysis and findings",
                "key_takeaways": ["takeaway1", "takeaway2"],
                "raw_data": input_data
            }
        else:
            # Generic stage handling
            return {
                "processed_by": self.agent_id,
                "stage": stage_name,
                "processed_data": input_data
            }
```

### Key Points:
- Integrates Delegation pattern for flexible task assignment based on capabilities, workload, and priorities
- Uses Pipeline pattern for complex multi-stage task processing
- Demonstrates the separation between task allocation logic and task execution logic
- Illustrates OpenMAS's reasoning agnosticism, allowing different agents to use different reasoning approaches
- Maintains protocol independence across all communication patterns

## Summary

The examples in this document demonstrate how OpenMAS communication patterns can be integrated to solve complex multi-agent scenarios. By combining multiple patterns, developers can create sophisticated agent systems that leverage the strengths of each pattern while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

The combination of patterns enables complex behaviors such as:

1. **Workflow Orchestration** - Combining multiple patterns to create sophisticated workflows
2. **Collaborative Decision-Making** - Using Pub-Sub, Request-Response, and Events for group decisions
3. **Distributed Monitoring** - Leveraging Streaming and Events for real-time monitoring
4. **Dynamic Task Allocation** - Integrating Delegation and Pipeline for efficient task distribution

Agents can flexibly choose which patterns to use based on their specific requirements, and the pattern implementations ensure consistent behavior regardless of the underlying transport protocol or reasoning approach used.
