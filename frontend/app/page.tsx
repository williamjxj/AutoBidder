import ProposalGenerator from '@/components/proposal-generator'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-muted">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Auto Bidder AI</h1>
          <p className="text-muted-foreground text-lg">
            AI-powered proposal automation agent
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Seamlessly integrates job scraping, requirement analysis, and personalized proposal drafting
          </p>
        </div>

        <ProposalGenerator />

        <footer className="mt-12 text-center text-sm text-muted-foreground">
          <p>Powered by LangChain, Llama-index, and OpenAI</p>
        </footer>
      </div>
    </main>
  )
}
