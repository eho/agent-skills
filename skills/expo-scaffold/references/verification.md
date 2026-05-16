# Verification

Run the strongest checks that are practical for the project and installed package manager.

## Required Checks

```sh
npx expo install --check
npx expo-doctor
npx tsc --noEmit
```

If `expo-doctor` is unavailable through `npx expo-doctor`, use the current Expo-recommended invocation.

Run lint after install. The first Expo lint run may install `eslint` and `eslint-config-expo`; if so, install those dependencies, then run lint again:

```sh
npx expo lint
```

## Runtime Smoke Check

Start with a clean Metro cache:

```sh
npx expo start --web --port 8090 --clear
```

Use an explicit port to avoid hitting another Expo app already running on Metro's default port. Verify `127.0.0.1:8090` or the selected explicit port.

For a coding agent with browser/device automation, verify:

- The bundler starts.
- The placeholder screen renders.
- Gluestack components do not throw provider or import errors.
- NativeWind classes visibly apply.
- Metro resolves runtime aliases, including `@/*` and `@/assets/*`. TypeScript passing is not enough; confirm the app bundles.

## EAS Config Check

Run non-building config checks where possible:

```sh
npx eas-cli@latest build:inspect --platform ios --profile preview --stage archive --output /private/tmp/<slug>-eas-inspect --force
```

With Bun:

```sh
bunx eas build:inspect --platform ios --profile preview --stage archive --output /private/tmp/<slug>-eas-inspect --force
```

If credentials, login, or project creation are required, stop and report the exact next command for the user to run after authenticating.

## Final Report

Summarize:

- Expo SDK and React Native versions selected.
- NativeWind version selected and why.
- Gluestack commands run and components added.
- EAS build/update profiles and channels.
- Verification commands and results.
- Any steps blocked by Expo login, credentials, bundle identifiers, package names, or app store metadata.
