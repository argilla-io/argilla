import { Page } from "@playwright/test";

export type Role = "admin" | "owner" | "annotator";

export const loginUserAndWaitFor = async (
  page: Page,
  waitForURL: string,
  role: Role = "admin"
) => {
  await page.route("*/**/api/v1/me", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    await route.fulfill({
      json: {
        ...json,
        username: "FAKE_USER",
        first_name: "FAKE",
        full_name: "FAKE_USER",
        role,
        workspaces: ["WORKSPACE 1"],
      },
    });
  });

  await page.goto("/sign-in");

  await page.getByPlaceholder("Enter your username").fill("damian");

  await page.getByPlaceholder("Enter your password").fill("12345678");

  await page.getByRole("button", { name: "Enter" }).click();

  await page.waitForURL(`**/${waitForURL}`);
};
