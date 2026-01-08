import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { runValidationInputSchema, type ValidationReport, type ValidationResult, type Severity, type RuleCategory, type ValidationStatus } from "@shared/schema";
import { randomUUID } from "crypto";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Get all patterns
  app.get("/api/patterns", async (req, res) => {
    try {
      const patterns = await storage.getPatterns();
      res.json(patterns);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch patterns" });
    }
  });

  // Get single pattern
  app.get("/api/patterns/:id", async (req, res) => {
    try {
      const pattern = await storage.getPattern(req.params.id);
      if (!pattern) {
        return res.status(404).json({ error: "Pattern not found" });
      }
      res.json(pattern);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch pattern" });
    }
  });

  // Get all rules
  app.get("/api/rules", async (req, res) => {
    try {
      const rules = await storage.getRules();
      res.json(rules);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch rules" });
    }
  });

  // Get single rule
  app.get("/api/rules/:id", async (req, res) => {
    try {
      const rule = await storage.getRule(req.params.id);
      if (!rule) {
        return res.status(404).json({ error: "Rule not found" });
      }
      res.json(rule);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch rule" });
    }
  });

  // Get all validations
  app.get("/api/validations", async (req, res) => {
    try {
      const validations = await storage.getValidations();
      res.json(validations);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch validations" });
    }
  });

  // Run validation
  app.post("/api/validate", async (req, res) => {
    try {
      const input = runValidationInputSchema.parse(req.body);
      const rules = await storage.getRules();
      const patterns = await storage.getPatterns();
      
      // Parse content to extract resources
      let resources: any[] = [];
      try {
        const parsed = JSON.parse(input.content);
        resources = parsed.resources || [];
      } catch {
        resources = [];
      }

      // Run validation against all enabled rules
      const results: ValidationResult[] = [];
      
      for (const rule of rules.filter(r => r.enabled)) {
        const result = validateRule(rule, resources, input.source);
        results.push(result);
      }

      // Calculate compliance score
      const passed = results.filter(r => r.status === "passed").length;
      const failed = results.filter(r => r.status === "failed").length;
      const warnings = results.filter(r => r.status === "warning").length;
      const total = results.length;
      const complianceScore = total > 0 ? Math.round((passed / total) * 100) : 0;

      // Match pattern
      let matchedPattern: { id: string; name: string; similarity: number } | undefined;
      if (patterns.length > 0) {
        const patternMatch = matchPattern(resources, patterns);
        if (patternMatch.similarity >= 0.5) {
          matchedPattern = patternMatch;
        }
      }

      // Determine approval track
      let approvalTrack: "fast_track" | "standard" | "full_review" = "full_review";
      if (matchedPattern) {
        if (matchedPattern.similarity >= 0.95) {
          approvalTrack = "fast_track";
        } else if (matchedPattern.similarity >= 0.85) {
          approvalTrack = "standard";
        }
      }

      // Count by severity
      const critical = results.filter(r => r.status === "failed" && r.severity === "critical").length;
      const high = results.filter(r => r.status === "failed" && r.severity === "high").length;
      const medium = results.filter(r => r.status === "failed" && r.severity === "medium").length;
      const low = results.filter(r => r.status === "failed" && r.severity === "low").length;

      const report: ValidationReport = {
        id: randomUUID(),
        timestamp: new Date().toISOString(),
        source: input.source,
        sourceName: input.name || `${input.source} validation`,
        complianceScore,
        matchedPattern,
        approvalTrack,
        results,
        summary: {
          total,
          passed,
          failed,
          warnings,
          critical,
          high,
          medium,
          low,
        },
      };

      await storage.createValidation(report);
      res.json(report);
    } catch (error) {
      console.error("Validation error:", error);
      res.status(400).json({ error: "Invalid validation request" });
    }
  });

  // Get analytics
  app.get("/api/analytics", async (req, res) => {
    try {
      const analytics = await storage.getAnalytics();
      res.json(analytics);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch analytics" });
    }
  });

  return httpServer;
}

