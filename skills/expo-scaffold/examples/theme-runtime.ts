import { useColorScheme } from "nativewind";

export type ResolvedThemeName = "light" | "dark";

export interface RuntimeTheme {
  name: ResolvedThemeName;
  statusBarStyle: "light" | "dark";
  launchBackground: string;
  launchForeground: string;
}

const lightTheme: RuntimeTheme = {
  name: "light",
  statusBarStyle: "dark",
  launchBackground: "#ffffff",
  launchForeground: "#171717",
};

const darkTheme: RuntimeTheme = {
  name: "dark",
  statusBarStyle: "light",
  launchBackground: "#000000",
  launchForeground: "#f5f5f5",
};

export function useRuntimeTheme(): RuntimeTheme {
  const { colorScheme } = useColorScheme();
  return colorScheme === "dark" ? darkTheme : lightTheme;
}

