import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { 
  BarChart3, 
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Layers,
} from "lucide-react";
import type { Analytics } from "@shared/schema";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";

const severityColors = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#ca8a04",
  low: "#2563eb",
};

function TopViolationsChart({ data }: { data: { ruleName: string; count: number; severity: string }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart 
        data={data} 
        layout="vertical"
        margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
      >
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 12 }} className="text-muted-foreground" />
        <YAxis 
          type="category" 
          dataKey="ruleName" 
          width={150}
          tick={{ fontSize: 11 }} 
          className="text-muted-foreground"
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: "hsl(var(--card))", 
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
          labelStyle={{ color: "hsl(var(--foreground))" }}
        />
        <Bar 
          dataKey="count" 
          radius={[0, 4, 4, 0]}
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={severityColors[entry.severity as keyof typeof severityColors] || "hsl(var(--primary))"} 
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function PatternUsageChart({ data }: { data: { patternName: string; count: number }[] }) {
  const COLORS = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
    "hsl(var(--chart-4))",
    "hsl(var(--chart-5))",
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="count"
          nameKey="patternName"
          label={({ patternName, percent }) => `${patternName} (${(percent * 100).toFixed(0)}%)`}
          labelLine={false}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          contentStyle={{ 
            backgroundColor: "hsl(var(--card))", 
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

function ComplianceTrendChart({ data }: { data: { date: string; score: number; validations: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: -20, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }} 
          className="text-muted-foreground"
          tickLine={false}
        />
        <YAxis 
          yAxisId="left"
          domain={[0, 100]} 
          tick={{ fontSize: 12 }} 
          className="text-muted-foreground"
          tickLine={false}
        />
        <YAxis 
          yAxisId="right"
          orientation="right"
          tick={{ fontSize: 12 }} 
          className="text-muted-foreground"
          tickLine={false}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: "hsl(var(--card))", 
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
          labelStyle={{ color: "hsl(var(--foreground))" }}
        />
        <Line 
          yAxisId="left"
          type="monotone" 
          dataKey="score" 
          stroke="hsl(var(--primary))" 
          strokeWidth={2}
          dot={{ fill: "hsl(var(--primary))", strokeWidth: 2 }}
          name="Compliance Score"
        />
        <Line 
          yAxisId="right"
          type="monotone" 
          dataKey="validations" 
          stroke="hsl(var(--chart-2))" 
          strokeWidth={2}
          dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2 }}
          name="Validations"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function StatCard({ 
  title, 
  value, 
  description,
  icon: Icon,
  trend,
  loading,
}: { 
  title: string; 
  value: string | number;
  description?: string;
  icon: React.ElementType;
  trend?: "positive" | "negative";
  loading?: boolean;
}) {
  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <Skeleton className="h-10 w-10 rounded-md mb-4" />
          <Skeleton className="h-8 w-20 mb-2" />
          <Skeleton className="h-4 w-32" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-center w-10 h-10 rounded-md bg-primary/10 mb-4">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        <p className="text-3xl font-bold tracking-tight" data-testid={`stat-${title.toLowerCase().replace(/\s+/g, "-")}`}>
          {value}
        </p>
        <p className="text-sm text-muted-foreground mt-1">{title}</p>
        {description && (
          <p className={`text-xs mt-2 ${
            trend === "positive" ? "text-green-600 dark:text-green-400" :
            trend === "negative" ? "text-red-600 dark:text-red-400" :
            "text-muted-foreground"
          }`}>
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery<Analytics>({
    queryKey: ["/api/analytics"],
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">Compliance metrics and trend analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Pass Rate"
          value={analytics ? `${analytics.passRate}%` : "0%"}
          description="+5% from last week"
          icon={CheckCircle2}
          trend="positive"
          loading={isLoading}
        />
        <StatCard
          title="Total Validations"
          value={analytics?.totalValidations ?? 0}
          description="Last 30 days"
          icon={BarChart3}
          loading={isLoading}
        />
        <StatCard
          title="Active Patterns"
          value={analytics?.totalPatterns ?? 0}
          icon={Layers}
          loading={isLoading}
        />
        <StatCard
          title="Open Issues"
          value={analytics?.activeIssues ?? 0}
          description="-3 from last week"
          icon={AlertTriangle}
          trend="positive"
          loading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Compliance Trend</CardTitle>
            <CardDescription>Score and validation volume over time</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : (
              <ComplianceTrendChart data={analytics?.recentTrend ?? []} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">Pattern Usage</CardTitle>
            <CardDescription>Distribution of matched patterns</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : analytics?.patternUsage && analytics.patternUsage.length > 0 ? (
              <PatternUsageChart data={analytics.patternUsage} />
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Layers className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No pattern data yet</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-medium">Top Rule Violations</CardTitle>
          <CardDescription>Most frequently violated rules by severity</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : analytics?.topViolations && analytics.topViolations.length > 0 ? (
            <TopViolationsChart data={analytics.topViolations} />
          ) : (
            <div className="h-[300px] flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <CheckCircle2 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No violations recorded</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
