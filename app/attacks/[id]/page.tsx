"use client";
import React from "react";
import { notFound } from "next/navigation";
import { Box, HStack, Tab, TabList, TabPanel, TabPanels, Tabs, Tooltip, VStack, theme } from "@chakra-ui/react";

import AppCard from "@/app/_components/app-card";
import AttackOverviewStepper, { AttackStep, AttackStepKey } from "./_components/attack-overview-stepper";
import AttackPipeline from "./_components/attack-pipeline/attack-pipeline";
import AttackConsole, { AttackStatus } from "./_components/console/attack-console";
import AttackActionButtons from "./_components/attack-action-buttons";
import { ATTACK_LIST } from "@/app/_attacks/attacks";
import { ATTACK_USERNAME_LOCAL_STORAGE_KEY } from "@/app/page";
import DownloadLogsButton from "./_components/download-logs-button";
import AttackReport from "./_components/console/attack-report";

interface DestroyResponse {
  response: {
    id: string;
    message: string[];
    status: "destroy_started" | "destroy_complete";
  };
}

const Page = ({ params }: { params: { id: string } }) => {
  const username = window.localStorage ? localStorage.getItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY)! : "";

  const [attackStep, setAttackStep] = React.useState<AttackStep>({
    key: AttackStepKey.Create,
    isActive: false,
  });

  const [responseAttackStep, setResponseAttackStep] = React.useState<number | null>(null);
  const [status, setStatus] = React.useState<AttackStatus | null>(null); // TDB: Move this elsewhere (global logs/request state?)
  const [logs, setLogs] = React.useState<string[]>([]); // TDB: Move this elsewhere (global logs/request state?)

  const attackId = Number(params.id);
  const attack = ATTACK_LIST.find((attack) => attack.id === attackId);
  if (!attack) return notFound();

  const handleStartAttack = React.useCallback(() => {
    setAttackStep({
      key: AttackStepKey.Create,
      isActive: false,
    });

    fetch(`http://localhost:3000/api/${attack.createEndpoint}/${username}`);

    setAttackStep({
      key: AttackStepKey.Create,
      isActive: true,
    });
  }, []);

  const handleRunAttack = () => {
    fetch(`http://localhost:3000/api/${attack.attackEndpoint}/${username}`);

    setAttackStep({
      key: AttackStepKey.Attack,
      isActive: true,
    });
    setResponseAttackStep(null);
  };

  const handleDestroy = () => {
    fetch(`http://localhost:3000/api/${attack.startDestroyEndpoint}/${username}`);

    setAttackStep({
      key: AttackStepKey.Destroy,
      isActive: true,
    });
  };

  const shouldDisplayReport = attackStep.key === AttackStepKey.Destroy && !attackStep.isActive;

  return (
    <VStack align="start" w="100%" flex={1} h={`calc(100% - 40px - ${theme.space[4]})`}>
      <AppCard w="100%" pr={2} minW="850px" h="65px">
        <AttackOverviewStepper attackStep={attackStep} />
      </AppCard>

      <HStack flex={1} w="100%" align="start" h={`calc(100% - 65px - ${theme.space[2]})`}>
        <AppCard flex={1} maxW="65%" h="100%">
          <Box h="100%" w="100%">
            <AttackPipeline
              responseAttackStep={responseAttackStep}
              attack={attack}
              status={status}
              step={attackStep}
              onStartAttack={handleStartAttack}
            />
          </Box>

          <AttackActionButtons attackStep={attackStep} onDestroy={handleDestroy} onAttack={handleRunAttack} />
        </AppCard>

        <AppCard h="100%" flex={1} maxW="35%" backgroundColor="gray.100" alignItems="start" px={0}>
          <Tabs align="end" variant="enclosed" w="100%" h="100%" borderColor="gray.300">
            <TabList pr={4}>
              <Tab _selected={{ borderColor: "inherit", borderBottomColor: "gray.100" }}>Activity Logs</Tab>
              <Tooltip
                isDisabled={shouldDisplayReport}
                label="API Exchange is available only after finishing the attack and not destroyed yet"
              >
                <Tab _selected={{ borderColor: "inherit", borderBottomColor: "gray.100" }} isDisabled={!shouldDisplayReport}>
                  API Exchange
                </Tab>
              </Tooltip>
            </TabList>

            <TabPanels h="calc(100% - 42px)">
              <TabPanel h="100%">
                <AttackConsole
                  logs={logs}
                  attack={attack}
                  step={attackStep}
                  setStep={setAttackStep}
                  setLogs={setLogs}
                  onChangeStep={(step) => setResponseAttackStep(step)}
                  onChangeStatus={(status) => setStatus(status)}
                />
              </TabPanel>
              {shouldDisplayReport && (
                <TabPanel h="100%" p={1} pr={0} pb={0}>
                  <AttackReport attack={attack} />

                  <DownloadLogsButton attack={attack} />
                </TabPanel>
              )}
            </TabPanels>
          </Tabs>
        </AppCard>
      </HStack>
    </VStack>
  );
};

export default Page;
