# Platform guidance

Read this reference when designing artwork, generating production assets, or editing Expo icon configuration.

## Design

- Design for the product promise, not just its market category.
- Compare concepts by silhouette and metaphor rather than palette-only variations.
- Check candidates at 48–64 px before polishing.
- Generate square artwork without a baked launcher mask, rounded card, border, or outer shadow.
- Preserve the selected source separately from generated derivatives.

A compact generation prompt should state the product promise, audience, metaphor, palette, rendering style, small-size requirement, and product-specific exclusions.

## iOS

- A conventional PNG icon should be square, opaque, and ideally 1024×1024.
- Do not bake rounded corners into the source.
- Expo SDKs that support Apple Icon Composer can accept a `.icon` directory. Use it for artwork designed for that layered format, not as a mandatory conversion target.

## Android

- Adaptive icons use separate foreground and background layers.
- Android documents a 66×66 critical-content safe zone inside a 108×108 layer. `66 / 108 ≈ 0.611`, which is the generator’s default maximum foreground bound.
- Use a transparent foreground and either a solid `backgroundColor` or a deliberate `backgroundImage`.
- A monochrome layer enables themed icons. It must be a clean single-color mark, but it may be simplified rather than sharing the full-color foreground’s exact alpha mask.
- Expo documents adaptive `backgroundColor` as a six-character `#RRGGBB` value.

## Optional adjacent assets

- Expo recommends a transparent 1024×1024 PNG for splash artwork.
- Splash composition, background, and dark appearance may differ from the launcher icon; do not overwrite existing choices incidentally.
- Test final splash appearance in a preview or production/release build, not Expo Go or a development build.
- Generate a favicon only when the project targets web. Inspect the reduction because detailed launcher art may need a simplified favicon.

## Configuration shape

Core launcher fields:

```json
{
  "expo": {
    "icon": "./assets/images/icon.png",
    "ios": {
      "icon": "./assets/images/icon.png"
    },
    "android": {
      "icon": "./assets/images/icon.png",
      "adaptiveIcon": {
        "backgroundColor": "#1E2630",
        "foregroundImage": "./assets/images/android-icon-foreground.png",
        "monochromeImage": "./assets/images/android-icon-monochrome.png"
      }
    }
  }
}
```

Add web favicon and `expo-splash-screen` fields only when those outputs are in scope. Merge fields rather than replacing unrelated platform or plugin configuration.

## Official references

- Expo app icons: `https://docs.expo.dev/develop/user-interface/app-icons/`
- Expo splash screen and app icon guide: `https://docs.expo.dev/develop/user-interface/splash-screen-and-app-icon/`
- Expo splash-screen config: `https://docs.expo.dev/versions/latest/sdk/splash-screen/`
- Expo app config schema: `https://docs.expo.dev/versions/latest/config/app/`
- Android adaptive icons: `https://developer.android.com/develop/ui/compose/system/icon_design_adaptive`
