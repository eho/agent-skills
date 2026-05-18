# Package Installation Policy

Use the package manager and installer that match the package's role. Do not maintain a hand-written copy of every transitive dependency in the scaffold.

## Default Rules

- Use `expo install` for Expo SDK packages, React Native packages, and native modules where Expo has SDK compatibility knowledge. With Bun, use the Expo CLI through Bun, such as `bunx expo install <packages>`.
- Use the selected package manager directly for ordinary JavaScript packages, dev tools, CLIs, and packages where Expo does not provide version mapping.
- Let the package manager install dependencies declared by installed packages. Do not copy a library's full dependency tree into the app manifest.
- Install a package explicitly only when it is a direct app import, direct runtime requirement, direct dev/tooling requirement, documented peer dependency that the app must provide, workspace package import, official setup-doc requirement, or a verified workaround for an undeclared runtime import.
- Put dependencies in the package that owns the runtime graph. Mobile runtime dependencies belong in the Expo app package, such as `apps/mobile/package.json`; root workspace manifests should contain workspace tooling and shared scripts, not mobile-only runtime packages.
- Keep backend-only, landing-only, and build-tool-only packages out of the mobile app dependency graph unless mobile runtime code imports them.

## Expo And React Native Packages

Prefer Expo CLI for packages that need to match the installed Expo SDK and React Native version:

```sh
npx expo install expo-dev-client react-native-svg react-native-web
```

With Bun:

```sh
bunx expo install expo-dev-client react-native-svg react-native-web
```

After installing, run `expo install --check` or the package-manager equivalent. If Expo recommends a different version, prefer the Expo-compatible version unless the user requested and accepted a specific override.

## Direct Package Manager Installs

Use the selected package manager for packages that Expo does not version-map, such as gluestack JS packages, Tailwind tooling, app-specific libraries, local CLIs, and EAS CLI dev dependencies:

```sh
npm install <package>
npm install --save-dev <tool>
```

With Bun:

```sh
bun add <package>
bun add -d <tool>
```

Pin versions when compatibility is known to a major or minor line, or when official docs/source for a manually copied component set require a matching package set. Avoid unpinned `latest` when the docs or source path are version-specific.

## Missing Module Diagnostics

When Metro, TypeScript, or a runtime bundle reports a missing module, do not immediately add every nearby package. Classify the failure first:

- If app source imports the module directly, add it to the app's dependencies or devDependencies according to how it is used.
- If official setup docs list it as a required package or peer dependency, add it explicitly in the owning package.
- If a workspace package imports it, add it to that workspace package and ensure the mobile app depends on the workspace package only when mobile runtime code uses it.
- If the installed library imports it but does not declare it in published `dependencies` or `peerDependencies`, treat it as a narrow upstream packaging workaround. Add only the missing package, document the affected library/version and evidence, and keep a native Metro bundle check in verification.
- If the module exists elsewhere in the workspace, fix the install location or workspace dependency edge instead of relying on hoisting.

## Known Undeclared Runtime Imports

Known exceptions should stay narrow and version-scoped. For example, affected `react-native-svg` releases can import `Buffer` from `buffer` without declaring `buffer` in package metadata. When a scaffold installs one of those affected releases, add `buffer@^6.0.3` to the Expo app dependencies and verify with a native Metro bundle check. Do not generalize this into listing all transitive packages.

If a future `react-native-svg` release declares `buffer` itself or stops importing it, remove the explicit workaround instead of keeping stale dependency cargo.

## Verification

Package installation is not complete until:

- The selected lockfile is updated by the selected package manager.
- Unexpected lockfiles from other package managers are removed when they were generated accidentally.
- `expo install --check`, `expo-doctor`, TypeScript, and lint pass or have documented residual warnings.
- At least one native or native-equivalent Metro bundle check passes for scaffolds with native/styling/UI dependencies.
