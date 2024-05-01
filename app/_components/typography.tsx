"use client";
import { Text, TextProps, forwardRef } from "@chakra-ui/react";

// Heading
export const H1Text = forwardRef<TextProps, "h1">(({ textStyle = "h1", as = "h1", ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const H2Text = forwardRef<TextProps, "h2">(({ textStyle = "h2", as = "h2", ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const H3Text = forwardRef<TextProps, "h3">(({ textStyle = "h3", as = "h3", ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const H4Text = forwardRef<TextProps, "h4">(({ textStyle = "h4", as = "h4", ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const H5Text = forwardRef<TextProps, "h5">(({ textStyle = "h5", as = "h5", ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const H6Text = forwardRef<TextProps, "h6">(({ textStyle = "h6", as = "h6", ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

// Subtitle
export const SubtitleLargeText = forwardRef<TextProps, "span">(({ textStyle = "subtitleLg", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const SubtitleMediumText = forwardRef<TextProps, "span">(({ textStyle = "subtitleMd", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

// Body
export const BodyLargeText = forwardRef<TextProps, "span">(({ textStyle = "bodyLg", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyExtraLargeText = forwardRef<TextProps, "span">(({ textStyle = "bodyExtraLg", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyMediumText = forwardRef<TextProps, "span">(({ textStyle = "bodyMd", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodySmallText = forwardRef<TextProps, "span">(({ textStyle = "bodySm", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyXsText = forwardRef<TextProps, "span">(({ textStyle = "bodyXs", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyStrongLargeText = forwardRef<TextProps, "span">(({ textStyle = "bodyStrongLg", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyStrongMediumText = forwardRef<TextProps, "span">(({ textStyle = "bodyStrongMd", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyStrongSmallText = forwardRef<TextProps, "span">(({ textStyle = "bodyStrongSm", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));

export const BodyStrongXsText = forwardRef<TextProps, "span">(({ textStyle = "bodyStrongXs", as, ...rest }, ref) => (
  <Text ref={ref} textStyle={textStyle} as={as} {...rest} />
));
