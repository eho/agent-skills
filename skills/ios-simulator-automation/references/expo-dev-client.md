# Expo development clients

Read this only for an Expo-hosted target.

Classify the change before building:

- For JavaScript or asset-only changes, reuse a compatible installed development build and load Metro for the exact revision.
- For native source, generated native files, entitlements, extensions, config plugins, pods, or build-configuration changes, build and install a new artifact.
- If uncertain, inspect the changed native inputs; an automation failure alone does not justify rebuilding.

Before reusing Metro, verify its project root, revision, port/interface, public-environment fingerprint, public/proxy base URL, and owner. Do not trust a recent-project entry, old QR code, successful URL open, or bundle request as proof of identity or stability.

Open the known host or development-client identifier, wait for bundling, inspect the foreground state, and require a stable app-owned semantic observation before starting the feature flow.
