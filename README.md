# Personal Agent Skills

Skills I've built for my own AI-assisted development workflow. The design-to-implementation pipeline here is what I use to build projects like [Kore](https://github.com/eho/kore).

## Skills

| Skill | Command | Description |
| :--- | :--- | :--- |
| [**Design Doc**](skills/design-doc/SKILL.md) | `/design-doc` | Synthesize a discussion or outline into a complete design document with architecture, data contracts, and agent-ready user stories with acceptance criteria. |
| [**Design Doc Reviewer**](skills/design-doc-reviewer/SKILL.md) | `/design-doc-reviewer` | Independent, read-only readiness review with mechanical validation and evidence-backed blockers. |
| [**Design Doc Review Loop**](skills/design-doc-review-loop/SKILL.md) | `/design-doc-review-loop` | Review and revise until validation passes and no blockers remain, then mark the design doc `Revised`. |
| [**Design to Issues**](skills/design-to-issues/SKILL.md) | `/design-to-issues` | Reconcile a revised design document with canonical GitHub Issues, including changed or stale delivered stories, dependencies, labels, and Milestone tracking. |
| [**Feature Delivery**](skills/feature-delivery/SKILL.md) | `/feature-delivery` | Goal-aware, resumable delivery of every design-doc story through issue reconciliation, implementation, independent review, merge, and final audit remediation. |
| [**User Story Delivery**](skills/user-story-delivery/SKILL.md) | `/user-story-delivery` | Deliver one GitHub user story through implementation, independent review, revision, and repository-policy merge completion. |
| [**User Story Implementer**](skills/user-story-implementer/SKILL.md) | `/user-story-implementer` | Pick up a single open GitHub Issue, implement it end-to-end (code, tests, PR), and move on. Designed to run in a fresh context per story. |
| [**User Story Reviewer**](skills/user-story-reviewer/SKILL.md) | `/user-story-reviewer` | Review a Pull Request against the original issue's acceptance criteria, checking completeness, test coverage, and code quality. |
| [**Post-Implementation Reviewer**](skills/post-implementation-reviewer/SKILL.md) | `/post-implementation-reviewer` | Independent, report-only final audit of story completion, integration behavior, design alignment, verification, and release readiness. |
| [**Kore**](skills/kore/SKILL.md) | `/kore` | Search, browse, save, and synthesize a personal knowledge base built from bookmarks, notes, and accumulated insights. |
| [**Blog Writer**](skills/blog-writer/SKILL.md) | `/blog-writer` | Transform technical documents, outlines, or raw notes into an engaging, human-sounding blog post. |
| [**Public Repo Explorer**](skills/public-repo-explorer/SKILL.md) | `/public-repo-explorer` | Efficiently browse public GitHub repositories using shallow clones — scan, examine, and extract information without cluttering the workspace. |
| [**iOS Simulator Automation**](skills/ios-simulator-automation/SKILL.md) | `/ios-simulator-automation` | Coordinate agent-device and serve-sim for reliable app/system automation, bounded fallback, cleanup, and evidence handoff. |
| [**iOS WidgetKit Development**](skills/ios-widgetkit-development/SKILL.md) | `/ios-widgetkit-development` | Implement, diagnose, and verify WidgetKit and AppIntent widgets across generated source, native targets, storage, configuration, rendering, and interactions. |
| [**Project Bootstrap**](skills/project-bootstrap/SKILL.md) | `/project-bootstrap` | Initialize or refresh repository conventions so coding agents have accurate project commands, docs rules, and guardrails. |
| [**Expo Scaffold**](skills/expo-scaffold/SKILL.md) | `/expo-scaffold` | Create a production-oriented Expo starter with Expo Router, development builds, NativeWind, gluestack, EAS, and agent-friendly project context. |
| [**Expo gluestack Setup**](skills/expo-gluestack-setup/SKILL.md) | `/expo-gluestack-setup` | Add, repair, or verify official gluestack-ui setup for Expo or React Native projects. |

## Project Bootstrap Workflow

Use these skills when starting or preparing a repository before normal feature work:

```
/project-bootstrap
     ↓
/expo-scaffold
     └─ /expo-gluestack-setup
```

**1. Prepare the repository** — Use `/project-bootstrap` to create or refresh `AGENTS.md`, capture package-manager rules, project commands, documentation conventions, testing expectations, and repo-specific guardrails for coding agents.

**2. Scaffold an Expo app** — Use `/expo-scaffold` when starting a new Expo project or Expo-centered monorepo. It sets up the app structure, Expo Router, development builds, NativeWind, EAS defaults, starter screens, and agent-friendly project context.

**3. Configure gluestack when needed** — Use `/expo-gluestack-setup` directly for an existing Expo or React Native app, or let `/expo-scaffold` invoke it as the gluestack specialist during a new scaffold.

## Development Workflow

The nine development skills form a pipeline from idea to shipped feature. `/feature-delivery` is the top-level orchestrator once a design document is revised and ready:

