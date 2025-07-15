"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bug, RefreshCw } from "lucide-react"

export function DisplayNameDebugger() {
  const [debugData, setDebugData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [showDebugger, setShowDebugger] = useState(false)

  const runDebugTest = async () => {
    setIsLoading(true)
    setDebugData(null)

    try {
      const token = localStorage.getItem("auth_token")
      const userData = localStorage.getItem("user_data")

      const debugInfo = {
        timestamp: new Date().toISOString(),
        auth: {
          hasToken: !!token,
          tokenLength: token?.length || 0,
          tokenPreview: token ? `${token.substring(0, 20)}...` : "No token",
          hasUserData: !!userData,
          userData: userData ? JSON.parse(userData) : null,
        },
        tests: [],
      }

      // Test multiple endpoint variations
      const endpointsToTest = [
        {
          name: "Working Postman URL via Proxy",
          url: "https://surfdata-b4vwwr6iw-martins-projects-383d438b.vercel.app/api/surf-sessions",
          useProxy: true,
        },
        {
          name: "Working Postman URL with Auth via Proxy",
          url: "https://surfdata-b4vwwr6iw-martins-projects-383d438b.vercel.app/api/surf-sessions",
          useProxy: true,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: token ? `Bearer ${token}` : "",
          },
        },
        {
          name: "Working Postman URL with User-Agent via Proxy",
          url: "https://surfdata-b4vwwr6iw-martins-projects-383d438b.vercel.app/api/surf-sessions",
          useProxy: true,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: token ? `Bearer ${token}` : "",
            "User-Agent": "PostmanRuntime/7.32.3",
          },
        },
        {
          name: "Current App API via Proxy",
          url: "https://surfdata-b4vwwr6iw-martins-projects-383d438b.vercel.app/api/surf-sessions",
          useProxy: true,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: token ? `Bearer ${token}` : "",
            "X-Requested-With": "XMLHttpRequest",
          },
        },
      ]

      for (const endpoint of endpointsToTest) {
        console.log(`=== TESTING ENDPOINT: ${endpoint.name} ===`)

        try {
          const headers = endpoint.headers || {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: token ? `Bearer ${token}` : "",
          }

          // Only test via proxy since direct requests are failing due to CORS
          if (endpoint.useProxy) {
            try {
              const proxyResponse = await fetch("/api/auth/cors-proxy", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  url: endpoint.url,
                  method: "GET",
                  headers,
                }),
              })

              const proxyText = await proxyResponse.text()
              console.log(`${endpoint.name} - Proxy Response status:`, proxyResponse.status)
              console.log(`${endpoint.name} - Proxy Response text (first 500 chars):`, proxyText.substring(0, 500))

              let proxyData
              try {
                proxyData = JSON.parse(proxyText)
              } catch (e) {
                debugInfo.tests.push({
                  name: `${endpoint.name} - Proxy`,
                  success: false,
                  error: "Failed to parse JSON",
                  status: proxyResponse.status,
                  rawResponse: proxyText.substring(0, 1000),
                })
                continue
              }

              const proxyTest = {
                name: `${endpoint.name} - Proxy`,
                url: endpoint.url,
                status: proxyResponse.status,
                success: proxyResponse.ok,
                dataStructure: typeof proxyData,
                hasDataArray: !!(proxyData.data && Array.isArray(proxyData.data)),
                isDirectArray: Array.isArray(proxyData),
                itemCount: 0,
                displayNameCount: 0,
                userEmailCount: 0,
                userIdCount: 0,
                sampleItems: [],
                allFieldsInFirstItem: [],
                requestHeaders: headers,
              }

              let proxyItems = []
              if (proxyData.data && Array.isArray(proxyData.data)) {
                proxyItems = proxyData.data
              } else if (Array.isArray(proxyData)) {
                proxyItems = proxyData
              }

              if (proxyItems.length > 0) {
                proxyTest.itemCount = proxyItems.length
                proxyTest.displayNameCount = proxyItems.filter(
                  (item: any) => item.display_name !== undefined && item.display_name !== null,
                ).length
                proxyTest.userEmailCount = proxyItems.filter((item: any) => !!item.user_email).length
                proxyTest.userIdCount = proxyItems.filter((item: any) => !!item.user_id).length

                // Get all fields from the first item
                proxyTest.allFieldsInFirstItem = Object.keys(proxyItems[0] || {})

                proxyTest.sampleItems = proxyItems.slice(0, 2).map((item: any) => ({
                  id: item.id,
                  display_name: item.display_name,
                  user_email: item.user_email,
                  user_id: item.user_id,
                  session_name: item.session_name,
                  allFields: Object.keys(item),
                }))
              }

              debugInfo.tests.push(proxyTest)
              console.log(`${endpoint.name} - Proxy test result:`, proxyTest)
            } catch (proxyError) {
              debugInfo.tests.push({
                name: `${endpoint.name} - Proxy`,
                success: false,
                error: proxyError instanceof Error ? proxyError.message : String(proxyError),
              })
            }
          }
        } catch (error) {
          debugInfo.tests.push({
            name: `${endpoint.name}`,
            success: false,
            error: error instanceof Error ? error.message : String(error),
          })
        }
      }

      setDebugData(debugInfo)
    } catch (error) {
      setDebugData({
        error: error instanceof Error ? error.message : String(error),
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Button
          onClick={() => setShowDebugger(!showDebugger)}
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
        >
          <Bug className="h-4 w-4" />
          {showDebugger ? "Hide" : "Show"} Display Name Debugger
        </Button>

        {showDebugger && (
          <Button
            onClick={runDebugTest}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="flex items-center gap-1"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            {isLoading ? "Testing..." : "Run Debug Test"}
          </Button>
        )}
      </div>

      {showDebugger && (
        <Card>
          <CardHeader>
            <CardTitle>Display Name Debug Results</CardTitle>
          </CardHeader>
          <CardContent>
            {debugData ? (
              <div className="space-y-4">
                {debugData.error ? (
                  <div className="text-red-600 font-mono text-sm">Error: {debugData.error}</div>
                ) : (
                  <>
                    <div className="text-sm">
                      <strong>Timestamp:</strong> {debugData.timestamp}
                    </div>

                    <div className="text-sm">
                      <strong>Auth Status:</strong>
                      <ul className="ml-4 mt-1">
                        <li>Has Token: {debugData.auth.hasToken ? "✅" : "❌"}</li>
                        <li>Token Length: {debugData.auth.tokenLength}</li>
                        <li>Token Preview: {debugData.auth.tokenPreview}</li>
                        <li>Has User Data: {debugData.auth.hasUserData ? "✅" : "❌"}</li>
                        {debugData.auth.userData && <li>User Email: {debugData.auth.userData.email || "N/A"}</li>}
                      </ul>
                    </div>

                    <div className="space-y-3">
                      <strong>Test Results:</strong>
                      {debugData.tests.map((test: any, index: number) => (
                        <div key={index} className="border rounded p-3 text-sm">
                          <div className="font-medium mb-2">
                            {test.name} {test.success ? "✅" : "❌"}
                          </div>

                          {test.success ? (
                            <div className="space-y-1">
                              <div>URL: {test.url}</div>
                              <div>Status: {test.status}</div>
                              <div>Data Structure: {test.dataStructure}</div>
                              <div>Items: {test.itemCount}</div>
                              <div className="text-red-600 font-bold">
                                With display_name: {test.displayNameCount}/{test.itemCount}
                              </div>
                              <div>
                                With user_email: {test.userEmailCount}/{test.itemCount}
                              </div>
                              <div>
                                With user_id: {test.userIdCount}/{test.itemCount}
                              </div>

                              {test.requestHeaders && (
                                <div className="mt-2">
                                  <div className="font-medium">Request Headers Sent:</div>
                                  <pre className="text-xs bg-yellow-50 dark:bg-yellow-900 p-2 rounded mt-1 overflow-auto">
                                    {JSON.stringify(test.requestHeaders, null, 2)}
                                  </pre>
                                </div>
                              )}

                              {test.allFieldsInFirstItem && test.allFieldsInFirstItem.length > 0 && (
                                <div className="mt-2">
                                  <div className="font-medium">All Fields in First Item:</div>
                                  <div className="text-xs bg-blue-50 dark:bg-blue-900 p-2 rounded mt-1">
                                    {test.allFieldsInFirstItem.join(", ")}
                                  </div>
                                </div>
                              )}

                              {test.sampleItems && test.sampleItems.length > 0 && (
                                <div className="mt-2">
                                  <div className="font-medium">Sample Items:</div>
                                  <pre className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded mt-1 overflow-auto">
                                    {JSON.stringify(test.sampleItems, null, 2)}
                                  </pre>
                                </div>
                              )}

                              {test.responseHeaders && (
                                <div className="mt-2">
                                  <div className="font-medium">Response Headers:</div>
                                  <pre className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded mt-1 overflow-auto">
                                    {JSON.stringify(test.responseHeaders, null, 2)}
                                  </pre>
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="text-red-600">
                              Error: {test.error}
                              {test.rawResponse && (
                                <div className="mt-2">
                                  <div className="font-medium">Raw Response:</div>
                                  <pre className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded mt-1 overflow-auto">
                                    {test.rawResponse}
                                  </pre>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="text-muted-foreground">Click "Run Debug Test" to analyze the display_name data flow</div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
