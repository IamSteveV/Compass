import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  ShieldCheck, 
  Layers, 
  FileCheck, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import type { Analytics, ValidationReport } from "@shared/schema";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";

function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendValue,
  loading 
}: { 
  title: string; 
  value: string | number; 
  icon: React.ElementType; 
  trend?: "up" | "down";
  trendValue?: string;
  loading?: boolean;
}) {
  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-10 w-10 rounded-md" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-8 w-20 mt-4" />
          <Skeleton className="h-4 w-24 mt-2" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center justify-center w-10 h-10 rounded-md bg-primary/10">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-sm ${
              trend === "up" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            }`}>
              {trend === "up" ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        <div className="mt-4">
          <p className="text-3xl font-bold tracking-tight" data-testid={`metric-${title.toLowerCase().replace(/\s+/g, "-")}`}>
            {value}
          </p>
          <p className="text-sm text-muted-foreground mt-1">{title}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function ComplianceChart({ data }: { data: { date: string; score: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }} 
          className="text-muted-foreground"
          tickLine={false}
          axisLine={false}
        />
        <YAxis 
          domain={[0, 100]} 
          tick={{ fontSize: 12 }} 
          className="text-muted-foreground"
          tickLine={false}
          axisLine={false}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: "hsl(var(--card))", 
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
          labelStyle={{ color: "hsl(var(--foreground))" }}
        />
        <Area 
          type="monotone" 
          dataKey="score" 
          stroke="hsl(var(--primary))" 
          fill="url(#colorScore)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function CategoryChart({ data }: { data: { category: string; passed: number; failed: number }[] }) {
  const chartColors = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
    "hsl(var(--chart-4))",
    "hsl(var(--chart-5))",
    "hsl(var(--primary))",
  ];

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis 
          dataKey="category" 
          tick={{ fontSize: 11 }} 
          className="text-muted-foreground"
          tickLine={false}
          axisLine={false}
        />
        <YAxis 
          tick={{ fontSize: 12 }} 
          className="text-muted-foreground"
          tickLine={false}
          axisLine={false}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: "hsl(var(--card))", 
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
          labelStyle={{ color: "hsl(var(--foreground))" }}
        />
        <Bar dataKey="passed" stackId="a" fill="hsl(160 75% 40%)" name="Passed" radius={[0, 0, 0, 0]} />
        <Bar dataKey="failed" stackId="a" fill="hsl(0 84% 42%)" name="Failed" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function RecentValidationsTable({ data, loading }: { data?: ValidationReport[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <FileCheck className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p>No validations yet</p>
        <p className="text-sm">Run your first validation to see results here</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {data.slice(0, 5).map((report) => (
        <div 
          key={report.id} 
          className="flex items-center justify-between p-4 rounded-md bg-muted/30 hover-elevate"
          data-testid={`validation-row-${report.id}`}
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
              report.complianceScore >= 90 
                ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400"
                : report.complianceScore >= 70
                ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400"
                : "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400"
            }`}>
              {report.complianceScore >= 90 ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <XCircle className="w-4 h-4" />
              )}
            </div>
            <div className="min-w-0">
              <p className="font-medium truncate">{report.sourceName}</p>
              <p className="text-xs text-muted-foreground">{report.source} validation</p>
            </div>
          </div>
          <div className="flex items-center gap-4 flex-shrink-0">
            <Badge variant={report.approvalTrack === "fast_track" ? "default" : "secondary"}>
              {report.approvalTrack.replace("_", " ")}
            </Badge>
            <div className="text-right">
              <p className="font-semibold">{report.complianceScore}%</p>
              <p className="text-xs text-muted-foreground">
                {new Date(report.timestamp).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery<Analytics>({
    queryKey: ["/api/analytics"],
  });

  const { data: validations, isLoading: validationsLoading } = useQuery<ValidationReport[]>({
    queryKey: ["/api/validations"],
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Architecture validation overview</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Compliance Score"
          value={analytics ? `${analytics.complianceScore}%` : "0%"}
          icon={ShieldCheck}
          trend="up"
          trendValue="+2.5%"
          loading={analyticsLoading}
        />
        <MetricCard
          title="Total Patterns"
          value={analytics?.totalPatterns ?? 0}
          icon={Layers}
          loading={analyticsLoading}
        />
        <MetricCard
          title="Validations"
          value={analytics?.totalValidations ?? 0}
          icon={FileCheck}
          trend="up"
          trendValue="+12"
          loading={analyticsLoading}
        />
        <MetricCard
          title="Active Issues"
          value={analytics?.activeIssues ?? 0}
          icon={AlertTriangle}
          trend="down"
          trendValue="-3"
          loading={analyticsLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Compliance Trend</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <Skeleton className="h-[250px] w-full" />
            ) : (
              <ComplianceChart data={analytics?.recentTrend ?? []} />
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Validation by Category</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <Skeleton className="h-[250px] w-full" />
            ) : (
              <CategoryChart data={analytics?.categoryBreakdown ?? []} />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-medium">Recent Validations</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentValidationsTable data={validations} loading={validationsLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
