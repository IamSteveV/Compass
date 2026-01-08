import { type User, type InsertUser, type Pattern, type Rule, type ValidationReport, type Analytics, type RuleCategory, type Severity } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  getPatterns(): Promise<Pattern[]>;
  getPattern(id: string): Promise<Pattern | undefined>;
  
  getRules(): Promise<Rule[]>;
  getRule(id: string): Promise<Rule | undefined>;
  
  getValidations(): Promise<ValidationReport[]>;
  createValidation(report: ValidationReport): Promise<ValidationReport>;
  
  getAnalytics(): Promise<Analytics>;
}

// Pre-defined patterns based on Compass system
const patterns: Pattern[] = [
  {
    id: "PAT-001",
    name: "Standard 3-Tier Web Application",
    version: "1.0",
    status: "approved",
    owner: "Enterprise Architecture",
    description: "A standard three-tier web application pattern with load-balanced web tier, application tier, and highly available database tier. Suitable for most enterprise web applications.",
    components: [
      { name: "Load Balancer", type: "alb", tier: "web", minimumInstances: 1 },
      { name: "Web Servers", type: "ec2", tier: "web", minimumInstances: 2 },
      { name: "App Servers", type: "ec2", tier: "app", minimumInstances: 2 },
      { name: "Database", type: "rds", tier: "data", minimumInstances: 1 },
    ],
    networkTopology: [
      { source: "Load Balancer", target: "Web Servers", protocol: "https" },
      { source: "Web Servers", target: "App Servers", protocol: "https" },
      { source: "App Servers", target: "Database", protocol: "tcp/5432" },
    ],
    compliance: ["PCI-DSS", "SOX", "SOC2"],
    technologies: ["AWS", "EC2", "RDS", "ALB", "PostgreSQL"],
  },
  {
    id: "PAT-002",
    name: "Microservices Architecture",
    version: "1.0",
    status: "approved",
    owner: "Cloud Platform Team",
    description: "A cloud-native microservices architecture with API gateway, containerized services, individual databases per service, and message queue for async communication.",
    components: [
      { name: "API Gateway", type: "apigw", tier: "edge", minimumInstances: 1 },
      { name: "Service Instances", type: "ecs", tier: "app", minimumInstances: 3 },
      { name: "Service Databases", type: "rds", tier: "data", minimumInstances: 1 },
      { name: "Message Queue", type: "sqs", tier: "integration", minimumInstances: 1 },
    ],
    networkTopology: [
      { source: "API Gateway", target: "Service Instances", protocol: "https" },
      { source: "Service Instances", target: "Service Databases", protocol: "tcp/5432" },
      { source: "Service Instances", target: "Message Queue", protocol: "https" },
    ],
    compliance: ["Cloud-Native", "SOC2", "ISO27001"],
    technologies: ["AWS", "ECS", "Fargate", "RDS", "SQS", "API Gateway"],
  },
  {
    id: "COMP-001",
    name: "High Availability Database",
    version: "1.0",
    status: "approved",
    owner: "Database Team",
    description: "A highly available database pattern with multi-AZ primary, read replicas, automated backups, and encryption at rest. Designed for mission-critical data workloads.",
    components: [
      { name: "Primary Database", type: "rds", tier: "data", minimumInstances: 1 },
      { name: "Read Replicas", type: "rds", tier: "data", minimumInstances: 2 },
    ],
    networkTopology: [
      { source: "Primary Database", target: "Read Replicas", protocol: "replication" },
    ],
    compliance: ["HA", "DR", "Backup", "Encryption"],
    technologies: ["AWS", "RDS", "PostgreSQL", "Multi-AZ"],
  },
];

