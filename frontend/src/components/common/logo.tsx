"use client";

import { Box } from "@mui/material";
import Image from "next/image";
import Link from "next/link";
import PropTypes from "prop-types";
import type React from "react";
import { useEffect, useState } from "react";

// 테마에 따라 자동으로 로고를 변경하는 통합 컴포넌트
export const MyLogo = ({
	alt = "MySingle",
	className,
	width = 45,
	height = 60,
	href,
	icon = false, // 아이콘 모드 여부
	noLink = false, // Link 래핑 비활성화 옵션
	...props
}: React.ImgHTMLAttributes<HTMLImageElement> & {
	width?: number;
	height?: number;
	href?: string;
	icon?: boolean; // 아이콘 모드 속성 추가
	noLink?: boolean; // Link 래핑 비활성화 속성 추가
}) => {
	const [isDarkMode, setIsDarkMode] = useState(false);
	const [mounted, setMounted] = useState(false);

	// 클라이언트 사이드 렌더링 및 테마 감지
	useEffect(() => {
		setMounted(true);

		// 초기 테마 상태 감지
		setIsDarkMode(document.documentElement.classList.contains("dark"));

		// MutationObserver로 dark 클래스 변경 감지
		const observer = new MutationObserver((mutations) => {
			mutations.forEach((mutation) => {
				if (
					mutation.attributeName === "class" &&
					mutation.target === document.documentElement
				) {
					setIsDarkMode(document.documentElement.classList.contains("dark"));
				}
			});
		});

		// <html> 요소의 클래스 변경 감시 시작
		observer.observe(document.documentElement, { attributes: true });

		// 정리 함수
		return () => observer.disconnect();
	}, []);

	// 마운트 전에는 라이트 테마 로고 사용, 마운트 후에는 실제 테마에 따라 로고 변경
	// 아이콘 모드일 경우 정사각형 로고 사용
	const logoSrc = !mounted
		? icon
			? "/images/logo_sq_light.png"
			: "/images/logo_light.png"
		: isDarkMode
			? icon
				? "/images/logo_sq_dark.png"
				: "/images/logo_dark.png"
			: icon
				? "/images/logo_sq_light.png"
				: "/images/logo_light.png";

	const LogoImage = (
		<Box
			className={`relative ${className || ""}`}
			sx={{
				width: width,
				height: height,
				position: "relative",
			}}
		>
			<Image
				src={logoSrc}
				alt={alt}
				className="object-contain"
				fill
				sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
				priority
				{...props}
			/>
		</Box>
	);

	// noLink가 true이거나 href가 제공되지 않았을 때는 Link로 래핑하지 않음
	if (noLink || !href) {
		return LogoImage;
	}

	return (
		<Link href={href} className="inline-block">
			{LogoImage}
		</Link>
	);
};

MyLogo.propTypes = {
	alt: PropTypes.string,
	className: PropTypes.string,
	width: PropTypes.number,
	height: PropTypes.number,
	href: PropTypes.string,
	icon: PropTypes.bool,
	noLink: PropTypes.bool,
};

// 기존 코드와의 호환성을 위해 MyLogoDark 내보내기
export const MyLogoDark = MyLogo;
