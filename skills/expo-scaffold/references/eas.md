# EAS Build And Update

Configure EAS with official CLI commands when the user is authenticated and the project is initialized. Otherwise create a local EAS-ready scaffold manually and leave account-backed fields absent.

## Build Configuration

When authenticated, run from the project root:

```sh
npx eas-cli@latest build:configure
```

If the user already has an `eas` binary installed, use it directly. With Bun, keep the same `eas-cli` package identity:

```sh
bunx eas-cli@latest build:configure
```

When unauthenticated or working in a local-only scaffold, create or update `eas.json` manually with these build profiles:

- `development`: development client, internal distribution, `development` channel, auto build increment enabled.
- `preview`: internal distribution, `preview` channel, auto build increment enabled.
- `production`: store-ready production build, `production` channel, auto build increment enabled.

Install `expo-dev-client` before relying on the development profile. Prefer `cli.appVersionSource: "remote"` for account-backed new EAS projects unless the user has a local versioning policy. For a local-only scaffold, it is acceptable to include the intended CLI config and profiles, but do not invent remote metadata. Set `autoIncrement: true` on each build profile so EAS automatically increments native build numbers for every cloud build.

Do not invent submit credentials, app store IDs, EAS owner, or project IDs.

For starters that include EAS package scripts, add `eas-cli` as a dev dependency unless the repository intentionally relies on one-off package-manager invocations:

```sh
npm install --save-dev eas-cli
```

For Bun:

```sh
bun add -d eas-cli
```

## Update Configuration

Install the updates runtime:

```sh
npx expo install expo-updates
```

Distinguish local EAS-ready config from fully configured EAS Update. Do not run `eas update:configure` until the user is authenticated and the project has been initialized with EAS. Local scaffold work can prepare `runtimeVersion`, profiles, channels, and scripts, but account-backed OTA updates are not fully live until EAS writes:

- `expo.updates.url`
- `expo.extra.eas.projectId`

For new apps, prefer:

```json
"runtimeVersion": {
  "policy": "appVersion"
}
```

Use matching EAS Build channels so preview builds receive preview updates and production builds receive production updates. For SDK 55 and later, EAS Update publish commands require an explicit `--environment` flag; use the environment that matches the channel unless the project has a documented environment policy.

Minimum local-only EAS scaffold:

- `eas.json` with development, preview, and production profiles.
- Build and update scripts in `package.json`.
- `runtimeVersion.policy` set to `appVersion`.
- No `updates.url`.
- No `extra.eas.projectId`.
- No invented `owner`.

When authenticated and initialized, run:

```sh
npx eas-cli@latest update:configure
```

With Bun:

```sh
bunx eas-cli@latest update:configure
```

If authentication or project creation is required, stop after local config and report the exact commands, using the package-manager form that matches the project:

```sh
npx eas-cli@latest login
npx eas-cli@latest init
npx eas-cli@latest update:configure
```

For Bun:

```sh
bunx eas-cli@latest login
bunx eas-cli@latest init
bunx eas-cli@latest update:configure
```

## Recommended Scripts

Merge scripts like these into `package.json`, adapting package manager conventions:

```json
{
  "start": "expo start",
  "ios": "expo run:ios",
  "android": "expo run:android",
  "web": "expo start --web",
  "build:dev": "eas build --platform all --profile development",
  "build:preview": "eas build --platform all --profile preview",
  "build:production": "eas build --platform all --profile production",
  "update:preview": "eas update --channel preview --environment preview --message \"Preview update\"",
  "update:production": "eas update --channel production --environment production --message \"Production update\""
}
```

Add `eas-cli` as a dev dependency when scripts call `eas`, so package scripts resolve the local CLI binary on a clean checkout instead of assuming a global install. Alternatively, use package-manager one-off commands directly in scripts if that is the repository convention and the invocation has been verified. For example, Bun projects may use `bunx --bun eas-cli@latest ...` only if that syntax is verified in the current Bun/EAS environment; otherwise prefer the local dev dependency so `bun run build:preview` works on a clean checkout.

For SDKs before 55, verify whether `--environment` is supported and required before adding it.

`expo run:ios` and `expo run:android` create native directories when none exist. That is acceptable for local development builds, but do not commit generated `ios/` or `android/` folders unless the user asks.

If the user wants iOS-only or Android-only, set the platform in scripts accordingly.

## Explain The Boundary

Tell the user that EAS Update can deliver compatible JavaScript and asset changes. Native dependency changes, app config changes that affect native projects, runtime version changes, and SDK upgrades require a new build.

## Post-Scaffold Operations

At the end of every scaffold, return a short `Post-scaffold operations` checklist. Include only items that still require the user's account, credentials, devices, store access, or deliberate product decisions. Mark each item as required, optional, or conditional.

Common required or conditional operations:

- `eas login`: required before account-backed EAS Build, EAS Update, or Submit can run.
- `eas init`: required to create/link the Expo project and write account-backed project metadata when the scaffold did not run authenticated EAS initialization.
- `eas update:configure`: required after installing `expo-updates` when `expo.updates.url` and `expo.extra.eas.projectId` are still absent.
- First development build: required before testing in a development client. Use `eas build --platform <platform> --profile development` for cloud builds, or `expo run:ios` / `expo run:android` for local builds.
- Install the development build on a simulator, emulator, or device, then run `expo start`; Expo Go is not the target runtime for scaffolds using `expo-dev-client`.
- iOS credentials and Apple Developer access: required for physical-device iOS builds and store builds; iOS 16+ devices may also need Developer Mode enabled before running internal/development builds.
- Android signing credentials or Google Play setup: required before production/store Android builds or submission. Let EAS manage credentials only with user approval.
- Store submission setup: optional unless the user requested submit automation. Requires app store records, bundle/package identifiers, Apple/Google credentials, and `eas submit` or submit profiles.
- EAS secrets/environment variables: required when app config, API URLs, build hooks, or runtime code reference secrets or environment-specific values.
- Domain/backend/landing deployment: conditional when the scaffold includes a backend, Expo API routes, or a landing app. List the deployment target and any environment variables that still need real values.
- Native rebuild after native changes: required whenever native dependencies, config plugins, app config affecting native projects, runtime version policy, or Expo SDK change after the first build.
- Publish first OTA update: optional after `eas update:configure` and at least one compatible build exists. Use the scaffolded `update:preview` or `update:production` scripts with the matching channel/environment.

Do not present these operations as failures. They are the normal boundary between a local scaffold and account/device/store-backed setup.
