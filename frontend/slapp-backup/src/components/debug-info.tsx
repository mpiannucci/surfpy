"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ApiTester } from "./api-tester"

export function DebugInfo({ data, source }: { data: any; source: string }) {
  const [showRaw, setShowRaw] = useState(false)
  const [showApiTester, setShowApiTester] = useState(false)

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between">
            <span>Debug Info (Data Source: {source})</span>
            <div className="space-x-2">
              <Button variant="outline" size="sm" onClick={() => setShowRaw(!showRaw)}>
                {showRaw ? "Hide Raw Data" : "Show Raw Data"}
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowApiTester(!showApiTester)}>
                {showApiTester ? "Hide API Tester" : "Show API Tester"}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {showRaw ? (
            <pre className="bg-gray-100 p-4 rounded-md overflow-auto max-h-[500px] text-xs">
              {JSON.stringify(data, null, 2)}
            </pre>
          ) : (
            <div>
              <p>Data summary:</p>
              <ul className="list-disc pl-5 mt-2">
                <li>Total items: {Array.isArray(data) ? data.length : data?.data?.length || 0}</li>
                <li>
                  Items with user_email:{" "}
                  {Array.isArray(data)
                    ? data.filter((item) => !!item.user_email).length
                    : data?.data?.filter((item: any) => !!item.user_email).length || 0}
                </li>
                <li>
                  First few user_emails:{" "}
                  {Array.isArray(data)
                    ? data
                        .slice(0, 3)
                        .map((item) => item.user_email || "MISSING")
                        .join(", ")
                    : data?.data
                        ?.slice(0, 3)
                        .map((item: any) => item.user_email || "MISSING")
                        .join(", ") || "None"}
                </li>
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {showApiTester && <ApiTester />}
    </div>
  )
}
