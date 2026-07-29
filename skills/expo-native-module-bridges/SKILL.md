---
name: expo-native-module-bridges
description: Implement or debug JavaScript-to-native argument handling in Expo Modules. Use when Swift Function or AsyncFunction calls fail before reaching the native API, especially with raw dictionaries, numeric values, swallowed promise rejections, or stale native builds.
---

# Expo Native Module Bridges

Prefer typed Expo arguments or `Record` types over raw `[String: Any]`
dictionaries.

Remember that JavaScript numbers arrive through Expo's JSI bridge as Swift
`Double`. A raw `as? Int` cast can therefore reject a valid JavaScript integer
before the platform API is called. When an exact integer is required, validate
that the `Double` is finite, integral, and in range before converting it.

Test bridge-facing parsers with realistic `Double` fixtures, plus malformed,
non-finite, and boundary inputs. Ensure rejected `AsyncFunction` promises are
surfaced by the JavaScript caller.

After changing native Swift or module definitions, rebuild and reinstall the
native app. When diagnosis is ambiguous, compare the bridge path with a
known-good native control path that exercises the same platform capability.