```
💬 Discuss
     ↓
/design-doc  ◄─────────────────┐
     ↓                         │ iterate
/design-doc-review-loop ───────┘
     └─ /design-doc-reviewer
     ↓
/feature-delivery
     ├─ /design-to-issues
     ├─ /user-story-delivery  ◄──────────┐
     │    ├─ /user-story-implementer     │
     │    └─ /user-story-reviewer ───────┤ next story / revision
     └─ /post-implementation-reviewer
```

**1. Discuss the design** — Before triggering any skill, have a free-form conversation with the AI about the feature. This is an exploratory back-and-forth to get the general direction and key ideas into shape. No structure needed yet — just think out loud.

**2. Write the design** — Once the direction feels right, trigger `/design-doc`. It mines the discussion, verifies relevant repository contracts, asks only material clarifying questions, and produces a concise `Draft` with canonical user stories and mechanical validation.

**3. Review and revise the design** — Use `/design-doc-review-loop` to run an independent full review, revise against evidence-backed blocking findings, and use focused follow-ups for prior blockers and affected surfaces. Mechanical validation plus zero blockers promotes the design to `Status: Revised`; non-blocking suggestions may remain or be waived. Use `/design-doc-reviewer` directly for a one-time, read-only verdict.

**4. Deliver the feature** — Use `/feature-delivery` to synchronize a revised design document with GitHub Issues, deliver each open dependency-ready issue through `/user-story-delivery`, and run `/post-implementation-reviewer` after every story is complete. GitHub Issues and Pull Requests remain the progress record. Blocking audit findings return through the same issue-delivery workflow before the feature finishes.

**5. Push stories to GitHub manually when needed** — Use `/design-to-issues` directly when you only want to synchronize reviewed, agent-ready user stories with GitHub Issues. It creates missing issues, updates changed story contracts in place, reopens changed completed stories, preserves unchanged completed stories, repairs dependency metadata and labels, and creates or reuses the feature milestone.

**6. Implement and review one story manually when needed** — Use `/user-story-delivery` directly for the full loop around a single issue. It runs `/user-story-implementer`, hands the resulting PR to an independent `/user-story-reviewer`, addresses findings on the same PR, and verifies repository-policy merge and issue closure before declaring the story done. Use `/user-story-implementer` or `/user-story-reviewer` directly when you only want one half of the workflow.

**7. Final review manually when needed** — Run `/post-implementation-reviewer` directly once the full feature appears complete. It is report-only by default. In `/feature-delivery`, blocking findings are converted into traceable implementation work and the entire audit is rerun after remediation.

### Using Feature Delivery with `/goal`

Use a goal when you want the agent to persist until the complete design document is delivered, including review and final-audit remediation:

```text
/goal

Use $feature-delivery to fully deliver @docs/design/<feature>.md.
Continue through issue reconciliation, implementation, independent review,
merge, and final-audit remediation until the feature is Ready.
```

The design document should have `Status: Revised`, meaning its latest independent review found no blockers and mechanical story validation passed.

While the goal is active, `/feature-delivery`:

1. Reads the design document and synchronizes every story with one canonical GitHub Issue.
2. Uses issue state, linked PRs, reviews, checks, and merge state to determine remaining work.
3. Sends each dependency-ready open issue through `/user-story-delivery`.
4. Verifies the reviewed PR merged and the issue closed before treating a story as done.
5. Continues unrelated stories when another story is blocked.
6. Runs a report-only overall audit after all stories are complete.
7. Routes blocking audit findings through ordinary issue delivery and reruns the audit.

The goal completes only when every in-scope story is implemented, independently reviewed, merged, closed, and backed by acceptance-criteria evidence, and the overall audit finds no blocking issue.

Creating issues, opening or approving PRs, or filing follow-up issues does not count as completion. After interruption, the workflow reads current GitHub state and continues.

---

## Installation

```bash
bunx skills add eho/agent-skills
```

---

## Community Skills

A curated reference of skills from the community that I find useful.

> Skills are managed with the help of the [**Skill Curator**](skills/skill-curator/SKILL.md) skill.

### React Native

