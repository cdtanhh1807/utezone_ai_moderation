// types/Report.ts
export type ReportType = 'account' | 'post' | 'comment' | 'message';
export type ReportSource = 'user' | 'ai';
export type ReportStatus = 'pending' | 'approved' | 'rejected';

export interface Report {
  id: string;
  type: ReportType;
  source: ReportSource;
  reporterID: string;
  reporterEmail: string;     // ➕ thêm
  reporterName: string;      // ➕ thêm
  targetID: string;
  targetOwnerEmail: string;  // ➕ thêm
  targetOwnerName: string;   // ➕ thêm
  policyID: string;
  policyName: string;
  description: string;
  reportedAt: string;
  verifyStatus: boolean;
  status: ReportStatus;
}