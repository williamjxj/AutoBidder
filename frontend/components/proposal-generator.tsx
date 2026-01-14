'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'

interface AnalysisResult {
  key_requirements: string[]
  technologies: string[]
  skills: string[]
  estimated_complexity: string
  match_score: number | null
}

interface ProposalResult {
  proposal: string
  confidence_score: number
  suggestions: string[]
  sources: string[]
}

export default function ProposalGenerator() {
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [customInstructions, setCustomInstructions] = useState('')
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [proposal, setProposal] = useState<ProposalResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const analyzeJob = async () => {
    if (!jobDescription) {
      setError('Please enter a job description')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/api/v1/proposals/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: jobDescription,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to analyze job requirements')
      }

      const data = await response.json()
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const generateProposal = async () => {
    if (!jobTitle || !jobDescription) {
      setError('Please enter both job title and description')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${apiUrl}/api/v1/proposals/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_requirement: {
            title: jobTitle,
            description: jobDescription,
            requirements: analysis?.key_requirements || [],
          },
          custom_instructions: customInstructions || null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate proposal')
      }

      const data = await response.json()
      setProposal(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Job Information</CardTitle>
          <CardDescription>Enter the job details to analyze and generate a proposal</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="jobTitle" className="text-sm font-medium">
              Job Title
            </label>
            <Input
              id="jobTitle"
              placeholder="e.g., Full-Stack Developer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="jobDescription" className="text-sm font-medium">
              Job Description
            </label>
            <Textarea
              id="jobDescription"
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="min-h-[200px]"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="customInstructions" className="text-sm font-medium">
              Custom Instructions (Optional)
            </label>
            <Textarea
              id="customInstructions"
              placeholder="Add any specific requirements or preferences..."
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              className="min-h-[100px]"
            />
          </div>

          <div className="flex gap-2">
            <Button onClick={analyzeJob} disabled={loading}>
              {loading ? 'Analyzing...' : 'Analyze Job'}
            </Button>
            <Button onClick={generateProposal} disabled={loading} variant="secondary">
              {loading ? 'Generating...' : 'Generate Proposal'}
            </Button>
          </div>

          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Job Analysis</CardTitle>
            <CardDescription>AI-powered analysis of the job requirements</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Key Requirements</h3>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {analysis.key_requirements.map((req, idx) => (
                  <li key={idx}>{req}</li>
                ))}
              </ul>
            </div>

            {analysis.technologies.length > 0 && (
              <div>
                <h3 className="font-medium mb-2">Technologies</h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.technologies.map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-primary/10 text-primary rounded-md text-sm"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {analysis.skills.length > 0 && (
              <div>
                <h3 className="font-medium mb-2">Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h3 className="font-medium mb-2">Complexity</h3>
              <span className="px-3 py-1 bg-accent text-accent-foreground rounded-md text-sm">
                {analysis.estimated_complexity}
              </span>
            </div>

            {analysis.match_score !== null && (
              <div>
                <h3 className="font-medium mb-2">Match Score</h3>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${analysis.match_score * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {(analysis.match_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {proposal && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Proposal</CardTitle>
            <CardDescription>
              AI-generated proposal with {(proposal.confidence_score * 100).toFixed(0)}% confidence
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted p-4 rounded-md whitespace-pre-wrap text-sm">
              {proposal.proposal}
            </div>

            {proposal.suggestions.length > 0 && (
              <div>
                <h3 className="font-medium mb-2">Suggestions for Improvement</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  {proposal.suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}

            {proposal.sources.length > 0 && (
              <div>
                <h3 className="font-medium mb-2">Knowledge Sources</h3>
                <div className="flex flex-wrap gap-2">
                  {proposal.sources.map((source, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <Button
              onClick={() => {
                navigator.clipboard.writeText(proposal.proposal)
              }}
              variant="outline"
            >
              Copy to Clipboard
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
