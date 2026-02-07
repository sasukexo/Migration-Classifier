export interface VM {
  "VM Name": string;
  OS: string;
  CPU: number;
  RAM: number;
  "Power State": string;
  decision: string;
  strategy: string;
  risk: string;
  reason: string;
}

export interface ApiResponse {
  total: number;
  summary: Record<string, number>;
  data: VM[];
}
