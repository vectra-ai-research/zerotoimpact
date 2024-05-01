"use client";
import { Avatar, HStack } from "@chakra-ui/react";
import Link from "next/link";

import { BodySmallText, H3Text } from "./typography";
import { ATTACK_USERNAME_LOCAL_STORAGE_KEY } from "../page";
import React from "react";

const AppHeader = () => {
  const [savedLocalStorageUsername, setLocalStorageUsername] = React.useState("Guest User");

  React.useEffect(() => {
    const savedLocalStorageUsername = localStorage.getItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY);

    if (savedLocalStorageUsername) {
      setLocalStorageUsername(savedLocalStorageUsername);
    }
  }, []);

  return (
    <HStack as="header" w="100svw" backgroundColor="red.300" h="60px" alignItems="center" justify="space-between" p={4}>
      <Link href="/">
        <H3Text textAlign="center">ZeroToImpact</H3Text>
        <BodySmallText>
          The ZeroToImpact Project: Simulate, understand, and mitigate cybersecurity threats from inception to impact
        </BodySmallText>
      </Link>

      <Avatar size="sm" name={savedLocalStorageUsername} backgroundColor="red.500" color="white" />
    </HStack>
  );
};

export default AppHeader;
