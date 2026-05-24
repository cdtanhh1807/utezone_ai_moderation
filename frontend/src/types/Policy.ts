export type PolicyLevel = '1' | '2' | '3';
export type PolicyStatus = 'active' | 'inactive';
export type PolicyPermission = "000" | "011" | "101" | "110";

export interface PolicyAction {
  permission: PolicyPermission;
  detail: string;
}

export interface Policy {
  id: string;
  name: string;
  description: string;
  level: PolicyLevel;
  status: PolicyStatus;
  action: PolicyAction;
  createdAt: string; // ISO
  updatedAt: string; // ISO
}