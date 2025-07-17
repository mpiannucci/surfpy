"use client"

import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { format, addDays, startOfDay } from "date-fns"

interface DayNavigatorProps {
  currentDayIndex: number
  onDayChange: (direction: number) => void
}

export function DayNavigator({ currentDayIndex, onDayChange }: DayNavigatorProps) {
  const today = startOfDay(new Date())
  const displayDate = addDays(today, currentDayIndex)

  let dayLabel = format(displayDate, "EEEE, MMM d")
  if (currentDayIndex === 0) {
    dayLabel = "Today"
  } else if (currentDayIndex === 1) {
    dayLabel = "Tomorrow"
  }

  return (
    <div className="flex items-center justify-between">
      <Button 
        variant="outline" 
        size="icon" 
        onClick={() => onDayChange(-1)} 
        disabled={currentDayIndex === 0}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <h2 className="text-xl font-bold text-center">{dayLabel}</h2>
      <Button 
        variant="outline" 
        size="icon" 
        onClick={() => onDayChange(1)} 
        disabled={currentDayIndex === 6}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  )
}