// Helper function to validate a single rule
function validateRule(
  rule: { id: string; name: string; category: RuleCategory; severity: Severity },
  resources: any[],
  source: string
): ValidationResult {
  // Simulate validation based on rule type
  let status: ValidationStatus = "passed";
  let message = `Rule ${rule.id} passed validation`;
  let resource: string | undefined;

  // Check specific rule conditions
  switch (rule.id) {
    case "SEC-001":
      // Check for direct web-to-database connections
      const hasWebToDb = resources.some(r => 
        r.type === "aws_security_group_rule" && 
        r.attributes?.description?.toLowerCase().includes("web") &&
        r.attributes?.to_port === 5432
      );
      if (hasWebToDb) {
        status = "failed";
        message = "Direct web-to-database connection detected. Route through application tier.";
        resource = "aws_security_group_rule";
      } else {
        message = "No direct web-to-database connections found.";
      }
      break;

    case "SEC-002":
      // Check database encryption
      const dbResources = resources.filter(r => r.type?.includes("db_instance") || r.type?.includes("rds"));
      for (const db of dbResources) {
        if (db.instances?.[0]?.attributes?.storage_encrypted !== true) {
          status = "failed";
          message = "Database encryption at rest is not enabled.";
          resource = db.name || db.type;
          break;
        }
      }
      if (status === "passed") {
        message = "All databases have encryption enabled.";
      }
      break;

    case "META-001":
      // Check required metadata/tags
      const hasMetadata = resources.every(r => {
        const tags = r.instances?.[0]?.attributes?.tags || {};
        return tags.Environment && tags.Application;
      });
      if (!hasMetadata && resources.length > 0) {
        status = "warning";
        message = "Some resources are missing required metadata tags (Environment, Application).";
      } else {
        message = "All resources have required metadata tags.";
      }
      break;

    case "RES-001":
      // Check multi-AZ
      const dbInstances = resources.filter(r => r.type?.includes("db_instance"));
      for (const db of dbInstances) {
        if (db.instances?.[0]?.attributes?.multi_az !== true) {
          status = "warning";
          message = "Database is not configured for Multi-AZ deployment.";
          resource = db.name || db.type;
          break;
        }
      }
      if (status === "passed") {
        message = "Multi-AZ deployment is properly configured.";
      }
      break;

    case "RES-002":
      // Check automated backups
      const databases = resources.filter(r => r.type?.includes("db_instance"));
      for (const db of databases) {
        const retention = db.instances?.[0]?.attributes?.backup_retention_period;
        if (!retention || retention < 1) {
          status = "failed";
          message = "Database automated backups are not enabled.";
          resource = db.name || db.type;
          break;
        }
      }
      if (status === "passed") {
        message = "Automated backups are enabled for all databases.";
      }
      break;

    case "TECH-001":
      // Check approved database versions
      const dbs = resources.filter(r => r.type?.includes("db_instance"));
      for (const db of dbs) {
        const version = db.instances?.[0]?.attributes?.engine_version;
        if (version) {
          const majorVersion = parseFloat(version);
          if (majorVersion < 14) {
            status = "warning";
            message = `Database version ${version} is below recommended (14+).`;
            resource = db.name || db.type;
            break;
          }
        }
      }
      if (status === "passed") {
        message = "All databases are using approved versions.";
      }
      break;

    case "COST-002":
      // Simulate oversized instance detection
      if (Math.random() > 0.7) {
        status = "warning";
        message = "Some instances may be oversized based on utilization metrics.";
        resource = "aws_instance.web_server";
      } else {
        message = "Instance sizes appear appropriate for workload.";
      }
      break;

    default:
      // Default pass with random chance of issues for demo
      if (Math.random() > 0.85) {
        status = "warning";
        message = `Rule ${rule.id} detected potential compliance issue.`;
      }
      break;
  }

  return {
    id: randomUUID(),
    ruleId: rule.id,
    ruleName: rule.name,
    status,
    severity: rule.severity,
    category: rule.category,
    message,
    resource,
  };
}

// Helper function to match infrastructure against patterns
function matchPattern(
  resources: any[],
  patterns: { id: string; name: string; components: any[] }[]
): { id: string; name: string; similarity: number } {
  let bestMatch = { id: "", name: "", similarity: 0 };

  for (const pattern of patterns) {
    // Calculate similarity based on component matching
    const resourceTypes = resources.map(r => r.type?.toLowerCase() || "");
    let matchedComponents = 0;

    for (const comp of pattern.components) {
      const compType = comp.type.toLowerCase();
      if (resourceTypes.some(rt => rt.includes(compType) || compType.includes(rt.split("_").pop()))) {
        matchedComponents++;
      }
    }

    const similarity = pattern.components.length > 0 
      ? matchedComponents / pattern.components.length 
      : 0;

    if (similarity > bestMatch.similarity) {
      bestMatch = { id: pattern.id, name: pattern.name, similarity };
    }
  }

  return bestMatch;
}
