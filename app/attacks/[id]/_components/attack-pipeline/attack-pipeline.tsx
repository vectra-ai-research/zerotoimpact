"use client";
import React from "react";
import { Divider, HStack, VStack } from "@chakra-ui/react";

import AttackPipelineInitialState from "./attack-pipeline-initial-state";
import { ATTACK_PIPELINE, Attack, CREATE_INFRASTRUCTURE_PIPELINE } from "@/app/_attacks/attacks";
import { AttackStep, AttackStepKey } from "../attack-overview-stepper";
import AttackPipelineStep from "./attack-pipeline-step";
import AttackPipelineStepSeparator from "./attack-pipeline-step-separator";
import { H5Text } from "@/app/_components/typography";
import { AttackStatus } from "../console/attack-console";

interface AttackPipelineProps {
  attack: Attack;
  step: AttackStep;
  status: AttackStatus | null;
  responseAttackStep: number | null;
  onStartAttack: () => void;
}

const AttackPipeline = ({ attack, step, status, responseAttackStep, onStartAttack }: AttackPipelineProps) => {
  const [createStep, setCreateStep] = React.useState<number | null>(0);
  const [attackStep, setAttackStep] = React.useState<number | null>(null);
  const [attackFailed, setAttackFailed] = React.useState<boolean>(false);

  const createPipelineSteps = CREATE_INFRASTRUCTURE_PIPELINE[attack.id];
  const attackPipelineSteps = ATTACK_PIPELINE[attack.id];

  React.useEffect(() => {
    if (responseAttackStep === null) return;

    // Failed
    if (status === "status_failed") {
      setAttackFailed(true);
    }

    if (status === "create_failed") {
      setCreateStep(responseAttackStep - 1);
      setAttackFailed(true);
    }

    if (status === "attack_failed") {
      setCreateStep(createPipelineSteps.length); // Set createStep to the last step plus 1 to show the last step as completed
      setAttackStep(responseAttackStep - 1);
      setAttackFailed(true);
    }

    // Create
    if (status === "create_started") {
      setCreateStep(responseAttackStep - 1);
    }

    if (status === "create_complete") {
      setCreateStep(responseAttackStep); // Set createStep to the last step plus 1 to show the last step as completed
    }

    // Attack
    if (status === "attack_started") {
      setCreateStep(createPipelineSteps.length); // Set createStep to the last step plus 1 to show the last step as completed
      setAttackStep(responseAttackStep - 1);
    }

    if (status === "attack_complete") {
      setCreateStep(createPipelineSteps.length); // Set createStep to the last step plus 1 to show the last step as completed
      setAttackStep(responseAttackStep); // Set attackStep to the last step plus 1 to show the last step as completed
    }
  }, [responseAttackStep, status]);

  React.useEffect(() => {
    if (step.key === AttackStepKey.Attack && step.isActive && attackStep === null && responseAttackStep === null) {
      setAttackStep(0);
    }
  }, [step]);

  if ((step.key === AttackStepKey.Create && !step.isActive) || step.key === AttackStepKey.Finish) {
    return (
      <AttackPipelineInitialState
        title={step.key === AttackStepKey.Create ? "Let's Start!" : "Let's do it again!"}
        buttonLabel={step.key === AttackStepKey.Create ? "Start Attack" : "Restart Attack"}
        onStartAttack={() => {
          setCreateStep(0);
          setAttackStep(null);
          onStartAttack();
          setAttackFailed(false);
        }}
      />
    );
  }

  return (
    <HStack w="100%" h="100%" alignItems="start">
      <VStack flex={1} gap={7} align="center" justify="center" height="100%">
        <H5Text>Create Infrastructure pipeline</H5Text>

        <VStack w="100%" p={2} overflowY="auto" height="100%">
          {createPipelineSteps.map((step, index) => {
            const StepState = (() => {
              if (createStep === null || createStep < index) return "pending";
              if (createStep > index) return "completed";
              if (attackFailed && createStep === index) return "failed";
              return "in-progress";
            })();

            const separatorState = (createStep || 0) > index ? "completed" : "pending";

            return (
              <React.Fragment key={index}>
                <AttackPipelineStep atackStepKey={AttackStepKey.Create} {...step} state={StepState} />
                <AttackPipelineStepSeparator state={separatorState} />
              </React.Fragment>
            );
          })}
        </VStack>
      </VStack>

      <Divider orientation="vertical" />

      <VStack flex={1} gap={7} align="center" justify="center" height="100%">
        <H5Text>Attack pipeline</H5Text>

        <VStack w="100%" p={2} overflowY="auto" height="100%">
          {attackPipelineSteps.map((step, index) => {
            const StepState = (() => {
              if (attackStep === null || attackStep < index) return "pending";
              if (attackStep > index) return "completed";
              return "in-progress";
            })();

            const separatorState = (attackStep || 0) > index ? "completed" : "pending";

            return (
              <React.Fragment key={index}>
                <AttackPipelineStep atackStepKey={AttackStepKey.Attack} {...step} state={StepState} />
                <AttackPipelineStepSeparator state={separatorState} />
              </React.Fragment>
            );
          })}
        </VStack>
      </VStack>
    </HStack>
  );
};

export default AttackPipeline;
