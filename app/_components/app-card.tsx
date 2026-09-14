"use client";
import React from "react";

import { BoxProps, Flex } from "@chakra-ui/react";

const AppCard = React.forwardRef(({ children, ...props }: BoxProps, ref) => {
  return (
    <Flex
      ref={ref}
      borderWidth="1px"
      borderColor="gray.300"
      borderStyle="solid"
      borderRadius="10px"
      p={2}
      alignItems="center"
      position="relative"
      {...props}
    >
      {children}
    </Flex>
  );
});

export default AppCard;
