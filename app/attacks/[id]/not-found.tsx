"use client";
import { Link } from "@chakra-ui/next-js";
import { Center, Divider, HStack, VStack } from "@chakra-ui/react";

import { BodyStrongMediumText, H2Text } from "@/app/_components/typography";

export default function NotFound() {
  return (
    <VStack as={Center} h="100%" w="100%">
      <HStack>
        <H2Text>404</H2Text>

        <Divider orientation="vertical" />

        <BodyStrongMediumText>Could not find this attack.</BodyStrongMediumText>
      </HStack>

      <Link href="/" color="blue.400" _hover={{ color: "blue.500" }}>
        Return Home
      </Link>
    </VStack>
  );
}
