import "../global.css";

// Place this at src/app/_layout.tsx for SDK 55-style projects. The same import
// shape also works for root-level app/_layout.tsx when global.css is at root.
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

import { GluestackUIProvider } from "../components/ui/gluestack-ui-provider";

export default function RootLayout() {
  return (
    <GluestackUIProvider mode="system">
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }} />
    </GluestackUIProvider>
  );
}
