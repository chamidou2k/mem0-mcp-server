# Tasks

## 1. Read operations: drop agent_id

- [x] 1.1 Remove `agent_id` from `list_memories` query params; verify a unit test asserts the request scopes by `user_id` only and omits `agent_id`
- [x] 1.2 Remove `agent_id` from `get_memory` query params; verify a unit test asserts the request scopes by `user_id` only and omits `agent_id`
- [x] 1.3 Remove `agent_id` from `search_memories` payload; verify a unit test asserts the search scopes by `user_id` only and omits `agent_id`

## 2. Write operations: keep agent_id

- [x] 2.1 Keep `agent_id` on the `add_memory` payload; verify a unit test asserts the payload includes `agent_id`
- [x] 2.2 Add `agent_id` to the `update_memory` payload; verify a unit test asserts the payload includes `agent_id`

## 3. Verify end-to-end

- [x] 3.1 Verify `mem0_list_memories` no longer returns the hub 500 and returns the user's full memory store; verify with a live call against the configured hub

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result.
