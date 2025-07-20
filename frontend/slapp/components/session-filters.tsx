"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Filter, ChevronDown, X } from "lucide-react"

// --- Filter Types ---
export interface SessionFiltersState {
  showOnlyMySessions: boolean
  location: string
  dateRange: string
  swellHeight: string
  swellPeriod: string
  swellDirection: string
  funRating: number
  keywords: string
  surfer: string
}

interface SessionFiltersProps {
  filters: SessionFiltersState
  setFilters: (filters: SessionFiltersState) => void
  initialState: SessionFiltersState // New prop
}

export function SessionFilters({ filters, setFilters, initialState }: SessionFiltersProps) {
  const [isMoreFiltersOpen, setIsMoreFiltersOpen] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFilters({ ...filters, [name]: value })
  }

  const handleSelectChange = (name: string, value: string) => {
    setFilters({ ...filters, [name]: value })
  }

  const handleSliderCommit = (value: number[]) => {
    setFilters({ ...filters, funRating: value[0] })
  }

  const handleClearFilters = () => {
    setFilters(initialState)
  }

  return (
    <Collapsible open={isMoreFiltersOpen} onOpenChange={setIsMoreFiltersOpen} className="p-4 border rounded-lg bg-card text-card-foreground mb-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-end">
        <div>
          <Label htmlFor="location">Location</Label>
          <Input id="location" name="location" placeholder="e.g., Lido Beach" value={filters.location} onChange={handleInputChange} />
        </div>
        <div>
          <Label htmlFor="dateRange">Date</Label>
          <Select name="dateRange" onValueChange={(v) => handleSelectChange("dateRange", v)} value={filters.dateRange}>
            <SelectTrigger><SelectValue placeholder="Select date range" /></SelectTrigger>
            <SelectContent>
                <SelectItem value="any">Any Time</SelectItem>
                <SelectItem value="past7">Past 7 Days</SelectItem>
                <SelectItem value="past30">Past 30 Days</SelectItem>
                <SelectItem value="thisMonth">This Month</SelectItem>
                <SelectItem value="thisYear">This Year</SelectItem>
                <SelectItem value="lastYear">Last Year</SelectItem>
                <SelectItem value="2023">2023</SelectItem>
                <SelectItem value="2022">2022</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-2">
            <CollapsibleTrigger asChild>
                <Button variant="outline" className="w-full lg:w-auto">
                  <Filter className="mr-2 h-4 w-4" />
                  More Filters
                  <ChevronDown className={`ml-2 h-4 w-4 transition-transform ${isMoreFiltersOpen ? 'rotate-180' : ''}`} />
                </Button>
            </CollapsibleTrigger>
            <Button variant="outline" onClick={handleClearFilters} className="w-full lg:w-auto">
                <X className="mr-2 h-4 w-4" />
                Clear
            </Button>
        </div>
      </div>

      <CollapsibleContent className="pt-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
                <Label>Swell Height</Label>
                <Select name="swellHeight" onValueChange={(v) => handleSelectChange("swellHeight", v)} value={filters.swellHeight}>
                    <SelectTrigger><SelectValue placeholder="Swell Height" /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="any">Any Height</SelectItem>
                        <SelectItem value="1-2">1-2 ft</SelectItem>
                        <SelectItem value="2-3">2-3 ft</SelectItem>
                        <SelectItem value="3-5">3-5 ft</SelectItem>
                        <SelectItem value="5+">5+ ft</SelectItem>
                    </SelectContent>
                </Select>
            </div>
            <div>
                <Label>Swell Period</Label>
                <Select name="swellPeriod" onValueChange={(v) => handleSelectChange("swellPeriod", v)} value={filters.swellPeriod}>
                    <SelectTrigger><SelectValue placeholder="Swell Period" /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="any">Any Period</SelectItem>
                        <SelectItem value="1-5">1-5 s</SelectItem>
                        <SelectItem value="5-8">5-8 s</SelectItem>
                        <SelectItem value="8-12">8-12 s</SelectItem>
                        <SelectItem value="12+">12+ s</SelectItem>
                    </SelectContent>
                </Select>
            </div>
            <div>
                <Label>Swell Direction</Label>
                <Select name="swellDirection" onValueChange={(v) => handleSelectChange("swellDirection", v)} value={filters.swellDirection}>
                    <SelectTrigger><SelectValue placeholder="Swell Direction" /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="any">Any Direction</SelectItem>
                        <SelectItem value="N">N</SelectItem>
                        <SelectItem value="E">E</SelectItem>
                        <SelectItem value="S">S</SelectItem>
                        <SelectItem value="W">W</SelectItem>
                    </SelectContent>
                </Select>
            </div>
            <div className="space-y-2 pt-2">
                <Label>Min Fun Rating: {filters.funRating}</Label>
                <Slider defaultValue={[filters.funRating]} max={10} step={1} onValueCommit={handleSliderCommit} />
            </div>
            <div>
                <Label>Keywords</Label>
                <Input name="keywords" placeholder="Keywords in notes..." value={filters.keywords} onChange={handleInputChange} />
            </div>
            <div>
                <Label>Surfer Name</Label>
                <Input name="surfer" placeholder="Surfer name..." value={filters.surfer} onChange={handleInputChange} />
            </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
