// Owner: Member A (WBS 5.2.3). CI checks that en.json and ar.json have identical keys.
import { describe, expect, it } from "vitest";
import en from "./en.json";
import ar from "./ar.json";

describe("i18n key parity (en <-> ar)", () => {
  it("has exactly the same keys", () => {
    expect(Object.keys(ar).sort()).toEqual(Object.keys(en).sort());
  });

  it("has a translation for every key", () => {
    const missing = Object.entries(ar)
      .filter(([, v]) => !v || v.trim().length === 0)
      .map(([k]) => k);
    expect(missing).toEqual([]);
  });

  it("preserves interpolation placeholders ({percent}, {error}, {time}, {wbs}) between en and ar", () => {
    const extractPlaceholders = (s: string) => (s.match(/\{\w+\}/g) ?? []).sort();
    for (const [key, enVal] of Object.entries(en)) {
      const arVal = (ar as Record<string, string>)[key] ?? "";
      expect(extractPlaceholders(arVal)).toEqual(extractPlaceholders(enVal));
    }
  });
});

