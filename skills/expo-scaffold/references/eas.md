# EAS Build And Update

Configure EAS with official CLI commands whenever possible, then make small edits for predictable starter profiles and scripts.

## Build Configuration

Run from the project root:

```sh
npx eas-cli@latest build:configure
```

If the user already has `eas` installed or uses `bunx`, adapt the command:

```sh
bunx eas build:configure
```

Create or update `eas.json` with these build profiles:

- `development`: development client, internal distribution, `development` channel, auto build increment enabled.
- `preview`: internal distribution, `preview` channel, auto build increment enabled.
- `production`: store-ready production build, `production` channel, auto build increment enabled.

Prefer `cli.appVersionSource: "remote"` for new EAS projects unless the user has a local versioning policy. Set `autoIncrement: true` on each build profile so EAS automatically increments native build numbers for every cloud build.

Do not invent submit credentials or app store IDs.

## Update Configuration

Install and configure updates:

```sh
npx expo install expo-updates
npx eas-cli@latest update:configure
```

Distinguish local EAS-ready config from fully configured EAS Update. `eas update:configure --non-interactive` can fail before `eas init` or when the user is not authenticated. Local scaffold work can prepare `runtimeVersion`, profiles, channels, and scripts, but these require authenticated project setup before OTA updates are fully live:

- `expo.updates.url`
- `expo.extra.eas.projectId`
- `expo.runtimeVersion`

For new apps, prefer:

```json
"runtimeVersion": {
  "policy": "appVersion"
}
```

Use matching EAS Build channels so preview builds receive preview updates and production builds receive production updates.

If authentication or project creation is required, stop after local config and report the exact commands:

```sh
eas login
eas init
eas update:configure
```

## Recommended Scripts

Merge scripts like these into `package.json`, adapting package manager conventions:

```json
{
  "build:dev": "eas build --platform all --profile development",
  "build:preview": "eas build --platform all --profile preview",
  "build:production": "eas build --platform all --profile production",
  "update:preview": "eas update --channel preview --message \"Preview update\"",
  "update:production": "eas update --channel production --message \"Production update\""
}
```

If the user wants iOS-only or Android-only, set the platform in scripts accordingly.

## Explain The Boundary

Tell the user that EAS Update can deliver compatible JavaScript and asset changes. Native dependency changes, app config changes that affect native projects, runtime version changes, and SDK upgrades require a new build.
