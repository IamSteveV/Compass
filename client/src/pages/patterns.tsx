import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { 
  Layers, 
  Search, 
  Server, 
  Database, 
  Globe, 
  Network,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle,
} from "lucide-react";
import type { Pattern } from "@shared/schema";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";

const patternIcons: Record<string, React.ElementType> = {
  "PAT-001": Globe,
  "PAT-002": Network,
  "COMP-001": Database,
};

const statusColors = {
  approved: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300",
  draft: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
  deprecated: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300",
};

const statusIcons = {
  approved: CheckCircle2,
  draft: Clock,
  deprecated: AlertCircle,
};

function PatternCard({ pattern, onView }: { pattern: Pattern; onView: () => void }) {
  const Icon = patternIcons[pattern.id] || Layers;
  const StatusIcon = statusIcons[pattern.status];

  return (
    <Card className="flex flex-col hover-elevate" data-testid={`pattern-card-${pattern.id}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-md bg-primary/10">
              <Icon className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base font-medium">{pattern.name}</CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">{pattern.id} v{pattern.version}</p>
            </div>
          </div>
          <Badge variant="secondary" className={statusColors[pattern.status]}>
            <StatusIcon className="w-3 h-3 mr-1" />
            {pattern.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <CardDescription className="line-clamp-2 text-sm">
          {pattern.description}
        </CardDescription>
        <div className="flex flex-wrap gap-1.5 mt-4">
          {pattern.technologies.slice(0, 3).map((tech) => (
            <Badge key={tech} variant="outline" className="text-xs">
              {tech}
            </Badge>
          ))}
          {pattern.technologies.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{pattern.technologies.length - 3}
            </Badge>
          )}
        </div>
      </CardContent>
      <CardFooter className="pt-3 border-t">
        <div className="flex items-center justify-between w-full gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Server className="w-3.5 h-3.5" />
            <span>{pattern.components.length} components</span>
          </div>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onView}
            data-testid={`button-view-${pattern.id}`}
          >
            <Eye className="w-4 h-4 mr-1" />
            View Details
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

function PatternDetailDialog({ 
  pattern, 
  open, 
  onClose 
}: { 
  pattern: Pattern | null; 
  open: boolean; 
  onClose: () => void;
}) {
  if (!pattern) return null;
  
  const Icon = patternIcons[pattern.id] || Layers;
  const StatusIcon = statusIcons[pattern.status];

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex items-center justify-center w-12 h-12 rounded-md bg-primary/10">
              <Icon className="w-6 h-6 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-xl">{pattern.name}</DialogTitle>
              <DialogDescription className="text-sm">
                {pattern.id} v{pattern.version} by {pattern.owner}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary" className={statusColors[pattern.status]}>
                <StatusIcon className="w-3 h-3 mr-1" />
                {pattern.status}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{pattern.description}</p>
          </div>

          <Separator />

          <div>
            <h4 className="font-medium mb-3">Components</h4>
            <div className="space-y-2">
              {pattern.components.map((comp, idx) => (
                <div 
                  key={idx} 
                  className="flex items-center justify-between p-3 rounded-md bg-muted/30"
                >
                  <div className="flex items-center gap-2">
                    <Server className="w-4 h-4 text-muted-foreground" />
                    <span className="font-medium text-sm">{comp.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">{comp.tier}</Badge>
                    <span className="text-xs text-muted-foreground">
                      min: {comp.minimumInstances} instances
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          <div>
            <h4 className="font-medium mb-3">Network Topology</h4>
            <div className="space-y-2">
              {pattern.networkTopology.map((link, idx) => (
                <div 
                  key={idx} 
                  className="flex items-center gap-3 p-3 rounded-md bg-muted/30 text-sm"
                >
                  <span className="font-medium">{link.source}</span>
                  <span className="text-muted-foreground">→</span>
                  <span className="font-medium">{link.target}</span>
                  <Badge variant="outline" className="ml-auto text-xs">{link.protocol}</Badge>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Technologies</h4>
              <div className="flex flex-wrap gap-1.5">
                {pattern.technologies.map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">{tech}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Compliance</h4>
              <div className="flex flex-wrap gap-1.5">
                {pattern.compliance.map((comp) => (
                  <Badge key={comp} variant="outline" className="text-xs">{comp}</Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function PatternSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          <Skeleton className="w-10 h-10 rounded-md" />
          <div className="flex-1">
            <Skeleton className="h-5 w-3/4 mb-2" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-2/3 mb-4" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-16" />
        </div>
      </CardContent>
      <CardFooter className="pt-3 border-t">
        <Skeleton className="h-8 w-full" />
      </CardFooter>
    </Card>
  );
}

export default function PatternsPage() {
  const [search, setSearch] = useState("");
  const [selectedPattern, setSelectedPattern] = useState<Pattern | null>(null);

  const { data: patterns, isLoading } = useQuery<Pattern[]>({
    queryKey: ["/api/patterns"],
  });

  const filteredPatterns = patterns?.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.id.toLowerCase().includes(search.toLowerCase()) ||
    p.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Pattern Library</h1>
          <p className="text-muted-foreground">Pre-approved architecture patterns</p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search patterns..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
          data-testid="input-search-patterns"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <>
            <PatternSkeleton />
            <PatternSkeleton />
            <PatternSkeleton />
          </>
        ) : filteredPatterns?.length === 0 ? (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <Layers className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium">No patterns found</p>
            <p className="text-sm">Try adjusting your search query</p>
          </div>
        ) : (
          filteredPatterns?.map((pattern) => (
            <PatternCard 
              key={pattern.id} 
              pattern={pattern} 
              onView={() => setSelectedPattern(pattern)}
            />
          ))
        )}
      </div>

      <PatternDetailDialog 
        pattern={selectedPattern}
        open={!!selectedPattern}
        onClose={() => setSelectedPattern(null)}
      />
    </div>
  );
}
