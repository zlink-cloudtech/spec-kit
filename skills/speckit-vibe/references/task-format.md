# Task Format Reference

Detailed documentation for task format in speckit vibe coding.

## Task Line Format

Every task MUST follow this exact format:

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

### Components

| Component | Required | Description |
|-----------|----------|-------------|
| `- [ ]` | Yes | Markdown checkbox |
| `TaskID` | Yes | Sequential ID (T001, T002...) |
| `[P]` | No | Parallel marker |
| `[Story]` | Conditional | User story label |
| Description | Yes | Clear action with file path |

## Examples

### Basic Task (No Parallel, No Story)
```markdown
- [ ] T001 Create project structure per implementation plan
```

### Parallel Task
```markdown
- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py
```

### Task with User Story
```markdown
- [ ] T012 [US1] Create User model in src/models/user.py
```

### Parallel Task with User Story
```markdown
- [ ] T015 [P] [US1] Implement UserRepository in src/repositories/user_repository.py
```

### Completed Task
```markdown
- [X] T001 Create project structure per implementation plan
```

## Task IDs

Task IDs are sequential and indicate execution order:

- **T001-T010**: Typically Setup phase
- **T011-T020**: Typically Foundational phase
- **T021+**: User story phases

### Numbering Rules
1. IDs are globally unique within tasks.md
2. Sequential order indicates dependency
3. Leave gaps for future insertions (T001, T005, T010)

## Parallel Marker [P]

The `[P]` marker indicates a task can run concurrently with other `[P]` tasks.

### When to Use [P]
- Tasks modify different files
- No dependencies on incomplete tasks
- No shared state requirements

### When NOT to Use [P]
- Task depends on another incomplete task
- Multiple tasks modify same file
- Task requires output from another task

### Example Parallel Group
```markdown
- [ ] T020 [P] [US1] Create User model in src/models/user.py
- [ ] T021 [P] [US1] Create Role model in src/models/role.py
- [ ] T022 [P] [US1] Create Permission model in src/models/permission.py
- [ ] T023 [US1] Create UserService (depends on models) in src/services/user_service.py
```

T020, T021, T022 run in parallel. T023 waits for them to complete.

## User Story Labels

User story labels map tasks to requirements from spec.md.

### Format
- `[US1]` - User Story 1 (highest priority)
- `[US2]` - User Story 2
- `[US3]` - User Story 3
- etc.

### Rules
| Phase | Story Label |
|-------|-------------|
| Setup | None |
| Foundational | None |
| User Story phases | Required |
| Polish | None |

## Phase Organization

### Phase 1: Setup
```markdown
## Phase 1: Setup

**Goal**: Initialize project structure and dependencies

**Tasks**:
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize package.json with dependencies in package.json
- [ ] T003 Create TypeScript configuration in tsconfig.json
```

### Phase 2: Foundational
```markdown
## Phase 2: Foundational

**Goal**: Implement blocking prerequisites

**Tasks**:
- [ ] T010 [P] Set up database connection in src/db/connection.ts
- [ ] T011 [P] Create base entity class in src/models/base.ts
- [ ] T012 Implement error handling middleware in src/middleware/error.ts
```

### Phase 3+: User Stories
```markdown
## Phase 3: User Authentication (US1)

**Goal**: Implement user registration and login

**Users**: End User, Administrator

**Relevant Architecture**: AuthService, UserRepository, JWT middleware

**Independent Test Criteria**:
- Users can register with email/password
- Users can log in and receive JWT
- Protected routes reject invalid tokens

**Tasks**:
- [ ] T020 [P] [US1] Create User model in src/models/user.py
- [ ] T021 [P] [US1] Create AuthService in src/services/auth_service.py
- [ ] T022 [US1] Implement registration endpoint in src/routes/auth.py
- [ ] T023 [US1] Implement login endpoint in src/routes/auth.py
```

## Task Description Guidelines

### Good Descriptions
```markdown
- [ ] T020 [P] [US1] Create User model with email, password, roles in src/models/user.py
- [ ] T021 [US1] Implement password hashing in AuthService.hash_password() in src/services/auth.py
- [ ] T022 [US1] Add email validation regex to UserValidator in src/validators/user.py
```

### Bad Descriptions
```markdown
- [ ] T020 Create model                    # Missing file path
- [ ] T021 [US1] Do authentication stuff   # Too vague
- [ ] T022 Implement everything            # Not specific
```

### Requirements
1. **Action verb**: Create, Implement, Add, Update, Configure
2. **Specific target**: What exactly is being created/modified
3. **File path**: Where the change happens

## Dependency Tracking

### Implicit Dependencies (via order)
```markdown
- [ ] T001 Create project structure
- [ ] T002 Initialize npm (depends on T001)
- [ ] T003 Install dependencies (depends on T002)
```

### Explicit Dependencies (via comments)
```markdown
- [ ] T020 [P] [US1] Create User model in src/models/user.py
- [ ] T021 [P] [US1] Create Role model in src/models/role.py
- [ ] T022 [US1] Create UserService in src/services/user_service.py
  # Depends on: T020, T021
```

### Dependency Section
```markdown
## Dependencies

- US1 (User Auth) → Foundation complete
- US2 (User Profile) → US1 complete
- US3 (Admin Panel) → US1, US2 complete
```

## Skill-Linked Tasks

Tasks using specific skills include skill label:

```markdown
- [ ] T030 [Skill: mcp-builder] Create MCP server structure in src/mcp/
- [ ] T031 [Skill: mcp-builder] Implement tool definitions in src/mcp/tools.ts
```

These tasks MUST follow the skill's workflow exactly.

## Task Updates During Implementation

### Marking Complete
Change `- [ ]` to `- [X]`:
```markdown
- [X] T001 Create project structure per implementation plan
```

### Adding New Tasks
Insert with new IDs:
```markdown
- [X] T020 [P] [US1] Create User model
- [ ] T020-1 [US1] Add email index to User model  # New task
- [ ] T021 [P] [US1] Create Role model
```

### Splitting Tasks
```markdown
# Before
- [ ] T020 [US1] Implement user authentication

# After
- [ ] T020 [US1] Create User model in src/models/user.py
- [ ] T020-1 [US1] Implement password hashing in src/services/auth.py
- [ ] T020-2 [US1] Create JWT token generation in src/services/jwt.py
```

## Validation

### vibe-task.sh Validation
The script validates:
1. Task ID format (T + digits)
2. Checkbox format
3. File path presence
4. Parallel marker validity

### Manual Validation
Check tasks.md for:
- [ ] All tasks have IDs
- [ ] All user story tasks have labels
- [ ] All tasks have file paths
- [ ] Parallel tasks are correctly marked
- [ ] No orphaned dependencies
