import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  FileCheck, 
  Play, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle,
  Shield,
  Loader2,
  FileJson,
  Database,
  ArrowRight,
} from "lucide-react";
import type { ValidationReport, ValidationResult } from "@shared/schema";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

const sampleTerraformPlan = `{
  "resources": [
    {
      "type": "aws_instance",
      "name": "web_server",
      "provider": "aws",
      "instances": [
        {
          "attributes": {
            "instance_type": "t3.medium",
            "availability_zone": "us-east-1a",
            "tags": {
              "Environment": "production",
              "Application": "MyWebApp",
              "Owner": "platform-team"
            }
          }
        }
      ]
    },
    {
      "type": "aws_db_instance",
      "name": "main_database",
      "provider": "aws",
      "instances": [
        {
          "attributes": {
            "engine": "postgres",
            "engine_version": "15.3",
            "instance_class": "db.r5.large",
            "multi_az": true,
            "storage_encrypted": true,
            "backup_retention_period": 30
          }
        }
      ]
    },
    {
      "type": "aws_lb",
      "name": "app_lb",
      "provider": "aws",
      "instances": [
        {
          "attributes": {
            "load_balancer_type": "application",
            "internal": false
          }
        }
      ]
    }
  ]
}`;

const severityColors = {
  critical: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800",
  high: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-200 dark:border-orange-800",
  medium: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800",
  low: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800",
};

const statusIcons = {
  passed: CheckCircle2,
  failed: XCircle,
  warning: AlertTriangle,
  skipped: Shield,
};

