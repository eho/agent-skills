# Theme And Color Mode

Use official gluestack-ui and NativeWind docs as the source of truth. Existing apps can show useful patterns, but gluestack CLI output and docs may drift across SDKs and gluestack releases.

## Default For gluestack-ui v3

For a new scaffold, make the app follow the system appearance:

```tsx
<GluestackUIProvider mode="system">
  {children}
</GluestackUIProvider>
```

gluestack-ui v3 supports color mode through the provider `mode` prop and CSS-variable token maps. Prefer this token path for the scaffold because it keeps screens readable:

- Define light and dark values in `components/ui/gluestack-ui-provider/config.ts` with `vars(...)`.
- Map Tailwind colors to CSS variables, such as `rgb(var(--color-background-0)/<alpha-value>)`.
- Use token classes in app code: `bg-background-0`, `text-typography-900`, `border-outline-200`, `bg-primary-500`.
- Avoid defaulting to `dark:bg-*` and `dark:text-*` pairs for normal surfaces, text, borders, buttons, cards, and reusable primitives.

Use `dark:` classes only for intentional exceptions outside the token system, or when official docs say a generated component expects them.

## NativeWind Dark Mode Strategy

gluestack's dark-mode docs describe two strategies:

- CSS-variable tokens with provider mode.
- Tailwind/NativeWind `dark:` classes.

For token-based gluestack styling, do not add extra `DARK_MODE=...` scripts unless current docs or CLI output require it. If the scaffold deliberately uses `dark:` classes, follow the current gluestack docs: native devices may require `darkMode: "media"` while web may require `darkMode: "class"`. Re-check before writing scripts because this is explicitly documented as a temporary workaround.

## Status Bar And JS-Only Theme Values

Token classes do not cover every runtime value. Add a small helper only when needed for values that cannot be expressed through gluestack/NativeWind classes:

- `expo-status-bar` style.
- Splash or launch overlay colors.
- Blur tint.
- Chart colors.
- Gradients.
- Third-party provider theme objects.

For the system-following default, keep this helper read-only. Do not add a persisted theme store unless the user asks for an in-app light/dark/system preference.

Use `examples/theme-runtime.ts` if JS-only theme values are needed. Otherwise keep the scaffold simpler and rely on `GluestackUIProvider mode="system"`.

## Root Layout

The root layout should wrap the router with the generated gluestack provider. For Expo Router:

```tsx
import "@/global.css";

import { GluestackUIProvider } from "@/components/ui/gluestack-ui-provider";
import { StatusBar } from "expo-status-bar";
import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <GluestackUIProvider mode="system">
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }} />
    </GluestackUIProvider>
  );
}
```

If the generated provider API differs, use the generated API. Do not hand-write a provider that conflicts with the CLI output.

## References

- Official gluestack dark mode docs: `https://gluestack.io/ui/docs/home/theme-configuration/dark-mode`
- Official gluestack theme customization docs: `https://gluestack.io/ui/docs/home/theme-configuration/customizing-theme`
- Official NativeWind color scheme hook: `https://www.nativewind.dev/docs/api/use-color-scheme`

