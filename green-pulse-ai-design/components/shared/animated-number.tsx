'use client'

import { animate, useReducedMotion } from 'framer-motion'
import { useEffect, useRef } from 'react'

import { formatNumber } from '@/lib/format'

interface AnimatedNumberProps {
  value: number
  decimals?: number
}

export function AnimatedNumber({ value, decimals = 0 }: AnimatedNumberProps) {
  const nodeRef = useRef<HTMLSpanElement>(null)
  const previousValue = useRef(0)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    const node = nodeRef.current
    if (!node) return

    if (reduceMotion) {
      node.textContent = formatNumber(value, decimals)
      previousValue.current = value
      return
    }

    const controls = animate(previousValue.current, value, {
      duration: 0.9,
      ease: 'easeOut',
      onUpdate: (latest) => {
        node.textContent = formatNumber(latest, decimals)
      },
      onComplete: () => {
        previousValue.current = value
      },
    })

    return () => controls.stop()
  }, [value, decimals, reduceMotion])

  return <span ref={nodeRef}>{formatNumber(0, decimals)}</span>
}
