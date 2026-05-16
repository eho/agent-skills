# Verification

Run the strongest checks that are practical for the project and installed package manager.

## Required Checks

```sh
npx expo install --check
npx expo-doctor
npx tsc --noEmit
```

If `expo-doctor` is unavailable through `npx expo-doctor`, use the current Expo-recommended invocation.

## Runtime Smoke Check

Start with a clean Metro cache:

```sh
npx expo start --clear
```

For a coding agent with browser/device automation, verify:

- The bundler starts.
- The placeholder screen renders.
- Gluestack components do not throw provider or import errors.
- NativeWind classes visibly apply.

## EAS Config Check

Run non-building config checks where possible:

```sh
npx eas-cli@latest build:inspect --platform ios --profile preview
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
