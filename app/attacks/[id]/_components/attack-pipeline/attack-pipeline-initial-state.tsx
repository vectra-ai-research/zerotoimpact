"use client";
import { Button, Center, VStack } from "@chakra-ui/react";
import { VscDebugStart } from "react-icons/vsc";

import { H3Text } from "@/app/_components/typography";

interface AttackPipelineInitialStateProps {
  title: string;
  buttonLabel: string;
  onStartAttack: () => void;
}

const AttackPipelineInitialState = ({ title, buttonLabel, onStartAttack }: AttackPipelineInitialStateProps) => {
  return (
    <Center w="100%" h="100%" as={VStack}>
      <H3Text color="gray.600">{title}</H3Text>
      <Button leftIcon={<VscDebugStart />} onClick={onStartAttack}>
        {buttonLabel}
      </Button>
    </Center>
  );
};

export default AttackPipelineInitialState;
