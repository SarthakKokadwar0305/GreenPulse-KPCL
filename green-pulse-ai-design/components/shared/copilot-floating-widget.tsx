'use client'

import React, { useState, useEffect, useRef } from 'react'
import {
  Sparkles,
  X,
  Send,
  Bot,
  User as UserIcon,
  Maximize2,
  Minimize2,
  FileText,
  Clock,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react'
import Link from 'next/navigation'
import { useRouter } from 'next/navigation'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/store/auth-store'

interface FloatingMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Array<{ document: string; page: number }>
  timestamp: string
}

export function CopilotFloatingWidget() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<FloatingMessage[]>([
    {
      id: 'init-1',
      role: 'assistant',
      content:
        'Hello! I am your **GreenPulse Industrial Copilot**. Ask me anything about current energy spikes, active machine health, or factory SOPs.',
      timestamp: 'Now',
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `float-${Math.random().toString(36).substring(2, 7)}`)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const text = inputValue.trim()
    if (!text || loading) return

    const userMsg: FloatingMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages((prev) => [...prev, userMsg])
    setInputValue('')
    setLoading(true)

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      const authStorage = typeof window !== 'undefined' ? localStorage.getItem('greenpulse-auth-session') : null
      let token = typeof window !== 'undefined' ? localStorage.getItem('greenpulse_token') : null
      if (!token && authStorage) {
        try {
          const parsed = JSON.parse(authStorage)
          token = parsed?.state?.accessToken
        } catch {}
      }

      const res = await fetch(`${apiBase}/api/v1/copilot/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Role': user?.role || 'PLANT_HEAD',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          query: text,
          session_id: sessionId,
        }),
      })

      if (res.ok) {
        const json = await res.json()
        const asstMsg: FloatingMessage = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: json.data?.response || json.response || 'Telemetry analyzed successfully.',
          citations: json.data?.citations?.map((c: any) => ({ document: c.document, page: c.page })),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, asstMsg])
      } else {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.message || `Server returned ${res.status}`)
      }
    } catch (err: any) {
      console.error('Copilot request failed:', err)
      const fallbackMsg: FloatingMessage = {
        id: `asst-fb-${Date.now()}`,
        role: 'assistant',
        content: `### Connection Error\nCould not retrieve response from Copilot service (${err?.message || 'Network error'}). Please verify the FastAPI backend server on port 8000 is active.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, fallbackMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-primary px-4 py-3 text-primary-foreground shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-primary/25 active:scale-95 sm:px-5"
          title="Open AI Copilot"
        >
          <Sparkles className="size-5 animate-pulse" />
          <span className="text-xs font-semibold tracking-wide">Ask Industrial AI</span>
          <span className="flex size-2 rounded-full bg-emerald-400" />
        </button>
      )}

      {/* Slide-out / Floating Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 flex h-[580px] w-[380px] sm:w-[440px] flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl animate-in slide-in-from-bottom-5 duration-300">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border bg-muted/40 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Sparkles className="size-4" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-foreground">GreenPulse Copilot</span>
                  <Badge variant="outline" className="text-[9px] px-1 py-0 border-primary/30 text-primary">
                    Gemma 3
                  </Badge>
                </div>
                <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                  <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live SCADA + Qdrant RAG
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="size-7 text-muted-foreground hover:text-foreground"
                onClick={() => router.push('/copilot')}
                title="Full Screen Workspace"
              >
                <Maximize2 className="size-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="size-7 text-muted-foreground hover:text-foreground"
                onClick={() => setIsOpen(false)}
                title="Close"
              >
                <X className="size-4" />
              </Button>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3.5 text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.role === 'assistant' && (
                  <div className="size-6 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-0.5 text-primary">
                    <Bot className="size-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-xl px-3.5 py-2.5 ${
                    m.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-none'
                      : 'bg-muted/50 border border-border/80 rounded-tl-none text-foreground'
                  }`}
                >
                  <div className="prose prose-invert prose-xs leading-relaxed space-y-1.5">
                    {m.content.split('\n\n').map((para, i) => (
                      <p key={i}>{para}</p>
                    ))}
                  </div>
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2 pt-1.5 border-t border-border/40 flex flex-wrap gap-1">
                      {m.citations.map((c, ci) => (
                        <span
                          key={ci}
                          className="inline-flex items-center gap-1 text-[9px] bg-background/80 rounded px-1.5 py-0.5 text-muted-foreground"
                        >
                          <FileText className="size-2.5 text-purple-400" />
                          {c.document} (p.{c.page})
                        </span>
                      ))}
                    </div>
                  )}
                  <span className="mt-1 block text-right text-[9px] text-muted-foreground/70">
                    {m.timestamp}
                  </span>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2 items-center text-xs text-muted-foreground">
                <div className="size-6 rounded-full bg-primary/10 flex items-center justify-center text-primary animate-spin">
                  <Sparkles className="size-3" />
                </div>
                <span>Analyzing telemetry & documents...</span>
              </div>
            )}
            <div ref={scrollRef} />
          </div>

          {/* Quick Suggestion Pills */}
          <div className="border-t border-border/40 bg-muted/20 px-3 py-1.5 flex gap-1 overflow-x-auto no-scrollbar">
            <button
              onClick={() => {
                setInputValue("Show highest energy consuming machine")
                handleSend()
              }}
              className="text-[10px] text-muted-foreground bg-card border border-border/60 hover:text-foreground rounded px-2 py-0.5 whitespace-nowrap"
            >
              Highest Machine kW
            </button>
            <button
              onClick={() => {
                setInputValue("Explain active alerts")
                handleSend()
              }}
              className="text-[10px] text-muted-foreground bg-card border border-border/60 hover:text-foreground rounded px-2 py-0.5 whitespace-nowrap"
            >
              Active Alerts
            </button>
            <button
              onClick={() => {
                setInputValue("Peak Demand SOP curtailment")
                handleSend()
              }}
              className="text-[10px] text-muted-foreground bg-card border border-border/60 hover:text-foreground rounded px-2 py-0.5 whitespace-nowrap"
            >
              Peak Demand SOP
            </button>
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-border bg-card p-3">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask Copilot..."
              className="h-9 text-xs bg-muted/30"
              disabled={loading}
            />
            <Button type="submit" size="sm" className="h-9 px-3" disabled={loading || !inputValue.trim()}>
              <Send className="size-3.5" />
            </Button>
          </form>
        </div>
      )}
    </>
  )
}
