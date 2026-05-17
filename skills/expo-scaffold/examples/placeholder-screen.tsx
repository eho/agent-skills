import { Box } from "@/components/ui/box";
import { Button, ButtonText } from "@/components/ui/button";
import { Heading } from "@/components/ui/heading";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";

export default function HomeScreen() {
  return (
    <Box className="flex-1 bg-background-0 px-6 py-12">
      <VStack space="lg" className="mx-auto w-full max-w-md">
        <VStack space="sm">
          <Heading size="2xl">Ready to build</Heading>
          <Text className="text-typography-600">
            This screen verifies Expo Router, NativeWind, and gluestack-ui are
            wired together.
          </Text>
        </VStack>

        <Button>
          <ButtonText>Continue</ButtonText>
        </Button>

        <Text className="text-typography-500">
          Development builds use expo-dev-client for native runtime testing.
        </Text>
      </VStack>
    </Box>
  );
}