// Pre-defined validation rules based on Compass system
const rules: Rule[] = [
  // Security Rules
  { id: "SEC-001", name: "No Direct Web-to-Database Connections", description: "Web tier must not connect directly to database tier. All database access must go through the application tier.", category: "security", severity: "critical", enabled: true },
  { id: "SEC-002", name: "Production Database Encryption", description: "All production databases must have encryption at rest enabled using customer-managed keys.", category: "security", severity: "critical", enabled: true },
  { id: "SEC-003", name: "DMZ Isolation", description: "DMZ components must be isolated from internal database tier with no direct connectivity.", category: "security", severity: "critical", enabled: true },
  { id: "SEC-004", name: "Production Backup Requirement", description: "All production servers must have automated backup enabled with minimum 30-day retention.", category: "security", severity: "high", enabled: true },
  
  // Metadata Rules
  { id: "META-001", name: "Required Metadata Fields", description: "All resources must have Environment, Application, Owner, and CostCenter tags defined.", category: "metadata", severity: "high", enabled: true },
  { id: "META-002", name: "Production DR Tier", description: "Production environments must have DR tier designation (Tier 1, 2, or 3) specified.", category: "metadata", severity: "medium", enabled: true },
  
  // Technology Rules
  { id: "TECH-001", name: "Approved Database Versions", description: "Only approved database versions are permitted: PostgreSQL 14+, MySQL 8.0+, Oracle 19c+.", category: "technology", severity: "medium", enabled: true },
  { id: "TECH-002", name: "Approved Instance Types", description: "Only approved instance types are permitted per tier. Web/App: t3, m5, c5. Database: r5, r6g.", category: "technology", severity: "low", enabled: true },
  
  // Resilience Rules
  { id: "RES-001", name: "Production Multi-AZ Requirement", description: "All production workloads must be deployed across multiple availability zones.", category: "resilience", severity: "high", enabled: true },
  { id: "RES-002", name: "Database Automated Backups", description: "All databases must have automated backups enabled with point-in-time recovery.", category: "resilience", severity: "high", enabled: true },
  
  // Network Rules
  { id: "NET-001", name: "Database Tier Subnet Isolation", description: "Database tier must be deployed in private subnets with no public IP addresses.", category: "network", severity: "critical", enabled: true },
  { id: "NET-002", name: "Load Balancer SSL/TLS", description: "All load balancers must terminate SSL/TLS with minimum TLS 1.2.", category: "network", severity: "high", enabled: true },
  { id: "NET-003", name: "VPC Flow Logs", description: "VPC flow logs must be enabled for network traffic analysis and security monitoring.", category: "network", severity: "medium", enabled: true },
  
  // Cost Rules
  { id: "COST-001", name: "Unused Resource Detection", description: "Resources with no activity for 30+ days should be flagged for review or termination.", category: "cost", severity: "low", enabled: true },
  { id: "COST-002", name: "Oversized Instance Detection", description: "Instances with average CPU < 10% over 7 days should be considered for downsizing.", category: "cost", severity: "low", enabled: true },
];

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private validations: ValidationReport[];

  constructor() {
    this.users = new Map();
    this.validations = [];
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async getPatterns(): Promise<Pattern[]> {
    return patterns;
  }

  async getPattern(id: string): Promise<Pattern | undefined> {
    return patterns.find(p => p.id === id);
  }

  async getRules(): Promise<Rule[]> {
    return rules;
  }

  async getRule(id: string): Promise<Rule | undefined> {
    return rules.find(r => r.id === id);
  }

  async getValidations(): Promise<ValidationReport[]> {
    return this.validations.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  async createValidation(report: ValidationReport): Promise<ValidationReport> {
    this.validations.push(report);
    return report;
  }

  async getAnalytics(): Promise<Analytics> {
    const totalValidations = this.validations.length;
    const passedValidations = this.validations.filter(v => v.complianceScore >= 80).length;
    const passRate = totalValidations > 0 ? Math.round((passedValidations / totalValidations) * 100) : 85;
    
    // Calculate average compliance score
    const avgScore = totalValidations > 0
      ? Math.round(this.validations.reduce((sum, v) => sum + v.complianceScore, 0) / totalValidations)
      : 87;

    // Count active issues (failed results)
    const activeIssues = this.validations.reduce((count, v) => 
      count + v.results.filter(r => r.status === "failed").length, 0
    );

    // Generate trend data for last 7 days
    const recentTrend = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      recentTrend.push({
        date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        score: Math.round(80 + Math.random() * 15),
        validations: Math.floor(5 + Math.random() * 10),
      });
    }

    // Category breakdown
    const categoryBreakdown: { category: RuleCategory; passed: number; failed: number }[] = [
      { category: "security", passed: 85, failed: 15 },
      { category: "metadata", passed: 92, failed: 8 },
      { category: "technology", passed: 78, failed: 22 },
      { category: "resilience", passed: 88, failed: 12 },
      { category: "network", passed: 95, failed: 5 },
      { category: "cost", passed: 70, failed: 30 },
    ];

    // Top violations
    const topViolations: { ruleId: string; ruleName: string; count: number; severity: Severity }[] = [
      { ruleId: "COST-002", ruleName: "Oversized Instance Detection", count: 23, severity: "low" },
      { ruleId: "META-001", ruleName: "Required Metadata Fields", count: 18, severity: "high" },
      { ruleId: "TECH-002", ruleName: "Approved Instance Types", count: 12, severity: "low" },
      { ruleId: "RES-001", ruleName: "Production Multi-AZ", count: 8, severity: "high" },
      { ruleId: "SEC-004", ruleName: "Production Backup Requirement", count: 5, severity: "high" },
    ];

    // Pattern usage
    const patternUsage = [
      { patternId: "PAT-001", patternName: "3-Tier Web", count: 45 },
      { patternId: "PAT-002", patternName: "Microservices", count: 32 },
      { patternId: "COMP-001", patternName: "HA Database", count: 23 },
    ];

    return {
      totalValidations: totalValidations || 47,
      complianceScore: avgScore,
      totalPatterns: patterns.length,
      activeIssues: activeIssues || 12,
      passRate,
      recentTrend,
      categoryBreakdown,
      topViolations,
      patternUsage,
    };
  }
}

export const storage = new MemStorage();
