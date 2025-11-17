import { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { getApiKeyStatus, generateApiKey, revokeApiKey, ApiKeyStatus } from '@/lib/api';
import { toast } from 'sonner';
import { Key, Copy, Trash2, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export default function ApiSettings() {
  const [apiKeyStatus, setApiKeyStatus] = useState<ApiKeyStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRevoking, setIsRevoking] = useState(false);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    loadApiKeyStatus();
  }, []);

  const loadApiKeyStatus = async () => {
    try {
      const status = await getApiKeyStatus();
      setApiKeyStatus(status);
    } catch (error) {
      toast.error('Failed to load API key status');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateApiKey = async () => {
    if (apiKeyStatus?.has_api_key) {
      if (!confirm('This will replace your existing API key. Any applications using the old key will stop working. Continue?')) {
        return;
      }
    }

    setIsGenerating(true);
    try {
      const response = await generateApiKey();
      setNewApiKey(response.api_key);
      setShowKey(true);
      toast.success('API key generated successfully');
      await loadApiKeyStatus();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to generate API key');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRevokeApiKey = async () => {
    if (!confirm('Are you sure you want to revoke your API key? Any applications using it will stop working immediately.')) {
      return;
    }

    setIsRevoking(true);
    try {
      await revokeApiKey();
      toast.success('API key revoked successfully');
      setNewApiKey(null);
      await loadApiKeyStatus();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to revoke API key');
    } finally {
      setIsRevoking(false);
    }
  };

  const handleCopyToClipboard = () => {
    if (newApiKey) {
      navigator.clipboard.writeText(newApiKey);
      toast.success('API key copied to clipboard');
    }
  };

  const handleDismissKey = () => {
    setShowKey(false);
    setNewApiKey(null);
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center p-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Key className="h-8 w-8" />
            API Settings
          </h2>
          <p className="text-muted-foreground mt-1">
            Manage your API key for programmatic access
          </p>
        </div>

        {/* New API Key Display */}
        {showKey && newApiKey && (
          <Card className="border-green-500 bg-green-50 dark:bg-green-950">
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                <CardTitle className="text-green-900 dark:text-green-100">API Key Generated</CardTitle>
              </div>
              <CardDescription className="text-green-700 dark:text-green-300">
                Make sure to copy your API key now. You won't be able to see it again!
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newApiKey}
                  readOnly
                  className="font-mono text-sm bg-white dark:bg-gray-900"
                />
                <Button onClick={handleCopyToClipboard} variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
              </div>
              <Button onClick={handleDismissKey} variant="outline" className="w-full">
                I've saved my API key
              </Button>
            </CardContent>
          </Card>
        )}

        {/* API Key Status */}
        <Card>
          <CardHeader>
            <CardTitle>API Key Status</CardTitle>
            <CardDescription>
              Use your API key to authenticate requests to the CRM API
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium">Current Status</p>
                <div className="flex items-center gap-2">
                  {apiKeyStatus?.has_api_key ? (
                    <>
                      <Badge variant="default" className="gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        Active
                      </Badge>
                      {apiKeyStatus.api_key_prefix && (
                        <span className="text-sm text-muted-foreground font-mono">
                          {apiKeyStatus.api_key_prefix}
                        </span>
                      )}
                    </>
                  ) : (
                    <Badge variant="secondary">No API Key</Badge>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleGenerateApiKey}
                  disabled={isGenerating}
                  variant={apiKeyStatus?.has_api_key ? "outline" : "default"}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Key className="h-4 w-4 mr-2" />
                      {apiKeyStatus?.has_api_key ? 'Regenerate' : 'Generate'} API Key
                    </>
                  )}
                </Button>
                {apiKeyStatus?.has_api_key && (
                  <Button
                    onClick={handleRevokeApiKey}
                    disabled={isRevoking}
                    variant="destructive"
                  >
                    {isRevoking ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Revoking...
                      </>
                    ) : (
                      <>
                        <Trash2 className="h-4 w-4 mr-2" />
                        Revoke
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Available Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle>Available API Endpoints</CardTitle>
            <CardDescription>
              Your API key has limited access to these endpoints only
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-md p-4">
              <div className="flex gap-2">
                <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
                    Limited Access
                  </p>
                  <p className="text-sm text-amber-700 dark:text-amber-300">
                    API keys are designed for automation and have restricted access. They can only access the endpoints listed below. For full API access, use JWT token authentication.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-sm font-medium mb-1">GET /contracts</p>
                <p className="text-xs text-muted-foreground">View all contracts (read-only)</p>
              </div>

              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-sm font-medium mb-1">POST /contracts/import/samgov</p>
                <p className="text-xs text-muted-foreground">Import contract opportunities from SAM.gov</p>
              </div>

              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-sm font-medium mb-1">GET /auth/me</p>
                <p className="text-xs text-muted-foreground">Get your own user information</p>
              </div>
            </div>

            <div className="bg-muted p-4 rounded-md">
              <p className="text-sm font-medium mb-2">Not Available with API Key:</p>
              <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
                <li>Creating, updating, or deleting individual contracts</li>
                <li>Managing contacts and communications</li>
                <li>User management and authentication</li>
                <li>Password reset operations</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Documentation */}
        <Card>
          <CardHeader>
            <CardTitle>Usage Examples</CardTitle>
            <CardDescription>
              Authenticate your API requests using the Bearer token scheme
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm font-medium">Authentication Header</p>
              <div className="bg-muted p-3 rounded-md font-mono text-sm">
                Authorization: Bearer YOUR_API_KEY
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Example: Import Contracts from SAM.gov</p>
              <div className="bg-muted p-3 rounded-md font-mono text-xs overflow-x-auto">
                <pre>{`curl -X POST http://localhost:8000/contracts/import/samgov \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "opportunities": [
      {
        "noticeId": "abc123xyz",
        "title": "IT Services for Federal Agency",
        "solicitationNumber": "RFP-2024-001",
        "description": "Seeking IT support services...",
        "responseDeadLine": "2024-12-31T23:59:59Z",
        "naicsCode": "541512",
        "uiLink": "https://sam.gov/opp/abc123xyz",
        "source": "SAM.gov",
        "pointOfContact": [
          {
            "fullName": "John Smith",
            "email": "john.smith@agency.gov",
            "phone": "555-0100",
            "type": "primary"
          }
        ]
      }
    ],
    "auto_create_contacts": true
  }'`}</pre>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                This will create a contract record and optionally create contact records from the point-of-contact information.
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Example: Get All Contracts</p>
              <div className="bg-muted p-3 rounded-md font-mono text-sm overflow-x-auto">
                <pre>{`curl -X GET http://localhost:8000/contracts \\
  -H "Authorization: Bearer YOUR_API_KEY"`}</pre>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-md p-4">
              <div className="flex gap-2">
                <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Security Best Practices
                  </p>
                  <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1 list-disc list-inside">
                    <li>Never share your API key or commit it to version control</li>
                    <li>Store it securely in environment variables or secrets management</li>
                    <li>Rotate your API key regularly for better security</li>
                    <li>Revoke immediately if you suspect it has been compromised</li>
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
