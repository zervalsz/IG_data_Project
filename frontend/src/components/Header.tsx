"use client";

import { Link } from "@/navigation";
import { useTranslations } from "next-intl";
import { LanguageSwitcher } from "./LanguageSwitcher";

interface HeaderProps {
  currentLocale: string;
}

export function Header({ currentLocale }: HeaderProps) {
  const t = useTranslations("header");

  const navItems = [
    { href: "/style-generator", label: t("nav.styleGenerator") },
    { href: "/trend-generator", label: t("nav.trendGenerator") },
    { href: "/#creators", label: t("nav.creators") },
  ];

  return (
    <header className="border-b border-black/10 bg-white/90 backdrop-blur">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          {t("brand")}
        </Link>
        <nav className="hidden items-center gap-6 text-sm text-black/70 md:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-black">
              {item.label}
            </Link>
          ))}
        </nav>
        <LanguageSwitcher />
      </div>
    </header>
  );
}
