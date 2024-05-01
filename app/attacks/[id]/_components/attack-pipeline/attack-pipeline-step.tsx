import Img from "next/image";
import {
  Image,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Spinner,
  VStack,
} from "@chakra-ui/react";

import { BodyMediumText, H5Text } from "@/app/_components/typography";
import AppCard from "@/app/_components/app-card";
import { AttackStepKey } from "../attack-overview-stepper";

interface AttackPipelineStepDescription {
  title?: string;
  content: string;
}

export interface AttackPipelineStepProps {
  atackStepKey: AttackStepKey;
  title: string;
  imageSrc?: any;
  description: AttackPipelineStepDescription;
  state?: "completed" | "in-progress" | "pending" | "failed";
}

const AttackPipelineStep = ({ atackStepKey, title, imageSrc, description, state = "pending" }: AttackPipelineStepProps) => {
  const color = (() => {
    if (state === "failed") return "red";
    if (state === "completed") return "green";
    if (state === "in-progress") return "yellow";
    return "gray";
  })();

  return (
    <Popover trigger="hover" placement={atackStepKey === AttackStepKey.Create ? "right" : "left"}>
      <PopoverTrigger>
        <AppCard
          as={VStack}
          cursor="pointer"
          w="250px"
          minW="250px"
          h="140px"
          minH="140px"
          borderWidth="2px"
          alignItems="center"
          justifyContent="center"
          borderColor={`${color}.300`}
          position="relative"
          bg={`${color}.50`}
        >
          <H5Text>{title}</H5Text>
          {imageSrc && (
            <Image w="50px" as={Img} src={imageSrc} alt="Pipeline flow create" objectFit="contain" borderRadius="10px" />
          )}

          {state === "in-progress" && <Spinner size="sm" position="absolute" top="8px" right="8px" />}
        </AppCard>
      </PopoverTrigger>

      <PopoverContent bg={`${color}.100`}>
        {description.title && <PopoverHeader>{description.title}</PopoverHeader>}
        <PopoverArrow bg={`${color}.100`} />
        <PopoverBody>
          <BodyMediumText>{description.content}</BodyMediumText>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

export default AttackPipelineStep;
