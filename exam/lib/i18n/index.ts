import uz from "./uz";
import ru from "./ru";
import en from "./en";

export type Lang = "uz" | "ru" | "en";
export type { DictKey } from "./uz";

export const dictionaries = { uz, ru, en } as const;

export const LOCALES: Record<Lang, string> = {
  uz: "uz-UZ",
  ru: "ru-RU",
  en: "en-US",
};

export function translate(
  lang: Lang,
  key: string,
  vars?: Record<string, string | number>
): string {
  let s: string =
    (dictionaries[lang] as Record<string, string>)[key] ??
    (uz as Record<string, string>)[key] ??
    key;
  if (vars) {
    for (const k in vars) s = s.split(`{${k}}`).join(String(vars[k]));
  }
  return s;
}
