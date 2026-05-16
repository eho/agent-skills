# Splash And Launch Experience

Use Expo's current splash-screen docs as the authority. Existing projects can show useful patterns, but Expo SDK splash behavior changes across releases, especially on Android.

## Native Splash

The native splash screen is static and build-time configured. Configure it with the `expo-splash-screen` config plugin, not the legacy top-level `expo.splash` shape for new scaffolds.

Install if needed:

```sh
npx expo install expo-splash-screen
```

Add a plugin entry like this, adapting asset paths and colors:

```json
[
  "expo-splash-screen",
  {
    "image": "./assets/splash-icon.png",
    "imageWidth": 200,
    "resizeMode": "contain",
    "backgroundColor": "#ffffff",
    "dark": {
      "image": "./assets/splash-icon-dark.png",
      "backgroundColor": "#000000"
    }
  }
]
```

Use the light and dark splash background colors as the first app root background colors to avoid a flash when the native splash hides.

Important Expo behavior to report to the user:

- Splash config changes require a new native build.
- Expo Go and development builds may not perfectly match standalone splash behavior on recent SDKs.
- Test final splash appearance in a release or store-like build when visual precision matters.

## Holding The Splash

If the app must load fonts, persisted state, migrations, or initial data before the first frame, call `SplashScreen.preventAutoHideAsync()` in module scope. Hide the splash as soon as the first usable app frame is ready.

Use `examples/root-layout-with-splash.tsx` as a starting point. Keep readiness checks minimal for a scaffold:

- fonts loaded, if custom fonts are included
- persisted theme/settings hydrated, if a persisted store is included
- database migrations complete, if local DB support is included

Do not wait on slow network requests by default.

## Animated Launch Overlay

Expo's native splash is not the place for custom React animation. For an animated splash, use this sequence:

1. Show the native static splash while required local resources load.
2. Render the app root with the same background color.
3. Hide the native splash.
4. Render a React/Reanimated overlay above the app root.
5. Animate the overlay out, then unmount it.

This avoids a blank frame and keeps the app's first real screen mounted underneath the animation.

Use `examples/app-launch-overlay.tsx` as a starting point only when the user asks for an animated launch experience. Keep the animation short; do not block normal app usage on decorative timing.

## References

- Official Expo splash-screen docs: `https://docs.expo.dev/versions/latest/sdk/splash-screen/`
- Expo splash and app icon guide: `https://docs.expo.dev/develop/user-interface/splash-screen-and-app-icon/`