| Skill Name | Source | Description |
| :--- | :--- | :--- |
| [**React Native Best Practices**](https://github.com/callstackincubator/agent-skills/tree/main/skills/react-native-best-practices/SKILL.md) | [Callstack](https://github.com/callstackincubator/agent-skills) | Performance optimization skills based on *The Ultimate Guide to React Native Optimization* by Callstack. |
| [**Upgrading React Native**](https://github.com/callstackincubator/agent-skills/tree/main/skills/upgrading-react-native/SKILL.md) | [Callstack](https://github.com/callstackincubator/agent-skills) | A comprehensive React Native upgrade workflow including templates, dependency management, and solutions for common pitfalls. |
| [**React Native Guidelines**](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-native-guidelines/SKILL.md) | [Vercel](https://github.com/vercel-labs/agent-skills) | Performance, architecture, and platform-specific patterns optimized for AI agents. |
| [**Upgrading Expo**](https://github.com/expo/skills/tree/main/plugins/upgrading-expo/skills/upgrading-expo/SKILL.md) | [Expo](https://github.com/expo/skills) | Guidelines for upgrading Expo SDK versions and fixing dependency issues. |
| [**Building Native UI**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/building-native-ui/SKILL.md) | [Expo](https://github.com/expo/skills) | Complete guide for building beautiful apps with Expo Router. Covers fundamentals, styling, components, and animations. |
| [**Expo Dev Client**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/expo-dev-client/SKILL.md) | [Expo](https://github.com/expo/skills) | Build and distribute Expo development clients locally or via TestFlight. |
| [**Expo UI SwiftUI**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/expo-ui-swift-ui/SKILL.md) | [Expo](https://github.com/expo/skills) | Using SwiftUI Views and modifiers in your app with `@expo/ui/swift-ui`. |
| [**Expo Tailwind Setup**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/expo-tailwind-setup/SKILL.md) | [Expo](https://github.com/expo/skills) | Set up Tailwind CSS v4 in Expo with react-native-css and NativeWind v5 for universal styling. |
| [**Use DOM**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/use-dom/SKILL.md) | [Expo](https://github.com/expo/skills) | Use Expo DOM components to run web code in a webview on native and as-is on web. |
| [**Native Data Fetching**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/native-data-fetching/SKILL.md) | [Expo](https://github.com/expo/skills) | Covers fetch API, React Query, SWR, error handling, caching, offline support, and Expo Router data loaders. |
| [**Expo API Routes**](https://github.com/expo/skills/tree/main/plugins/expo-app-design/skills/expo-api-routes/SKILL.md) | [Expo](https://github.com/expo/skills) | Guidelines for creating API routes in Expo Router with EAS Hosting. |

### Web & React

| Skill Name | Source | Description |
| :--- | :--- | :--- |
| [**React Best Practices**](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices/SKILL.md) | [Vercel](https://github.com/vercel-labs/agent-skills) | React and Next.js performance optimization guidelines from Vercel Engineering. |
| [**Composition Patterns**](https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns/SKILL.md) | [Vercel](https://github.com/vercel-labs/agent-skills) | React composition patterns to avoid boolean prop proliferation and ensure scalability. |
| [**Web Design Guidelines**](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines/SKILL.md) | [Vercel](https://github.com/vercel-labs/agent-skills) | Review UI code for compliance with 100+ web interface best practices. |

### Cloud & Infrastructure (AWS)

| Skill Name | Source | Description |
| :--- | :--- | :--- |
| [**AWS MCP Setup**](https://github.com/zxkane/aws-skills/tree/main/plugins/aws-common/skills/aws-mcp-setup/SKILL.md) | [zxkane](https://github.com/zxkane/aws-skills) | Configure AWS Documentation MCP server to query up-to-date AWS knowledge, APIs, and best practices. |
| [**AWS Serverless EDA**](https://github.com/zxkane/aws-skills/tree/main/plugins/serverless-eda/skills/aws-serverless-eda/SKILL.md) | [zxkane](https://github.com/zxkane/aws-skills) | AWS serverless and event-driven architecture expert based on Well-Architected Framework. |
| [**AWS Cost Operations**](https://github.com/zxkane/aws-skills/tree/main/plugins/aws-cost-ops/skills/aws-cost-operations/SKILL.md) | [zxkane](https://github.com/zxkane/aws-skills) | AWS cost optimization, monitoring, and operational best practices. |
| [**AWS CDK Development**](https://github.com/zxkane/aws-skills/tree/main/plugins/aws-cdk/skills/aws-cdk-development/SKILL.md) | [zxkane](https://github.com/zxkane/aws-skills) | AWS Cloud Development Kit (CDK) expert for building cloud infrastructure with TypeScript/Python. |

### Workflows & Tools

| Skill Name | Source | Description |
| :--- | :--- | :--- |
| [**PDF**](https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md) | [Anthropic](https://github.com/anthropics/skills) | Use this skill whenever the user wants to do anything with PDF files. |
| [**GitHub**](https://github.com/callstackincubator/agent-skills/tree/main/skills/github/SKILL.md) | [Callstack](https://github.com/callstackincubator/agent-skills) | GitHub workflow patterns for Pull Requests, code reviews, and branching strategies. |
| [**Expo Deployment**](https://github.com/expo/skills/tree/main/plugins/expo-deployment/skills/expo-deployment/SKILL.md) | [Expo](https://github.com/expo/skills) | Deploying Expo apps to iOS App Store, Android Play Store, web hosting, and API routes. |
| [**Expo CI/CD Workflows**](https://github.com/expo/skills/tree/main/plugins/expo-deployment/skills/expo-cicd-workflows/SKILL.md) | [Expo](https://github.com/expo/skills) | Helps understand and write EAS workflow YAML files for Expo projects. |
| [**qmd**](https://github.com/levineam/qmd-skill/blob/main/SKILL.md) | [levineam](https://github.com/levineam/qmd-skill) | Local hybrid search for markdown notes and docs. Use when searching notes, finding related content, or retrieving documents from indexed collections. |
| [**Algorithmic Art**](https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/SKILL.md) | [Anthropic](https://github.com/anthropics/skills) | Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. |
