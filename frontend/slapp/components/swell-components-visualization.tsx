"use client"

import { useEffect, useRef } from "react"

interface SwellComponent {
  height: number
  period: number
  direction: number
}

interface SwellComponents {
  swell_1?: SwellComponent
  swell_2?: SwellComponent
  swell_3?: SwellComponent
  swell_4?: SwellComponent
  [key: string]: SwellComponent | undefined
}

interface SwellComponentsVisualizationProps {
  swellComponents: SwellComponents
}

export function SwellComponentsVisualization({ swellComponents }: SwellComponentsVisualizationProps) {
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
    const radius = Math.min(centerX, centerY) - 40 // Increased margin for labels

    // Draw compass circle
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.strokeStyle = "#334155" // darker blue-gray for dark theme
    ctx.lineWidth = 2
    ctx.stroke()

    // Draw compass directions
    const directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    ctx.font = "bold 16px sans-serif" // Increased font size and made bold
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillStyle = "#94a3b8" // light blue-gray for dark theme

    directions.forEach((dir, i) => {
      const angle = (i * Math.PI) / 4
      const x = centerX + (radius + 25) * Math.sin(angle) // Increased distance from circle
      const y = centerY - (radius + 25) * Math.cos(angle)
      ctx.fillText(dir, x, y)
    })

    // Extract swell components into an array
    const swells = Object.entries(swellComponents)
      .filter(([_, component]) => component !== undefined)
      .map(([key, component]) => ({
        name: key.replace("_", " ").toUpperCase(),
        ...component!,
      }))

    // Draw swells
    swells.forEach((swell, index) => {
      const angle = (swell.direction * Math.PI) / 180
      const length = (radius * swell.height) / 3 // Adjusted scale for better visibility
      const width = Math.max(3, (swell.period / 20) * 12) // Minimum width of 3px, adjusted scale

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

      // Different colors for different swells - brighter for dark theme
      const colors = ["#38bdf8", "#818cf8", "#a78bfa", "#f472b6"] // Brighter colors
      ctx.strokeStyle = colors[index % colors.length]
      ctx.stroke()

      // Draw arrow head
      const headLength = Math.max(15, width * 1.5) // Scale arrowhead with line width
      const angle1 = angle - Math.PI / 6
      const angle2 = angle + Math.PI / 6

      ctx.beginPath()
      ctx.moveTo(x2, y2)
      ctx.lineTo(x2 - headLength * Math.sin(angle1), y2 + headLength * Math.cos(angle1))
      ctx.lineTo(x2 - headLength * Math.sin(angle2), y2 + headLength * Math.cos(angle2))
      ctx.closePath()
      ctx.fillStyle = colors[index % colors.length]
      ctx.fill()

      // Add swell label with improved positioning and background
      const labelX = x2 + 30 * Math.sin(angle)
      const labelY = y2 - 30 * Math.cos(angle)

      // Draw label background
      const labelText = `${swell.name}: ${swell.height.toFixed(1)}ft @ ${swell.period.toFixed(1)}s`
      ctx.font = "bold 14px sans-serif" // Increased font size and made bold
      const textMetrics = ctx.measureText(labelText)
      const padding = 6

      ctx.fillStyle = "rgba(15, 23, 42, 0.75)" // Semi-transparent dark background
      ctx.fillRect(
        labelX - padding - (angle > Math.PI / 2 && angle < (3 * Math.PI) / 2 ? textMetrics.width : 0),
        labelY - 14 - padding,
        textMetrics.width + padding * 2,
        28,
      )

      // Draw label text
      ctx.fillStyle = colors[index % colors.length]
      ctx.fillText(
        labelText,
        labelX - (angle > Math.PI / 2 && angle < (3 * Math.PI) / 2 ? textMetrics.width : 0),
        labelY,
      )
    })

    // Add a legend at the bottom
    if (swells.length > 0) {
      const colors = ["#38bdf8", "#818cf8", "#a78bfa", "#f472b6"]
      const legendY = rect.height - 30
      const legendItemWidth = rect.width / (swells.length + 1)

      swells.forEach((swell, index) => {
        const legendX = (index + 1) * legendItemWidth

        // Draw color box
        ctx.fillStyle = colors[index % colors.length]
        ctx.fillRect(legendX - 40, legendY, 15, 15)

        // Draw text
        ctx.fillStyle = "#e2e8f0"
        ctx.font = "14px sans-serif"
        ctx.textAlign = "left"
        ctx.fillText(swell.name, legendX - 20, legendY + 12)
      })
    }
  }, [swellComponents])

  return (
    <div className="aspect-square w-full max-w-[400px] mx-auto">
      {" "}
      {/* Increased max width */}
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        aria-label="Swell components visualization showing direction, height, and period"
      />
    </div>
  )
}
