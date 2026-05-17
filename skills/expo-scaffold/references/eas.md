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