function ValidationResultItem({ result }: { result: ValidationResult }) {
  const StatusIcon = statusIcons[result.status];
  const statusColors = {
    passed: "text-green-600 dark:text-green-400",
    failed: "text-red-600 dark:text-red-400",
    warning: "text-yellow-600 dark:text-yellow-400",
    skipped: "text-muted-foreground",
  };

  return (
    <div 
      className="p-4 rounded-md border bg-card hover-elevate"
      data-testid={`validation-result-${result.ruleId}`}
    >
      <div className="flex items-start gap-3">
        <StatusIcon className={`w-5 h-5 mt-0.5 ${statusColors[result.status]}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">{result.ruleName}</span>
              <Badge variant="outline" className="text-xs">{result.ruleId}</Badge>
            </div>
            <Badge variant="secondary" className={`text-xs ${severityColors[result.severity]}`}>
              {result.severity}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">{result.message}</p>
          {result.resource && (
            <p className="text-xs text-muted-foreground mt-1">
              Resource: <code className="font-mono bg-muted px-1 rounded">{result.resource}</code>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function ValidationReportView({ report }: { report: ValidationReport }) {
  const passedResults = report.results.filter(r => r.status === "passed");
  const failedResults = report.results.filter(r => r.status === "failed");
  const warningResults = report.results.filter(r => r.status === "warning");

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Compliance Score</p>
                <p className="text-3xl font-bold" data-testid="compliance-score">
                  {report.complianceScore}%
                </p>
              </div>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                report.complianceScore >= 90 
                  ? "bg-green-100 dark:bg-green-900/30 text-green-600"
                  : report.complianceScore >= 70
                  ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600"
                  : "bg-red-100 dark:bg-red-900/30 text-red-600"
              }`}>
                <Shield className="w-6 h-6" />
              </div>
            </div>
            <Progress 
              value={report.complianceScore} 
              className="mt-3 h-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Matched Pattern</p>
                <p className="text-lg font-semibold" data-testid="matched-pattern">
                  {report.matchedPattern?.name ?? "No match"}
                </p>
              </div>
            </div>
            {report.matchedPattern && (
              <div className="mt-2 flex items-center gap-2">
                <Progress value={report.matchedPattern.similarity * 100} className="flex-1 h-2" />
                <span className="text-sm font-medium">
                  {Math.round(report.matchedPattern.similarity * 100)}%
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Approval Track</p>
                <p className="text-lg font-semibold capitalize" data-testid="approval-track">
                  {report.approvalTrack.replace("_", " ")}
                </p>
              </div>
              <Badge 
                variant={report.approvalTrack === "fast_track" ? "default" : "secondary"}
                className="capitalize"
              >
                {report.approvalTrack.replace("_", " ")}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="p-3 rounded-md bg-muted/30 text-center">
          <p className="text-2xl font-bold">{report.summary.total}</p>
          <p className="text-xs text-muted-foreground">Total Rules</p>
        </div>
        <div className="p-3 rounded-md bg-green-100 dark:bg-green-900/20 text-center">
          <p className="text-2xl font-bold text-green-700 dark:text-green-300">{report.summary.passed}</p>
          <p className="text-xs text-green-600 dark:text-green-400">Passed</p>
        </div>
        <div className="p-3 rounded-md bg-red-100 dark:bg-red-900/20 text-center">
          <p className="text-2xl font-bold text-red-700 dark:text-red-300">{report.summary.failed}</p>
          <p className="text-xs text-red-600 dark:text-red-400">Failed</p>
        </div>
        <div className="p-3 rounded-md bg-yellow-100 dark:bg-yellow-900/20 text-center">
          <p className="text-2xl font-bold text-yellow-700 dark:text-yellow-300">{report.summary.warnings}</p>
          <p className="text-xs text-yellow-600 dark:text-yellow-400">Warnings</p>
        </div>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">All ({report.results.length})</TabsTrigger>
          <TabsTrigger value="failed">Failed ({failedResults.length})</TabsTrigger>
          <TabsTrigger value="warnings">Warnings ({warningResults.length})</TabsTrigger>
          <TabsTrigger value="passed">Passed ({passedResults.length})</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="space-y-3 mt-4">
          {report.results.map((result, idx) => (
            <ValidationResultItem key={idx} result={result} />
          ))}
        </TabsContent>
        <TabsContent value="failed" className="space-y-3 mt-4">
          {failedResults.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <p>No failed validations</p>
            </div>
          ) : (
            failedResults.map((result, idx) => (
              <ValidationResultItem key={idx} result={result} />
            ))
          )}
        </TabsContent>
        <TabsContent value="warnings" className="space-y-3 mt-4">
          {warningResults.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <p>No warnings</p>
            </div>
          ) : (
            warningResults.map((result, idx) => (
              <ValidationResultItem key={idx} result={result} />
            ))
          )}
        </TabsContent>
        <TabsContent value="passed" className="space-y-3 mt-4">
          {passedResults.map((result, idx) => (
            <ValidationResultItem key={idx} result={result} />
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function ValidationPage() {
  const [source, setSource] = useState<"terraform" | "cmdb">("terraform");
  const [content, setContent] = useState(sampleTerraformPlan);
  const [report, setReport] = useState<ValidationReport | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const validateMutation = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", "/api/validate", {
        source,
        content,
        name: source === "terraform" ? "Terraform Plan" : "CMDB Application",
      });
      return res.json() as Promise<ValidationReport>;
    },
    onSuccess: (data) => {
      setReport(data);
      queryClient.invalidateQueries({ queryKey: ["/api/validations"] });
      queryClient.invalidateQueries({ queryKey: ["/api/analytics"] });
      toast({
        title: "Validation Complete",
        description: `Compliance score: ${data.complianceScore}%`,
      });
    },
    onError: () => {
      toast({
        title: "Validation Failed",
        description: "There was an error running the validation.",
        variant: "destructive",
      });
    },
  });

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Validation Engine</h1>
        <p className="text-muted-foreground">Validate infrastructure against architectural standards</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Validation Source</CardTitle>
            <CardDescription>Select your infrastructure source and provide the configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Tabs value={source} onValueChange={(v) => setSource(v as "terraform" | "cmdb")}>
              <TabsList className="w-full">
                <TabsTrigger value="terraform" className="flex-1" data-testid="tab-terraform">
                  <FileJson className="w-4 h-4 mr-2" />
                  Terraform Plan
                </TabsTrigger>
                <TabsTrigger value="cmdb" className="flex-1" data-testid="tab-cmdb">
                  <Database className="w-4 h-4 mr-2" />
                  CMDB Query
                </TabsTrigger>
              </TabsList>
            </Tabs>

            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={source === "terraform" 
                ? "Paste your Terraform plan JSON here..." 
                : "Enter CMDB application ID or name..."
              }
              className="min-h-[300px] font-mono text-sm"
              data-testid="input-validation-content"
            />

            <Button 
              className="w-full" 
              onClick={() => validateMutation.mutate()}
              disabled={validateMutation.isPending || !content.trim()}
              data-testid="button-run-validation"
            >
              {validateMutation.isPending ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Play className="w-4 h-4 mr-2" />
              )}
              Run Validation
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg font-medium">Validation Results</CardTitle>
            <CardDescription>
              {report 
                ? `Validated ${report.sourceName} on ${new Date(report.timestamp).toLocaleString()}`
                : "Run a validation to see results"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {validateMutation.isPending ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
                <p className="text-muted-foreground">Running validation...</p>
              </div>
            ) : report ? (
              <ValidationReportView report={report} />
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <FileCheck className="w-12 h-12 mb-4 opacity-50" />
                <p className="text-lg font-medium">No results yet</p>
                <p className="text-sm">Configure and run a validation to see results</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
