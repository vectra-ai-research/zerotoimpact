import { HStack, IconButton, Tooltip } from "@chakra-ui/react";
import { VscDebugStart } from "react-icons/vsc";
import { MdClose } from "react-icons/md";

import { AttackStep, AttackStepKey } from "./attack-overview-stepper";

interface AttackActionButtonProps {
  attackStep: AttackStep;
  onDestroy: () => void;
  onAttack: () => void;
}

const AttackActionButtons = ({ attackStep, onAttack, onDestroy }: AttackActionButtonProps) => {
  const shouldDisplayDestroyButton = attackStep.key === AttackStepKey.Destroy && !attackStep.isActive;
  const shouldDisplayAttackButton = attackStep.key === AttackStepKey.Attack && !attackStep.isActive;

  return (
    <HStack position="absolute" top="10px" right="10px">
      {shouldDisplayAttackButton && (
        <Tooltip label="Run Attack">
          <IconButton
            colorScheme="yellow"
            aria-label="Run Attack"
            size="lg"
            icon={<VscDebugStart color="white" />}
            onClick={onAttack}
          />
        </Tooltip>
      )}

      {shouldDisplayDestroyButton && (
        <Tooltip label="Destoy Infrastructure">
          <IconButton
            colorScheme="red"
            aria-label="Destoy Infrastructure"
            size="lg"
            icon={<MdClose color="white" />}
            onClick={onDestroy}
          />
        </Tooltip>
      )}
    </HStack>
  );
};

export default AttackActionButtons;
