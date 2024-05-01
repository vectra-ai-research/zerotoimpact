import { Box, theme } from "@chakra-ui/react";

interface AttackPipelineStepSeparatorProps {
  state?: "completed" | "pending";
}

const AttackPipelineStepSeparator = ({ state = "pending" }: AttackPipelineStepSeparatorProps) => {
  return (
    <Box
      h="100px"
      minH="100px"
      w="2px"
      backgroundColor={state === "completed" ? "green.300" : "gray.300"}
      borderRadius="1px"
      _last={{ display: "none" }}
      position="relative"
      top="-2px"
    >
      <Box
        w={0}
        h={0}
        borderTop={`10px solid ${state === "completed" ? theme.colors.green[300] : theme.colors.gray[300]}`}
        borderRight={`5px solid transparent`}
        borderLeft={`5px solid transparent`}
        position="absolute"
        bottom="-5px"
        right="-4px"
      />
    </Box>
  );
};

export default AttackPipelineStepSeparator;
