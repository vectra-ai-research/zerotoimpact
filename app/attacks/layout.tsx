"use client";
import React from "react";
import { HStack, IconButton, VStack } from "@chakra-ui/react";
import { ArrowBackIcon } from "@chakra-ui/icons";
import { useParams } from "next/navigation";
import Link from "next/link";

import { BodyStrongLargeText } from "../_components/typography";
import { ATTACK_LIST } from "../_attacks/attacks";

const Layout = ({ children }: { children: React.ReactNode }) => {
  const params = useParams<{ id: string }>();

  const attackId = Number(params.id);
  const attack = ATTACK_LIST.find((attack) => attack.id === attackId);
  const attackName = attack?.name;

  const shouldDisplayNavigation = Boolean(attack);

  return (
    <VStack align="start" w="100%" h="100%" gap={4}>
      {shouldDisplayNavigation && (
        <HStack gap={0}>
          <Link href="/">
            <IconButton isRound={true} variant="" aria-label="Done" fontSize="20px" icon={<ArrowBackIcon />} />
          </Link>

          <BodyStrongLargeText>{attackName}</BodyStrongLargeText>
        </HStack>
      )}

      {children}
    </VStack>
  );
};

export default Layout;
