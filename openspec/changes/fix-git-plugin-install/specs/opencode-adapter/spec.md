# Spec Delta

## MODIFIED Requirements

### Requirement: The adapter installs from the project repository

The adapter SHALL be installable from the project's Git repository with a single
specifier and without a build step. The repository SHALL contain a root
`package.json`, marked `private`, so the installer's Git dependency preparation
step succeeds, and the compiled entry point referenced by the adapter package's
`main`/`exports` fields SHALL be committed to the repository.

#### Scenario: Git install needs no build
- **WHEN** the adapter package is resolved from the Git repository
- **THEN** the compiled entry point (`dist/index.js`) referenced by
  `main`/`exports` is present in the checkout

#### Scenario: Repository root resolves for a Git install
- **WHEN** the installer prepares the repository as a Git dependency
- **THEN** it finds a root `package.json` and can then select the adapter package
  from `integrations/opencode`
