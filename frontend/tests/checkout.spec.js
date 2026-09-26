import { expect, test } from "@playwright/test";

for (const gateway of ["paypal", "stripe", "paystack", "flutterwave"]) {
  for (const outcome of ["success", "failure", "cancel"]) {
    test(`${gateway}: ${outcome}`, async ({ page }) => {
      await page.goto("/");
      await expect(
        page.getByText("Local simulator", { exact: true }),
      ).toBeVisible();
      if (gateway === "paypal" && outcome === "success")
        await page.screenshot({
          path: test.info().outputPath("checkout.png"),
          fullPage: true,
        });
      await page.locator(`input[value="${gateway}"]`).check();
      await page.getByLabel("Email address").fill("buyer@example.com");
      await page.getByRole("button", { name: "Open simulator" }).click();
      await expect(
        page.getByRole("heading", { name: "Choose a test outcome." }),
      ).toBeVisible();
      if (outcome === "cancel")
        await page
          .getByRole("link", { name: "Cancel checkout", exact: true })
          .click();
      else
        await page.getByRole("button", { name: `Simulate ${outcome}` }).click();
      const heading = {
        success: "Payment confirmed",
        failure: "Payment unsuccessful",
        cancel: "You left checkout",
      }[outcome];
      await expect(page.getByRole("heading", { name: heading })).toBeVisible();
      await expect(page.locator(".status")).toHaveText(
        { success: "paid", failure: "failed", cancel: "pending" }[outcome],
      );
      await page.reload();
      await expect(page.getByRole("heading", { name: heading })).toBeVisible();
      await expect(page.locator("body")).not.toContainText("buyer@example.com");
      await expect(page.locator("body")).not.toContainText("undefined");
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
    });
  }
}

test("unknown payment gives a recoverable error", async ({ page }) => {
  await page.goto(
    "/return/00000000-0000-4000-8000-000000000000?status=successful",
  );
  await expect(page.getByRole("alert")).toContainText("Payment not found");
  await expect(
    page.getByRole("heading", { name: "Payment confirmed" }),
  ).toHaveCount(0);
  await page.getByRole("link", { name: "New checkout" }).click();
  await expect(
    page.getByRole("heading", { name: "Try the payment flow." }),
  ).toBeVisible();
});

test("backend failure keeps the checkout retryable", async ({ page }) => {
  await page.route("**/api/checkout/payments", (route) =>
    route.fulfill({
      status: 502,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Provider temporarily unavailable." }),
    }),
  );
  await page.goto("/");
  await page.getByLabel("Email address").fill("buyer@example.com");
  await page.getByRole("button", { name: "Open simulator" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Provider temporarily unavailable",
  );
  await expect(
    page.getByRole("button", { name: "Open simulator" }),
  ).toBeEnabled();
  await page.unroute("**/api/checkout/payments");
  await page.getByRole("button", { name: "Open simulator" }).click();
  await expect(
    page.getByRole("heading", { name: "Choose a test outcome." }),
  ).toBeVisible();
});

test("sandbox without credentials explains setup and disables checkout", async ({
  page,
}) => {
  await page.route("**/api/checkout/config", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.mode = "sandbox";
    config.gateways.forEach((gateway) => {
      gateway.ready = false;
    });
    await route.fulfill({ json: config });
  });
  await page.goto("/");
  await expect(
    page.getByText("Provider sandbox", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("status")).toContainText("sandbox credentials");
  await expect(
    page.getByRole("button", { name: "Continue to PayPal" }),
  ).toBeDisabled();
});

test("corrupt session data does not prevent checkout", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() =>
    sessionStorage.setItem("checkout-attempt", "{broken"),
  );
  await page.getByLabel("Email address").fill("buyer@example.com");
  await page.getByRole("button", { name: "Open simulator" }).click();
  await expect(
    page.getByRole("heading", { name: "Choose a test outcome." }),
  ).toBeVisible();
});
