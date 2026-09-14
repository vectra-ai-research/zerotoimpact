import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Box, ColorModeScript, VStack, theme } from "@chakra-ui/react";

import { Providers } from "./providers";
import AppHeader from "./_components/app-header";
import NextTopLoader from "nextjs-toploader";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ZeroToImpact",
  description: "Attacks Across The Cyber Killchain Simulator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <NextTopLoader color="#960303" initialPosition={0.08} height={6} showSpinner={false} />

        <Providers>
          <ColorModeScript initialColorMode={theme.config.initialColorMode} />

          <VStack as="main" w="100svw" h="100svh" align="start" gap={0}>
            <AppHeader />

            <Box flex={1} w="100%" h={`calc(100% - 60px)`} p={4}>
              {children}
            </Box>
          </VStack>
        </Providers>
      </body>
    </html>
  );
}
