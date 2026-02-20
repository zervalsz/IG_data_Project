import { LandingPage } from '@/components/LandingPage'

interface PageProps {
  params: { locale: string }
}

export default async function LocalePage({ params }: PageProps) {
  // render the new LandingPage
  return <LandingPage />
}
