"use client";
import {
  Box,
  Spinner,
  Step,
  StepDescription,
  StepIcon,
  StepIndicator,
  StepNumber,
  StepSeparator,
  StepStatus,
  StepTitle,
  Stepper,
} from "@chakra-ui/react";

export interface AttackStep {
  key: AttackStepKey;
  isActive: boolean;
}

export enum AttackStepKey {
  Create = 0,
  Attack = 1,
  Destroy = 2,
  Finish = 3,
}

interface Step {
  key: "create" | "attack" | "destroy";
  title: string;
  description: string;
}

interface AttackOverviewStepperProps {
  attackStep: AttackStep;
}

export const STEPS: Step[] = [
  { key: "create", title: "First", description: "Create vulnerable infrastructure" },
  { key: "attack", title: "Second", description: "Run attack" },
  { key: "destroy", title: "Third", description: "Destroy infrastructure" },
];

const AttackOverviewStepper = ({ attackStep }: AttackOverviewStepperProps) => {
  return (
    <Stepper index={attackStep.key} colorScheme="red" w="100%">
      {STEPS.map((step) => (
        <Step key={step.key}>
          <StepIndicator>
            <StepStatus
              complete={<StepIcon />}
              incomplete={<StepNumber />}
              active={attackStep.isActive ? <Spinner size="sm" /> : <StepNumber />}
            />
          </StepIndicator>

          <Box flexShrink="0">
            <StepTitle>{step.title}</StepTitle>
            <StepDescription>{step.description}</StepDescription>
          </Box>

          <StepSeparator />
        </Step>
      ))}
    </Stepper>
  );
};

export default AttackOverviewStepper;
