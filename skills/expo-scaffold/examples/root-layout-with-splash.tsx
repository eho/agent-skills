import "@/global.css";

import { useEffect, useRef, useState } from "react";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";

import { GluestackUIProvider } from "@/components/ui/gluestack-ui-provider";
import { AppLaunchOverlay } from "@/components/layout/AppLaunchOverlay";
import { useRuntimeTheme } from "@/lib/theme-runtime";

SplashScreen.preventAutoHideAsync();
SplashScreen.setOptions({
  duration: 300,
  fade: true,
});

export default function RootLayout() {
  const [isReady, setIsReady] = useState(false);
  const [showLaunchOverlay, setShowLaunchOverlay] = useState(true);
  const didHideSplash = useRef(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Load local-only startup work here, such as fonts or persisted stores.
      } finally {
        setIsReady(true);
      }
    }

    void prepare();
  }, []);

  useEffect(() => {
    if (!isReady || didHideSplash.current) {
      return;
    }

    didHideSplash.current = true;
    SplashScreen.hideAsync().catch((error) => {
      console.error("Failed to hide splash screen", error);
    });
  }, [isReady]);

  if (!isReady) {
    return null;
  }

  return (
    <GluestackUIProvider mode="system">
      <AppShell />
      {showLaunchOverlay ? (
        <AppLaunchOverlay
          appName="App Name"
          onFinish={() => setShowLaunchOverlay(false)}
        />
      ) : null}
    </GluestackUIProvider>
  );
}

function AppShell() {
  const theme = useRuntimeTheme();

  return (
    <>
      <StatusBar style={theme.statusBarStyle} />
      <Stack screenOptions={{ headerShown: false }} />
    </>
  );
}
