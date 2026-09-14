"use client";
import React from "react";
import {
  Button,
  Center,
  Divider,
  HStack,
  Input,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import Link from "next/link";

import { H3Text, H4Text } from "./_components/typography";
import AppCard from "./_components/app-card";
import { ATTACK_LIST } from "./_attacks/attacks";

export const ATTACK_USERNAME_LOCAL_STORAGE_KEY = "ATTACK_USERNAME";

const Home = () => {
  const [username, setUsername] = React.useState("");
  const [localStorageUsername, setLocalStorageUsername] = React.useState<string | null>(null);
  const [appIsReady, setAppIsReady] = React.useState<Boolean>();

  React.useEffect(() => {
    setAppIsReady(true);
    const savedLocalStorageUsername = localStorage.getItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY);

    if (savedLocalStorageUsername) {
      setLocalStorageUsername(savedLocalStorageUsername);
    }
  }, []);

  if (appIsReady && !localStorageUsername) {
    return (
      <Center>
        <VStack>
          <H4Text>Enter your username</H4Text>
          <HStack>
            <Input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Username" size="sm" />
            <Button
              size="sm"
              colorScheme="red"
              onClick={() => {
                localStorage.setItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY, username);
                setLocalStorageUsername(username);
              }}
            >
              Save
            </Button>
          </HStack>
        </VStack>
      </Center>
    );
  }

  return (
    <VStack align="start">
      <VStack w="100%">
        <H4Text>Welcome, {localStorageUsername}</H4Text>
        <Button
          size="sm"
          variant="link"
          onClick={() => {
            localStorage.removeItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY);
            setLocalStorageUsername(null);
          }}
        >
          Clear user
        </Button>
      </VStack>

      <Divider />

      <H3Text>List of attacks</H3Text>

      <AppCard>
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Platform</Th>
                <Th>Description</Th>
              </Tr>
            </Thead>

            <Tbody>
              {ATTACK_LIST.map((attack) => (
                <Tr key={attack.name}>
                  <Td>
                    <Button
                      as={attack.isDisabled ? undefined : Link}
                      variant="link"
                      href={attack.isDisabled ? undefined : `/attacks/${attack.id}`}
                      color="blue.400"
                      _hover={{ color: "blue.500" }}
                      isDisabled={attack.isDisabled}
                      shallow={attack.isDisabled ? undefined : true}
                    >
                      {attack.name}
                    </Button>
                  </Td>
                  <Td>{attack.platform}</Td>
                  <Td whiteSpace="wrap">{attack.description}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </AppCard>
    </VStack>
  );
};

export default Home;
