import { ThemeConfig, extendTheme } from "@chakra-ui/react";

import textStyles from "./typography";

const config: ThemeConfig = {
  initialColorMode: "light",
  useSystemColorMode: false,
};

export default extendTheme({
  textStyles,
  config,
});
