import { Page } from "@playwright/test";

export const loginUserAndWaitFor = async (page: Page, waitForURL: string) => {
  await page.route("*/**/api/me", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    await route.fulfill({
      json: {
        ...json,
        username: "FAKE_USER",
        first_name: "FAKE",
        full_name: "FAKE_USER",
        workspaces: ["WORKSPACE 1"],
      },
    });
  });

  await page.goto("/login");

  await page.getByPlaceholder("Enter your username").fill("damian");

  await page.getByPlaceholder("Enter your password").fill("12345678");

  await page.getByRole("button", { name: "Enter" }).click();

  await page.waitForURL(`**/${waitForURL}`);
};
