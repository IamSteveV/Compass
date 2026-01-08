import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { 
  Shield, 
  Search, 
  FileText, 
  Cpu, 
  Activity,
  Network,
  DollarSign,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import type { Rule, RuleCategory, Severity } from "@shared/schema";
import { useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const categoryIcons: Record<RuleCategory, React.ElementType> = {
  security: Shield,
  metadata: FileText,
  technology: Cpu,
  resilience: Activity,
  network: Network,
  cost: DollarSign,
};

const categoryColors: Record<RuleCategory, string> = {
  security: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300",
  metadata: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300",
  technology: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300",
  resilience: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300",
  network: "bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300",
  cost: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
};

const severityColors: Record<Severity, string> = {
  critical: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300",
  high: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300",
  medium: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
  low: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300",
};

const categoryDescriptions: Record<RuleCategory, string> = {
  security: "Rules ensuring secure architecture configurations",
  metadata: "Rules validating required documentation and metadata",
  technology: "Rules checking approved technologies and versions",
  resilience: "Rules verifying high availability and disaster recovery",
  network: "Rules for network segmentation and connectivity",
  cost: "Rules for cost optimization and resource efficiency",
};

function RuleItem({ rule }: { rule: Rule }) {
  return (
    <div 
      className="p-4 rounded-md border bg-card hover-elevate"
      data-testid={`rule-item-${rule.id}`}
    >
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-medium">{rule.name}</span>
            <Badge variant="outline" className="text-xs font-mono">{rule.id}</Badge>
          </div>
          <p className="text-sm text-muted-foreground">{rule.description}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Badge variant="secondary" className={`text-xs ${severityColors[rule.severity]}`}>
            {rule.severity}
          </Badge>
          <Badge variant={rule.enabled ? "default" : "secondary"} className="text-xs">
            {rule.enabled ? "Enabled" : "Disabled"}
          </Badge>
        </div>
      </div>
    </div>
  );
}

function CategorySection({ 
  category, 
  rules,
  expanded,
  onToggle,
}: { 
  category: RuleCategory; 
  rules: Rule[];
  expanded: boolean;
  onToggle: () => void;
}) {
  const Icon = categoryIcons[category];
  
  return (
    <Card>
      <CardHeader 
        className="cursor-pointer hover-elevate" 
        onClick={onToggle}
        data-testid={`category-header-${category}`}
      >
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`flex items-center justify-center w-10 h-10 rounded-md ${categoryColors[category]}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <CardTitle className="text-lg font-medium capitalize">{category}</CardTitle>
              <CardDescription className="text-sm">
                {categoryDescriptions[category]}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="secondary">{rules.length} rules</Badge>
            {expanded ? (
              <ChevronDown className="w-5 h-5 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-5 h-5 text-muted-foreground" />
            )}
          </div>
        </div>
      </CardHeader>
      {expanded && (
        <CardContent className="pt-0">
          <div className="space-y-3">
            {rules.map((rule) => (
              <RuleItem key={rule.id} rule={rule} />
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

function RuleSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <Skeleton className="w-10 h-10 rounded-md" />
          <div className="flex-1">
            <Skeleton className="h-5 w-32 mb-2" />
            <Skeleton className="h-4 w-48" />
          </div>
        </div>
      </CardHeader>
    </Card>
  );
}

export default function RulesPage() {
  const [search, setSearch] = useState("");
  const [expandedCategories, setExpandedCategories] = useState<RuleCategory[]>(["security"]);

  const { data: rules, isLoading } = useQuery<Rule[]>({
    queryKey: ["/api/rules"],
  });

  const toggleCategory = (category: RuleCategory) => {
    setExpandedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

  const filteredRules = rules?.filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.id.toLowerCase().includes(search.toLowerCase()) ||
    r.description.toLowerCase().includes(search.toLowerCase())
  );

  const groupedRules = filteredRules?.reduce((acc, rule) => {
    if (!acc[rule.category]) acc[rule.category] = [];
    acc[rule.category].push(rule);
    return acc;
  }, {} as Record<RuleCategory, Rule[]>);

  const categories: RuleCategory[] = ["security", "metadata", "technology", "resilience", "network", "cost"];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Validation Rules</h1>
          <p className="text-muted-foreground">Browse and manage architectural validation rules</p>
        </div>
        <Badge variant="secondary" className="text-sm">
          {rules?.length ?? 0} total rules
        </Badge>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search rules..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
          data-testid="input-search-rules"
        />
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <>
            <RuleSkeleton />
            <RuleSkeleton />
            <RuleSkeleton />
          </>
        ) : (
          categories.map((category) => {
            const categoryRules = groupedRules?.[category] ?? [];
            if (categoryRules.length === 0 && search) return null;
            return (
              <CategorySection
                key={category}
                category={category}
                rules={categoryRules}
                expanded={expandedCategories.includes(category)}
                onToggle={() => toggleCategory(category)}
              />
            );
          })
        )}
      </div>
    </div>
  );
}
