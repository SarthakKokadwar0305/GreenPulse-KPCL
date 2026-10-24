'use client'

import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

const STAGGER_SECONDS = 0.05
const MAX_STAGGER_STEPS = 8

interface RevealProps {
  children: ReactNode
  index?: number
  className?: string
}

export function Reveal({ children, index = 0, className }: RevealProps) {
  const delay = Math.min(index, MAX_STAGGER_STEPS) * STAGGER_SECONDS

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}
