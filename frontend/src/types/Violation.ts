export interface Violation {
  violatorID: string;
  policyId: string;
  count: number;
  actionId: string;
  updatedAt: string[]; // ISO
}