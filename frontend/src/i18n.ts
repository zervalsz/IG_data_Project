import { getRequestConfig } from "next-intl/server";

export default getRequestConfig(async ({ locale }) => {
  // Handle favicon.ico or other non-locale requests that might slip through
  if (locale === 'favicon.ico') {
    return {
      locale: 'en',
      messages: {}
    };
  }

  const currentLocale = locale || "en";

  try {
    return {
      locale: currentLocale,
      messages: (await import(`../messages/${currentLocale}.json`)).default,
    };
  } catch (error) {
    console.error(`Failed to load messages for locale: ${currentLocale}`, error);
    return {
      locale: 'en',
      messages: (await import(`../messages/en.json`)).default,
    };
  }
});
