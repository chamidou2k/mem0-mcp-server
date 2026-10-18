# Spec Delta

## Purpose

Defines the hub filter used by each memory operation: writes attribute a memory to the configured agent, while reads return the user's full memory store regardless of agent.

## ADDED Requirements

### Requirement: Write operations carry the configured agent identifier
When the server adds or updates a memory, it SHALL include the configured `agent_id` so the hub attributes the memory to that agent. An absent `agent_id` SHALL be omitted from the request.

#### Scenario: Adding a memory with an agent id
- **WHEN** the server adds a memory while `agent_id` is configured
- **THEN** the request to the hub SHALL include `agent_id`

#### Scenario: Adding a memory without an agent id
- **WHEN** the server adds a memory while no `agent_id` is configured
- **THEN** the request to the hub SHALL NOT include `agent_id`

### Requirement: Read operations scope by user only
When the server lists, retrieves, or searches memories, it SHALL scope the request to `user_id` and SHALL NOT send `agent_id`, so the result spans every agent that wrote to that user.

#### Scenario: Listing memories ignores the agent id
- **WHEN** the server lists memories for a configured `user_id` and `agent_id`
- **THEN** the request to the hub SHALL scope only by `user_id` and SHALL NOT include `agent_id`

#### Scenario: Searching memories ignores the agent id
- **WHEN** the server searches memories while both `user_id` and `agent_id` are configured
- **THEN** the search SHALL scope only by `user_id` and SHALL NOT include `agent_id`

#### Scenario: Retrieving a memory ignores the agent id
- **WHEN** the server retrieves a memory while both `user_id` and `agent_id` are configured
- **THEN** the retrieval SHALL scope only by `user_id` and SHALL NOT include `agent_id`
