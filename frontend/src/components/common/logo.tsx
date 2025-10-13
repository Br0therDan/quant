"use client";

import { Box } from "@mui/material";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

interface MyLogoProps {
  alt?: string;
  className?: string;
  width?: number;
  height?: number;
  href?: string;
  icon?: boolean;
  noLink?: boolean;
}

export const MyLogo = ({
  alt = "MySingle",
  className = "",
  width = 60,
  height = 60,
  href,
  icon = false,
  noLink = false,
}: MyLogoProps) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // 초기 테마 감지 및 변경 감지
    const updateTheme = () => {
      setIsDarkMode(document.documentElement.classList.contains("dark"));
    };

    updateTheme();

    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  // 로고 경로 결정
  const logoSrc = icon
    ? "/images/icon.png"
    : isDarkMode
    ? "/images/logo_dark.png"
    : "/images/logo_light.png";

  const LogoImage = (
    <Box
      className={`relative ${className}`}
      sx={{ width, height, position: "relative" }}
    >
      <Image
        src={logoSrc}
        alt={alt}
        fill
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        priority
        style={{ objectFit: "contain" }}
      />
    </Box>
  );

  if (noLink || !href) {
    return LogoImage;
  }

  return (
    <Link href={href} className="inline-block">
      {LogoImage}
    </Link>
  );
};

export const MyLogoDark = MyLogo;
