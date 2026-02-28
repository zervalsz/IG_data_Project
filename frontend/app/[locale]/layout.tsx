import { NextIntlClientProvider } from 'next-intl'
import { getMessages } from 'next-intl/server'
import '../globals.css'

export default async function LocaleLayout({ children, params }: { children: React.ReactNode; params: { locale: string } }) {
  // params may be a thenable in Next.js; await it before accessing properties
  // (prevents the runtime error: `params` should be awaited before using its properties)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const awaitedParams: any = await (params as any)
  const { locale } = awaitedParams

  const messages = await getMessages({ locale })

  return (
    <NextIntlClientProvider messages={messages} locale={locale}>
      {children}
    </NextIntlClientProvider>
  )
}
