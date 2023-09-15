import { test, expect } from "@playwright/test";
import { goToAnnotationPageWith12Ranking } from "./goToAnnotationPage";

test.use({
  viewport: { width: 1600, height: 1400 },
  userAgent: "Mac",
});

test.describe("Annotation page shortcuts for mac", () => {
  test.describe("Shortcuts panel", () => {
    test("open shortcut panel", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);

      await page.locator("span:last-child > .icon-button").click();
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot();
    });
  });
});
