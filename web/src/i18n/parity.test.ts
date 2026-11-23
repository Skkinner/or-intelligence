// Owner: Member A (WBS 5.2.3). CI checks that en.json and ar.json have identical keys.
import { describe, expect, it } from "vitest";
import en from "./en.json";
import ar from "./ar.json";

describe("i18n key parity (en <-> ar)", () => {
  it("has exactly the same keys", () => {
    expect(Object.keys(ar).sort()).toEqual(Object.keys(en).sort());
  });

  // TODO(A, 5.2.3): un-skip once every Arabic string is translated (empty strings fall back to English).
  it.skip("has a translation for every key", () => {
    const missing = Object.entries(ar).filter(([, v]) => !v).map(([k]) => k);
    expect(missing).toEqual([]);
  });
});
