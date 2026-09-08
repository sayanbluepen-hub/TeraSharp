import { useState, useCallback, useRef } from 'react'
import { DEMO_MODE } from '../utils/constants'
import { mockEnhanceImage, type EnhancementJob, type EnhancementOptions, clearMockJob, getMockJob } from '../services/mockApi'
import { realEnhanceImage, pollJobStatus } from '../services/api'

export type EnhancementStatus = 'idle' | 'processing' | 'complete' | 'error'

interface UseEnhancementReturn {
  status: EnhancementStatus
  currentStep: number
  job: EnhancementJob | null
  error: string | null
  startEnhancement: (file: File | null, previewUrl: string, options: EnhancementOptions) => Promise<void>
  reset: () => void
}

export function useEnhancement(): UseEnhancementReturn {
  const [status, setStatus] = useState<EnhancementStatus>('idle')
  const [currentStep, setCurrentStep] = useState(0)
  const [job, setJob] = useState<EnhancementJob | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const reset = useCallback(() => {
    setStatus('idle')
    setCurrentStep(0)
    setJob(null)
    setError(null)
    clearMockJob()
    if (pollingRef.current) clearInterval(pollingRef.current)
  }, [])

  const startEnhancement = useCallback(async (
    file: File | null,
    previewUrl: string,
    options: EnhancementOptions,
  ) => {
    setStatus('processing')
    setCurrentStep(0)
    setError(null)

    try {
      if (DEMO_MODE) {
        const completedJob = await mockEnhanceImage(file, previewUrl, options, (step) => {
          setCurrentStep(step)
        })
        setJob(completedJob)
        setStatus('complete')
      } else {
        // Real backend flow
        if (!file) throw new Error('No file selected')
        const { jobId } = await realEnhanceImage(file, options)

        // Poll every 2 seconds
        pollingRef.current = setInterval(async () => {
          try {
            const polledJob = await pollJobStatus(jobId)
            setCurrentStep(polledJob.currentStep ?? 0)
            if (polledJob.status === 'complete') {
              clearInterval(pollingRef.current!)
              setJob(polledJob)
              setStatus('complete')
            } else if (polledJob.status === 'error') {
              clearInterval(pollingRef.current!)
              setError(polledJob.error ?? 'Processing failed')
              setStatus('error')
            }
          } catch (pollErr) {
            clearInterval(pollingRef.current!)
            setError('Lost connection to server.')
            setStatus('error')
          }
        }, 2000)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'An unexpected error occurred.'
      setError(msg)
      setStatus('error')
    }
  }, [])

  // Expose mock job if needed externally
  const effectiveJob = job ?? (DEMO_MODE ? getMockJob() : null)

  return { status, currentStep, job: effectiveJob, error, startEnhancement, reset }
}
