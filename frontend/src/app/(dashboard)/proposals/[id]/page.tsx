/**
 * Proposal Detail Page
 *
 * Displays proposal content with quality score and suggestions (T034, FR-009).
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { PageHeader } from '@/components/shared/page-header'
import { PageContainer } from '@/components/shared/page-container'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { getProposal, getProposalQuality } from '@/lib/api/client'
import { LoadingSkeleton } from '@/components/workflow/progress-overlay'
import { ArrowLeft } from 'lucide-react'

export default function ProposalDetailPage() {
  const router = useRouter()
  const params = useParams()
  const id = params?.id as string
  const [proposal, setProposal] = useState<any | null>(null)
  const [quality, setQuality] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [qualityError, setQualityError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      if (!id) return
      setIsLoading(true)
      try {
        const p = await getProposal(id)
        setProposal(p)
        if (p) {
          try {
            const q = await getProposalQuality(id)
            setQuality(q)
          } catch {
            setQualityError('Quality data not available')
          }
        }
      } catch (error) {
        console.error('Error loading proposal:', error)
        setProposal(null)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [id])

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingSkeleton lines={8} />
      </PageContainer>
    )
  }

  if (!proposal) {
    return (
      <PageContainer>
        <p className="text-muted-foreground">Proposal not found.</p>
        <Button variant="outline" onClick={() => router.push('/proposals')} className="mt-4">
          Back to Proposals
        </Button>
      </PageContainer>
    )
  }

  return (
    <PageContainer className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/proposals')}
          aria-label="Back to proposals"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <PageHeader
          title={proposal.title}
          description={`Status: ${proposal.status}`}
        />
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge variant="secondary" className="capitalize">
          {proposal.status}
        </Badge>
        {proposal.source === 'auto_generated' && (
          <Badge variant="outline">Auto-generated</Badge>
        )}
        {proposal.quality_score != null && (
          <Badge variant="default">Quality: {proposal.quality_score}/100</Badge>
        )}
      </div>

      <Card>
        <CardHeader>
          <h3 className="font-semibold">Proposal Content</h3>
        </CardHeader>
        <CardContent className="space-y-4">
          {proposal.budget && (
            <p className="text-sm text-muted-foreground">
              <strong>Budget:</strong> {proposal.budget}
            </p>
          )}
          {proposal.timeline && (
            <p className="text-sm text-muted-foreground">
              <strong>Timeline:</strong> {proposal.timeline}
            </p>
          )}
          <div className="prose dark:prose-invert max-w-none">
            <p className="whitespace-pre-wrap">{proposal.description}</p>
          </div>
        </CardContent>
      </Card>

      {/* Quality Score & Suggestions (T034) */}
      {(quality || proposal.quality_score != null) && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Quality Feedback</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            {qualityError && (
              <p className="text-sm text-muted-foreground">{qualityError}</p>
            )}
            {quality && (
              <>
                <div>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span>Overall Score</span>
                    <span className="font-medium">
                      {quality.overall_score ?? proposal.quality_score ?? 0}/100
                    </span>
                  </div>
                  <Progress
                    value={quality.overall_score ?? proposal.quality_score ?? 0}
                    className="h-2"
                  />
                </div>
                {quality.dimension_scores &&
                  Object.keys(quality.dimension_scores).length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium mb-2">
                        Dimension Scores
                      </h4>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                        {Object.entries(quality.dimension_scores).map(
                          ([dim, score]) => (
                            <div
                              key={dim}
                              className="flex justify-between rounded bg-muted/50 px-2 py-1"
                            >
                              <span className="capitalize">{dim}</span>
                              <span>{Math.round(Number(score))}</span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
                {quality.suggestions && quality.suggestions.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Suggestions</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {quality.suggestions.map((s: string, i: number) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={() => router.push(`/proposals/new?editId=${proposal.id}`)}
        >
          Edit
        </Button>
        <Button variant="outline" onClick={() => router.push('/proposals')}>
          Back to List
        </Button>
      </div>
    </PageContainer>
  )
}
