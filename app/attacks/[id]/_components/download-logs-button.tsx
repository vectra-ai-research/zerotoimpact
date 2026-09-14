import { FaFileDownload } from "react-icons/fa";
import { IconButton, Tooltip } from "@chakra-ui/react";

import { Attack } from "@/app/_attacks/attacks";
import { ATTACK_USERNAME_LOCAL_STORAGE_KEY } from "@/app/page";
import { ApiResponse } from "./console/attack-console";

interface DownloadLogsButtonProps {
  attack: Attack;
}

const DownloadLogsButton = ({ attack }: DownloadLogsButtonProps) => {
  const username = window.localStorage ? localStorage.getItem(ATTACK_USERNAME_LOCAL_STORAGE_KEY)! : "";

  const handleDownload = () => {
    fetch(`http://localhost:3000/api/${attack.statusEndpoint}/${username}`)
      .then((res) => res.json())
      .then((data: ApiResponse) => {
        const apiExchange = data.response.exchange;
        var element = document.createElement("a");
        element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(JSON.stringify(apiExchange, null, 4)));
        element.setAttribute("download", "logs.txt");

        element.style.display = "none";
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
      });
  };

  return (
    <Tooltip label="Download logs">
      <IconButton
        position="absolute"
        bottom="25px"
        right="25px"
        colorScheme="red"
        aria-label="Download logs"
        size="lg"
        icon={<FaFileDownload color="white" />}
        onClick={handleDownload}
      />
    </Tooltip>
  );
};

export default DownloadLogsButton;
