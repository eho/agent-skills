import { useEffect } from "react";
import { Image, Text, View } from "react-native";
import Animated, {
  Easing,
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";

import { useRuntimeTheme } from "../../lib/theme-runtime";

const mark = require("../../assets/splash-icon.png");

interface AppLaunchOverlayProps {
  appName: string;
  onFinish: () => void;
}

export function AppLaunchOverlay({
  appName,
  onFinish,
}: AppLaunchOverlayProps) {
  const theme = useRuntimeTheme();
  const opacity = useSharedValue(1);
  const scale = useSharedValue(0.96);
  const translateY = useSharedValue(12);

  useEffect(() => {
    scale.value = withTiming(1, {
      duration: 360,
      easing: Easing.out(Easing.cubic),
    });
    translateY.value = withTiming(0, {
      duration: 360,
      easing: Easing.out(Easing.cubic),
    });

    const timer = setTimeout(() => {
      opacity.value = withTiming(
        0,
        { duration: 260, easing: Easing.inOut(Easing.ease) },
        (finished) => {
          if (finished) {
            runOnJS(onFinish)();
          }
        }
      );
    }, 700);

    return () => clearTimeout(timer);
  }, [onFinish, opacity, scale, translateY]);

  const overlayStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  const contentStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }, { translateY: translateY.value }],
  }));

  return (
    <Animated.View
      className="absolute inset-0 items-center justify-center"
      pointerEvents="none"
      style={[{ backgroundColor: theme.launchBackground }, overlayStyle]}
    >
      <Animated.View className="items-center gap-4" style={contentStyle}>
        <View className="h-28 w-28 items-center justify-center rounded-3xl bg-background-50">
          <Image
            source={mark}
            className="h-20 w-20"
            resizeMode="contain"
            accessibilityIgnoresInvertColors
          />
        </View>
        <Text
          className="text-2xl font-semibold"
          style={{ color: theme.launchForeground }}
        >
          {appName}
        </Text>
      </Animated.View>
    </Animated.View>
  );
}
