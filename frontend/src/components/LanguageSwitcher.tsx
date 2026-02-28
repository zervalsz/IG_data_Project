"use client";

import { useTransition } from "react";
import { useLocale } from "next-intl";
import { usePathname, useRouter } from "@/navigation";

const locales = [
  { code: "zh", label: "中文" },
  { code: "en", label: "EN" },
];

export function LanguageSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const activeLocale = useLocale();
  const [isPending, startTransition] = useTransition();

  return (
    <div className="flex items-center gap-2">
      {locales.map((locale) => {
        const isActive = locale.code === activeLocale;
        return (
          <button
            key={locale.code}
            type="button"
            onClick={() =>
              startTransition(() => {
                router.replace(pathname, { locale: locale.code });
              })
            }
            className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
              isActive
                ? "border-black bg-black text-white"
                : "border-black/20 text-black/70 hover:border-black/60 hover:text-black"
            } ${isPending ? "opacity-70" : ""}`}
            disabled={isPending}
          >
            {locale.label}
          </button>
        );
      })}
    </div>
  );
}
