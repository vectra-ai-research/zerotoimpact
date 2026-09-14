import React from "react";
import { Box } from "@chakra-ui/react";

import { Attack } from "@/app/_attacks/attacks";
import { ATTACK_USERNAME_LOCAL_STORAGE_KEY } from "@/app/page";
import { BodyStrongSmallText } from "@/app/_components/typography";
import { ApiResponse } from "./attack-console";

interface AttackReportProps {
  attack: Attack;
}

const AttackReport = ({ attack }: AttackReportProps) => {
  const [report, setReport] = React.useState<string | null>(null);

  React.useEffect(() => {
    const username = window.localStorage ? localStorage.getItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY)! : "";

    fetch(`http://localhost:3000/api/${attack.statusEndpoint}/${username}`)
      .then((res) => res.json())
      .then((data: ApiResponse) => {
        const response = data.response;
        const apiExchange = response.exchange;
        setReport(JSON.stringify(apiExchange, null, 4));
      });
  }, []);

  return (
    <Box h="100%" overflow="auto">
      <BodyStrongSmallText as="pre" fontFamily="Consolas" textAlign="start">
        {report}
      </BodyStrongSmallText>
    </Box>
  );
};

export default AttackReport;
