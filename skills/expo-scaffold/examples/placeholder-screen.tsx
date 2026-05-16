import { Badge, BadgeText } from "@/components/ui/badge";
import { Box } from "@/components/ui/box";
import { Button, ButtonText } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Divider } from "@/components/ui/divider";
import { Heading } from "@/components/ui/heading";
import { Input, InputField } from "@/components/ui/input";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";

export default function HomeScreen() {
  return (
    <Box className="flex-1 bg-background-0 px-6 py-12">
      <VStack space="lg" className="mx-auto w-full max-w-md">
        <Badge className="self-start">
          <BadgeText>Expo starter</BadgeText>
        </Badge>

        <VStack space="sm">
          <Heading size="2xl">Ready to build</Heading>
          <Text className="text-typography-600">
            This screen verifies Expo Router, NativeWind, and gluestack-ui are
            wired together.
          </Text>
        </VStack>

        <Card className="gap-4 rounded-lg border border-outline-200 p-5">
          <VStack space="md">
            <Input>
              <InputField placeholder="Project note" />
            </Input>
            <Divider />
            <Button>
              <ButtonText>Continue</ButtonText>
            </Button>
          </VStack>
        </Card>
      </VStack>
    </Box>
  );
}
