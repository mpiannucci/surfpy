"use client"

import { useEffect, useRef } from "react"
import type { Swell } from "@/lib/types"

interface SwellVisualizationProps {
  swells: Swell[]
}

export function SwellVisualization({ swells }: SwellVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Draw compass
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    const radius = Math.min(centerX, centerY) - 20

    // Draw compass circle
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.strokeStyle = "#e2e8f0"
    ctx.lineWidth = 2
    ctx.stroke()

    // Draw compass directions
    const directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    ctx.font = "14px sans-serif"
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillStyle = "#64748b"

    directions.forEach((dir, i) => {
      const angle = (i * Math.PI) / 4
      const x = centerX + (radius + 15) * Math.sin(angle)
      const y = centerY - (radius + 15) * Math.cos(angle)
      ctx.fillText(dir, x, y)
    })

    // Draw swells
    swells.forEach((swell, index) => {
      const angle = (swell.direction * Math.PI) / 180
      const length = (radius * swell.height) / 10 // Scale by height
      const width = (swell.period / 20) * 10 // Scale by period

      // Calculate arrow points
      const x1 = centerX
      const y1 = centerY
      const x2 = centerX + length * Math.sin(angle)
      const y2 = centerY - length * Math.cos(angle)

      // Draw arrow line
      ctx.beginPath()
      ctx.moveTo(x1, y1)
      ctx.lineTo(x2, y2)
      ctx.lineWidth = width

      // Different colors for different swells
      const colors = ["#0ea5e9", "#6366f1", "#8b5cf6"]
      ctx.strokeStyle = colors[index % colors.length]
      ctx.stroke()

      // Draw arrow head
      const headLength = 15
      const angle1 = angle - Math.PI / 6
      const angle2 = angle + Math.PI / 6

      ctx.beginPath()
      ctx.moveTo(x2, y2)
      ctx.lineTo(x2 - headLength * Math.sin(angle1), y2 + headLength * Math.cos(angle1))
      ctx.lineTo(x2 - headLength * Math.sin(angle2), y2 + headLength * Math.cos(angle2))
      ctx.closePath()
      ctx.fillStyle = colors[index % colors.length]
      ctx.fill()

      // Add swell label
      ctx.font = "12px sans-serif"
      ctx.fillStyle = "#64748b"
      ctx.fillText(
        `${swell.height.toFixed(1)}ft @ ${swell.period.toFixed(1)}s`,
        x2 + 15 * Math.sin(angle),
        y2 - 15 * Math.cos(angle),
      )
    })
  }, [swells])

  return (
    <div className="aspect-square w-full max-w-[300px] mx-auto">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        aria-label="Swell visualization showing direction, height, and period"
      />
    </div>
  )
}
