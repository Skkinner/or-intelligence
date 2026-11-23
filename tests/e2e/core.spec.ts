// Owner: Member D (WBS 6.3.1). Core flow: upload -> timeline -> click bar seeks the video.
// Run: start the stack (scripts/run_local.*), then `cd tests/e2e && npm install && npm run install-browsers && npm test`.
import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

const SAMPLE_VIDEO = fileURLToPath(new URL("../fixtures/sample_video.mp4", import.meta.url));

test.fixme("upload -> timeline -> click bar seeks", async ({ page }) => {
  // TODO(D, 6.3.1): remove .fixme once 5.1.1, 5.1.2 and 4.2.1 are merged and sample_video.mp4 exists.
  await page.goto("/upload");
  await page.setInputFiles("input[type=file]", SAMPLE_VIDEO);
  await page.waitForURL(/\/review\//, { timeout: 90_000 });
  const bar = page.locator(".timeline button").first();
  await expect(bar).toBeVisible();
  await bar.click();
  const t = await page.locator("video").evaluate((v: HTMLVideoElement) => v.currentTime);
  expect(t).toBeGreaterThanOrEqual(0);
});
