import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, boolean, jsonb, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Users table (existing)
export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

// Severity levels for validation rules
export const severityEnum = z.enum(["critical", "high", "medium", "low"]);
export type Severity = z.infer<typeof severityEnum>;

// Rule categories
export const categoryEnum = z.enum(["security", "metadata", "technology", "resilience", "network", "cost"]);
export type RuleCategory = z.infer<typeof categoryEnum>;

// Validation status
export const validationStatusEnum = z.enum(["passed", "failed", "warning", "skipped"]);
export type ValidationStatus = z.infer<typeof validationStatusEnum>;

// Pattern status
export const patternStatusEnum = z.enum(["approved", "draft", "deprecated"]);
export type PatternStatus = z.infer<typeof patternStatusEnum>;

// Approval track
export const approvalTrackEnum = z.enum(["fast_track", "standard", "full_review"]);
export type ApprovalTrack = z.infer<typeof approvalTrackEnum>;

// Architecture Pattern schema
export const patternSchema = z.object({
  id: z.string(),
  name: z.string(),
  version: z.string(),
  status: patternStatusEnum,
  owner: z.string(),
  description: z.string(),
  components: z.array(z.object({
    name: z.string(),
    type: z.string(),
    tier: z.string(),
    minimumInstances: z.number(),
  })),
  networkTopology: z.array(z.object({
    source: z.string(),
    target: z.string(),
    protocol: z.string(),
  })),
  compliance: z.array(z.string()),
  technologies: z.array(z.string()),
});

export type Pattern = z.infer<typeof patternSchema>;

// Validation Rule schema
export const ruleSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  category: categoryEnum,
  severity: severityEnum,
  enabled: z.boolean(),
});

export type Rule = z.infer<typeof ruleSchema>;

// Validation Result schema
export const validationResultSchema = z.object({
  id: z.string(),
  ruleId: z.string(),
  ruleName: z.string(),
  status: validationStatusEnum,
  severity: severityEnum,
  category: categoryEnum,
  message: z.string(),
  resource: z.string().optional(),
  details: z.string().optional(),
});

export type ValidationResult = z.infer<typeof validationResultSchema>;

// Validation Report schema
export const validationReportSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  source: z.enum(["terraform", "cmdb", "manual"]),
  sourceName: z.string(),
  complianceScore: z.number(),
  matchedPattern: z.object({
    id: z.string(),
    name: z.string(),
    similarity: z.number(),
  }).optional(),
  approvalTrack: approvalTrackEnum,
  results: z.array(validationResultSchema),
  summary: z.object({
    total: z.number(),
    passed: z.number(),
    failed: z.number(),
    warnings: z.number(),
    critical: z.number(),
    high: z.number(),
    medium: z.number(),
    low: z.number(),
  }),
});

export type ValidationReport = z.infer<typeof validationReportSchema>;

// Analytics data schema
export const analyticsSchema = z.object({
  totalValidations: z.number(),
  complianceScore: z.number(),
  totalPatterns: z.number(),
  activeIssues: z.number(),
  passRate: z.number(),
  recentTrend: z.array(z.object({
    date: z.string(),
    score: z.number(),
    validations: z.number(),
  })),
  categoryBreakdown: z.array(z.object({
    category: categoryEnum,
    passed: z.number(),
    failed: z.number(),
  })),
  topViolations: z.array(z.object({
    ruleId: z.string(),
    ruleName: z.string(),
    count: z.number(),
    severity: severityEnum,
  })),
  patternUsage: z.array(z.object({
    patternId: z.string(),
    patternName: z.string(),
    count: z.number(),
  })),
});

export type Analytics = z.infer<typeof analyticsSchema>;

// Input schemas for API
export const runValidationInputSchema = z.object({
  source: z.enum(["terraform", "cmdb"]),
  content: z.string(),
  name: z.string().optional(),
});

export type RunValidationInput = z.infer<typeof runValidationInputSchema>;
