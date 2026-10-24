'use client'

import type { ReactNode } from 'react'

import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { cn } from '@/lib/utils'

export interface SegmentedOption<T extends string> {
  value: T
  label: string
  count?: number
  icon?: ReactNode
}

interface SegmentedControlProps<T extends string> {
  value: T
  options: SegmentedOption<T>[]
  onChange: (value: T) => void
  ariaLabel: string
  className?: string
}

export function SegmentedControl<T extends string>({
  value,
  options,
  onChange,
  ariaLabel,
  className,
}: SegmentedControlProps<T>) {
  return (
    <ToggleGroup
      value={[value]}
      onValueChange={(next) => {
        const selected = next[0] as T | undefined
        if (selected) onChange(selected)
      }}
      spacing={0}
      aria-label={ariaLabel}
      className={cn('gap-0.5 rounded-tile bg-muted p-1', className)}
    >
      {options.map((option) => (
        <ToggleGroupItem
          key={option.value}
          value={option.value}
          className="h-8 gap-1.5 rounded-[10px] px-3 text-[13px] font-medium text-muted-foreground data-pressed:bg-card data-pressed:text-foreground data-pressed:shadow-card"
        >
          {option.icon}
          {option.label}
          {option.count !== undefined && (
            <span className="text-[11px] font-semibold tabular-nums opacity-70">
              {option.count}
            </span>
          )}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  )
}
